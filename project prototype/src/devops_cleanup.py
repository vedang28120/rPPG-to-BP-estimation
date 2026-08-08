import os
import shutil
from pathlib import Path

# ANSI Escape Codes for coloring
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_DIR = os.path.join(ROOT_DIR, '_archive')

# Files and folders to strictly keep (The dynamic whitelist)
WHITELIST = {
    'data',
    'models',
    'outputs',
    'results',
    'src',
    'requirements.txt',
    'sample_face.jpg'
}

# Standard environments or logs to ignore entirely
IGNORE_LIST = {
    '.git',
    '__pycache__',
    '.venv',
    '.env',
    '.agents',
    '_archive',
    'scratch'
}

def is_essential(item_path):
    rel_path = os.path.relpath(item_path, ROOT_DIR)
    
    # Check if the root component of the path is in the whitelist or ignore list
    root_component = Path(rel_path).parts[0]
    
    if root_component in IGNORE_LIST:
        return 'ignore'
    
    if root_component in WHITELIST:
        return 'keep'
        
    return 'archive'

def main():
    print(f"Scanning directory: {ROOT_DIR}")
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    items = os.listdir(ROOT_DIR)
    
    archived_count = 0
    kept_count = 0
    ignored_count = 0
    
    for item in items:
        item_path = os.path.join(ROOT_DIR, item)
        status = is_essential(item_path)
        
        if status == 'ignore':
            print(f"{Colors.YELLOW}[IGNORED]{Colors.END} {item}")
            ignored_count += 1
        elif status == 'keep':
            print(f"{Colors.GREEN}[RETAINED]{Colors.END} {item}")
            kept_count += 1
        elif status == 'archive':
            print(f"{Colors.RED}[ARCHIVED]{Colors.END} {item}")
            
            # Handle potential filename collisions in _archive
            dest_path = os.path.join(ARCHIVE_DIR, item)
            if os.path.exists(dest_path):
                # Simply remove the old archived version if it exists to replace it
                if os.path.isdir(dest_path):
                    shutil.rmtree(dest_path)
                else:
                    os.remove(dest_path)
                    
            shutil.move(item_path, dest_path)
            archived_count += 1
            
    print("\n" + "="*40)
    print("CLEANUP SUMMARY")
    print(f"{Colors.GREEN}Retained:{Colors.END} {kept_count}")
    print(f"{Colors.YELLOW}Ignored:{Colors.END} {ignored_count}")
    print(f"{Colors.RED}Archived:{Colors.END} {archived_count}")
    print("="*40 + "\n")

if __name__ == '__main__':
    main()
