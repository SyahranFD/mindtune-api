#!/bin/bash

# Script untuk setup SSL dengan Certbot untuk MindTune API

set -e

echo "=== MindTune API SSL Setup Script ==="
echo ""

# Fungsi untuk menampilkan bantuan
show_help() {
    echo "Penggunaan: ./setup-ssl.sh <domain>"
    echo ""
    echo "Contoh:"
    echo "  ./setup-ssl.sh example.com"
    echo "  ./setup-ssl.sh api.example.com"
    echo ""
}

# Periksa argumen
if [ $# -eq 0 ]; then
    echo "ERROR: Domain tidak ditentukan."
    show_help
    exit 1
fi

DOMAIN="$1"

echo "Domain: $DOMAIN"
echo ""

# Periksa apakah Nginx terinstal
if ! command -v nginx &> /dev/null; then
    echo "Nginx belum terinstal. Menginstal Nginx..."
    sudo apt update
    sudo apt install -y nginx
fi

# Periksa apakah Certbot terinstal
if ! command -v certbot &> /dev/null; then
    echo "Certbot belum terinstal. Menginstal Certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Buat konfigurasi Nginx untuk domain
echo "Membuat konfigurasi Nginx untuk $DOMAIN..."

NGINX_CONF="/etc/nginx/sites-available/$DOMAIN"

# Buat konfigurasi Nginx
sudo tee "$NGINX_CONF" > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Konfigurasi untuk WebSocket jika diperlukan
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
}
EOF

# Aktifkan konfigurasi Nginx
echo "Mengaktifkan konfigurasi Nginx..."
sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/

# Uji konfigurasi Nginx
echo "Menguji konfigurasi Nginx..."
sudo nginx -t

# Restart Nginx
echo "Me-restart Nginx..."
sudo systemctl restart nginx

# Dapatkan sertifikat SSL dengan Certbot
echo "Mendapatkan sertifikat SSL dengan Certbot..."
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN"

# Verifikasi auto-renewal
echo "Memverifikasi auto-renewal Certbot..."
sudo certbot renew --dry-run

echo ""
echo "Setup SSL selesai untuk $DOMAIN!"
echo "Sertifikat akan diperbarui secara otomatis oleh Certbot."

exit 0