"""
Localize repository to Traditional Chinese (Taiwan phrasing) and remove non-Windows platform logic.
Uses opencc (s2twp).
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
import opencc

REPO_ROOT = Path(__file__).resolve().parent.parent

# OpenCC converter: Simplified to Traditional (Taiwan standard + phrases)
converter = opencc.OpenCC('s2twp')

# Files/folders to skip
SKIP_PARTS = {'.git', '.venv', '__pycache__', '.pytest_cache'}
SKIP_FILES = {'upstream_baseline.json'}

CHINESE_CHAR_RE = re.compile(r'[一-鿿]')

def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.xlsx', '.pyc', '.zip'}:
        return False
    return True

def convert_text_files():
    print("==> Converting file contents to Traditional Chinese...")
    converted_count = 0
    all_files = subprocess.check_output(['git', 'ls-files'], cwd=REPO_ROOT, text=True, encoding='utf-8').splitlines()
    
    for rel_path in all_files:
        p = REPO_ROOT / rel_path
        if not p.is_file():
            continue
        if any(part in p.parts for part in SKIP_PARTS):
            continue
        if p.name in SKIP_FILES:
            continue
        if not is_text_file(p):
            continue
        
        try:
            content = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                content = p.read_text(encoding='gb18030')
            except Exception:
                continue
                
        if not CHINESE_CHAR_RE.search(content):
            continue
            
        new_content = converter.convert(content)
        
        # Specific terminology refinements if needed
        # Remove non-Windows logic in documentation/comments
        if "category-selection" in rel_path and "SKILL.md" in rel_path:
            # Clean non-windows snippet
            new_content = re.sub(
                r'# Linux/Mac\s*\n\s*export SORFTIME_API_KEY="your_api_key"\s*\n',
                '',
                new_content
            )
        
        if new_content != content:
            p.write_text(new_content, encoding='utf-8')
            converted_count += 1
            
    print(f"Converted {converted_count} files to Traditional Chinese.")

def clean_non_windows_in_readme():
    readme_zh = REPO_ROOT / "README.md"
    if readme_zh.is_file():
        txt = readme_zh.read_text(encoding='utf-8')
        txt = txt.replace("本專案採用 Windows-first 標準化開發環境，亦可在 macOS 與 Linux 下流暢運行：", "本專案專為 Windows 11 + PowerShell 環境打造，提供完整自動化檢驗：")
        readme_zh.write_text(txt, encoding='utf-8')

    readme_en = REPO_ROOT / "README.en.md"
    if readme_en.is_file():
        txt = readme_en.read_text(encoding='utf-8')
        txt = txt.replace("Supports US, EU, UK, JP, and other major marketplaces, extended with TikTok video analysis, creator insights, and 1688 supply-chain cost extraction.", "Supports 14 Amazon marketplaces (US, EU, UK, JP, etc.) on Windows 11 + PowerShell, extended with TikTok video analysis, creator insights, and 1688 supply-chain cost extraction.")
        readme_en.write_text(txt, encoding='utf-8')

def rename_chinese_paths():
    print("==> Checking and renaming Simplified Chinese filenames to Traditional Chinese...")
    # Get all git tracked files
    tracked = subprocess.check_output(['git', 'ls-files'], cwd=REPO_ROOT, text=True, encoding='utf-8').splitlines()
    
    # Sort by path depth descending so we rename files before parent directories
    files_to_check = sorted(tracked, key=lambda x: len(Path(x).parts), reverse=True)
    
    renamed = 0
    for rel_path in files_to_check:
        p = REPO_ROOT / rel_path
        if not p.exists():
            continue
        
        target_name = converter.convert(p.name)
        if target_name != p.name:
            target_path = p.parent / target_name
            print(f"Renaming file: {p.name} -> {target_name}")
            subprocess.run(['git', 'mv', str(p), str(target_path)], cwd=REPO_ROOT, check=True)
            renamed += 1
            
    # Also check directory names
    for root, dirs, _ in os.walk(REPO_ROOT, topdown=False):
        if any(part in Path(root).parts for part in SKIP_PARTS):
            continue
        for d in dirs:
            orig_dir = Path(root) / d
            trad_name = converter.convert(d)
            if trad_name != d and orig_dir.exists():
                trad_dir = Path(root) / trad_name
                print(f"Renaming directory: {orig_dir} -> {trad_dir}")
                subprocess.run(['git', 'mv', str(orig_dir), str(trad_dir)], cwd=REPO_ROOT, check=True)
                renamed += 1
                
    print(f"Renamed {renamed} paths.")

if __name__ == '__main__':
    convert_text_files()
    clean_non_windows_in_readme()
    rename_chinese_paths()
    # Re-run convert text files in case paths referenced each other
    convert_text_files()
    print("Localization complete.")

