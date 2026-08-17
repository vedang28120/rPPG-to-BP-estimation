"""
Download and verify TS-CAN pretrained weights and MODEL-06 checkpoints.
"""
import os
import sys
import urllib.request

def download_file(url, destination_path):
    os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
    if os.path.exists(destination_path) and os.path.getsize(destination_path) > 1000000:
        print(f"[OK] Weights already exist at: {destination_path} ({os.path.getsize(destination_path):,} bytes)")
        return True
    
    print(f"[*] Downloading TS-CAN weights from: {url}")
    print(f"[*] Target path: {destination_path}...")
    try:
        def progress_callback(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100.0, downloaded * 100.0 / total_size)
                sys.stdout.write(f"\r    Downloading: {percent:.1f}% ({downloaded/(1024*1024):.2f}/{total_size/(1024*1024):.2f} MB)")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(url, destination_path, reporthook=progress_callback)
        sys.stdout.write("\n")
        print(f"[OK] Download completed successfully ({os.path.getsize(destination_path):,} bytes)!")
        return True
    except Exception as e:
        print(f"\n[!] Error downloading weights: {e}")
        return False

def setup_all_checkpoints():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    checkpoints_dir = os.path.join(current_dir, "checkpoints")
    os.makedirs(checkpoints_dir, exist_ok=True)
    
    # 1. Download TS-CAN weights
    tscan_url = "https://raw.githubusercontent.com/xliucs/MTTS-CAN/master/mtts_can.hdf5"
    tscan_dest = os.path.join(checkpoints_dir, "mtts_can.hdf5")
    download_file(tscan_url, tscan_dest)
    
    # 2. Check for best MODEL-06 Blood Pressure Checkpoints
    potential_bp_paths = [
        r"C:\Users\simpl\Downloads\master roadmap models and results\MODEL-06_Phase3_Bayesian.pth",
        r"C:\Users\simpl\Downloads\master roadmap models and results\MODEL-06_Phase1_LDS.pth",
        os.path.join(current_dir, "..", "models", "checkpoints", "MODEL-06-SepHead_original.pth"),
        os.path.join(current_dir, "..", "models", "checkpoints", "best_rigorous_bp_resnet.pth")
    ]
    
    found_bp = None
    for p in potential_bp_paths:
        if os.path.exists(p):
            print(f"[OK] Found MODEL-06 BP checkpoint: {p}")
            found_bp = p
            break
            
    if not found_bp:
        print("[!] Warning: No local MODEL-06 BP checkpoint found.")
        
    return tscan_dest, found_bp

if __name__ == "__main__":
    setup_all_checkpoints()
