package com.rppg.bpestimation

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.ImageFormat
import android.hardware.camera2.*
import android.media.Image
import android.media.ImageReader
import android.os.Handler
import android.os.HandlerThread
import android.util.Range
import android.util.Size
import android.view.Surface

class CameraService(private val context: Context) {

    private val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
    private var cameraDevice: CameraDevice? = null
    private var captureSession: CameraCaptureSession? = null
    private var imageReader: ImageReader? = null
    private var backgroundThread: HandlerThread? = null
    private var backgroundHandler: Handler? = null
    private var captureRequestBuilder: CaptureRequest.Builder? = null

    private var onFrameCallback: ((Image) -> Unit)? = null
    var activeLensFacing = CameraCharacteristics.LENS_FACING_FRONT
    private var currentSurface: Surface? = null
    private var currentWidth: Int = 0
    private var currentHeight: Int = 0

    // Non-blocking analysis architecture
    private val frameAnalysisExecutor = java.util.concurrent.Executors.newSingleThreadExecutor()
    private val isAnalyzing = java.util.concurrent.atomic.AtomicBoolean(false)

    fun switchCamera() {
        activeLensFacing = if (activeLensFacing == CameraCharacteristics.LENS_FACING_FRONT) {
            CameraCharacteristics.LENS_FACING_BACK
        } else {
            CameraCharacteristics.LENS_FACING_FRONT
        }
        
        stopCamera()
        currentSurface?.let { startCamera(it, currentWidth, currentHeight) }
    }

    fun setOnFrameCallback(callback: (Image) -> Unit) {
        this.onFrameCallback = callback
    }

    private fun startBackgroundThread() {
        backgroundThread = HandlerThread("CameraBackground").also { it.start() }
        backgroundHandler = Handler(backgroundThread!!.looper)
    }

    private fun stopBackgroundThread() {
        backgroundThread?.quitSafely()
        try {
            backgroundThread?.join()
            backgroundThread = null
            backgroundHandler = null
        } catch (e: InterruptedException) {
            e.printStackTrace()
        }
    }

