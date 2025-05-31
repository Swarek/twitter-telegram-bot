#!/usr/bin/env python3
"""Script de debug pour tester différentes APIs RapidAPI"""
import asyncio
import aiohttp
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import get_logger
logger = get_logger(__name__)

async def test_twitter_apis(username: str = "elonmusk"):
    """Tester différentes APIs Twitter sur RapidAPI"""
    
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    if not rapidapi_key:
        logger.error("❌ RAPIDAPI_KEY non trouvée dans .env")
        return
    
    # Différentes APIs Twitter à tester
    apis_to_test = [
        {
            'name': 'Twitter135 - UserTweets',
            'url': 'https://twitter135.p.rapidapi.com/v2/UserTweets/',
            'host': 'twitter135.p.rapidapi.com',
            'params': {'username': username, 'count': '5'}
        },
        {
            'name': 'Twitter135 - UserByScreenName',
            'url': 'https://twitter135.p.rapidapi.com/v1.1/UserByScreenName/',
            'host': 'twitter135.p.rapidapi.com',
            'params': {'username': username}
        },
        {
            'name': 'Twitter API v2',
            'url': f'https://twitter-v23.p.rapidapi.com/user/{username}/tweets',
            'host': 'twitter-v23.p.rapidapi.com',
            'params': {}
        },
        {
            'name': 'Twitter154',
            'url': 'https://twitter154.p.rapidapi.com/user/tweets',
            'host': 'twitter154.p.rapidapi.com',
            'params': {'username': username, 'limit': '5'}
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for api in apis_to_test:
            logger.info(f"\n📌 Test de : {api['name']}")
            logger.info(f"URL : {api['url']}")
            
            headers = {
                'X-RapidAPI-Key': rapidapi_key,
                'X-RapidAPI-Host': api['host']
            }
            
            try:
                async with session.get(api['url'], headers=headers, params=api['params']) as response:
                    status = response.status
                    logger.info(f"Status : {status}")
                    
                    if status == 200:
                        data = await response.json()
                        logger.info(f"✅ Succès ! Réponse reçue")
                        
                        # Afficher un aperçu de la structure
                        if isinstance(data, dict):
                            logger.info(f"Clés principales : {list(data.keys())[:5]}")
                        elif isinstance(data, list):
                            logger.info(f"Liste de {len(data)} éléments")
                            
                        # Sauvegarder pour analyse
                        filename = f"debug_{api['name'].replace(' ', '_').replace('-', '_')}.json"
                        with open(filename, 'w') as f:
                            json.dump(data, f, indent=2, default=str)
                        logger.info(f"💾 Données sauvegardées dans : {filename}")
                        
                    elif status == 403:
                        logger.error(f"❌ 403 Forbidden - Vérifiez l'abonnement à cette API")
                        text = await response.text()
                        logger.error(f"Message : {text[:200]}")
                        
                    elif status == 404:
                        logger.error(f"❌ 404 Not Found - Endpoint incorrect")
                        
                    else:
                        logger.error(f"❌ Erreur {status}")
                        text = await response.text()
                        logger.error(f"Réponse : {text[:200]}")
                        
            except Exception as e:
                logger.error(f"❌ Exception : {e}")
            
            await asyncio.sleep(1)  # Délai entre les tests

async def test_simple_api():
    """Tester une API simple pour vérifier que RapidAPI fonctionne"""
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    
    logger.info("\n🧪 Test d'une API simple (Chuck Norris Jokes - gratuite)")
    
    url = "https://matchilling-chuck-norris-jokes-v1.p.rapidapi.com/jokes/random"
    headers = {
        'X-RapidAPI-Key': rapidapi_key,
        'X-RapidAPI-Host': 'matchilling-chuck-norris-jokes-v1.p.rapidapi.com'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ RapidAPI fonctionne ! Voici une blague :")
                    logger.info(f"📝 {data.get('value', 'Pas de blague')}")
                else:
                    logger.error(f"❌ Erreur {response.status}")
        except Exception as e:
            logger.error(f"❌ Exception : {e}")

async def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "elonmusk"
    
    logger.info("🔍 Debug des APIs Twitter sur RapidAPI")
    logger.info(f"Username test : @{username}")
    
    # Tester d'abord que RapidAPI fonctionne
    await test_simple_api()
    
    # Tester les APIs Twitter
    await test_twitter_apis(username)
    
    logger.info("\n📊 Résumé :")
    logger.info("- Si vous voyez des 403, vérifiez que vous êtes abonné à l'API")
    logger.info("- Si vous voyez des 200, l'API fonctionne !")
    logger.info("- Regardez les fichiers debug_*.json créés pour voir les données")

if __name__ == "__main__":
    asyncio.run(main())