#!/usr/bin/env python3
"""Lancer le bot avec les APIs gratuites/peu chères"""
import sys
import os

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import asyncio
from main_cheap import main

if __name__ == "__main__":
    print("🚀 Démarrage du bot Twitter-Telegram (APIs économiques)...")
    print("💰 Utilise RapidAPI gratuit ou APIs très peu chères")
    print("📋 Comptes surveillés: (configurés dans .env)")
    print("📢 Canal Telegram: (configuré dans .env)")
    print("-" * 50)
    
    # Vérifier la configuration
    rapidapi_key = os.getenv('RAPIDAPI_KEY', '')
    twitterapi_io_key = os.getenv('TWITTERAPI_IO_KEY', '')
    
    if not rapidapi_key and not twitterapi_io_key:
        print("\n⚠️  ATTENTION: Aucune API configurée!")
        print("Veuillez suivre le guide CHEAP_APIS_GUIDE.md pour configurer une API gratuite.")
        print("\nPour démarrer rapidement:")
        print("1. Inscrivez-vous sur https://rapidapi.com (gratuit)")
        print("2. Cherchez 'Twitter135' et abonnez-vous au plan gratuit")
        print("3. Ajoutez votre clé dans .env : RAPIDAPI_KEY=votre_cle")
        sys.exit(1)
    
    if rapidapi_key:
        print("✅ RapidAPI configurée")
    if twitterapi_io_key:
        print("✅ TwitterAPI.io configurée")
    
    print("\nDémarrage...\n")
    
    asyncio.run(main())