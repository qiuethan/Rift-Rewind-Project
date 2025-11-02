#!/usr/bin/env python3
"""
Download League of Legends region and champion images
"""
import os
import urllib.request
from pathlib import Path

# Create directories
REGIONS_DIR = Path("app/frontend/public/img/regions")
CHAMPIONS_DIR = Path("app/frontend/public/img/champions")
REGIONS_DIR.mkdir(parents=True, exist_ok=True)
CHAMPIONS_DIR.mkdir(parents=True, exist_ok=True)

# Champion Data Dragon base URL
DDRAGON_VERSION = "14.1.1"
CHAMPION_BASE = f"https://ddragon.leagueoflegends.com/cdn/{DDRAGON_VERSION}/img/champion"
SPLASH_BASE = "https://ddragon.leagueoflegends.com/cdn/img/champion/splash"

# Region-specific champions
REGION_CHAMPIONS = {
    "piltover": ["Jayce", "Vi", "Caitlyn", "Jinx", "Ekko", "Heimerdinger"],
    "ionia": ["Yasuo", "Ahri", "Akali", "Shen", "Zed", "Irelia"],
    "demacia": ["Garen", "Lux", "JarvanIV", "Fiora", "Vayne", "XinZhao"],
    "noxus": ["Darius", "Draven", "Katarina", "Swain", "Talon", "Vladimir"],
    "freljord": ["Ashe", "Sejuani", "Braum", "Lissandra", "Trundle", "Anivia"],
    "shadowisles": ["Thresh", "Hecarim", "Kalista", "Viego", "Gwen", "Maokai"],
    "shurima": ["Azir", "Nasus", "Renekton", "Sivir", "Taliyah", "Xerath"],
    "targon": ["Leona", "Diana", "Pantheon", "Taric", "AurelionSol", "Zoe"],
    "bilgewater": ["MissFortune", "Gangplank", "Pyke", "Nautilus", "Graves", "TwistedFate"],
    "ixtal": ["Qiyana", "Rengar", "Nidalee", "Zyra", "Neeko", "Malphite"]
}

# Placeholder hero images (using Unsplash)
REGION_HERO_URLS = {
    "piltover": "https://images.unsplash.com/photo-1518005020951-eccb494ad742?w=1920&h=1080&fit=crop",
    "ionia": "https://images.unsplash.com/photo-1528164344705-47542687000d?w=1920&h=1080&fit=crop",
    "demacia": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1920&h=1080&fit=crop",
    "noxus": "https://images.unsplash.com/photo-1509803874385-db7c23652552?w=1920&h=1080&fit=crop",
    "freljord": "https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=1920&h=1080&fit=crop",
    "shadowisles": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1920&h=1080&fit=crop",
    "shurima": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=1920&h=1080&fit=crop",
    "targon": "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1920&h=1080&fit=crop",
    "bilgewater": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1920&h=1080&fit=crop",
    "ixtal": "https://images.unsplash.com/photo-1511497584788-876760111969?w=1920&h=1080&fit=crop"
}

def download_file(url, filepath):
    """Download a file from URL to filepath"""
    try:
        print(f"Downloading {filepath.name}...")
        urllib.request.urlretrieve(url, filepath)
        print(f"✓ Downloaded {filepath.name}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filepath.name}: {e}")
        return False

def download_champion_portraits():
    """Download champion portrait images"""
    print("\n=== Downloading Champion Portraits ===")
    for region, champions in REGION_CHAMPIONS.items():
        print(f"\n{region.upper()}:")
        for champ in champions:
            url = f"{CHAMPION_BASE}/{champ}.png"
            filepath = CHAMPIONS_DIR / f"{champ.lower()}.png"
            download_file(url, filepath)

def download_hero_images():
    """Download region hero background images"""
    print("\n=== Downloading Region Hero Images ===")
    for region, url in REGION_HERO_URLS.items():
        filepath = REGIONS_DIR / f"{region}-hero.jpg"
        download_file(url, filepath)
        
        # Also create bg version
        bg_filepath = REGIONS_DIR / f"{region}-bg.jpg"
        if not bg_filepath.exists():
            download_file(url, bg_filepath)

if __name__ == "__main__":
    print("League of Legends Image Downloader")
    print("=" * 50)
    
    download_hero_images()
    download_champion_portraits()
    
    print("\n" + "=" * 50)
    print("✓ Download complete!")
    print(f"Champion images: {CHAMPIONS_DIR}")
    print(f"Region images: {REGIONS_DIR}")
