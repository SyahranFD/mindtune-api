#!/bin/bash

# Script untuk setup keamanan dasar di VPS untuk MindTune API

set -e

echo "=== MindTune API Security Setup Script ==="
echo ""

# Update sistem
echo "Mengupdate sistem..."
sudo apt update && sudo apt upgrade -y

# Install fail2ban untuk melindungi dari serangan brute force
echo "Menginstal fail2ban..."
sudo apt install -y fail2ban

# Konfigurasi fail2ban
echo "Mengkonfigurasi fail2ban..."
sudo tee /etc/fail2ban/jail.local > /dev/null << EOF
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
findtime = 600
bantime = 3600
EOF

# Restart fail2ban
sudo systemctl restart fail2ban

# Setup UFW (Uncomplicated Firewall)
echo "Mengkonfigurasi firewall (UFW)..."

# Pastikan UFW terinstal
sudo apt install -y ufw

# Reset aturan UFW
sudo ufw --force reset

# Konfigurasi default
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Izinkan SSH
sudo ufw allow ssh

# Izinkan HTTP dan HTTPS
sudo ufw allow http
sudo ufw allow https

# Izinkan port aplikasi (jika diakses langsung tanpa Nginx)
sudo ufw allow 8000/tcp

# Aktifkan UFW
sudo ufw --force enable

# Tampilkan status UFW
echo ""
echo "Status UFW:"
sudo ufw status verbose

# Hardening SSH
echo ""
echo "Mengkonfigurasi SSH untuk keamanan yang lebih baik..."

# Backup file konfigurasi SSH
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# Konfigurasi SSH yang lebih aman
sudo tee /etc/ssh/sshd_config > /dev/null << EOF
# Konfigurasi SSH yang lebih aman
Port 22
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key

# Logging
SyslogFacility AUTH
LogLevel INFO

# Authentication
LoginGraceTime 30
PermitRootLogin no
StrictModes yes
MaxAuthTries 3
MaxSessions 5

PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

PasswordAuthentication yes  # Ubah ke 'no' setelah setup key-based auth

ChallengeResponseAuthentication no
UsePAM yes

X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server
EOF

# Restart SSH service
sudo systemctl restart sshd

# Setup automatic security updates
echo ""
echo "Mengkonfigurasi update keamanan otomatis..."
sudo apt install -y unattended-upgrades apt-listchanges

# Konfigurasi unattended-upgrades
sudo tee /etc/apt/apt.conf.d/50unattended-upgrades > /dev/null << EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}";
    "\${distro_id}:\${distro_codename}-security";
    "\${distro_id}ESMApps:\${distro_codename}-apps-security";
    "\${distro_id}ESM:\${distro_codename}-infra-security";
};

Unattended-Upgrade::Package-Blacklist {
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::InstallOnShutdown "false";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

sudo tee /etc/apt/apt.conf.d/20auto-upgrades > /dev/null << EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

# Restart unattended-upgrades
sudo systemctl restart unattended-upgrades

echo ""
echo "Setup keamanan dasar selesai!"
echo "CATATAN: Untuk keamanan yang lebih baik, pertimbangkan untuk:"
echo "1. Setup key-based authentication untuk SSH dan nonaktifkan password authentication"
echo "2. Mengubah port SSH default (22) ke port non-standar"
echo "3. Menginstal dan mengkonfigurasi tools monitoring seperti Fail2ban"

exit 0