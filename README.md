# Mobile Remote Photoplethysmography (rPPG) and Cuffless Blood Pressure Inference

This repository contains the codebase and implementation for a robust, mobile-centric pipeline designed to estimate continuous cuffless blood pressure via remote photoplethysmography (rPPG). 

Operating on standard smartphone hardware at 30 frames per second (FPS), this architecture is engineered to overcome significant hardware-induced temporal distortions (like Variable Frame Rate jitter) and physiological domain gaps (such as the Windkessel effect and template collapse).

## Project Structure
- **`android app/`**: The primary Android application. It implements a decoupled `Record-then-Process` asynchronous state machine to eliminate JNI bottlenecks, manages optical state via the Camera2 API, and runs the TensorFlow Lite inference.
- **`android app POS only/`**: A focused variant of the Android app specifically for isolating and testing the Plane-Orthogonal-to-Skin (POS) extraction algorithm.
- **`project prototype/`**: Python-based research prototypes, test scripts, and algorithmic verification logic.

## Key Technical Features
1. **Convergence-Hold-Lock**: A rigorous state machine utilizing the Camera2 API to lock Auto-Exposure and Auto-White Balance, preventing macroscopic luminance step-responses.
2. **PCHIP Interpolation**: Strict monotonic temporal standardization to correct VFR jitter without introducing artificial pulse inflections (preventing cubic spline ringing).
3. **POS Extraction**: Deterministic algebraic combinations of RGB channels to actively cancel specular reflection noise and isolate the hemoglobin pulsatile absorption.
4. **Dual-Stream Filtering**: A split processing pipeline using Butterworth bandpass for Heart Rate isolation, and Zero-Phase Wavelet Denoising (BayesShrink) for strict morphology preservation.
5. **LSTM Tensor Inference**: Multi-channel spatial derivative tensors (PPG, vPPG, aPPG) processed through an on-device Long Short-Term Memory network to map higher-order cardiovascular dynamics to systolic and diastolic pressure.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
