# MindTune API

API untuk aplikasi MindTune yang membantu pengguna membuat playlist terapi musik berdasarkan kondisi mood mereka.

## Deployment di VPS Hostinger dengan Docker

### Prasyarat

- VPS Hostinger dengan OS Linux (Ubuntu/Debian direkomendasikan)
- Docker dan Docker Compose terinstal
- Git terinstal
- Domain (opsional)

### Langkah-langkah Deployment

#### 1. Persiapan VPS

Login ke VPS Anda menggunakan SSH:

```bash
ssh username@your_server_ip
```

Update sistem dan install Docker + Docker Compose:

```bash
# Update sistem
sudo apt update && sudo apt upgrade -y

# Install dependensi
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Tambahkan GPG key Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Tambahkan repository Docker
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update package database
sudo apt update

# Install Docker
sudo apt install -y docker-ce

# Tambahkan user ke grup docker (agar tidak perlu sudo)
sudo usermod -aG docker ${USER}

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verifikasi instalasi
docker --version
docker-compose --version
```

Setelah menjalankan perintah di atas, logout dan login kembali agar perubahan grup docker diterapkan.

#### 2. Clone Repository

```bash
# Buat direktori untuk aplikasi
mkdir -p /var/www/mindtune-api
cd /var/www/mindtune-api

# Clone repository
git clone https://github.com/username/mindtune-api.git .
```

#### 3. Konfigurasi Environment Variables

```bash
# Salin file .env.example ke .env
cp .env.example .env

# Edit file .env dengan editor pilihan Anda
nano .env
```

Sesuaikan nilai-nilai dalam file .env dengan kredensial dan konfigurasi yang benar:

```
DB_USER=postgres
DB_PASS=password_yang_aman
DB_NAME=fastapi_mindtune_api
DB_HOST=db
DB_PORT=5432

SQLALCHEMY_DATABASE_URL=postgresql://postgres:password_yang_aman@db:5432/fastapi_mindtune_api

HF_TOKEN=token_huggingface_anda

SP_CLIENT_ID=client_id_spotify_anda
SP_CLIENT_SECRET=client_secret_spotify_anda
SP_REDIRECT_URI=https://domain-anda.com/api/users/callback
SP_SCOPE=user-read-private user-read-email user-library-read playlist-modify-private
```

#### 4. Build dan Jalankan dengan Docker Compose

```bash
# Build dan jalankan container
docker-compose up -d --build

# Cek status container
docker-compose ps
```

#### 5. Jalankan Migrasi Database

```bash
# Masuk ke container API
docker-compose exec api bash

# Jalankan migrasi Alembic
alembic upgrade head

# Keluar dari container
exit
```

#### 6. Konfigurasi Nginx (Opsional, jika menggunakan domain)

Install Nginx:

```bash
sudo apt install -y nginx
```

Buat konfigurasi Nginx untuk aplikasi:

```bash
sudo nano /etc/nginx/sites-available/mindtune-api
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
sudo ln -s /etc/nginx/sites-available/mindtune-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. Konfigurasi SSL dengan Certbot (Opsional)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d domain-anda.com -d www.domain-anda.com
```

### Pemeliharaan dan Update

#### Update Aplikasi

Untuk memperbarui aplikasi dengan perubahan terbaru dari repository:

```bash
# Masuk ke direktori aplikasi
cd /var/www/mindtune-api

# Pull perubahan terbaru
git pull

# Rebuild dan restart container
docker-compose up -d --build
```

#### Backup Database

Untuk membuat backup database:

```bash
# Backup database PostgreSQL
docker-compose exec db pg_dump -U postgres fastapi_mindtune_api > backup_$(date +%Y%m%d).sql
```

#### Melihat Log

```bash
# Log aplikasi API
docker-compose logs -f api

# Log database
docker-compose logs -f db
```

### Troubleshooting

#### Restart Layanan

```bash
# Restart semua layanan
docker-compose restart

# Restart layanan tertentu
docker-compose restart api
```

#### Periksa Status

```bash
# Cek status container
docker-compose ps

# Cek penggunaan resource
docker stats
```

#### Masalah Database

Jika terjadi masalah dengan database, Anda dapat masuk ke container database:

```bash
docker-compose exec db psql -U postgres -d fastapi_mindtune_api
```

### Keamanan

- Pastikan untuk menggunakan password yang kuat untuk database
- Batasi akses SSH hanya ke IP yang dipercaya
- Aktifkan firewall (UFW) dan hanya buka port yang diperlukan (22, 80, 443)
- Perbarui sistem secara berkala

```bash
# Konfigurasi UFW
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```