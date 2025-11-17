#!/bin/bash

# pihole configuration helper script

echo "=================================="
echo "Pi-hole Configuration Helper"
echo "=================================="
echo ""

# get pi ip address
PI_IP=$(hostname -I | awk '{print $1}')

echo "Your Pi-hole IP: $PI_IP"
echo ""

# check if pihole is installed
if ! command -v pihole &> /dev/null; then
    echo "Pi-hole not installed yet"
    echo "Run the install script first"
    exit 1
fi

echo "What do you want to configure?"
echo ""
echo "1) Change admin password"
echo "2) Update blocklists"
echo "3) Add custom DNS servers"
echo "4) Configure DHCP"
echo "5) Show current settings"
echo "6) Backup configuration"
echo "7) Restore configuration"
echo "8) Show device setup instructions"
echo ""

read -p "Choice (1-8): " choice

case $choice in
    1)
        echo ""
        echo "Setting new admin password..."
        pihole -a -p
        ;;
    
    2)
        echo ""
        echo "Updating gravity (blocklists)..."
        pihole -g
        echo "Done"
        ;;
    
    3)
        echo ""
        echo "Current DNS servers:"
        cat /etc/pihole/setupVars.conf | grep PIHOLE_DNS
        echo ""
        echo "Common options:"
        echo "  Google: 8.8.8.8, 8.8.4.4"
        echo "  Cloudflare: 1.1.1.1, 1.0.0.1"
        echo "  Quad9: 9.9.9.9, 149.112.112.112"
        echo ""
        echo "Edit /etc/pihole/setupVars.conf to change"
        echo "Then run: pihole restartdns"
        ;;
    
    4)
        echo ""
        echo "To enable DHCP:"
        echo "1. Go to http://$PI_IP/admin"
        echo "2. Settings -> DHCP"
        echo "3. Enable DHCP server"
        echo "4. Disable DHCP on your router"
        ;;
    
    5)
        echo ""
        echo "Current Pi-hole settings:"
        echo ""
        pihole -c -e
        ;;
    
    6)
        echo ""
        BACKUP_FILE="pihole-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
        echo "Creating backup..."
        pihole -a -t
        echo ""
        echo "Backup created in /var/www/html/admin/"
        echo "Download it from: http://$PI_IP/admin/scripts/pi-hole/php/teleporter.php"
        ;;
    
    7)
        echo ""
        echo "To restore from backup:"
        echo "1. Go to http://$PI_IP/admin"
        echo "2. Settings -> Teleporter"
        echo "3. Upload your backup file"
        ;;
    
    8)
        echo ""
        echo "=================================="
        echo "Device Setup Instructions"
        echo "=================================="
        echo ""
        echo "Option A: Configure Router (Recommended)"
        echo "  1. Log into your router admin panel"
        echo "  2. Find DNS settings (usually in DHCP/LAN settings)"
        echo "  3. Set Primary DNS to: $PI_IP"
        echo "  4. Leave Secondary DNS blank or use: 1.1.1.1"
        echo "  5. Save and reboot router"
        echo "  6. All devices will now use Pi-hole"
        echo ""
        echo "Option B: Configure Individual Devices"
        echo ""
        echo "  Windows:"
        echo "    Control Panel -> Network -> Change adapter settings"
        echo "    Right-click connection -> Properties"
        echo "    IPv4 -> Properties -> Use following DNS: $PI_IP"
        echo ""
        echo "  macOS:"
        echo "    System Preferences -> Network"
        echo "    Advanced -> DNS -> Add: $PI_IP"
        echo ""
        echo "  iPhone/iPad:"
        echo "    Settings -> WiFi -> (i) next to network"
        echo "    Configure DNS -> Manual -> Add: $PI_IP"
        echo ""
        echo "  Android:"
        echo "    Settings -> WiFi -> Long press network -> Modify"
        echo "    Advanced -> DNS 1: $PI_IP"
        echo ""
        echo "To test if it's working:"
        echo "  Visit: http://pi.hole/admin"
        echo "  Or: http://$PI_IP/admin"
        echo ""
        ;;
    
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Done!"
