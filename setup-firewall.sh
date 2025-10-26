#!/bin/bash

# Script untuk setup firewall (UFW) untuk MindTune API

set -e

echo "=== MindTune API Firewall Setup Script ==="
echo ""

# Periksa apakah UFW terinstal
if ! command -v ufw &> /dev/null; then
    echo "UFW belum terinstal. Menginstal UFW..."
    sudo apt update
    sudo apt install -y ufw
fi

# Reset aturan UFW
echo "Me-reset aturan UFW..."
sudo ufw --force reset

# Konfigurasi default
echo "Mengatur kebijakan default..."
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Izinkan SSH
echo "Mengizinkan koneksi SSH..."
sudo ufw allow ssh

# Izinkan HTTP dan HTTPS
echo "Mengizinkan koneksi HTTP dan HTTPS..."
sudo ufw allow http
sudo ufw allow https

# Izinkan port aplikasi (jika diakses langsung tanpa Nginx)
echo "Mengizinkan port aplikasi (8000)..."
sudo ufw allow 8000/tcp

# Izinkan port PostgreSQL (hanya dari localhost)
echo "Mengizinkan port PostgreSQL (5432) hanya dari localhost..."
sudo ufw allow from 127.0.0.1 to any port 5432

# Aktifkan UFW
echo "Mengaktifkan UFW..."
sudo ufw --force enable

# Tampilkan status UFW
echo ""
echo "Status UFW:"
sudo ufw status verbose

echo ""
echo "Setup firewall selesai!"
echo "PERINGATAN: Pastikan port SSH (22) diizinkan sebelum logout dari sesi ini."
echo "Jika Anda terkunci, Anda perlu mengakses VPS melalui console provider VPS."

exit 0