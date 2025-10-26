#!/bin/bash

# Script untuk melakukan deployment lengkap MindTune API di VPS

set -e

echo "=== MindTune API Full Deployment Script ==="
echo ""

# Fungsi untuk menampilkan bantuan
show_help() {
    echo "Penggunaan: ./deploy-all.sh [OPSI]"
    echo ""
    echo "Opsi:"
    echo "  --with-domain <domain>  Setup dengan domain (termasuk Nginx dan SSL)"
    echo "  --no-domain            Setup tanpa domain (hanya Docker)"
    echo "  --help                 Tampilkan bantuan ini"
    echo ""
}

# Fungsi untuk setup tanpa domain
setup_no_domain() {
    echo "=== Melakukan setup tanpa domain ==="
    
    # Setup VPS
    echo "Menjalankan setup VPS..."
    bash ./setup-vps.sh
    
    # Setup keamanan
    echo "Menjalankan setup keamanan..."
    bash ./setup-security.sh
    
    # Setup firewall
    echo "Menjalankan setup firewall..."
    bash ./setup-firewall.sh
    
    # Setup aplikasi
    echo "Menjalankan setup aplikasi..."
    bash ./deploy.sh --setup
    
    # Setup database
    echo "Menjalankan setup database..."
    bash ./setup-db.sh --all
    
    echo "Setup tanpa domain selesai!"
    echo "Aplikasi dapat diakses di: http://SERVER_IP:8000"
}

# Fungsi untuk setup dengan domain
setup_with_domain() {
    local domain=$1
    
    if [ -z "$domain" ]; then
        echo "ERROR: Domain tidak ditentukan."
        show_help
        exit 1
    fi
    
    echo "=== Melakukan setup dengan domain: $domain ==="
    
    # Setup VPS
    echo "Menjalankan setup VPS..."
    bash ./setup-vps.sh
    
    # Setup keamanan
    echo "Menjalankan setup keamanan..."
    bash ./setup-security.sh
    
    # Setup firewall
    echo "Menjalankan setup firewall..."
    bash ./setup-firewall.sh
    
    # Setup aplikasi
    echo "Menjalankan setup aplikasi..."
    bash ./deploy.sh --setup
    
    # Setup database
    echo "Menjalankan setup database..."
    bash ./setup-db.sh --all
    
    # Setup Nginx dan SSL
    echo "Menjalankan setup SSL dengan domain: $domain..."
    bash ./setup-ssl.sh "$domain"
    
    echo "Setup dengan domain selesai!"
    echo "Aplikasi dapat diakses di: https://$domain"
}

# Periksa argumen
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Proses argumen
case "$1" in
    --with-domain)
        if [ -z "$2" ]; then
            echo "ERROR: Domain tidak ditentukan."
            show_help
            exit 1
        fi
        setup_with_domain "$2"
        ;;
    --no-domain)
        setup_no_domain
        ;;
    --help)
        show_help
        ;;
    *)
        echo "Opsi tidak dikenal: $1"
        show_help
        exit 1
        ;;
esac

exit 0