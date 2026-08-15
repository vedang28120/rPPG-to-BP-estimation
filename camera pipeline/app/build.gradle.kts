plugins {
  alias(libs.plugins.android.application)
  alias(libs.plugins.kotlin.serialization)
  id("com.chaquo.python")
}

android {
    namespace = "com.rppg.bpestimation"
    compileSdk = 36
    defaultConfig {
        applicationId = "com.rppg.bpestimation"
        minSdk = 28
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
        
        ndk {
            abiFilters += listOf("arm64-v8a")
        }
    }
    
    flavorDimensions += "pyVersion"
    productFlavors {
        create("py310") {
            dimension = "pyVersion"
            ndk {
                abiFilters += listOf("arm64-v8a", "x86_64")
            }
        }
    }
    
    chaquopy {
        defaultConfig {
            version = "3.10"
            pip {
                install("numpy")
                install("scipy")
                install("PyWavelets")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    buildFeatures {
      viewBinding = true
      buildConfig = true
    }

    packaging {
      resources {
        excludes += "/META-INF/{AL2.0,LGPL2.1}"
      }
    }
}

kotlin {
    jvmToolchain(17)
}

dependencies {
  implementation(libs.androidx.core.ktx)
  implementation("androidx.appcompat:appcompat:1.6.1")
  implementation("com.google.android.material:material:1.11.0")
  implementation("androidx.constraintlayout:constraintlayout:2.1.4")
  implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
  
  // TensorFlow Lite
  implementation("org.tensorflow:tensorflow-lite:2.16.1")
  implementation("org.tensorflow:tensorflow-lite-select-tf-ops:2.16.1")
  
  // MediaPipe Tasks Vision
  implementation("com.google.mediapipe:tasks-vision:0.10.14")
  
  // MPAndroidChart
  implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")
}
