#!/bin/bash

# Script untuk update otomatis MindTune API dari repository
# Tambahkan ke crontab untuk update otomatis
# Contoh: 0 3 * * * /var/www/mindtune-api/auto-update.sh

set -e

# Direktori aplikasi
APP_DIR="/var/www/mindtune-api"

# Direktori log
LOG_DIR="$APP_DIR/logs"
LOG_FILE="$LOG_DIR/auto-update.log"

# Pastikan direktori log ada
mkdir -p "$LOG_DIR"

# Fungsi untuk logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

# Pindah ke direktori aplikasi
cd "$APP_DIR"

# Mulai proses update
log "Memulai proses auto-update..."

# Simpan hash commit saat ini
CURRENT_COMMIT=$(git rev-parse HEAD)
log "Commit saat ini: $CURRENT_COMMIT"

# Ambil perubahan terbaru dari repository
log "Mengambil perubahan terbaru dari repository..."
git fetch origin

# Periksa apakah ada perubahan
LATEST_COMMIT=$(git rev-parse origin/main)
log "Commit terbaru: $LATEST_COMMIT"

if [ "$CURRENT_COMMIT" == "$LATEST_COMMIT" ]; then
    log "Tidak ada perubahan baru. Keluar."
    exit 0
fi

# Backup database sebelum update
log "Membuat backup database sebelum update..."
BACKUP_FILE="$APP_DIR/backups/pre_update_$(date +%Y%m%d_%H%M%S).sql"
mkdir -p "$APP_DIR/backups"
docker-compose exec -T db pg_dump -U postgres fastapi_mindtune_api > "$BACKUP_FILE"
gzip "$BACKUP_FILE"
log "Backup database disimpan di: ${BACKUP_FILE}.gz"

# Pull perubahan terbaru
log "Melakukan git pull..."
git pull origin main

# Rebuild dan restart container
log "Membangun ulang dan me-restart container..."
docker-compose up -d --build

# Jalankan migrasi database
log "Menjalankan migrasi database..."
docker-compose exec -T api alembic upgrade head

# Periksa status aplikasi
log "Memeriksa status aplikasi..."
sleep 10

# Coba akses endpoint health
API_URL="http://localhost:8000/api/health"
response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ "$response" == "200" ]; then
    log "Update berhasil! Aplikasi berjalan dengan baik."
else
    log "PERINGATAN: Aplikasi mungkin tidak berjalan dengan baik. Status: $response"
    log "Mencoba me-restart aplikasi..."
    docker-compose restart api
    sleep 10
    
    # Periksa lagi setelah restart
    response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)
    if [ "$response" == "200" ]; then
        log "Aplikasi berhasil di-restart dan sekarang berjalan dengan baik."
    else
        log "KRITIS: Aplikasi masih tidak berjalan dengan baik setelah restart. Status: $response"
        log "Melakukan rollback ke commit sebelumnya..."
        
        # Rollback ke commit sebelumnya
        git reset --hard "$CURRENT_COMMIT"
        docker-compose up -d --build
        
        # Restore database dari backup
        log "Melakukan restore database dari backup..."
        gunzip -c "${BACKUP_FILE}.gz" | docker-compose exec -T db psql -U postgres -d fastapi_mindtune_api
        
        log "Rollback selesai. Aplikasi dikembalikan ke versi sebelumnya."
    fi
fi

log "Proses auto-update selesai."

exit 0