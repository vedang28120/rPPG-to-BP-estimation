import json
import os

py_script_path = r'c:\Users\simpl\.antigravity-ide\Projects\rPPG to BP estimation\colab_training\train_bp_mcd.py'
with open(py_script_path, 'r', encoding='utf-8') as f:
    train_code_lines = f.readlines()

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Gold Pipeline — Progressive PPG-to-BP Ablation Trainer\n",
    "\n",
    "Runs **Phases 1–6** of the Gold Pipeline progression:\n",
    "\n",
    "| Phase | Description |\n",
    "|---|---|\n",
    "| 1 | Lock current baseline & verify no data leakage |\n",
    "| 2 | Population Mean & Demographics-Only baselines |\n",
    "| 3 | Architecture ablation ladder (MODEL-03 → 04 → 05 → 06) |\n",
    "| 4 | Input channel ablation (PPG vs PPG+vPPG vs PPG+vPPG+aPPG) |\n",
    "| 5 | SBP investigation (separate heads, weighted loss) |\n",
    "| 6 | Regression-to-mean diagnostics |\n",
    "\n",
    "### Hardware Setup\n",
    "**Runtime** → **Change runtime type** → **T4 GPU** → **Save**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 1. Install Hugging Face Hub (Lightweight Pure-Python Package)\n",
    "!pip install -q huggingface_hub\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 2. Authenticate with Hugging Face (Required for Gated MCD Dataset)\n",
    "import os\n",
    "from huggingface_hub import login\n",
    "\n",
    "hf_token = input(\"Enter your Hugging Face Token: \").strip()\n",
    "if hf_token:\n",
    "    os.environ[\"HF_TOKEN\"] = hf_token\n",
    "    login(token=hf_token)\n",
    "    print(\"Authenticated!\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 3. Verify GPU\n",
    "import torch\n",
    "print('CUDA:', torch.cuda.is_available())\n",
    "if torch.cuda.is_available(): print('GPU:', torch.cuda.get_device_name(0))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 4. Create Workspace Directories (Upload pre-trained .pth checkpoints to ./models/ here)\n",
    "import os, shutil\n",
    "os.makedirs('./models', exist_ok=True)\n",
    "os.makedirs('./results', exist_ok=True)\n",
    "os.makedirs('./mcd_dataset', exist_ok=True)\n",
    "\n",
    "# Auto-map uploaded model_model06.pth from yesterday if placed in root or ./models\n",
    "if os.path.exists('./model_model06.pth') and not os.path.exists('./models/MODEL-06-SepHead_original.pth'):\n",
    "    shutil.copy('./model_model06.pth', './models/MODEL-06-SepHead_original.pth')\n",
    "    print('Auto-mapped uploaded model_model06.pth -> ./models/MODEL-06-SepHead_original.pth')\n",
    "elif os.path.exists('./models/model_model06.pth') and not os.path.exists('./models/MODEL-06-SepHead_original.pth'):\n",
    "    shutil.copy('./models/model_model06.pth', './models/MODEL-06-SepHead_original.pth')\n",
    "    print('Auto-mapped ./models/model_model06.pth -> ./models/MODEL-06-SepHead_original.pth')\n",
    "\n",
    "print('Workspace directories ready: ./models, ./results, ./mcd_dataset')\n",
    "print('Tip: Upload your pre-trained model_model06.pth file into Colab now to skip training!')\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 5. Gold Pipeline — Full Model Definitions & Training Logic\n"
   ] + train_code_lines
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 6. RUN ALL PHASES (1–6 + EXP-A/B/C Balancing)\n",
    "run_gold_pipeline(base_dir=\"./mcd_dataset\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 6. EXPORT BEST MODEL (run after phases complete)\n",
    "!pip install -q onnx onnxruntime onnx2tf tf2onnx\n",
    "import os, shutil, torch\n",
    "\n",
    "# Find the best .pth model from ablation results\n",
    "model_dir = './models'\n",
    "pth_files = [f for f in os.listdir(model_dir) if f.endswith('.pth')] if os.path.exists(model_dir) else []\n",
    "print(f'Available trained models: {pth_files}')\n",
    "\n",
    "# Export the full MODEL-06 (best expected) to ONNX and TFLite\n",
    "best_pth = './models/model_model06.pth'\n",
    "if not os.path.exists(best_pth):\n",
    "    best_pth = './models/best_rigorous_bp_resnet.pth'\n",
    "\n",
    "if os.path.exists(best_pth):\n",
    "    print(f'Exporting {best_pth}...')\n",
    "    model = DualBranchResNetBiGRUAttn(in_channels=3, demo_dim=3, use_demo=True, use_attn=True, use_branchB=True).to(device)\n",
    "    model.load_state_dict(torch.load(best_pth, map_location=device))\n",
    "    model.eval()\n",
    "    \n",
    "    dummy_wave = torch.randn(1, 3, 1250).to(device)\n",
    "    dummy_demo = torch.randn(1, 3).to(device)\n",
    "    \n",
    "    onnx_path = './models/best_bp_model.onnx'\n",
    "    torch.onnx.export(model, (dummy_wave, dummy_demo), onnx_path,\n",
    "        input_names=['wave', 'demo'], output_names=['bp_pred'],\n",
    "        dynamic_axes={'wave': {0: 'batch'}, 'demo': {0: 'batch'}, 'bp_pred': {0: 'batch'}},\n",
    "        opset_version=14)\n",
    "    print(f'ONNX exported: {onnx_path}')\n",
    "    \n",
    "    try:\n",
    "        !onnx2tf -i ./models/best_bp_model.onnx -o ./models/tf_saved_model\n",
    "        tflite_src = './models/tf_saved_model/best_bp_model_float32.tflite'\n",
    "        if os.path.exists(tflite_src):\n",
    "            shutil.copy(tflite_src, './models/best_bp_model.tflite')\n",
    "            print('TFLite exported: ./models/best_bp_model.tflite')\n",
    "        shutil.make_archive('./models/best_bp_model_tf', 'zip', './models/tf_saved_model')\n",
    "        print('TF SavedModel zipped: ./models/best_bp_model_tf.zip')\n",
    "    except Exception as e:\n",
    "        print(f'TFLite conversion note: {e}')\n",
    "    \n",
    "    try:\n",
    "        from google.colab import files\n",
    "        for f in ['./models/best_bp_model.onnx', './models/best_bp_model.tflite', './models/best_bp_model_tf.zip',\n",
    "                  './models/MODEL-06-SepHead_original.pth', './models/MODEL-06-SepHead_balanced_moderate.pth', './models/MODEL-06-SepHead_balanced_strong.pth',\n",
    "                  './results/ablation_ladder.csv', './results/balancing_comparison.csv',\n",
    "                  './results/bp_distribution_histograms.png', './results/regression_to_mean_diagnostic.png']:\n",
    "            if os.path.exists(f): files.download(f)\n",
    "    except: print('Files saved under ./models/ and ./results/')\n",
    "else:\n",
    "    print(f'No model found at {best_pth}')\n"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

nb_path = r'c:\Users\simpl\.antigravity-ide\Projects\rPPG to BP estimation\colab_training\train_bp_mcd_colab.ipynb'
with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1)

print("Successfully created Gold Pipeline Colab Notebook (Phases 1-6 + Export)!")
