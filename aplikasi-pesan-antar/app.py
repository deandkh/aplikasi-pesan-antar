"""Aplikasi Pesan Antar - jalankan dengan:  python app.py"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from frontend.ui import jalankan_aplikasi  # noqa: E402

if __name__ == "__main__":
    jalankan_aplikasi(os.path.join(BASE, "data"))
