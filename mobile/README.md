# Mobile Deployment Module (`mobile/`)

## Purpose
Houses Android source code, Camera2 API optical state machines, native JNI/C++ bindings, and production APK backup packages.

## Dependencies
- External Libraries: Android SDK, Gradle, Kotlin Coroutines, Camera2, TensorFlow Lite AAR
- Internal Modules: Ingests optimized models from `models/inference/` and Python DSP logic from `core_extraction/` and `filtering/`

## Key Files
- `android_app/`: Complete Android Studio project implementing the decoupled `Record-then-Process` asynchronous state machine, Camera2 Convergence-Hold-Lock (AE/AWB), and on-device inference.
- `backups/rPPG_BP_Estimation_Backup.apk`: Validated release build APK for rapid deployment, testing, and hardware verification.
