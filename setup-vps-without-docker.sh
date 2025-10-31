#!/bin/bash

# Script untuk setup MindTune API tanpa Docker di VPS
# Pastikan script ini dijalankan dengan hak akses sudo

# Warna untuk output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fungsi untuk menampilkan pesan
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Cek apakah script dijalankan dengan sudo
if [ "$EUID" -ne 0 ]; then
    print_error "Script ini harus dijalankan dengan sudo"
    exit 1
fi

# 1. Update sistem
print_message "Memperbarui sistem..."
apt update && apt upgrade -y

# 2. Install dependensi
print_message "Menginstall dependensi..."
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# 3. Konfigurasi PostgreSQL
print_message "Mengkonfigurasi PostgreSQL..."

# Cek apakah database sudah ada
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='fastapi_mindtune_api'")
if [ "$DB_EXISTS" = "1" ]; then
    print_warning "Database fastapi_mindtune_api sudah ada"
else
    print_message "Membuat database fastapi_mindtune_api..."
    sudo -u postgres psql -c "CREATE DATABASE fastapi_mindtune_api;"
fi

# Cek apakah user sudah ada
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='mindtune'")
if [ "$USER_EXISTS" = "1" ]; then
    print_warning "User mindtune sudah ada"
else
    print_message "Membuat user mindtune..."
    sudo -u postgres psql -c "CREATE USER mindtune WITH PASSWORD 'password_yang_aman';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_mindtune_api TO mindtune;"
fi

# 4. Setup direktori aplikasi
print_message "Menyiapkan direktori aplikasi..."
mkdir -p /var/www/mindtune-api
chown -R $SUDO_USER:$SUDO_USER /var/www/mindtune-api

# 5. Clone repository (jika belum ada)
if [ ! -d "/var/www/mindtune-api/.git" ]; then
    print_message "Cloning repository..."
    cd /var/www/mindtune-api
    sudo -u $SUDO_USER git clone https://github.com/username/mindtune-api.git .
else
    print_warning "Repository sudah ada, melewati proses clone"
fi

# 6. Setup Python environment
print_message "Menyiapkan Python environment..."
cd /var/www/mindtune-api
if [ ! -d "venv" ]; then
    sudo -u $SUDO_USER python3 -m venv venv
fi

# 7. Install dependensi Python
print_message "Menginstall dependensi Python..."
sudo -u $SUDO_USER bash -c "source venv/bin/activate && pip install -r requirement.txt && pip install gunicorn"

# 8. Setup file .env jika belum ada
if [ ! -f "/var/www/mindtune-api/.env" ]; then
    print_message "Menyiapkan file .env..."
    sudo -u $SUDO_USER cp .env.example .env
    print_warning "Silakan edit file .env dengan kredensial yang benar"
    print_warning "Gunakan perintah: nano /var/www/mindtune-api/.env"
else
    print_warning "File .env sudah ada, melewati proses setup"
fi

# 9. Setup Systemd service
print_message "Menyiapkan Systemd service..."
cat > /etc/systemd/system/mindtune-api.service << EOF
[Unit]
Description=MindTune API service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/mindtune-api
ExecStart=/var/www/mindtune-api/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
Restart=always
Environment="PATH=/var/www/mindtune-api/venv/bin"
EnvironmentFile=/var/www/mindtune-api/.env

[Install]
WantedBy=multi-user.target
EOF

# 10. Ubah kepemilikan folder ke www-data
print_message "Mengubah kepemilikan folder ke www-data..."
chown -R www-data:www-data /var/www/mindtune-api

# 11. Aktifkan dan jalankan service
print_message "Mengaktifkan service..."
systemctl enable mindtune-api
systemctl start mindtune-api

# 12. Cek status service
print_message "Status service mindtune-api:"
systemctl status mindtune-api

# 13. Selesai
print_message "Setup selesai!"
print_message "Silakan jalankan migrasi database dengan perintah:"
print_message "cd /var/www/mindtune-api && source venv/bin/activate && alembic upgrade head"
print_message "Jangan lupa untuk mengkonfigurasi Nginx untuk aplikasi Anda"