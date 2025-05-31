#!/usr/bin/env python3
"""Analyser les habitudes de publication d'un compte Twitter"""
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from src.scraper.twitter241_scraper import Twitter241Scraper
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def analyze_patterns(username: str):
    """Analyser quand un compte tweete habituellement"""
    async with Twitter241Scraper() as scraper:
        print(f"🔍 Analyse des habitudes de @{username}...")
        print("⚠️  Cette analyse utilise 1 requête API")
        
        # Récupérer les 20 derniers tweets
        tweets = await scraper.fetch_tweets(username, limit=20)
        
        if not tweets:
            print("❌ Aucun tweet trouvé")
            return
        
        # Analyser les heures de publication
        hours = defaultdict(int)
        days = defaultdict(int)
        intervals = []
        
        for i, tweet in enumerate(tweets):
            # Heures
            hour = tweet['created_at'].hour
            hours[hour] += 1
            
            # Jours de la semaine
            day = tweet['created_at'].strftime('%A')
            days[day] += 1
            
            # Intervalles entre tweets
            if i < len(tweets) - 1:
                interval = tweets[i]['created_at'] - tweets[i+1]['created_at']
                intervals.append(interval.total_seconds() / 3600)  # en heures
        
        # Afficher les résultats
        print(f"\n📊 Analyse de {len(tweets)} tweets récents:")
        
        print("\n⏰ Heures les plus actives:")
        sorted_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)
        for hour, count in sorted_hours[:5]:
            print(f"   {hour}h00-{hour+1}h00: {count} tweets")
        
        print("\n📅 Jours les plus actifs:")
        sorted_days = sorted(days.items(), key=lambda x: x[1], reverse=True)
        for day, count in sorted_days:
            print(f"   {day}: {count} tweets")
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            min_interval = min(intervals)
            max_interval = max(intervals)
            
            print(f"\n⏱️ Fréquence de publication:")
            print(f"   Intervalle moyen: {avg_interval:.1f} heures")
            print(f"   Minimum: {min_interval:.1f} heures")
            print(f"   Maximum: {max_interval:.1f} heures")
            
            # Recommandation
            print(f"\n💡 Recommandation:")
            if avg_interval < 24:
                checks_per_day = max(2, int(24 / avg_interval))
                print(f"   Ce compte tweete fréquemment ({avg_interval:.1f}h en moyenne)")
                print(f"   Pour capturer la plupart des tweets: {checks_per_day} vérifications/jour")
                print(f"   Coût estimé: {checks_per_day * 30 * 2} requêtes/mois")
            else:
                print(f"   Ce compte tweete peu ({avg_interval:.1f}h entre tweets)")
                print(f"   1 vérification par jour devrait suffire")
                print(f"   Coût estimé: 60 requêtes/mois")

if __name__ == "__main__":
    username = input("Entrez le nom d'utilisateur Twitter (sans @): ").strip()
    if not username:
        username = "elonmusk"
    
    asyncio.run(analyze_patterns(username))