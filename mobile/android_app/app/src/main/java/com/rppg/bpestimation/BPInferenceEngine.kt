package com.rppg.bpestimation

import android.content.Context
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

class BPInferenceEngine(context: Context) {

    companion object {
        @Volatile
        private var interpreterInstance: Interpreter? = null

        fun getInterpreter(context: Context): Interpreter {
            return interpreterInstance ?: synchronized(this) {
                interpreterInstance ?: createInterpreter(context).also { interpreterInstance = it }
            }
        }

        private fun createInterpreter(context: Context): Interpreter {
            val model = loadModelFile(context, "lstm_ppg_nonmixed.tflite")
            val options = Interpreter.Options()
            return Interpreter(model, options)
        }

        private fun loadModelFile(context: Context, modelName: String): MappedByteBuffer {
            val fileDescriptor = context.assets.openFd(modelName)
            val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
            val fileChannel = inputStream.channel
            val startOffset = fileDescriptor.startOffset
            val declaredLength = fileDescriptor.declaredLength
            return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
        }
        
        fun close() {
            interpreterInstance?.close()
            interpreterInstance = null
        }
    }

    private var interpreter: Interpreter? = null

    init {
        interpreter = getInterpreter(context)
    }

    fun predict(bvpWindow: Array<FloatArray>): Pair<Float, Float> {
        if (interpreter == null) return Pair(0f, 0f)

        // Expected input shape: [1, 875, 3] for multi-channel morphology tensor
        val seqLength = 875
        val channels = 3
        val inputArray = Array(1) { Array(seqLength) { FloatArray(channels) } }
        for (i in 0 until seqLength) {
            for (c in 0 until channels) {
                if (i < bvpWindow.size && c < bvpWindow[i].size) {
                    inputArray[0][i][c] = bvpWindow[i][c]
                }
            }
        }

        // Expected output: Two tensors of shape [1, 1], usually [SBP, DBP]
        // TensorFlow Lite for multiple outputs requires a map
        val outputMap = HashMap<Int, Any>()
        val sbpOut = Array(1) { FloatArray(1) }
        val dbpOut = Array(1) { FloatArray(1) }
        outputMap[0] = sbpOut
        outputMap[1] = dbpOut

        interpreter?.runForMultipleInputsOutputs(arrayOf(inputArray), outputMap)

        val val1 = sbpOut[0][0]
        val val2 = dbpOut[0][0]

        // Blood pressure SBP is mathematically always higher than DBP (e.g. 120 / 80).
        val sbp = maxOf(val1, val2)
        val dbp = minOf(val1, val2)

        return Pair(sbp, dbp)
    }

    fun close() {
        Companion.close()
        interpreter = null
    }
}
