#!/bin/bash

# Script untuk menguji koneksi ke Hugging Face API

set -e

echo "=== MindTune API Connection Test Script ==="
echo ""

# Periksa koneksi ke Hugging Face API
echo "Menguji koneksi ke Hugging Face API..."

# Cek apakah curl terinstal
if ! command -v curl &> /dev/null; then
    echo "curl belum terinstal. Menginstal curl..."
    sudo apt update
    sudo apt install -y curl
fi

# Cek koneksi ke router.huggingface.co
echo "Menguji koneksi ke router.huggingface.co..."
if curl -s --head --request GET https://router.huggingface.co/v1 | grep "HTTP/" > /dev/null; then
    echo "✅ Koneksi ke router.huggingface.co berhasil!"
else
    echo "❌ Koneksi ke router.huggingface.co gagal!"
fi

# Cek DNS resolution
echo "\nMenguji DNS resolution untuk router.huggingface.co..."
host router.huggingface.co

# Cek traceroute ke router.huggingface.co
echo "\nMenjalankan traceroute ke router.huggingface.co..."
if ! command -v traceroute &> /dev/null; then
    echo "traceroute belum terinstal. Menginstal traceroute..."
    sudo apt update
    sudo apt install -y traceroute
fi
traceroute router.huggingface.co

# Cek firewall untuk koneksi keluar
echo "\nMemeriksa aturan firewall untuk koneksi keluar..."
sudo ufw status | grep "allow out"

echo "\nTest koneksi selesai."