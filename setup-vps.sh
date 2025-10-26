#!/bin/bash

# Script untuk setup awal VPS untuk MindTune API

set -e

echo "=== MindTune API VPS Setup Script ==="
echo ""

# Update sistem
echo "Mengupdate sistem..."
sudo apt update && sudo apt upgrade -y

# Install dependensi umum
echo "Menginstal dependensi umum..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
sudo apt install -y git vim nano htop net-tools

# Install Docker
echo "Menginstal Docker..."

# Tambahkan GPG key Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Tambahkan repository Docker
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update package database
sudo apt update

# Install Docker
sudo apt install -y docker-ce

# Tambahkan user ke grup docker
sudo usermod -aG docker ${USER}

# Install Docker Compose
echo "Menginstal Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verifikasi instalasi
echo ""
echo "Versi Docker:"
docker --version

echo ""
echo "Versi Docker Compose:"
docker-compose --version

# Setup direktori aplikasi
echo ""
echo "Membuat direktori aplikasi..."
mkdir -p /var/www/mindtune-api

echo ""
echo "Setup VPS selesai!"
echo "CATATAN: Anda perlu logout dan login kembali agar perubahan grup docker diterapkan."
echo "Setelah itu, Anda dapat melanjutkan dengan clone repository dan setup aplikasi."

exit 0