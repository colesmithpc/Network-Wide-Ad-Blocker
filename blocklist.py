#!/usr/bin/env python3

import subprocess
import requests
import json
from datetime import datetime

class BlocklistManager:
    def __init__(self):
        self.blocklists = {
            'ads': [
                'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
                'https://adaway.org/hosts.txt',
                'https://v.firebog.net/hosts/AdguardDNS.txt',
            ],
            'tracking': [
                'https://v.firebog.net/hosts/Easyprivacy.txt',
                'https://v.firebog.net/hosts/Prigent-Ads.txt',
            ],
            'malware': [
                'https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt',
                'https://v.firebog.net/hosts/Prigent-Malware.txt',
            ],
            'social': [
                'https://v.firebog.net/hosts/Prigent-Facebook.txt',
            ]
        }
    
    def add_blocklists(self, categories=None):
        # if no categories specified, add all
        if not categories:
            categories = self.blocklists.keys()
        
        print("Adding blocklists to Pi-hole...")
        
        for category in categories:
            if category not in self.blocklists:
                print(f"Unknown category: {category}")
                continue
            
            print(f"\nAdding {category} blocklists:")
            
            for url in self.blocklists[category]:
                print(f"  Adding {url}")
                try:
                    # add to pihole
                    subprocess.run(
                        ['pihole', '-a', 'adlist', 'add', url],
                        capture_output=True,
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f"  Failed to add {url}: {e}")
        
        print("\nUpdating gravity (this takes a minute)...")
        try:
            subprocess.run(['pihole', '-g'], check=True)
            print("Done!")
        except subprocess.CalledProcessError:
            print("Failed to update gravity")
    
    def list_blocklists(self):
        print("Available blocklist categories:\n")
        for category, lists in self.blocklists.items():
            print(f"{category.upper()}:")
            for url in lists:
                print(f"  - {url}")
            print()
    
    def get_stats(self):
        try:
            # query pihole api
            result = subprocess.run(
                ['pihole', '-c', '-j'],
                capture_output=True,
                text=True,
                check=True
            )
            
            data = json.loads(result.stdout)
            
            print("Pi-hole Statistics:")
            print(f"  Domains blocked: {data.get('domains_being_blocked', 'N/A'):,}")
            print(f"  Total queries: {data.get('dns_queries_today', 'N/A'):,}")
            print(f"  Queries blocked: {data.get('ads_blocked_today', 'N/A'):,}")
            print(f"  Percent blocked: {data.get('ads_percentage_today', 'N/A')}%")
            
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            print("Couldn't get stats - is Pi-hole running?")
    
    def whitelist_domain(self, domain):
        print(f"Whitelisting {domain}...")
        try:
            subprocess.run(
                ['pihole', '-w', domain],
                check=True
            )
            print(f"Added {domain} to whitelist")
        except subprocess.CalledProcessError:
            print(f"Failed to whitelist {domain}")
    
    def blacklist_domain(self, domain):
        print(f"Blacklisting {domain}...")
        try:
            subprocess.run(
                ['pihole', '-b', domain],
                check=True
            )
            print(f"Added {domain} to blacklist")
        except subprocess.CalledProcessError:
            print(f"Failed to blacklist {domain}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Pi-hole blocklist manager')
    parser.add_argument('action', choices=['add', 'list', 'stats', 'whitelist', 'blacklist'])
    parser.add_argument('-c', '--categories', nargs='+', 
                       help='Categories to add (ads, tracking, malware, social)')
    parser.add_argument('-d', '--domain', help='Domain for whitelist/blacklist')
    
    args = parser.parse_args()
    
    manager = BlocklistManager()
    
    if args.action == 'add':
        manager.add_blocklists(args.categories)
    elif args.action == 'list':
        manager.list_blocklists()
    elif args.action == 'stats':
        manager.get_stats()
    elif args.action == 'whitelist':
        if args.domain:
            manager.whitelist_domain(args.domain)
        else:
            print("Need -d domain")
    elif args.action == 'blacklist':
        if args.domain:
            manager.blacklist_domain(args.domain)
        else:
            print("Need -d domain")

if __name__ == "__main__":
    main()
