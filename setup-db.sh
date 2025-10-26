#!/bin/bash

# Script untuk setup database MindTune API

set -e

echo "=== MindTune API Database Setup Script ==="
echo ""

# Fungsi untuk menampilkan bantuan
show_help() {
    echo "Penggunaan: ./setup-db.sh [OPSI]"
    echo ""
    echo "Opsi:"
    echo "  --create     Membuat database dan user"
    echo "  --migrate    Menjalankan migrasi database"
    echo "  --seed       Menjalankan seeder database (jika ada)"
    echo "  --all        Menjalankan semua opsi di atas"
    echo "  --help       Menampilkan bantuan ini"
    echo ""
}

# Fungsi untuk membuat database
create_db() {
    echo "=== Membuat database dan user ==="
    
    # Pastikan container database berjalan
    if ! docker-compose ps | grep -q "db.*Up"; then
        echo "Container database tidak berjalan. Menjalankan container..."
        docker-compose up -d db
        echo "Menunggu database siap..."
        sleep 10
    fi
    
    echo "Membuat database dan user..."
    
    # Ambil variabel dari .env
    if [ -f .env ]; then
        source .env
    else
        echo "File .env tidak ditemukan. Menggunakan nilai default."
        DB_USER="postgres"
        DB_PASS="admin"
        DB_NAME="fastapi_mindtune_api"
    fi
    
    # Periksa apakah database sudah ada
    DB_EXISTS=$(docker-compose exec -T db psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")
    
    if [ "$DB_EXISTS" == "1" ]; then
        echo "Database '$DB_NAME' sudah ada."
    else
        echo "Membuat database '$DB_NAME'..."
        docker-compose exec -T db psql -U postgres -c "CREATE DATABASE $DB_NAME;"
    fi
    
    # Periksa apakah user sudah ada (selain postgres)
    if [ "$DB_USER" != "postgres" ]; then
        USER_EXISTS=$(docker-compose exec -T db psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'")
        
        if [ "$USER_EXISTS" == "1" ]; then
            echo "User '$DB_USER' sudah ada."
        else
            echo "Membuat user '$DB_USER'..."
            docker-compose exec -T db psql -U postgres -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASS';"
            docker-compose exec -T db psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
        fi
    fi
    
    echo "Setup database selesai."
}

# Fungsi untuk menjalankan migrasi
run_migration() {
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

# Fungsi untuk menjalankan seeder
run_seed() {
    echo "=== Menjalankan seeder database ==="
    
    # Pastikan container API berjalan
    if ! docker-compose ps | grep -q "api.*Up"; then
        echo "Container API tidak berjalan. Menjalankan container..."
        docker-compose up -d api
        echo "Menunggu API siap..."
        sleep 10
    fi
    
    # Periksa apakah ada script seeder
    if [ -f app/seeders/seed.py ]; then
        echo "Menjalankan seeder..."
        docker-compose exec api python -m app.seeders.seed
        echo "Seeder selesai."
    else
        echo "Script seeder tidak ditemukan. Lewati."
    fi
}

# Periksa argumen
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Proses argumen
case "$1" in
    --create)
        create_db
        ;;
    --migrate)
        run_migration
        ;;
    --seed)
        run_seed
        ;;
    --all)
        create_db
        run_migration
        run_seed
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