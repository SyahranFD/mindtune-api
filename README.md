# MindTune API

API untuk aplikasi MindTune yang membantu pengguna membuat playlist terapi musik berdasarkan kondisi mood mereka.

## Deployment di VPS Tanpa Docker

### Prasyarat

- VPS dengan OS Linux (Ubuntu/Debian direkomendasikan)
- Python 3.9+ terinstal
- PostgreSQL terinstal
- Nginx terinstal
- Git terinstal
- Domain (opsional)

### Langkah-langkah Deployment

#### 1. Persiapan VPS

Login ke VPS Anda menggunakan SSH:

```bash
ssh username@your_server_ip
```

Update sistem dan install dependensi:

```bash
# Update sistem
sudo apt update && sudo apt upgrade -y

# Install dependensi
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git
```

#### 2. Konfigurasi PostgreSQL

```bash
# Masuk ke PostgreSQL
sudo -u postgres psql

# Buat database
CREATE DATABASE fastapi_mindtune_api;

# Buat user dan berikan password
CREATE USER mindtune WITH PASSWORD 'password_yang_aman';

# Berikan hak akses ke database
GRANT ALL PRIVILEGES ON DATABASE fastapi_mindtune_api TO mindtune;

# Keluar dari PostgreSQL
\q
```

#### 3. Clone Repository

```bash
# Buat direktori untuk aplikasi
sudo mkdir -p /var/www/mindtune-api-v1
sudo chown -R $USER:$USER /var/www/mindtune-api-v1
cd /var/www/mindtune-api-v1

# Clone repository
git clone https://github.com/username/mindtune-api.git .
```

#### 4. Setup Python Environment

```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Install dependensi
pip install -r requirement.txt
```

#### 5. Konfigurasi Environment Variables

```bash
# Salin file .env.example ke .env
cp .env.example .env

# Edit file .env dengan editor pilihan Anda
nano .env
```

Sesuaikan nilai-nilai dalam file .env dengan kredensial dan konfigurasi yang benar:

```
DB_USER=mindtune
DB_PASS=password_yang_aman
DB_NAME=fastapi_mindtune_api
DB_HOST=localhost
DB_PORT=5432

SQLALCHEMY_DATABASE_URL=postgresql://mindtune:password_yang_aman@localhost:5432/fastapi_mindtune_api

HF_TOKEN=token_huggingface_anda

SP_CLIENT_ID=client_id_spotify_anda
SP_CLIENT_SECRET=client_secret_spotify_anda
SP_REDIRECT_URI=https://domain-anda.com/api/users/callback
SP_SCOPE=user-read-private user-read-email user-library-read playlist-modify-private
```

#### 6. Jalankan Migrasi Database

```bash
# Pastikan virtual environment aktif
source venv/bin/activate

# Jalankan migrasi Alembic
alembic upgrade head
```

#### 7. Konfigurasi Gunicorn dan Systemd

Buat file service untuk Systemd:

```bash
sudo nano /etc/systemd/system/mindtune-api-v1.service
```

Tambahkan konfigurasi berikut:

```ini
[Unit]
Description=MindTune API service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/mindtune-api-v1
ExecStart=/var/www/mindtune-api-v1/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
Restart=always
Environment="PATH=/var/www/mindtune-api-v1/venv/bin"
EnvironmentFile=/var/www/mindtune-api-v1/.env

[Install]
WantedBy=multi-user.target
```

> **Catatan**: Jika port 8000 sudah digunakan oleh aplikasi lain di server Anda, Anda dapat mengubah port dengan mengganti baris ExecStart menjadi:
> ```
> ExecStart=/var/www/mindtune-api-v1/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8001
> ```
> Pastikan juga untuk menyesuaikan konfigurasi Nginx pada langkah 8 agar mengarah ke port yang sama.

Aktifkan dan jalankan service:

```bash
# Pastikan gunicorn terinstal
pip install gunicorn

# Ubah kepemilikan folder
sudo chown -R www-data:www-data /var/www/mindtune-api-v1

# Aktifkan service
sudo systemctl enable mindtune-api-v1

# Jalankan service
sudo systemctl start mindtune-api-v1

# Cek status service
sudo systemctl status mindtune-api-v1
```

#### 8. Konfigurasi Nginx

Buat konfigurasi Nginx untuk aplikasi:

```bash
sudo nano /etc/nginx/sites-available/mindtune-api-v1
```

Tambahkan konfigurasi berikut:

```nginx
server {
    listen 80;
    server_name domain-anda.com www.domain-anda.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Aktifkan konfigurasi dan restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/mindtune-api-v1 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. Konfigurasi SSL dengan Certbot (Opsional)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d domain-anda.com -d www.domain-anda.com
```

### Pemeliharaan dan Update

#### Update Aplikasi

Untuk memperbarui aplikasi dengan perubahan terbaru dari repository:

```bash
# Masuk ke direktori aplikasi
cd /var/www/mindtune-api-v1

# Aktifkan virtual environment
source venv/bin/activate

# Pull perubahan terbaru
git pull

# Install dependensi baru (jika ada)
pip install -r requirement.txt

# Jalankan migrasi (jika ada)
alembic upgrade head

# Restart service
sudo systemctl restart mindtune-api-v1
```

#### Backup Database

Untuk membuat backup database:

```bash
# Backup database PostgreSQL
sudo -u postgres pg_dump fastapi_mindtune_api > backup_$(date +%Y%m%d).sql
```

#### Melihat Log

```bash
# Log aplikasi API
sudo journalctl -u mindtune-api-v1

# Log Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

Panduan navigasi pager (less):

- Space / Page Down: ke halaman berikutnya
- b / Page Up: ke halaman sebelumnya
- Enter / panah bawah: turun satu baris
- y / k / panah atas: naik satu baris
- g: lompat ke awal
- G: lompat ke akhir
- /kata: cari maju; n hasil berikutnya; N hasil sebelumnya
- ?kata: cari mundur; n/N sama seperti di atas
- q: keluar dari pager

Opsi tanpa pager (langsung tampil penuh):

```bash
sudo journalctl -u mindtune-api-v1 --no-pager
SYSTEMD_PAGER=cat sudo journalctl -u mindtune-api-v1
sudo systemctl status mindtune-api-v1 --no-pager
```

Melihat log terbaru dan yang relevan:

```bash
# Live mengikuti log
sudo journalctl -u mindtune-api-v1 -f --no-pager

# Lompat ke akhir dan tampilkan 200 baris terakhir
sudo journalctl -u mindtune-api-v1 -e -n 200 --no-pager

# Filter berdasarkan waktu
sudo journalctl -u mindtune-api-v1 --since "30 minutes ago" --no-pager

# Tampilkan hanya error (prioritas err)
sudo journalctl -u mindtune-api-v1 -p err -n 100 --no-pager
```

## Troubleshooting

### Service Tidak Berjalan

Periksa status service:

```bash
sudo systemctl status mindtune-api-v1

Lihat log untuk mencari masalah:

sudo journalctl -u mindtune-api-v1
```

### Masalah Database

Jika terjadi masalah dengan database, coba masuk ke PostgreSQL:

```bash
sudo -u postgres psql
```

Kemudian periksa database dan tabel:

```sql
\l
\c fastapi_mindtune_api
\dt
```

### Restart Service

Jika perlu, restart service:

```bash
sudo systemctl restart mindtune-api-v1
sudo systemctl restart nginx
```

## Deployment dengan Docker

Untuk instruksi deployment menggunakan Docker, silakan lihat [DEPLOYMENT-DOCKER.md](DEPLOYMENT-DOCKER.md).