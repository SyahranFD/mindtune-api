#!/bin/bash

# Script untuk memperbaiki masalah DNS untuk router.huggingface.co

set -e

echo "=== MindTune API - Fix DNS for router.huggingface.co ==="
echo ""

# Mendapatkan IP untuk router.huggingface.co dari DNS Google
echo "Mencari IP untuk router.huggingface.co menggunakan Google DNS..."

# Cek apakah dig terinstal
if ! command -v dig &> /dev/null; then
    echo "dig belum terinstal. Menginstal dig..."
    sudo apt update
    sudo apt install -y dnsutils
fi

# Coba mendapatkan IP dari beberapa DNS publik
DNS_SERVERS=("8.8.8.8" "1.1.1.1" "9.9.9.9")
HF_IP=""

for dns in "${DNS_SERVERS[@]}"; do
    echo "Mencoba DNS server: $dns"
    IP=$(dig +short router.huggingface.co @$dns | head -n 1)
    
    if [ -n "$IP" ]; then
        HF_IP=$IP
        echo "✅ Berhasil mendapatkan IP dari DNS $dns: $HF_IP"
        break
    else
        echo "❌ Gagal mendapatkan IP dari DNS $dns"
    fi
done

# Jika tidak bisa mendapatkan IP dari DNS publik, gunakan IP dari api-inference.huggingface.co
if [ -z "$HF_IP" ]; then
    echo "Mencoba mendapatkan IP dari domain api-inference.huggingface.co..."
    API_IP=$(dig +short api-inference.huggingface.co @8.8.8.8 | head -n 1)
    
    if [ -n "$API_IP" ]; then
        HF_IP=$API_IP
        echo "✅ Menggunakan IP dari api-inference.huggingface.co: $HF_IP"
    else
        # Jika masih tidak bisa, gunakan IP dari huggingface.co
        echo "Mencoba mendapatkan IP dari domain huggingface.co..."
        HF_CO_IP=$(dig +short huggingface.co @8.8.8.8 | head -n 1)
        
        if [ -n "$HF_CO_IP" ]; then
            HF_IP=$HF_CO_IP
            echo "✅ Menggunakan IP dari huggingface.co: $HF_IP"
        fi
    fi
fi

# Jika masih tidak bisa mendapatkan IP, gunakan IP hardcoded
if [ -z "$HF_IP" ]; then
    HF_IP="18.67.181.124"  # IP dari huggingface.co
    echo "⚠️ Tidak bisa mendapatkan IP dari DNS. Menggunakan IP hardcoded: $HF_IP"
fi

# Tambahkan entri ke /etc/hosts
echo "\nMenambahkan router.huggingface.co ke /etc/hosts dengan IP $HF_IP..."

# Cek apakah sudah ada di /etc/hosts
if grep -q "router.huggingface.co" /etc/hosts; then
    echo "Menghapus entri lama router.huggingface.co dari /etc/hosts..."
    sudo sed -i '/router.huggingface.co/d' /etc/hosts
fi

# Tambahkan entri baru
echo "$HF_IP router.huggingface.co" | sudo tee -a /etc/hosts

# Verifikasi entri sudah ditambahkan
echo "\nVerifikasi entri di /etc/hosts:"
grep "router.huggingface.co" /etc/hosts

# Test koneksi ke router.huggingface.co
echo "\nMenguji koneksi ke router.huggingface.co..."
if curl -s --head --request GET https://router.huggingface.co/v1 | grep "HTTP/" > /dev/null; then
    echo "✅ Koneksi ke router.huggingface.co berhasil!"
else
    echo "❌ Koneksi ke router.huggingface.co masih gagal!"
    echo "Coba restart layanan jaringan dengan perintah: sudo systemctl restart networking"
fi

# Cek DNS resolution
echo "\nMenguji DNS resolution untuk router.huggingface.co..."
host router.huggingface.co

echo "\nPerbaikan DNS selesai. Jika masih mengalami masalah, coba restart server atau hubungi penyedia VPS Anda."