    @SuppressLint("MissingPermission")
    fun startCamera(previewSurface: Surface, width: Int, height: Int) {
        currentSurface = previewSurface
        currentWidth = width
        currentHeight = height
        startBackgroundThread()
        try {
            val cameraId = cameraManager.cameraIdList.firstOrNull { id ->
                val chars = cameraManager.getCameraCharacteristics(id)
                chars.get(CameraCharacteristics.LENS_FACING) == activeLensFacing
            } ?: cameraManager.cameraIdList.first()

            val chars = cameraManager.getCameraCharacteristics(cameraId)
            val map = chars.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
            val supportedSizes = map?.getOutputSizes(ImageFormat.YUV_420_888)
            
            // Pick a lower resolution (closest to 640x480) for the ImageReader to optimize MediaPipe
            val targetSize = supportedSizes?.minByOrNull { size ->
                Math.abs((size.width * size.height) - (640 * 480))
            } ?: Size(640, 480)

            imageReader = ImageReader.newInstance(targetSize.width, targetSize.height, ImageFormat.YUV_420_888, 2).apply {
                setOnImageAvailableListener({ reader ->
                    val image = reader.acquireLatestImage() ?: return@setOnImageAvailableListener
                    
                    // Emulate STRATEGY_KEEP_ONLY_LATEST by dropping frames if the analyzer is busy
                    if (isAnalyzing.get()) {
                        image.close()
                        return@setOnImageAvailableListener
                    }
                    
                    isAnalyzing.set(true)
                    frameAnalysisExecutor.execute {
                        try {
                            onFrameCallback?.invoke(image)
                        } catch (e: Exception) {
                            e.printStackTrace()
                        } finally {
                            // Ensure memory buffer is instantly returned to OS, preventing starvation
                            image.close()
                            isAnalyzing.set(false)
                        }
                    }
                }, backgroundHandler)
            }

            cameraManager.openCamera(cameraId, object : CameraDevice.StateCallback() {
                override fun onOpened(camera: CameraDevice) {
                    cameraDevice = camera
                    createCameraPreviewSession(previewSurface)
                }

                override fun onDisconnected(camera: CameraDevice) {
                    camera.close()
                    cameraDevice = null
                }

                override fun onError(camera: CameraDevice, error: Int) {
                    camera.close()
                    cameraDevice = null
                }
            }, backgroundHandler)

        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun createCameraPreviewSession(previewSurface: Surface) {
        try {
            val surface = imageReader!!.surface
            val surfaces = listOf(previewSurface, surface)

            captureRequestBuilder = cameraDevice!!.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW).apply {
                addTarget(previewSurface)
                addTarget(surface)

                // Flash is OFF by default, will be turned on during scanning via setTorchEnabled()
                set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_OFF)

                // 2. Hardware-Locked Camera Pipeline Settings
                
                // Use auto mode so we don't get a completely black frame, 
                // but disable scene modes (which often include beauty filters)
                set(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO)
                set(CaptureRequest.CONTROL_SCENE_MODE, CaptureRequest.CONTROL_SCENE_MODE_DISABLED)
                
                // Enable Auto-Exposure and Auto-White Balance so the camera can see.
                // (Setting these to OFF without manually providing ISO and Shutter Speed results in a black screen)
                set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
                set(CaptureRequest.CONTROL_AWB_MODE, CaptureRequest.CONTROL_AWB_MODE_AUTO)
                
                // 3. Lock Auto-Exposure and White Balance (Prevents dynamic brightening when face enters)
                // 3. Lock Auto-Exposure and White Balance (Prevents dynamic brightening when face enters)
                // Initialize to false so the camera can adapt to ambient light first
                set(CaptureRequest.CONTROL_AE_LOCK, false)
                set(CaptureRequest.CONTROL_AWB_LOCK, false)
                
                // 4. Disable Color Correction which can corrupt the raw RGB signal
                set(CaptureRequest.COLOR_CORRECTION_ABERRATION_MODE, CaptureRequest.COLOR_CORRECTION_ABERRATION_MODE_FAST)
                set(CaptureRequest.COLOR_CORRECTION_MODE, CaptureRequest.COLOR_CORRECTION_MODE_FAST)
                
                set(CaptureRequest.LENS_OPTICAL_STABILIZATION_MODE, CaptureRequest.LENS_OPTICAL_STABILIZATION_MODE_OFF)
                
                // Set NOISE_REDUCTION_MODE to OFF and EDGE_MODE to OFF.
                set(CaptureRequest.NOISE_REDUCTION_MODE, CaptureRequest.NOISE_REDUCTION_MODE_OFF)
                set(CaptureRequest.EDGE_MODE, CaptureRequest.EDGE_MODE_OFF)
                
                // Lock sensor frame capture to a strict, unthrottled 30 FPS.
                set(CaptureRequest.CONTROL_AE_TARGET_FPS_RANGE, Range(30, 30))
            }

            cameraDevice!!.createCaptureSession(surfaces, object : CameraCaptureSession.StateCallback() {
                override fun onConfigured(session: CameraCaptureSession) {
                    if (cameraDevice == null) return
                    captureSession = session
                    try {
                        captureSession!!.setRepeatingRequest(captureRequestBuilder!!.build(), captureCallback, backgroundHandler)
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }

                override fun onConfigureFailed(session: CameraCaptureSession) {
                }
            }, null)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun setTorchEnabled(enabled: Boolean) {
        if (activeLensFacing != CameraCharacteristics.LENS_FACING_BACK) return
        try {
            captureRequestBuilder?.set(CaptureRequest.FLASH_MODE, if (enabled) CaptureRequest.FLASH_MODE_TORCH else CaptureRequest.FLASH_MODE_OFF)
            captureRequestBuilder?.let {
                captureSession?.setRepeatingRequest(it.build(), null, backgroundHandler)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private var lastExposureTime: Long? = null
    private var lastSensitivity: Int? = null

    private val captureCallback = object : CameraCaptureSession.CaptureCallback() {
        override fun onCaptureCompleted(session: CameraCaptureSession, request: CaptureRequest, result: TotalCaptureResult) {
            val aeMode = request.get(CaptureRequest.CONTROL_AE_MODE)
            if (aeMode != CaptureRequest.CONTROL_AE_MODE_OFF) {
                lastExposureTime = result.get(CaptureResult.SENSOR_EXPOSURE_TIME)
                lastSensitivity = result.get(CaptureResult.SENSOR_SENSITIVITY)
            }
        }
    }

    fun setExposureAndWhiteBalanceLock(locked: Boolean) {
        try {
            if (locked && lastExposureTime != null && lastSensitivity != null) {
                // HARD-LOCK: Disable auto-exposure entirely and freeze sensor at last known values
                captureRequestBuilder?.set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_OFF)
                captureRequestBuilder?.set(CaptureRequest.SENSOR_EXPOSURE_TIME, lastExposureTime)
                captureRequestBuilder?.set(CaptureRequest.SENSOR_SENSITIVITY, lastSensitivity)
            } else {
                // UNLOCK: Re-enable auto-exposure
                captureRequestBuilder?.set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
            }

            // Also request the standard soft-locks
            captureRequestBuilder?.set(CaptureRequest.CONTROL_AE_LOCK, locked)
            captureRequestBuilder?.set(CaptureRequest.CONTROL_AWB_LOCK, locked)
            
            captureRequestBuilder?.let {
                captureSession?.setRepeatingRequest(it.build(), captureCallback, backgroundHandler)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun stopCamera() {
        captureSession?.close()
        captureSession = null
        cameraDevice?.close()
        cameraDevice = null
        imageReader?.close()
        imageReader = null
        stopBackgroundThread()
    }
}
