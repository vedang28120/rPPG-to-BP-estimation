"""
TFLite & ONNX Graph Exporter Module
Quantizes and converts trained neural architectures into mobile flatbuffer format for Android edge deployment.
"""

import os
import argparse

def export_keras_to_tflite(keras_model_path, output_tflite_path, quantize=False):
    """
    Converts a saved Keras model (.h5) into a lightweight .tflite flatbuffer.
    """
    import tensorflow as tf
    import tf_keras
    
    print(f"[EXPORTER] Loading Keras model: {keras_model_path}")
    model = tf_keras.models.load_model(keras_model_path, compile=False)
    
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    if quantize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        print("[EXPORTER] Enabled dynamic range quantization (INT8 weights / FP32 activations)")
        
    tflite_model = converter.convert()
    
    os.makedirs(os.path.dirname(output_tflite_path), exist_ok=True)
    with open(output_tflite_path, 'wb') as f:
        f.write(tflite_model)
        
    print(f"[EXPORTER] Successfully generated TFLite model at: {output_tflite_path} ({len(tflite_model)/1024:.1f} KB)")

def main():
    parser = argparse.ArgumentParser(description="Export models to TFLite format")
    parser.add_argument("--model_path", type=str, required=True, help="Input model path (.h5 or .pth)")
    parser.add_argument("--out_tflite", type=str, required=True, help="Output .tflite path")
    parser.add_argument("--quantize", action='store_true', help="Enable INT8 quantization")
    args = parser.parse_args()
    
    if args.model_path.endswith('.h5'):
        export_keras_to_tflite(args.model_path, args.out_tflite, args.quantize)
    else:
        print("[EXPORTER] PyTorch TFLite conversion requires ONNX intermediate conversion.")

if __name__ == '__main__':
    main()
