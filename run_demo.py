#!/usr/bin/env python3
"""Lancer le bot en mode démo"""
import sys
import os

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from main_demo import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())