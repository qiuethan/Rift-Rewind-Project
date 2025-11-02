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
    "piltover": "https://wiki.leagueoflegends.com/en-us/images/Piltover_Arcane_02.jpg",
    "ionia": "https://cdnportal.mobalytics.gg/production/1969/10/Ionia-Splash.jpg",
    "demacia": "https://wiki.leagueoflegends.com/en-us/images/Demacia_The_Grand_Plaza.jpg",
    "noxus": "https://wiki.leagueoflegends.com/en-us/images/thumb/Noxus_LoR_Background.jpg/800px-Noxus_LoR_Background.jpg",
    "freljord": "https://wiki.leagueoflegends.com/en-us/images/thumb/Freljord_LoR_Background.jpg/800px-Freljord_LoR_Background.jpg",
    "shadowisles": "https://cmsassets.rgpub.io/sanity/images/dsfx7636/universe/a16b2a6f1de9d71d750ed8b14ebfcc8f07c8b6a4-1920x721.jpg",
    "shurima": "https://wiki.leagueoflegends.com/en-us/images/thumb/Shurima_The_Ruins_Of_Shurima.jpg/1200px-Shurima_The_Ruins_Of_Shurima.jpg",
    "targon": "https://64.media.tumblr.com/da10d0926b2364d1c1360f007bfeb454/7e2a959ade29a81c-6a/s1280x1920/fe5bff1bd7ae36cdb5aafc12c0573d130ec2ce64.png",
    "bilgewater": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1920&h=1080&fit=crop",
    "ixtal": "https://cdnb.artstation.com/p/assets/images/images/029/672/207/large/lucas-parolin-ixtal-v01-2.jpg?1598264084"
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
