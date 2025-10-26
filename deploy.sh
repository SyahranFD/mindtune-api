#!/bin/bash

# Script untuk deployment dan update MindTune API di VPS

set -e

echo "=== MindTune API Deployment Script ==="
echo ""

# Fungsi untuk menampilkan bantuan
show_help() {
    echo "Penggunaan: ./deploy.sh [OPSI]"
    echo ""
    echo "Opsi:"
    echo "  --setup       Melakukan setup awal (build dan jalankan container)"
    echo "  --update      Update aplikasi dari git dan restart container"
    echo "  --migrate     Jalankan migrasi database"
    echo "  --logs        Tampilkan logs aplikasi"
    echo "  --backup      Backup database"
    echo "  --restart     Restart semua container"
    echo "  --help        Tampilkan bantuan ini"
    echo ""
}

# Fungsi untuk setup awal
setup() {
    echo "=== Melakukan setup awal ==="
    
    # Pastikan file .env ada
    if [ ! -f .env ]; then
        echo "File .env tidak ditemukan. Menyalin dari .env.example..."
        cp .env.example .env
        echo "Silakan edit file .env dengan konfigurasi yang benar."
        echo "Jalankan: nano .env"
        exit 1
    fi
    
    echo "Building dan menjalankan container..."
    docker-compose up -d --build
    
    echo "Setup selesai. Jalankan './deploy.sh --migrate' untuk menjalankan migrasi database."
}

# Fungsi untuk update aplikasi
update() {
    echo "=== Mengupdate aplikasi ==="
    
    echo "Mengambil perubahan terbaru dari git..."
    git pull
    
    echo "Membangun ulang dan me-restart container..."
    docker-compose up -d --build
    
    echo "Update selesai."
}

# Fungsi untuk menjalankan migrasi
migrate() {
    echo "=== Menjalankan migrasi database ==="
    
    echo "Menjalankan migrasi Alembic..."
    docker-compose exec api alembic upgrade head
    
    echo "Migrasi selesai."
}

# Fungsi untuk melihat logs
show_logs() {
    echo "=== Menampilkan logs aplikasi ==="
    docker-compose logs -f api
}

# Fungsi untuk backup database
backup_db() {
    echo "=== Membuat backup database ==="
    
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    echo "Membuat backup ke file: $BACKUP_FILE"
    
    docker-compose exec -T db pg_dump -U postgres fastapi_mindtune_api > $BACKUP_FILE
    
    echo "Backup selesai. File tersimpan di: $BACKUP_FILE"
}

# Fungsi untuk restart container
restart() {
    echo "=== Me-restart semua container ==="
    docker-compose restart
    echo "Restart selesai."
}

# Periksa argumen
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Proses argumen
case "$1" in
    --setup)
        setup
        ;;
    --update)
        update
        ;;
    --migrate)
        migrate
        ;;
    --logs)
        show_logs
        ;;
    --backup)
        backup_db
        ;;
    --restart)
        restart
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