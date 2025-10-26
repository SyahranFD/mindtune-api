#!/bin/bash

# Script untuk mengelola migrasi database dengan Alembic

set -e

echo "=== MindTune API Database Migration Script ==="
echo ""

# Fungsi untuk menampilkan bantuan
show_help() {
    echo "Penggunaan: ./migrate.sh [OPSI]"
    echo ""
    echo "Opsi:"
    echo "  --upgrade           Jalankan migrasi (upgrade ke versi terbaru)"
    echo "  --downgrade [rev]   Rollback migrasi ke revisi tertentu"
    echo "  --create [message]  Buat migrasi baru"
    echo "  --history           Tampilkan history migrasi"
    echo "  --current           Tampilkan versi database saat ini"
    echo "  --help              Tampilkan bantuan ini"
    echo ""
}

# Fungsi untuk menjalankan migrasi
run_upgrade() {
    echo "=== Menjalankan migrasi database ==="
    
    # Pastikan container API berjalan
    if ! docker-compose ps | grep -q "api.*Up"; then
        echo "Container API tidak berjalan. Menjalankan container..."
        docker-compose up -d api
        echo "Menunggu API siap..."
        sleep 10
    fi
    
    echo "Menjalankan migrasi Alembic..."
    docker-compose exec api alembic upgrade head
    
    echo "Migrasi selesai."
}

# Fungsi untuk rollback migrasi
run_downgrade() {
    local revision=$1
    
    if [ -z "$revision" ]; then
        echo "ERROR: Revisi tidak ditentukan."
        show_help
        exit 1
    fi
    
    echo "=== Melakukan rollback migrasi ke revisi: $revision ==="
    
    # Pastikan container API berjalan
    if ! docker-compose ps | grep -q "api.*Up"; then
        echo "Container API tidak berjalan. Menjalankan container..."
        docker-compose up -d api
        echo "Menunggu API siap..."
        sleep 10
    fi
    
    echo "Menjalankan rollback Alembic..."
    docker-compose exec api alembic downgrade "$revision"
    
    echo "Rollback selesai."
}

# Fungsi untuk membuat migrasi baru
create_migration() {
    local message=$1
    
    if [ -z "$message" ]; then
        echo "ERROR: Pesan migrasi tidak ditentukan."
        show_help
        exit 1
    fi
    
    echo "=== Membuat migrasi baru: $message ==="
    
    # Pastikan container API berjalan
    if ! docker-compose ps | grep -q "api.*Up"; then
        echo "Container API tidak berjalan. Menjalankan container..."
        docker-compose up -d api
        echo "Menunggu API siap..."
        sleep 10
    fi
    
    echo "Membuat migrasi Alembic..."
    docker-compose exec api alembic revision --autogenerate -m "$message"
    
    echo "Pembuatan migrasi selesai."
}

# Fungsi untuk menampilkan history migrasi
show_history() {
    echo "=== Menampilkan history migrasi ==="
    
    # Pastikan container API berjalan
    if ! docker-compose ps | grep -q "api.*Up"; then
        echo "Container API tidak berjalan. Menjalankan container..."
        docker-compose up -d api
        echo "Menunggu API siap..."
        sleep 10
    fi
    
    echo "History migrasi Alembic:"
    docker-compose exec api alembic history
}

# Fungsi untuk menampilkan versi database saat ini
show_current() {
    echo "=== Menampilkan versi database saat ini ==="
    
    # Pastikan container API berjalan
    if ! docker-compose ps | grep -q "api.*Up"; then
        echo "Container API tidak berjalan. Menjalankan container..."
        docker-compose up -d api
        echo "Menunggu API siap..."
        sleep 10
    fi
    
    echo "Versi database saat ini:"
    docker-compose exec api alembic current
}

# Periksa argumen
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Proses argumen
case "$1" in
    --upgrade)
        run_upgrade
        ;;
    --downgrade)
        run_downgrade "$2"
        ;;
    --create)
        create_migration "$2"
        ;;
    --history)
        show_history
        ;;
    --current)
        show_current
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