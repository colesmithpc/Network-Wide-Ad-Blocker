#!/bin/bash

# pi-hole network ad blocker installer
# run this on your raspberry pi

echo "=================================="
echo "Pi-hole Ad Blocker Setup"
echo "=================================="
echo ""

# check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

# update system first
echo "[*] Updating system packages..."
apt-get update
apt-get upgrade -y

echo ""
echo "[*] Installing dependencies..."
apt-get install -y curl git

# download and run pi-hole installer
echo ""
echo "[*] Downloading Pi-hole installer..."
curl -sSL https://install.pi-hole.net | bash

echo ""
echo "=================================="
echo "Pi-hole Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Note your admin password (shown above)"
echo "2. Access web interface at http://$(hostname -I | awk '{print $1}')/admin"
echo "3. Configure your router to use this Pi as DNS server"
echo "4. Or configure individual devices to use: $(hostname -I | awk '{print $1}')"
echo ""
echo "To change admin password: pihole -a -p"
echo ""
