#!/bin/bash

# Script untuk restore database MindTune API dari file backup

set -e

echo "=== MindTune API Database Restore Script ==="
echo ""

# Fungsi untuk menampilkan bantuan
show_help() {
    echo "Penggunaan: ./restore.sh <file_backup>"
    echo ""
    echo "Contoh:"
    echo "  ./restore.sh backups/mindtune_db_20230101_120000.sql.gz  # Untuk file terkompresi"
    echo "  ./restore.sh backups/backup_20230101.sql               # Untuk file SQL biasa"
    echo ""
}

# Periksa argumen
if [ $# -eq 0 ]; then
    echo "ERROR: File backup tidak ditentukan."
    show_help
    exit 1
fi

BACKUP_FILE="$1"

# Periksa apakah file backup ada
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: File backup '$BACKUP_FILE' tidak ditemukan."
    exit 1
fi

echo "File backup: $BACKUP_FILE"

# Konfirmasi dari pengguna
echo "PERINGATAN: Proses ini akan menimpa database yang ada."
echo "Pastikan Anda memiliki backup data penting sebelum melanjutkan."
echo ""
read -p "Apakah Anda yakin ingin melanjutkan? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "Restore dibatalkan."
    exit 0
fi

echo "Memulai proses restore..."

# Proses restore berdasarkan ekstensi file
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "Mendeteksi file terkompresi. Melakukan dekompresi dan restore..."
    gunzip -c "$BACKUP_FILE" | docker-compose exec -T db psql -U postgres -d fastapi_mindtune_api
else
    echo "Melakukan restore dari file SQL..."
    cat "$BACKUP_FILE" | docker-compose exec -T db psql -U postgres -d fastapi_mindtune_api
fi

echo "Restore database selesai."

# Restart aplikasi
echo "Me-restart aplikasi..."
docker-compose restart api

echo "Proses restore selesai. Aplikasi telah di-restart."

exit 0