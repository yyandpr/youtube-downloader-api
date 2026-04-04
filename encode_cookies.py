#!/usr/bin/env python3
"""Encode the YouTube cookies file to base64 for Railway env var."""
import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set env var from EditThisCookie JSON
import json

cookies_json = open('test_cookies.py', 'r').read()
start = cookies_json.index("COOKIES_JSON = '''") + len("COOKIES_JSON = '''")
end = cookies_json.rindex("'''")
json_str = cookies_json[start:end]

os.environ['YOUTUBE_COOKIES'] = json_str

from app.config import setup_youtube_cookies, COOKIES_FILE

setup_youtube_cookies()

with open(COOKIES_FILE, 'rb') as f:
    data = f.read()

encoded = base64.b64encode(data).decode()
print("Base64 encoded cookies (YOUTUBE_COOKIES_BASE64):")
print(encoded)
print()
print(f"Length: {len(encoded)} chars")