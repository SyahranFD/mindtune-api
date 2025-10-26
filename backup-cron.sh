#!/bin/bash

# Script untuk backup otomatis database MindTune API
# Tambahkan ke crontab untuk backup otomatis
# Contoh: 0 2 * * * /var/www/mindtune-api/backup-cron.sh

# Direktori untuk menyimpan backup
BACKUP_DIR="/var/www/mindtune-api/backups"

# Format nama file backup (tanggal-waktu)
BACKUP_FILE="$BACKUP_DIR/mindtune_db_$(date +%Y%m%d_%H%M%S).sql"

# Pastikan direktori backup ada
mkdir -p "$BACKUP_DIR"

# Direktori aplikasi
APP_DIR="/var/www/mindtune-api"

# Pindah ke direktori aplikasi
cd "$APP_DIR"

# Jalankan backup
echo "Membuat backup database ke $BACKUP_FILE"
docker-compose exec -T db pg_dump -U postgres fastapi_mindtune_api > "$BACKUP_FILE"

# Kompres file backup
gzip "$BACKUP_FILE"

# Hapus backup yang lebih lama dari 30 hari
find "$BACKUP_DIR" -name "mindtune_db_*.sql.gz" -type f -mtime +30 -delete

echo "Backup selesai: ${BACKUP_FILE}.gz"
echo "Backup yang lebih lama dari 30 hari telah dihapus."

# Log backup
echo "$(date): Backup database berhasil dibuat: ${BACKUP_FILE}.gz" >> "$BACKUP_DIR/backup.log"

exit 0