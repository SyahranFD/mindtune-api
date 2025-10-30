#!/bin/bash

# Script untuk memeriksa dan memperbaiki konfigurasi firewall untuk akses ke Hugging Face API

set -e

echo "=== MindTune API - Firewall Check and Fix for Hugging Face API ==="
echo ""

# Periksa apakah UFW terinstal
if ! command -v ufw &> /dev/null; then
    echo "UFW belum terinstal. Menginstal UFW..."
    sudo apt update
    sudo apt install -y ufw
fi

# Periksa status UFW
echo "Status UFW saat ini:"
sudo ufw status verbose

# Periksa apakah koneksi keluar diizinkan
echo "\nMemeriksa kebijakan keluar..."
OUTGOING_POLICY=$(sudo ufw status verbose | grep "Default:" | grep "outgoing" | awk '{print $2}')

if [ "$OUTGOING_POLICY" == "allow" ]; then
    echo "✅ Kebijakan keluar sudah diatur ke 'allow'"
else
    echo "❌ Kebijakan keluar tidak diatur ke 'allow'. Mengubah kebijakan..."
    sudo ufw default allow outgoing
fi

# Pastikan koneksi keluar ke port 443 (HTTPS) diizinkan secara eksplisit
echo "\nMenambahkan aturan eksplisit untuk koneksi HTTPS keluar..."
sudo ufw allow out to any port 443 proto tcp

# Periksa apakah domain Hugging Face dapat diakses
echo "\nMemeriksa koneksi ke domain Hugging Face..."

# Cek apakah curl terinstal
if ! command -v curl &> /dev/null; then
    echo "curl belum terinstal. Menginstal curl..."
    sudo apt update
    sudo apt install -y curl
fi

# Daftar domain Hugging Face yang perlu diakses
DOMAINS=("router.huggingface.co" "huggingface.co" "api-inference.huggingface.co")

for domain in "${DOMAINS[@]}"; do
    echo "Memeriksa koneksi ke $domain..."
    if curl -s --head --request GET https://$domain | grep "HTTP/" > /dev/null; then
        echo "✅ Koneksi ke $domain berhasil!"
    else
        echo "❌ Koneksi ke $domain gagal!"
    fi
    
    # Cek DNS resolution
    echo "DNS resolution untuk $domain:"
    host $domain || echo "❌ Gagal meresolusi DNS untuk $domain"
    
    echo ""
done

# Periksa apakah ada proxy yang dikonfigurasi
echo "Memeriksa konfigurasi proxy..."
if [ -n "$http_proxy" ] || [ -n "$https_proxy" ]; then
    echo "Proxy terdeteksi:"
    echo "http_proxy: $http_proxy"
    echo "https_proxy: $https_proxy"
else
    echo "Tidak ada proxy yang dikonfigurasi di lingkungan saat ini."
fi

# Periksa apakah iptables memblokir koneksi
echo "\nMemeriksa aturan iptables..."
sudo iptables -L OUTPUT -n | grep -i "huggingface\|443"

# Tambahkan aturan iptables untuk mengizinkan koneksi ke Hugging Face
echo "\nMenambahkan aturan iptables untuk mengizinkan koneksi ke Hugging Face..."
sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT

# Periksa apakah ada masalah dengan SSL/TLS
echo "\nMemeriksa koneksi SSL/TLS ke Hugging Face..."
if ! command -v openssl &> /dev/null; then
    echo "openssl belum terinstal. Menginstal openssl..."
    sudo apt update
    sudo apt install -y openssl
fi

echo "Menguji koneksi SSL ke router.huggingface.co:443..."
openssl s_client -connect router.huggingface.co:443 -servername router.huggingface.co < /dev/null | grep "Verify return code"

# Periksa apakah ada masalah dengan resolusi DNS
echo "\nMemeriksa resolusi DNS..."
if ! command -v dig &> /dev/null; then
    echo "dig belum terinstal. Menginstal dig..."
    sudo apt update
    sudo apt install -y dnsutils
fi

echo "Resolusi DNS untuk router.huggingface.co menggunakan Google DNS (8.8.8.8):"
dig @8.8.8.8 router.huggingface.co

# Tambahkan entri DNS ke /etc/hosts jika diperlukan
echo "\nMenambahkan entri DNS ke /etc/hosts..."
HF_IP=$(dig +short router.huggingface.co @8.8.8.8 | head -n 1)
if [ -n "$HF_IP" ]; then
    echo "IP untuk router.huggingface.co: $HF_IP"
    if ! grep -q "router.huggingface.co" /etc/hosts; then
        echo "Menambahkan router.huggingface.co ke /etc/hosts..."
        echo "$HF_IP router.huggingface.co" | sudo tee -a /etc/hosts
    else
        echo "router.huggingface.co sudah ada di /etc/hosts"
    fi
else
    echo "Tidak dapat menemukan IP untuk router.huggingface.co"
fi

echo "\nPemeriksaan dan perbaikan firewall selesai."
echo "Jika masih mengalami masalah koneksi, coba jalankan 'test-hf-connection.py' untuk diagnostik lebih lanjut."