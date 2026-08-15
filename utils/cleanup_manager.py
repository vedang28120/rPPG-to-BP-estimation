"""
Repository Hygiene & Cleanup Manager Module
Safely archives temporary build artifacts, scratch files, and unstructured logs while protecting core modules.
"""

import os
import shutil
from pathlib import Path

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_DIR = os.path.join(ROOT_DIR, '_archive')

WHITELIST_DIRECTORIES = {
    'data',
    'core_extraction',
    'filtering',
    'models',
    'utils',
    'results',
    'docs',
    'mobile'
}

WHITELIST_FILES = {
    'README.md',
    'LICENSE',
    'requirements.txt',
    '.gitignore',
    '.gitattributes'
}

def clean_repository(dry_run=True):
    print(f"[CLEANUP] Scanning repository root: {ROOT_DIR}")
    items = os.listdir(ROOT_DIR)
    
    for item in items:
        item_path = os.path.join(ROOT_DIR, item)
        if item.startswith('.') or item == '_archive':
            continue
            
        if os.path.isdir(item_path):
            if item in WHITELIST_DIRECTORIES:
                print(f" [KEEP DIR]  {item}")
            else:
                print(f" [ARCHIVE]   {item}/")
                if not dry_run:
                    os.makedirs(ARCHIVE_DIR, exist_ok=True)
                    shutil.move(item_path, os.path.join(ARCHIVE_DIR, item))
        else:
            if item in WHITELIST_FILES:
                print(f" [KEEP FILE] {item}")
            else:
                print(f" [ARCHIVE]   {item}")
                if not dry_run:
                    os.makedirs(ARCHIVE_DIR, exist_ok=True)
                    shutil.move(item_path, os.path.join(ARCHIVE_DIR, item))

if __name__ == '__main__':
    clean_repository(dry_run=True)
