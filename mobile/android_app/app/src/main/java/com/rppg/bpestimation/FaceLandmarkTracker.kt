package com.rppg.bpestimation

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.ImageFormat
import android.graphics.Matrix
import android.graphics.Rect
import android.graphics.RectF
import android.graphics.YuvImage
import android.media.Image
import com.google.mediapipe.framework.image.BitmapImageBuilder
import com.google.mediapipe.framework.image.MPImage
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.vision.core.RunningMode
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarker
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarkerResult
import java.io.ByteArrayOutputStream
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

class FaceLandmarkTracker(
    private val context: Context,
    private val onResult: (FloatArray, RectF?, RectF?, RectF?, FloatArray?, FloatArray?, Float, Long) -> Unit
) {
    var isFrontCamera: Boolean = true
    private var faceLandmarker: FaceLandmarker? = null
    
    private val landmarkExecutor = Executors.newSingleThreadExecutor()
    private val isLandmarking = AtomicBoolean(false)
    private var lastLandmarkTime = 0L

    @Volatile private var targetCentralBox: RectF? = null
    @Volatile private var targetLeftBox: RectF? = null
    @Volatile private var targetRightBox: RectF? = null
    @Volatile private var targetLCheekBox: RectF? = null
    @Volatile private var targetRCheekBox: RectF? = null
    @Volatile private var targetNormCentralBox: RectF? = null
    @Volatile private var targetNormLeftBox: RectF? = null
    @Volatile private var targetNormRightBox: RectF? = null
    @Volatile private var targetNormLCheekBox: RectF? = null
    @Volatile private var targetNormRCheekBox: RectF? = null

    @Volatile private var smoothCentralBox: RectF? = null
    @Volatile private var smoothLeftBox: RectF? = null
    @Volatile private var smoothRightBox: RectF? = null
    @Volatile private var smoothLCheekBox: RectF? = null
    @Volatile private var smoothRCheekBox: RectF? = null
    
    @Volatile private var latestSecFeatures: FloatArray? = null
    @Volatile private var latestFacePts: FloatArray? = null

    init {
        val baseOptions = BaseOptions.builder()
            .setModelAssetPath("face_landmarker.task")
            .setDelegate(com.google.mediapipe.tasks.core.Delegate.GPU)
            .build()

        val options = FaceLandmarker.FaceLandmarkerOptions.builder()
            .setBaseOptions(baseOptions)
            .setRunningMode(RunningMode.LIVE_STREAM)
            .setResultListener(this::returnLivestreamResult)
            .setErrorListener { error -> 
                error.printStackTrace() 
                isLandmarking.set(false)
            }
            .build()

        faceLandmarker = FaceLandmarker.createFromOptions(context, options)
    }

    private fun glideBox(current: RectF?, target: RectF, alpha: Float = 0.2f): RectF {
        if (current == null) return RectF(target)
        return RectF(
            current.left + (target.left - current.left) * alpha,
            current.top + (target.top - current.top) * alpha,
            current.right + (target.right - current.right) * alpha,
            current.bottom + (target.bottom - current.bottom) * alpha
        )
    }

    fun processImage(image: Image) {
        val imageTimestampMs = image.timestamp / 1000000L
        
        // 1. FAST PATH: Synchronous 30 FPS RGB extraction using EMA smoothed bounding boxes
        val meanRGB = FloatArray(15)
        if (targetCentralBox != null) {
            smoothCentralBox = glideBox(smoothCentralBox, targetCentralBox!!)
            smoothLeftBox = glideBox(smoothLeftBox, targetLeftBox!!)
            smoothRightBox = glideBox(smoothRightBox, targetRightBox!!)
            smoothLCheekBox = glideBox(smoothLCheekBox, targetLCheekBox!!)
            smoothRCheekBox = glideBox(smoothRCheekBox, targetRCheekBox!!)
            
            val rgb1 = getRgbFromYuvBox(image, smoothCentralBox!!)
            val rgb2 = getRgbFromYuvBox(image, smoothLeftBox!!)
            val rgb3 = getRgbFromYuvBox(image, smoothRightBox!!)
            val rgb4 = getRgbFromYuvBox(image, smoothLCheekBox!!)
            val rgb5 = getRgbFromYuvBox(image, smoothRCheekBox!!)
            
            System.arraycopy(rgb1, 0, meanRGB, 0, 3)
            System.arraycopy(rgb2, 0, meanRGB, 3, 3)
            System.arraycopy(rgb3, 0, meanRGB, 6, 3)
            System.arraycopy(rgb4, 0, meanRGB, 9, 3)
            System.arraycopy(rgb5, 0, meanRGB, 12, 3)
            
            val combinedForeheadBox = RectF(targetNormCentralBox).apply {
                union(targetNormLeftBox!!)
                union(targetNormRightBox!!)
            }
            onResult(meanRGB, combinedForeheadBox, targetNormLCheekBox, targetNormRCheekBox, latestSecFeatures, latestFacePts, latestEar, imageTimestampMs)
        } else {
            onResult(meanRGB, null, null, null, null, null, 0.3f, imageTimestampMs)
        }

        // 2. SLOW PATH: MediaPipe Face Tracking dynamically limited to ~15 FPS
        if (System.currentTimeMillis() - lastLandmarkTime > 60) {
            if (isLandmarking.compareAndSet(false, true)) {
                lastLandmarkTime = System.currentTimeMillis()
                val width = image.width
                val height = image.height
                val nv21Bytes = copyYuvToNv21Safe(image)
                
                landmarkExecutor.execute {
                    try {
                        val bitmap = nv21ToBitmap(nv21Bytes, width, height)
                        val matrix = Matrix()
                        if (isFrontCamera) {
                            matrix.postRotate(-90f)
                            matrix.postScale(-1f, 1f)
                        } else {
                            matrix.postRotate(90f)
                        }
                        val rotatedBitmap = Bitmap.createBitmap(bitmap, 0, 0, width, height, matrix, true)
                        bitmap.recycle()
                        
                        val mpImage = BitmapImageBuilder(rotatedBitmap).build()
                        faceLandmarker?.detectAsync(mpImage, imageTimestampMs)
                        rotatedBitmap.recycle()
                    } catch (e: Exception) {
                        e.printStackTrace()
                        isLandmarking.set(false)
                    }
                }
            }
        }
    }

    @Volatile private var latestEar: Float = 0.3f

    private fun returnLivestreamResult(result: FaceLandmarkerResult, input: MPImage) {
        val timestampMs = result.timestampMs()
        if (result.faceLandmarks().isNotEmpty()) {
            val landmarks = result.faceLandmarks()[0]
            
            val centralForeheadIndices = listOf(10, 151, 9, 8, 108, 337, 336, 107)
            val leftForeheadIndices = listOf(54, 103, 67, 109, 69, 104, 68, 71)
            val rightForeheadIndices = listOf(284, 332, 297, 338, 299, 333, 298, 301)
            val leftCheekIndices = listOf(116, 117, 118, 119, 100, 126, 209, 49)
            val rightCheekIndices = listOf(345, 346, 347, 348, 329, 355, 429, 279)
            
            targetCentralBox = getMappedBox(landmarks, centralForeheadIndices)
            targetLeftBox = getMappedBox(landmarks, leftForeheadIndices)
            targetRightBox = getMappedBox(landmarks, rightForeheadIndices)
            targetLCheekBox = getMappedBox(landmarks, leftCheekIndices)
            targetRCheekBox = getMappedBox(landmarks, rightCheekIndices)
            
            targetNormCentralBox = getBoundingBox(landmarks, centralForeheadIndices, 1, 1)
            targetNormLeftBox = getBoundingBox(landmarks, leftForeheadIndices, 1, 1)
            targetNormRightBox = getBoundingBox(landmarks, rightForeheadIndices, 1, 1)
            targetNormLCheekBox = getBoundingBox(landmarks, leftCheekIndices, 1, 1)
            targetNormRCheekBox = getBoundingBox(landmarks, rightCheekIndices, 1, 1)
            
            val l33 = landmarks[33]; val l133 = landmarks[133]
            val l159 = landmarks[159]; val l145 = landmarks[145]
            val l1 = landmarks[1]
            
            val vertical = Math.hypot((l159.x() - l145.x()).toDouble(), (l159.y() - l145.y()).toDouble())
            val horizontal = Math.hypot((l33.x() - l133.x()).toDouble(), (l33.y() - l133.y()).toDouble())
            latestEar = if (horizontal > 0) (vertical / horizontal).toFloat() else 0.3f
            
            latestSecFeatures = floatArrayOf(
                l33.x(), l33.y(), l133.x(), l133.y(),
                l159.x(), l159.y(), l145.x(), l145.y(), l1.z()
            )
            
            val facePts = FloatArray(landmarks.size * 2)
            for (i in landmarks.indices) {
                facePts[i * 2] = landmarks[i].x()
                facePts[i * 2 + 1] = landmarks[i].y()
            }
            latestFacePts = facePts
        } else {
            targetCentralBox = null
            smoothCentralBox = null
            latestEar = 0.3f
        }
        isLandmarking.set(false)
    }

    private fun getMappedBox(landmarks: List<com.google.mediapipe.tasks.components.containers.NormalizedLandmark>, indices: List<Int>): RectF {
        var minX = Float.MAX_VALUE
        var minY = Float.MAX_VALUE
        var maxX = Float.MIN_VALUE
        var maxY = Float.MIN_VALUE
        for (i in indices) {
            val px = landmarks[i].x()
            val py = landmarks[i].y()
            val lx = if (isFrontCamera) 1 - py else py
            val ly = 1 - px
            if (lx < minX) minX = lx
            if (ly < minY) minY = ly
            if (lx > maxX) maxX = lx
            if (ly > maxY) maxY = ly
        }
        return RectF(minX, minY, maxX, maxY)
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

    private fun getRgbFromYuvBox(image: Image, box: RectF): FloatArray {
        val width = image.width
        val height = image.height
        val left = (box.left * width).toInt().coerceIn(0, width - 1)
        val top = (box.top * height).toInt().coerceIn(0, height - 1)
        val right = (box.right * width).toInt().coerceIn(0, width - 1)
        val bottom = (box.bottom * height).toInt().coerceIn(0, height - 1)
        
        if (right <= left || bottom <= top) return floatArrayOf(0f, 0f, 0f)
        
        val yPlane = image.planes[0]
        val uPlane = image.planes[1]
        val vPlane = image.planes[2]
        val yRowStride = yPlane.rowStride
        val uvRowStride = uPlane.rowStride
        val uvPixelStride = uPlane.pixelStride
        
        var rSum = 0f; var gSum = 0f; var bSum = 0f
        var count = 0
        
        val yBuffer = yPlane.buffer
        val uBuffer = uPlane.buffer
        val vBuffer = vPlane.buffer
        
        for (y in top..bottom step 2) {
            val yOffset = y * yRowStride
            val uvOffset = (y shr 1) * uvRowStride
            for (x in left..right step 2) {
                val yIdx = yOffset + x
                val uvIdx = uvOffset + (x shr 1) * uvPixelStride
                
                val yVal = (yBuffer.get(yIdx).toInt() and 0xFF)
                val uVal = (uBuffer.get(uvIdx).toInt() and 0xFF) - 128
                val vVal = (vBuffer.get(uvIdx).toInt() and 0xFF) - 128
                
                val r = yVal + 1.370705f * vVal
                val g = yVal - 0.337633f * uVal - 0.698001f * vVal
                val b = yVal + 1.732446f * uVal
                
                rSum += r.coerceIn(0f, 255f); gSum += g.coerceIn(0f, 255f); bSum += b.coerceIn(0f, 255f)
                count++
            }
        }
        if (count == 0) return floatArrayOf(0f, 0f, 0f)
        return floatArrayOf(rSum / count, gSum / count, bSum / count)
    }

    private fun copyYuvToNv21Safe(image: Image): ByteArray {
        val width = image.width
        val height = image.height
        val nv21 = ByteArray(width * height * 3 / 2)
        
        val yPlane = image.planes[0]
        val yBuffer = yPlane.buffer
        val yRowStride = yPlane.rowStride
        var pos = 0
        
        if (yRowStride == width) {
            yBuffer.get(nv21, 0, width * height)
            pos = width * height
        } else {
            val yBytes = ByteArray(yBuffer.remaining())
            yBuffer.get(yBytes)
            for (r in 0 until height) {
                System.arraycopy(yBytes, r * yRowStride, nv21, pos, width)
                pos += width
            }
        }
        
        val uPlane = image.planes[1]
        val vPlane = image.planes[2]
        val vBuffer = vPlane.buffer
        val uBuffer = uPlane.buffer
        val uvRowStride = vPlane.rowStride
        val uvPixelStride = vPlane.pixelStride
        
        val vBytes = ByteArray(vBuffer.remaining())
        vBuffer.get(vBytes)
        val uBytes = ByteArray(uBuffer.remaining())
        uBuffer.get(uBytes)
        
        for (r in 0 until height / 2) {
            val rowOffset = r * uvRowStride
            for (c in 0 until width / 2) {
                val uvIdx = rowOffset + c * uvPixelStride
                nv21[pos++] = vBytes[uvIdx]
                nv21[pos++] = uBytes[uvIdx]
            }
        }
        
        yBuffer.rewind()
        uBuffer.rewind()
        vBuffer.rewind()
        
        return nv21
    }

    private fun nv21ToBitmap(nv21: ByteArray, width: Int, height: Int): Bitmap {
        val yuvImage = YuvImage(nv21, ImageFormat.NV21, width, height, null)
        val out = ByteArrayOutputStream()
        yuvImage.compressToJpeg(Rect(0, 0, width, height), 100, out)
        val bytes = out.toByteArray()
        return BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
    }
}
