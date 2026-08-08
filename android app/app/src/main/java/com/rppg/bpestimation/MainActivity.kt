package com.rppg.bpestimation

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.SurfaceTexture
import android.os.Bundle
import android.os.Environment
import android.view.TextureView
import android.widget.TextView
import android.widget.Toast
import android.view.animation.AnimationUtils
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import android.os.Handler
import android.os.Looper
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import com.google.android.material.floatingactionbutton.FloatingActionButton
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.*
import kotlin.math.roundToInt
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var cameraService: CameraService
    private lateinit var faceLandmarkTracker: FaceLandmarkTracker

    private lateinit var viewFinder: TextureView
    private lateinit var overlayView: OverlayView
    private lateinit var bvpChart: LineChart
    private lateinit var bpEngine: BPInferenceEngine
    
    private lateinit var tvBP: TextView
    private lateinit var tvMAP: TextView
    private lateinit var tvHR: TextView
    private lateinit var tvHRV: TextView
    private lateinit var tvDiagnosisBadge: TextView
    private lateinit var tvFPS: TextView
    
    private lateinit var btnStartScan: android.widget.Button
    private lateinit var progressBar: android.widget.ProgressBar
    private lateinit var loadingSpinner: android.widget.ProgressBar
    
    enum class AppState { IDLE, CALIBRATING, RECORDING, PROCESSING, RESULT }
    @Volatile private var appState = AppState.IDLE
    
    private var frameCount = 0
    private var lastFpsTime = 0L

    // Signal buffer (needs roughly 7 seconds of data, MAX_BUFFER_SIZE frames)
    private val FPS = 30f
    private val WINDOW_SIZE_SECONDS = 7f
    private val MAX_BUFFER_SIZE = (FPS * WINDOW_SIZE_SECONDS).toInt() // ~210 frames

    // Flat primitive arrays for strict memory bounding
    private val rgbBuffer = FloatArray(MAX_BUFFER_SIZE * 3)
    private val timestampBuffer = LongArray(MAX_BUFFER_SIZE)
    private val securityBuffer = FloatArray(MAX_BUFFER_SIZE * 9)
    private var bufferCount = 0

    private val chartEntries = mutableListOf<Entry>()
    private var chartX = 0f

    // Bounding CSV exports to the last 2 minutes to prevent OOM
    private val allExtractedData = java.util.ArrayDeque<FloatArray>()
    private val allVitalsLog = java.util.ArrayDeque<String>()
    
    private val uiHandler = Handler(Looper.getMainLooper())
    
    private var sessionState = "INITIAL_VERIFICATION"
    private var lastFaceSeenTime = System.currentTimeMillis()
    
    // EMA smoothing state
    private var smoothedHR: Float? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_main)

        viewFinder = findViewById(R.id.viewFinder)
        overlayView = findViewById(R.id.overlayView)
        bvpChart = findViewById(R.id.bvpChart)
        
        tvBP = findViewById(R.id.tvBP)
        tvMAP = findViewById(R.id.tvMAP)
        tvHR = findViewById(R.id.tvHR)
        tvHRV = findViewById(R.id.tvHRV)
        tvDiagnosisBadge = findViewById(R.id.tvDiagnosisBadge)
        
        findViewById<FloatingActionButton>(R.id.fabExport).setOnClickListener {
            exportDataToCSV()
        }
        
        findViewById<FloatingActionButton>(R.id.fabHelp).setOnClickListener {
            HelpBottomSheetDialogFragment().show(supportFragmentManager, "HelpBottomSheet")
        }

        findViewById<FloatingActionButton>(R.id.fabSwitchCamera).setOnClickListener {
            if (::cameraService.isInitialized && ::faceLandmarkTracker.isInitialized) {
                cameraService.switchCamera()
                faceLandmarkTracker.isFrontCamera = (cameraService.activeLensFacing == android.hardware.camera2.CameraCharacteristics.LENS_FACING_FRONT)
                
                // Clear buffers on switch
                synchronized(rgbBuffer) {
                    bufferCount = 0
                }
                appState = AppState.IDLE
                smoothedHR = null
                if (::cameraService.isInitialized) {
                    cameraService.unlockExposure()
                }
                
                runOnUiThread {
                    resetUIForIdle()
                    tvDiagnosisBadge.text = "SWITCHING LENS..."
                    tvDiagnosisBadge.setBackgroundColor(Color.parseColor("#555555"))
                }
            }
        }

        setupChart()
        bpEngine = BPInferenceEngine(this)

        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        
        btnStartScan = findViewById(R.id.btnStartScan)
        progressBar = findViewById(R.id.progressBar)
        loadingSpinner = findViewById(R.id.loadingSpinner)
        tvFPS = findViewById(R.id.tvFPS)
        
        btnStartScan.setOnClickListener {
            startRecordingState()
        }
        
        resetUIForIdle()
        
        if (allPermissionsGranted()) {
            startPipeline()
        } else {
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS)
        }
    }
    
    private fun setupChart() {
        bvpChart.description.isEnabled = false
        bvpChart.setTouchEnabled(false)
        bvpChart.isDragEnabled = false
        bvpChart.setScaleEnabled(false)
        bvpChart.setDrawGridBackground(false)
        
        bvpChart.axisLeft.setDrawGridLines(false)
        bvpChart.xAxis.setDrawGridLines(false)
        bvpChart.setVisibleXRangeMaximum(200f)
        bvpChart.setNoDataText("WAITING FOR VITAL SIGNS...")
        
        val dataSet = LineDataSet(chartEntries, "BVP Waveform").apply {
            color = Color.CYAN
            setDrawCircles(false)
            lineWidth = 2f
            mode = LineDataSet.Mode.CUBIC_BEZIER
            setDrawHighlightIndicators(false)
            isHighlightEnabled = false
        }
        bvpChart.data = LineData(dataSet)
        bvpChart.axisLeft.textColor = Color.WHITE
        bvpChart.axisRight.isEnabled = false
        bvpChart.xAxis.isEnabled = false
        bvpChart.legend.textColor = Color.WHITE
    }

    private fun resetUIForIdle() {
        btnStartScan.visibility = android.view.View.VISIBLE
        btnStartScan.text = "START SCAN"
        progressBar.visibility = android.view.View.GONE
        loadingSpinner.visibility = android.view.View.GONE
        tvDiagnosisBadge.text = "READY"
        tvDiagnosisBadge.setBackgroundColor(Color.parseColor("#555555"))
    }

    private fun startRecordingState() {
        appState = AppState.CALIBRATING
        if (::cameraService.isInitialized) {
            cameraService.unlockExposure() // Unlock to adapt to torch
            cameraService.setTorchEnabled(true)
        }
        
        runOnUiThread {
            btnStartScan.visibility = android.view.View.GONE
            tvDiagnosisBadge.text = "CALIBRATING EXPOSURE..."
            tvDiagnosisBadge.setBackgroundColor(Color.parseColor("#FF9800"))
            
            progressBar.visibility = android.view.View.GONE
            loadingSpinner.visibility = android.view.View.GONE
        }
        
        // Wait 1.5s for the torch to fully illuminate and the ISP to roughly adjust
        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Main).launch {
            kotlinx.coroutines.delay(1500)
            if (appState != AppState.CALIBRATING) return@launch
            
            // Trigger Precapture sequence and wait for convergence
            if (::cameraService.isInitialized) {
                cameraService.lockExposureAndStart {
                    if (appState != AppState.CALIBRATING) return@lockExposureAndStart
                    
                    appState = AppState.RECORDING
            lastFaceSeenTime = System.currentTimeMillis() // Reset to prevent instant timeout
            
            synchronized(rgbBuffer) {
                bufferCount = 0
            }
            
            progressBar.visibility = android.view.View.VISIBLE
            progressBar.progress = 0
            loadingSpinner.visibility = android.view.View.GONE
            tvDiagnosisBadge.text = "RECORDING (0/${MAX_BUFFER_SIZE})"
            tvDiagnosisBadge.setBackgroundColor(Color.parseColor("#007BFF"))
            
            // Clear chart
            val data = bvpChart.data
            val dataSet = data.getDataSetByIndex(0)
            dataSet.clear()
            chartX = 0f
            data.notifyDataChanged()
            bvpChart.notifyDataSetChanged()
            bvpChart.invalidate()
            
            tvBP.text = "POS Extracted"
            tvMAP.text = "Crest Time: -- ms"
            tvHR.text = "-- BPM"
            tvHRV.text = "HRV: -- ms"
                }
            }
        }
    }

    private fun startPipeline() {
        cameraService = CameraService(this)
        faceLandmarkTracker = FaceLandmarkTracker(this) { rgb, fh, lc, rc, secFeatures, facePts, timestampMs ->
            if (appState != AppState.RECORDING) return@FaceLandmarkTracker
            
            runOnUiThread {
                overlayView.updateBoxes(fh, lc, rc, facePts)
            }
            if (rgb[0] != 0f) {
                lastFaceSeenTime = System.currentTimeMillis()
                processRgbData(rgb, secFeatures, timestampMs)
            } else {
                if (System.currentTimeMillis() - lastFaceSeenTime > 2000) {
                    sessionState = "INITIAL_VERIFICATION"
                    synchronized(rgbBuffer) {
                        bufferCount = 0
                    }
                    runOnUiThread {
                        if (appState == AppState.RECORDING || appState == AppState.CALIBRATING) {
                            appState = AppState.IDLE
                            if (::cameraService.isInitialized) {
                                cameraService.setTorchEnabled(false)
                                cameraService.unlockExposure()
                            }
                            resetUIForIdle()
                            tvDiagnosisBadge.text = "FACE LOST. RESTARTING..."
                            tvDiagnosisBadge.setBackgroundColor(Color.parseColor("#FF9800"))
                        }
                    }
                }
            }
        }

        cameraService.setOnFrameCallback { image ->
            // FPS tracking
            frameCount++
            val currentTime = System.currentTimeMillis()
            if (currentTime - lastFpsTime >= 1000) {
                val fps = frameCount
                frameCount = 0
                lastFpsTime = currentTime

                runOnUiThread {
                    tvFPS.text = "FPS: $fps"
                }
            }
        
            // In RECORDING state, run MediaPipe. Otherwise, let CameraService close it instantly.
            if (appState == AppState.RECORDING) {
                faceLandmarkTracker.processImage(image)
            }
        }

        viewFinder.surfaceTextureListener = object : TextureView.SurfaceTextureListener {
            override fun onSurfaceTextureAvailable(surface: SurfaceTexture, width: Int, height: Int) {
                cameraService.startCamera(android.view.Surface(surface), width, height)
            }
            override fun onSurfaceTextureSizeChanged(surface: SurfaceTexture, width: Int, height: Int) {}
            override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean = true
            override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
        }
    }

    private fun processRgbData(rgb: FloatArray, secFeatures: FloatArray?, timestampMs: Long) {
        if (appState != AppState.RECORDING) return

        val snapshot: FloatArray
        val timestamps: LongArray
        val securitySnapshot: FloatArray

        synchronized(rgbBuffer) {
            if (bufferCount < MAX_BUFFER_SIZE) {
                val idx = bufferCount
                System.arraycopy(rgb, 0, rgbBuffer, idx * 3, 3)
                timestampBuffer[idx] = timestampMs
                if (secFeatures != null) {
                    System.arraycopy(secFeatures, 0, securityBuffer, idx * 9, 9)
                }
                bufferCount++
            }

            allExtractedData.addLast(rgb.clone())
            if (allExtractedData.size > 3600) allExtractedData.removeFirst()
            
            val currentCount = bufferCount
            runOnUiThread {
                progressBar.progress = currentCount
                tvDiagnosisBadge.text = "RECORDING ($currentCount/$MAX_BUFFER_SIZE)"
            }
            
            // Once 210 frames are collected, switch to processing
            if (bufferCount == MAX_BUFFER_SIZE) {
                appState = AppState.PROCESSING
                if (::cameraService.isInitialized) {
                    cameraService.setTorchEnabled(false)
                    cameraService.unlockExposure()
                }
                
                snapshot = rgbBuffer.clone()
                timestamps = timestampBuffer.clone()
                securitySnapshot = securityBuffer.clone()
            } else {
                return
            }
        }
        
        // Show loading spinner
        runOnUiThread {
            progressBar.visibility = android.view.View.GONE
            loadingSpinner.visibility = android.view.View.VISIBLE
            tvDiagnosisBadge.text = "ANALYZING VITALS..."
            tvDiagnosisBadge.setBackgroundColor(Color.parseColor("#FF9800"))
            overlayView.updateBoxes(null, null, null, null) // clear boxes
        }

        // Run Python inference entirely isolated from camera stream
        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Default).launch {
            try {
                val py = Python.getInstance()
                val posEngine = py.getModule("pos_engine")
                
                val result = posEngine.callAttr("process_window", snapshot, timestamps, securitySnapshot, sessionState)
                
                val statusCode = result.asList()[0].toString()
                if (statusCode != "SUCCESS") {
                    runOnUiThread {
                        tvDiagnosisBadge.text = statusCode.replace("_", " ")
                        tvDiagnosisBadge.setBackgroundColor(Color.parseColor("#D32F2F"))
                        
                        btnStartScan.visibility = android.view.View.VISIBLE
                        btnStartScan.text = "RETRY"
                        loadingSpinner.visibility = android.view.View.GONE
                        appState = AppState.RESULT
                    }
                    return@launch
                }
                
                sessionState = "CONTINUOUS_TRACKING" // verification passed
                
                val posWaveformList = result.asList()[1].asList()
                val ppgArray = FloatArray(posWaveformList.size) { i -> posWaveformList[i].toFloat() }
                
                // Extract 2D tensor for the LSTM [875 x 3]
                val tensorList = result.asList()[2].asList()
                val bvpWindow = Array(tensorList.size) { i ->
                    val row = tensorList[i].asList()
                    FloatArray(row.size) { j -> row[j].toFloat() }
                }
                
                val hr = result.asList()[3].toFloat()
                val hrv = result.asList()[4].toFloat()
                val crestTime = result.asList()[5].toFloat()
                
                Log.e("BPEstimation", "POS Output - HR: $hr, HRV: $hrv, CT: $crestTime, Status: $statusCode")
                
                // Run BP Inference
                val (sbp, dbp) = bpEngine.predict(bvpWindow)
                
                runOnUiThread {
                    updateUI(ppgArray, hr, hrv, crestTime, sbp, dbp)
                }
            } catch (e: Exception) {
                e.printStackTrace()
                runOnUiThread {
                    tvDiagnosisBadge.text = "INFERENCE FAILED"
                    tvDiagnosisBadge.setBackgroundColor(Color.parseColor("#D32F2F"))
                    btnStartScan.visibility = android.view.View.VISIBLE
                    btnStartScan.text = "RETRY"
                    loadingSpinner.visibility = android.view.View.GONE
                    appState = AppState.RESULT
                }
            }
        }
    }

    private fun updateUI(bvpWave: FloatArray, hr: Float, hrv: Float, crestTime: Float, sbp: Float, dbp: Float) {
        appState = AppState.RESULT
        
        btnStartScan.visibility = android.view.View.VISIBLE
        btnStartScan.text = "SCAN AGAIN"
        loadingSpinner.visibility = android.view.View.GONE
        
        // Apply EMA smoothing
        val finalHR = if (smoothedHR == null) hr else (0.2f * hr) + (0.8f * smoothedHR!!)
        smoothedHR = finalHR
        
        // Update Chart (display the static 7-second wave)
        val data = bvpChart.data
        val dataSet = data.getDataSetByIndex(0)
        dataSet.clear()
        chartX = 0f
        
        for (i in bvpWave.indices step (bvpWave.size / 200).coerceAtLeast(1)) {
            dataSet.addEntry(Entry(chartX++, bvpWave[i]))
        }
        
        data.notifyDataChanged()
        bvpChart.notifyDataSetChanged()
        bvpChart.fitScreen()
        bvpChart.invalidate()

        // Update Text
        val map = (sbp + 2 * dbp) / 3f
        tvBP.text = "${sbp.roundToInt()} / ${dbp.roundToInt()} mmHg"
        tvMAP.text = "MAP: ${map.roundToInt()} mmHg\nCT: ${String.format("%.1f", crestTime)} ms"
        tvHR.text = "${finalHR.roundToInt()} BPM"
        tvHRV.text = String.format("HRV: %.1f ms", hrv)

        // Clinical Diagnosis Badge
        tvDiagnosisBadge.text = "SIGNAL ACQUIRED"
        tvDiagnosisBadge.setBackgroundColor(Color.parseColor("#007BFF"))
        
        allVitalsLog.addLast("${System.currentTimeMillis()},${finalHR},${hrv},${crestTime}")
        if (allVitalsLog.size > 240) allVitalsLog.removeFirst() // 2 mins at ~2 updates/sec
    }
    
    private fun exportDataToCSV() {
        try {
            val dir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "rPPG_Logs")
            if (!dir.exists()) dir.mkdirs()
            
            val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
            
            val rgbFile = File(dir, "rgb_trace_$timestamp.csv")
            val rgbWriter = FileWriter(rgbFile)
            rgbWriter.append("R,G,B\n")
            allExtractedData.forEach { rgbWriter.append("${it[0]},${it[1]},${it[2]}\n") }
            rgbWriter.flush()
            rgbWriter.close()
            
            val vitalsFile = File(dir, "vitals_log_$timestamp.csv")
            val vitalsWriter = FileWriter(vitalsFile)
            vitalsWriter.append("Timestamp,HR,HRV_RMSSD,CrestTime_ms\n")
            allVitalsLog.forEach { vitalsWriter.append("$it\n") }
            vitalsWriter.flush()
            vitalsWriter.close()
            
            Toast.makeText(this, "Logs saved to Downloads/rPPG_Logs", Toast.LENGTH_LONG).show()
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(this, "Error saving logs", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroy() {
        if (::bpEngine.isInitialized) {
            bpEngine.close()
        }
        super.onDestroy()
        if (::cameraService.isInitialized) {
            cameraService.stopCamera()
        }
    }

    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            if (allPermissionsGranted()) {
                startPipeline()
            } else {
                Toast.makeText(this, "Permissions not granted by the user.", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }

    companion object {
        private const val REQUEST_CODE_PERMISSIONS = 10
        private val REQUIRED_PERMISSIONS = arrayOf(Manifest.permission.CAMERA)
    }
}
