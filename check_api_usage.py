#!/usr/bin/env python3
"""Vérifier l'utilisation de l'API Twitter241 sur RapidAPI"""
import asyncio
from datetime import datetime
from src.models import db

async def check_usage():
    await db.connect()
    
    # Compter les requêtes d'aujourd'hui
    query = """
    SELECT COUNT(*) as count, MIN(created_at) as first_req, MAX(created_at) as last_req
    FROM api_requests
    WHERE api_name = 'Twitter241' AND DATE(created_at) = CURRENT_DATE
    """
    
    try:
        async with db.pool.acquire() as conn:
            # D'abord, vérifions si la table existe
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'api_requests'
                )
            """)
            
            if not table_exists:
                print("⚠️  La table api_requests n'existe pas encore")
                print("   Le tracking des requêtes API n'est pas encore implémenté")
            else:
                result = await conn.fetchrow(query)
                print(f"📊 Utilisation API Twitter241 aujourd'hui ({datetime.now().date()}):")
                print(f"   Requêtes: {result['count']}/100")
                if result['first_req']:
                    print(f"   Première requête: {result['first_req']}")
                    print(f"   Dernière requête: {result['last_req']}")
    
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Estimation basée sur les tweets publiés
    published_today = await db.pool.fetchval("""
        SELECT COUNT(*) FROM published_tweets 
        WHERE DATE(published_at) = CURRENT_DATE
    """)
    
    print(f"\n📤 Tweets publiés aujourd'hui: {published_today}")
    print("   (Chaque publication = ~2 requêtes API: user info + tweets)")
    
    # Total global
    total_published = await db.get_published_tweets_count()
    print(f"\n📈 Total tweets publiés (tout temps): {total_published}")
    
    await db.disconnect()

if __name__ == "__main__":
    print("🔍 Vérification de l'utilisation de l'API RapidAPI...")
    print("=" * 50)
    asyncio.run(check_usage())
    print("\n💡 Conseil: Avec 100 requêtes/mois, vous pouvez:")
    print("   - Vérifier ~50 fois (2 requêtes par vérification)")
    print("   - Soit environ 1-2 vérifications par jour")
    print("   - Configurez un intervalle de poll plus long (ex: 12h)")