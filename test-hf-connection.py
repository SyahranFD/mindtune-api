#!/usr/bin/env python3

"""
Script untuk menguji koneksi ke Hugging Face API menggunakan Python

Cara penggunaan:
1. Pastikan variabel lingkungan HF_TOKEN sudah diatur
2. Jalankan script: python test-hf-connection.py
"""

import os
import sys
import time
import json
from dotenv import load_dotenv, find_dotenv

# Coba load token dari .env file
load_dotenv(find_dotenv())

# Cek apakah HF_TOKEN tersedia
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    print("❌ Error: HF_TOKEN tidak ditemukan dalam variabel lingkungan")
    print("Pastikan HF_TOKEN sudah diatur dalam file .env atau variabel lingkungan")
    sys.exit(1)

print("=== MindTune API - Test Koneksi Hugging Face API ===\n")
print(f"✅ HF_TOKEN ditemukan: {hf_token[:5]}...{hf_token[-5:]}")

# Tes koneksi menggunakan requests
print("\nMenguji koneksi menggunakan requests...")
try:
    import requests
    response = requests.get(
        "https://router.huggingface.co/v1",
        headers={"Authorization": f"Bearer {hf_token}"},
        timeout=10
    )
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text[:100]}..." if len(response.text) > 100 else f"Response: {response.text}")
    if response.status_code == 200:
        print("✅ Koneksi berhasil menggunakan requests!")
    else:
        print(f"❌ Koneksi gagal dengan status code: {response.status_code}")
except Exception as e:
    print(f"❌ Error saat menggunakan requests: {str(e)}")

# Tes koneksi menggunakan OpenAI client (seperti yang digunakan di aplikasi)
print("\nMenguji koneksi menggunakan OpenAI client...")
try:
    from openai import OpenAI
    
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=hf_token,
        timeout=30.0
    )
    
    start_time = time.time()
    print("Mengirim request ke API...")
    
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b:groq",
            messages=[
                {
                    "role": "user",
                    "content": "Hello, this is a test message."
                }
            ],
        )
        
        elapsed_time = time.time() - start_time
        print(f"✅ Koneksi berhasil menggunakan OpenAI client! (waktu: {elapsed_time:.2f} detik)")
        print(f"Response: {completion.choices[0].message.content[:100]}..." if len(completion.choices[0].message.content) > 100 else f"Response: {completion.choices[0].message.content}")
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ Error saat membuat completion: {str(e)} (waktu: {elapsed_time:.2f} detik)")
        
        # Analisis error
        error_str = str(e)
        if "Connection error" in error_str:
            print("\nAnalisis Error:")
            print("- Masalah koneksi terdeteksi. Kemungkinan penyebab:")
            print("  1. Firewall memblokir koneksi keluar")
            print("  2. DNS tidak dapat meresolusi domain router.huggingface.co")
            print("  3. Jaringan VPS memiliki masalah routing ke server Hugging Face")
            print("  4. Server Hugging Face sedang down atau tidak merespons")
            
            print("\nRekomendasi:")
            print("1. Jalankan 'test-connection.sh' untuk tes koneksi lebih detail")
            print("2. Periksa apakah firewall mengizinkan koneksi keluar ke port 443")
            print("3. Coba ping router.huggingface.co untuk memeriksa konektivitas dasar")
            print("4. Periksa status layanan Hugging Face di https://status.huggingface.co")
        elif "timeout" in error_str.lower():
            print("\nAnalisis Error:")
            print("- Timeout terdeteksi. Kemungkinan penyebab:")
            print("  1. Koneksi internet VPS lambat")
            print("  2. Server Hugging Face lambat merespons")
            print("  3. Request terlalu besar atau kompleks")
            
            print("\nRekomendasi:")
            print("1. Tingkatkan nilai timeout dalam kode")
            print("2. Periksa kualitas koneksi internet VPS")
            print("3. Coba lagi pada waktu yang berbeda")
        elif "authentication" in error_str.lower() or "unauthorized" in error_str.lower() or "401" in error_str:
            print("\nAnalisis Error:")
            print("- Masalah autentikasi terdeteksi. Kemungkinan penyebab:")
            print("  1. HF_TOKEN tidak valid")
            print("  2. HF_TOKEN kedaluwarsa")
            print("  3. Akun Hugging Face tidak memiliki akses ke model yang diminta")
            
            print("\nRekomendasi:")
            print("1. Periksa dan perbarui HF_TOKEN di file .env")
            print("2. Pastikan akun Hugging Face memiliki akses ke model yang diminta")
except ImportError as e:
    print(f"❌ Error: {str(e)}")
    print("Pastikan package 'openai' sudah diinstal: pip install openai")

print("\nTest koneksi selesai.")