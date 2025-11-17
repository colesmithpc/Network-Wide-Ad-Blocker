#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

class PiHoleMonitor:
    def __init__(self, pihole_url='http://localhost', api_token=None):
        self.pihole_url = pihole_url
        self.api_token = api_token
        self.stats_file = 'pihole_stats.json'
    
    def get_stats(self):
        # get stats from api
        try:
            url = f"{self.pihole_url}/admin/api.php"
            params = {}
            
            if self.api_token:
                params['auth'] = self.api_token
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            stats = {
                'timestamp': datetime.now().isoformat(),
                'domains_blocked': data.get('domains_being_blocked', 0),
                'queries_today': data.get('dns_queries_today', 0),
                'blocked_today': data.get('ads_blocked_today', 0),
                'percent_blocked': data.get('ads_percentage_today', 0),
                'status': data.get('status', 'unknown')
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return None
    
    def save_stats(self, stats):
        # append to history file
        try:
            history = []
            
            try:
                with open(self.stats_file, 'r') as f:
                    history = json.load(f)
            except FileNotFoundError:
                pass
            
            history.append(stats)
            
            # keep last 7 days only
            if len(history) > 10080:  # 7 days * 24 hours * 60 mins
                history = history[-10080:]
            
            with open(self.stats_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def print_stats(self, stats):
        if not stats:
            print("No stats available")
            return
        
        print("="*50)
        print(f"Pi-hole Stats - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        print(f"Status: {stats['status']}")
        print(f"Domains blocked: {stats['domains_blocked']:,}")
        print(f"Queries today: {stats['queries_today']:,}")
        print(f"Blocked today: {stats['blocked_today']:,}")
        print(f"Percent blocked: {stats['percent_blocked']:.1f}%")
        print("="*50)
    
    def get_top_blocked(self):
        try:
            url = f"{self.pihole_url}/admin/api.php?topItems=10"
            
            if self.api_token:
                url += f"&auth={self.api_token}"
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            print("\nTop Blocked Domains:")
            for domain, count in data.get('top_ads', {}).items():
                print(f"  {domain}: {count} hits")
            
        except Exception as e:
            print(f"Error getting top blocked: {e}")
    
    def check_health(self):
        stats = self.get_stats()
        
        if not stats:
            return False
        
        # check if pihole is running
        if stats['status'] != 'enabled':
            print("WARNING: Pi-hole is not enabled!")
            return False
        
        # check if blocking anything
        if stats['domains_blocked'] == 0:
            print("WARNING: No domains in blocklist!")
            return False
        
        return True
    
    def send_daily_report(self, email_config):
        stats = self.get_stats()
        
        if not stats:
            return
        
        # build email
        subject = f"Pi-hole Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""Pi-hole Daily Statistics
        
Queries Today: {stats['queries_today']:,}
Blocked Today: {stats['blocked_today']:,}
Percent Blocked: {stats['percent_blocked']:.1f}%
Total Domains Blocked: {stats['domains_blocked']:,}
Status: {stats['status']}

Pi-hole is protecting your network from ads and trackers.
        """
        
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = email_config['from_email']
            msg['To'] = email_config['to_email']
            
            server = smtplib.SMTP(email_config['smtp_server'], 
                                 email_config.get('smtp_port', 587))
            server.starttls()
            
            if email_config.get('password'):
                server.login(email_config['from_email'], 
                           email_config['password'])
            
            server.send_message(msg)
            server.quit()
            
            print(f"Daily report sent to {email_config['to_email']}")
            
        except Exception as e:
            print(f"Failed to send email: {e}")
    
    def monitor_loop(self, interval_minutes=5):
        print(f"Starting Pi-hole monitor - checking every {interval_minutes} minutes")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                stats = self.get_stats()
                
                if stats:
                    self.print_stats(stats)
                    self.save_stats(stats)
                    self.check_health()
                else:
                    print("Failed to get stats")
                
                print(f"\nNext check in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\nMonitor stopped")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Pi-hole monitoring tool')
    parser.add_argument('-u', '--url', default='http://localhost',
                       help='Pi-hole URL')
    parser.add_argument('-t', '--token', help='API token')
    parser.add_argument('-m', '--monitor', action='store_true',
                       help='Start monitoring loop')
    parser.add_argument('-i', '--interval', type=int, default=5,
                       help='Check interval in minutes')
    
    args = parser.parse_args()
    
    monitor = PiHoleMonitor(args.url, args.token)
    
    if args.monitor:
        monitor.monitor_loop(args.interval)
    else:
        stats = monitor.get_stats()
        monitor.print_stats(stats)
        monitor.get_top_blocked()

if __name__ == "__main__":
    main()
