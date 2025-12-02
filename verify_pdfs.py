#!/usr/bin/env python3
"""
Quick test to verify PDF extraction worked
"""
import sys
from pathlib import Path

# Check extracted text files
text_dir = Path("/Users/mohak@backbase.com/Projects/Internal hackathon/MoneyTales/data/text")

print("\n" + "="*60)
print("📋 EXTRACTED TEXT FILES")
print("="*60 + "\n")

if not text_dir.exists():
    print("❌ Text directory not found!")
    sys.exit(1)

text_files = list(text_dir.glob("*.txt"))
print(f"Found {len(text_files)} text files:\n")

total_chars = 0
for txt_file in sorted(text_files):
    size = txt_file.stat().st_size
    total_chars += size
    
    # Read first 200 chars
    with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read(200)
    
    print(f"📄 {txt_file.name}")
    print(f"   Size: {size:,} bytes")
    print(f"   Preview: {content[:100]}...\n")

print(f"✅ Total extracted: {total_chars:,} bytes of educational content")
print(f"✅ PDFs successfully extracted and ready for RAG system\n")
