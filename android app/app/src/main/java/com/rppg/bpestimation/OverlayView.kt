package com.rppg.bpestimation

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.RectF
import android.util.AttributeSet
import android.view.View

class OverlayView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val boxPaint = Paint().apply {
        color = Color.GREEN
        style = Paint.Style.STROKE
        strokeWidth = 8f
    }
    
    private val pointPaint = Paint().apply {
        color = Color.parseColor("#8000FFFF") // Semi-transparent cyan
        style = Paint.Style.FILL
        strokeWidth = 4f
    }
    
    private var foreheadBox: RectF? = null
    private var leftCheekBox: RectF? = null
    private var rightCheekBox: RectF? = null
    private var facePoints: FloatArray? = null

    fun updateBoxes(forehead: RectF?, leftCheek: RectF?, rightCheek: RectF?, points: FloatArray?) {
        this.foreheadBox = forehead
        this.leftCheekBox = leftCheek
        this.rightCheekBox = rightCheek
        this.facePoints = points
        postInvalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val w = width.toFloat()
        val h = height.toFloat()
        
        // Draw face wireframe points
        facePoints?.let { pts ->
            val scaledPts = FloatArray(pts.size)
            for (i in pts.indices step 2) {
                scaledPts[i] = pts[i] * w
                scaledPts[i+1] = pts[i+1] * h
            }
            canvas.drawPoints(scaledPts, pointPaint)
        }
        
        foreheadBox?.let { canvas.drawRect(it.left * w, it.top * h, it.right * w, it.bottom * h, boxPaint) }
        leftCheekBox?.let { canvas.drawRect(it.left * w, it.top * h, it.right * w, it.bottom * h, boxPaint) }
        rightCheekBox?.let { canvas.drawRect(it.left * w, it.top * h, it.right * w, it.bottom * h, boxPaint) }
    }
}
