#!/bin/bash

# Script untuk memantau status aplikasi MindTune API
# Tambahkan ke crontab untuk pemantauan otomatis
# Contoh: */10 * * * * /var/www/mindtune-api/monitor.sh

# Konfigurasi
APP_DIR="/var/www/mindtune-api"
LOG_FILE="$APP_DIR/logs/monitor.log"
API_URL="http://localhost:8000/api/health"
EMAIL="your-email@example.com"

# Pastikan direktori log ada
mkdir -p "$APP_DIR/logs"

# Pindah ke direktori aplikasi
cd "$APP_DIR"

# Fungsi untuk mengirim notifikasi
send_notification() {
    local subject="$1"
    local message="$2"
    
    echo "$message" | mail -s "$subject" "$EMAIL"
    echo "$(date): $subject - $message" >> "$LOG_FILE"
}

# Periksa apakah container berjalan
check_containers() {
    echo "Memeriksa status container..."
    
    # Periksa container API
    if ! docker-compose ps | grep -q "api.*Up"; then
        send_notification "[ALERT] MindTune API Container Down" "Container API tidak berjalan. Mencoba restart..."
        docker-compose restart api
        sleep 10
        
        # Periksa lagi setelah restart
        if ! docker-compose ps | grep -q "api.*Up"; then
            send_notification "[CRITICAL] MindTune API Container Failed" "Container API gagal restart. Diperlukan penanganan manual."
        else
            send_notification "[RESOLVED] MindTune API Container Restored" "Container API berhasil di-restart."
        fi
    fi
    
    # Periksa container Database
    if ! docker-compose ps | grep -q "db.*Up"; then
        send_notification "[ALERT] MindTune Database Container Down" "Container Database tidak berjalan. Mencoba restart..."
        docker-compose restart db
        sleep 20
        
        # Periksa lagi setelah restart
        if ! docker-compose ps | grep -q "db.*Up"; then
            send_notification "[CRITICAL] MindTune Database Container Failed" "Container Database gagal restart. Diperlukan penanganan manual."
        else
            send_notification "[RESOLVED] MindTune Database Container Restored" "Container Database berhasil di-restart."
        fi
    fi
}

# Periksa endpoint health
check_api_health() {
    echo "Memeriksa health API..."
    
    # Coba akses endpoint health
    response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)
    
    if [ "$response" != "200" ]; then
        send_notification "[ALERT] MindTune API Health Check Failed" "API health check mengembalikan status $response. Mencoba restart API..."
        docker-compose restart api
        sleep 10
        
        # Periksa lagi setelah restart
        response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)
        if [ "$response" != "200" ]; then
            send_notification "[CRITICAL] MindTune API Still Unhealthy" "API masih mengembalikan status $response setelah restart. Diperlukan penanganan manual."
        else
            send_notification "[RESOLVED] MindTune API Health Restored" "API health check kembali normal setelah restart."
        fi
    fi
}

# Periksa penggunaan disk
check_disk_usage() {
    echo "Memeriksa penggunaan disk..."
    
    # Ambil persentase penggunaan disk
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//g')
    
    if [ "$disk_usage" -gt 90 ]; then
        send_notification "[ALERT] High Disk Usage" "Penggunaan disk mencapai $disk_usage%. Silakan periksa dan bersihkan ruang disk."
    fi
}

# Periksa penggunaan memori container
check_container_memory() {
    echo "Memeriksa penggunaan memori container..."
    
    # Ambil penggunaan memori container API
    api_memory=$(docker stats --no-stream --format "{{.MemPerc}}" mindtune-api_api_1 | sed 's/%//g')
    
    if [ "$api_memory" -gt 80 ]; then
        send_notification "[ALERT] High API Container Memory Usage" "Penggunaan memori container API mencapai $api_memory%. Mempertimbangkan untuk restart container."
    fi
    
    # Ambil penggunaan memori container Database
    db_memory=$(docker stats --no-stream --format "{{.MemPerc}}" mindtune-api_db_1 | sed 's/%//g')
    
    if [ "$db_memory" -gt 80 ]; then
        send_notification "[ALERT] High Database Container Memory Usage" "Penggunaan memori container Database mencapai $db_memory%. Mempertimbangkan untuk restart container."
    fi
}

# Jalankan semua pemeriksaan
echo "=== Memulai pemantauan MindTune API ($(date)) ==="
check_containers
check_api_health
check_disk_usage
check_container_memory
echo "Pemantauan selesai."

exit 0