#!/usr/bin/env python3
"""Lancer le bot Twitter-Telegram"""
import sys
import os

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from main_hybrid import main
import asyncio

if __name__ == "__main__":
    print("🚀 Démarrage du bot Twitter-Telegram...")
    print("📋 Comptes surveillés: (configurés dans .env)")
    print("📢 Canal Telegram: (configuré dans .env)")
    print("-" * 50)
    
    asyncio.run(main())