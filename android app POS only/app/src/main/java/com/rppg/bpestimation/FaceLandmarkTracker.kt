package com.rppg.bpestimation

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Color
import android.graphics.ImageFormat
import android.graphics.Matrix
import android.graphics.Rect
import android.graphics.RectF
import android.graphics.YuvImage
import android.media.Image
import android.os.SystemClock
import com.google.mediapipe.framework.image.BitmapImageBuilder
import com.google.mediapipe.framework.image.MPImage
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.vision.core.RunningMode
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarker
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarkerResult
import java.io.ByteArrayOutputStream

class FaceLandmarkTracker(
    private val context: Context,
    private val onResult: (FloatArray, RectF?, RectF?, RectF?, FloatArray?, FloatArray?, Long) -> Unit
) {

    var isFrontCamera: Boolean = true
    private var faceLandmarker: FaceLandmarker? = null
    
    // Store bitmaps temporarily for the async callback, keyed by timestamp
    private val pendingBitmaps = java.util.concurrent.ConcurrentHashMap<Long, Bitmap>()

    companion object {
        @Volatile
        private var faceLandmarkerInstance: FaceLandmarker? = null
        private var currentListener: ((FaceLandmarkerResult, MPImage) -> Unit)? = null
        
        fun getFaceLandmarker(context: Context, listener: (FaceLandmarkerResult, MPImage) -> Unit): FaceLandmarker {
            currentListener = listener
            return faceLandmarkerInstance ?: synchronized(this) {
                faceLandmarkerInstance ?: createFaceLandmarker(context).also { faceLandmarkerInstance = it }
            }
        }

        private fun createFaceLandmarker(context: Context): FaceLandmarker {
            val baseOptions = BaseOptions.builder()
                .setModelAssetPath("face_landmarker.task")
                .setDelegate(com.google.mediapipe.tasks.core.Delegate.GPU)
                .build()

            val options = FaceLandmarker.FaceLandmarkerOptions.builder()
                .setBaseOptions(baseOptions)
                .setRunningMode(RunningMode.LIVE_STREAM)
                .setResultListener { result, image -> currentListener?.invoke(result, image) }
                .setErrorListener { error -> error.printStackTrace() }
                .build()

            return FaceLandmarker.createFromOptions(context, options)
        }
    }

    private var maskBitmap: Bitmap? = null
    private var maskCanvas: android.graphics.Canvas? = null
    private val maskPaint = android.graphics.Paint().apply {
        color = Color.WHITE
        style = android.graphics.Paint.Style.FILL
    }
    private val clearPaint = android.graphics.Paint().apply {
        color = Color.BLACK
        style = android.graphics.Paint.Style.FILL
    }

    init {
        faceLandmarker = getFaceLandmarker(context, this::returnLivestreamResult)
    }

    fun processImage(image: Image) {
        val bitmap = imageToBitmap(image)
        val imageTimestampMs = image.timestamp / 1000000L
        
        if (bitmap == null) return
        
        // Rotate and mirror dynamically based on active lens (assuming portrait)
        val matrix = Matrix()
        if (isFrontCamera) {
            matrix.postRotate(-90f)
            matrix.postScale(-1f, 1f) // Mirror
        } else {
            matrix.postRotate(90f) // Rear camera does not need horizontal mirror
        }
        
        val rotatedBitmap = Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
        
        // Recycle the intermediate bitmap immediately
        bitmap.recycle()
        
        // Clean up pending bitmaps that might have been dropped by MediaPipe
        val iterator = pendingBitmaps.iterator()
        while (iterator.hasNext()) {
            val entry = iterator.next()
            if (imageTimestampMs - entry.key > 1000) {
                entry.value.recycle()
                iterator.remove()
            }
        }
        
        pendingBitmaps[imageTimestampMs] = rotatedBitmap
        
        val mpImage = BitmapImageBuilder(rotatedBitmap).build()
        
        faceLandmarker?.detectAsync(mpImage, imageTimestampMs)
    }

    private fun returnLivestreamResult(result: FaceLandmarkerResult, input: MPImage) {
        val timestamp = result.timestampMs()
        val bitmap = pendingBitmaps.remove(timestamp) ?: return
        
        if (result.faceLandmarks().isNotEmpty()) {
            val landmarks = result.faceLandmarks()[0]
            
            val width = bitmap.width
            val height = bitmap.height
            
            if (maskBitmap == null || maskBitmap!!.width != width || maskBitmap!!.height != height) {
                maskBitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
                maskCanvas = android.graphics.Canvas(maskBitmap!!)
            }
            
            // Forehead: 54, 103, 67, 109, 10, 338, 297, 332, 284, 298, 333, 299, 337, 151, 108, 69, 104, 68
            val foreheadIndices = listOf(54, 103, 67, 109, 10, 338, 297, 332, 284, 298, 333, 299, 337, 151, 108, 69, 104, 68)
            // Left cheek: 116, 117, 118, 119, 100, 126, 209, 49, 129, 203, 205
            val leftCheekIndices = listOf(116, 117, 118, 119, 100, 126, 209, 49, 129, 203, 205)
            // Right cheek: 345, 346, 347, 348, 329, 355, 429, 279, 358, 423, 425
            val rightCheekIndices = listOf(345, 346, 347, 348, 329, 355, 429, 279, 358, 423, 425)
            
            val foreheadBox = getBoundingBox(landmarks, foreheadIndices, width, height)
            val leftCheekBox = getBoundingBox(landmarks, leftCheekIndices, width, height)
            val rightCheekBox = getBoundingBox(landmarks, rightCheekIndices, width, height)
            
            val foreheadPath = getPolygonPath(landmarks, foreheadIndices, width, height)
            val leftCheekPath = getPolygonPath(landmarks, leftCheekIndices, width, height)
            val rightCheekPath = getPolygonPath(landmarks, rightCheekIndices, width, height)
            
            maskCanvas?.drawPaint(clearPaint)
            maskCanvas?.drawPath(foreheadPath, maskPaint)
            maskCanvas?.drawPath(leftCheekPath, maskPaint)
            maskCanvas?.drawPath(rightCheekPath, maskPaint)
            
            val overallBox = RectF(foreheadBox)
            overallBox.union(leftCheekBox)
            overallBox.union(rightCheekBox)
            
            val averageRGB = getAverageRGBFromMask(bitmap, maskBitmap!!, overallBox)
            
            val meanR = averageRGB[0]
            val meanG = averageRGB[1]
            val meanB = averageRGB[2]
            
            // Extract Security Features: Left Eye (33, 133, 159, 145) and Nose Tip (1)
            val l33 = landmarks[33]
            val l133 = landmarks[133]
            val l159 = landmarks[159]
            val l145 = landmarks[145]
            val l1 = landmarks[1]
            
            val securityFeatures = floatArrayOf(
                l33.x(), l33.y(),
                l133.x(), l133.y(),
                l159.x(), l159.y(),
                l145.x(), l145.y(),
                l1.z()
            )
            
            val normForeheadBox = getBoundingBox(landmarks, foreheadIndices, 1, 1)
            val normLeftCheekBox = getBoundingBox(landmarks, leftCheekIndices, 1, 1)
            val normRightCheekBox = getBoundingBox(landmarks, rightCheekIndices, 1, 1)
            
            // Extract all face points for wireframe (normalized)
            val facePoints = FloatArray(landmarks.size * 2)
            for (i in landmarks.indices) {
                facePoints[i * 2] = landmarks[i].x()
                facePoints[i * 2 + 1] = landmarks[i].y()
            }
            
            onResult(floatArrayOf(meanR, meanG, meanB), normForeheadBox, normLeftCheekBox, normRightCheekBox, securityFeatures, facePoints, timestamp)
        } else {
            // No face detected
            onResult(floatArrayOf(0f, 0f, 0f), null, null, null, null, null, timestamp)
        }
        
        // Ensure memory is returned to OS!
        bitmap.recycle()
    }

    private fun getBoundingBox(landmarks: List<com.google.mediapipe.tasks.components.containers.NormalizedLandmark>, indices: List<Int>, w: Int, h: Int): RectF {
        var minX = Float.MAX_VALUE
        var minY = Float.MAX_VALUE
        var maxX = Float.MIN_VALUE
        var maxY = Float.MIN_VALUE
        
        for (i in indices) {
            val lx = landmarks[i].x() * w
            val ly = landmarks[i].y() * h
            if (lx < minX) minX = lx
            if (ly < minY) minY = ly
            if (lx > maxX) maxX = lx
            if (ly > maxY) maxY = ly
        }
        
        return RectF(minX, minY, maxX, maxY)
    }

    private fun getPolygonPath(landmarks: List<com.google.mediapipe.tasks.components.containers.NormalizedLandmark>, indices: List<Int>, w: Int, h: Int): android.graphics.Path {
        val path = android.graphics.Path()
        if (indices.isEmpty()) return path
        
        for (i in indices.indices) {
            val lx = landmarks[indices[i]].x() * w
            val ly = landmarks[indices[i]].y() * h
            if (i == 0) {
                path.moveTo(lx, ly)
            } else {
                path.lineTo(lx, ly)
            }
        }
        path.close()
        return path
    }

    private fun getAverageRGBFromMask(bitmap: Bitmap, mask: Bitmap, box: RectF): FloatArray {
        var rSum = 0f
        var gSum = 0f
        var bSum = 0f
        var count = 0
        
        val left = box.left.toInt().coerceAtLeast(0)
        val top = box.top.toInt().coerceAtLeast(0)
        val right = box.right.toInt().coerceAtMost(bitmap.width - 1)
        val bottom = box.bottom.toInt().coerceAtMost(bitmap.height - 1)
        
        if (right <= left || bottom <= top) return floatArrayOf(0f, 0f, 0f)

        val w = right - left
        val h = bottom - top
        
        val maskPixels = IntArray(w * h)
        val bitmapPixels = IntArray(w * h)
        
        mask.getPixels(maskPixels, 0, w, left, top, w, h)
        bitmap.getPixels(bitmapPixels, 0, w, left, top, w, h)
        
        for (i in 0 until w * h) {
            if (maskPixels[i] != Color.BLACK) {
                val pixel = bitmapPixels[i]
                rSum += Color.red(pixel)
                gSum += Color.green(pixel)
                bSum += Color.blue(pixel)
                count++
            }
        }
        
        if (count == 0) return floatArrayOf(0f, 0f, 0f)
        return floatArrayOf(rSum / count, gSum / count, bSum / count)
    }

    private fun imageToBitmap(image: Image): Bitmap? {
        val yPlane = image.planes[0]
        val uPlane = image.planes[1]
        val vPlane = image.planes[2]

        val yBuffer = yPlane.buffer
        val uBuffer = uPlane.buffer
        val vBuffer = vPlane.buffer

        val yRowStride = yPlane.rowStride
        val uvRowStride = uPlane.rowStride
        val uvPixelStride = uPlane.pixelStride

        val width = image.width
        val height = image.height

        val argbArray = IntArray(width * height)

        for (y in 0 until height) {
            val yOffset = y * yRowStride
            val uvOffset = (y shr 1) * uvRowStride

            for (x in 0 until width) {
                val yValue = (yBuffer.get(yOffset + x).toInt() and 0xFF)

                val uvIndex = uvOffset + (x shr 1) * uvPixelStride
                val uValue = (uBuffer.get(uvIndex).toInt() and 0xFF) - 128
                val vValue = (vBuffer.get(uvIndex).toInt() and 0xFF) - 128

                var r = (yValue + 1.370705f * vValue).toInt()
                var g = (yValue - 0.337633f * uValue - 0.698001f * vValue).toInt()
                var b = (yValue + 1.732446f * uValue).toInt()

                r = r.coerceIn(0, 255)
                g = g.coerceIn(0, 255)
                b = b.coerceIn(0, 255)

                argbArray[y * width + x] = (0xFF shl 24) or (r shl 16) or (g shl 8) or b
            }
        }
        
        yBuffer.rewind()
        uBuffer.rewind()
        vBuffer.rewind()

        return Bitmap.createBitmap(argbArray, width, height, Bitmap.Config.ARGB_8888)
    }
}
