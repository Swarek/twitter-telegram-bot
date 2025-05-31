#!/usr/bin/env python3
"""Gérer plusieurs comptes Twitter et calculer l'utilisation API"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import db
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def show_accounts():
    """Afficher tous les comptes et calculer l'utilisation API"""
    await db.connect()
    
    accounts = await db.get_active_accounts()
    
    print("\n📋 COMPTES TWITTER SURVEILLÉS")
    print("=" * 60)
    
    if not accounts:
        print("❌ Aucun compte configuré")
        print("\nPour ajouter un compte:")
        print("python scripts/add_account_simple.py -u username -c @channel")
    else:
        for i, acc in enumerate(accounts, 1):
            print(f"\n{i}. @{acc['username']}")
            print(f"   → Canal: {acc['telegram_channel_id']}")
            print(f"   → Actif: {'✅' if acc['is_active'] else '❌'}")
            if acc['last_tweet_id']:
                print(f"   → Dernier tweet: {acc['last_tweet_id']}")
    
    # Calculer l'utilisation API
    print("\n💰 COÛT API ESTIMÉ")
    print("=" * 60)
    
    active_accounts = len([a for a in accounts if a['is_active']])
    checks_per_day = 3  # Depuis .env
    
    # Chaque vérification = 1 requête user info + 1 requête tweets
    requests_per_check = active_accounts * 2
    daily_requests = requests_per_check * checks_per_day
    monthly_requests = daily_requests * 30
    
    print(f"Comptes actifs: {active_accounts}")
    print(f"Vérifications/jour: {checks_per_day}")
    print(f"Requêtes/vérification: {requests_per_check}")
    print(f"Requêtes/jour: {daily_requests}")
    print(f"Requêtes/mois: {monthly_requests}")
    
    if monthly_requests > 100:
        print(f"\n⚠️  ATTENTION: Dépassement du quota!")
        print(f"   Limite: 100 requêtes/mois")
        print(f"   Utilisation prévue: {monthly_requests} requêtes/mois")
        
        # Recommandations
        max_accounts = 100 // (2 * checks_per_day * 30)
        print(f"\n💡 Recommandations:")
        print(f"   - Maximum {max_accounts} comptes avec 3 checks/jour")
        print(f"   - Ou réduire à 1-2 vérifications/jour")
    else:
        print(f"\n✅ Utilisation dans les limites ({monthly_requests}/100)")
    
    await db.disconnect()

async def add_multiple_accounts():
    """Ajouter plusieurs comptes en une fois"""
    print("\n➕ AJOUTER PLUSIEURS COMPTES")
    print("=" * 60)
    print("Format: username1:channel1, username2:channel2, ...")
    print("Exemple: elonmusk:@news, katyperry:@music")
    print("(Appuyez Enter sans rien écrire pour annuler)")
    
    input_str = input("\nEntrez les comptes: ").strip()
    
    if not input_str:
        print("❌ Annulé")
        return
    
    await db.connect()
    
    # Parser l'entrée
    pairs = [p.strip() for p in input_str.split(',')]
    added = 0
    
    for pair in pairs:
        try:
            username, channel = pair.split(':')
            username = username.strip().lstrip('@')
            channel = channel.strip()
            
            if not channel.startswith('@') and not channel.startswith('-'):
                channel = '@' + channel
            
            account_id = await db.add_twitter_account(
                username=username,
                channel_id=channel,
                twitter_id=None
            )
            
            print(f"✅ @{username} → {channel}")
            added += 1
            
        except Exception as e:
            print(f"❌ Erreur pour '{pair}': {e}")
    
    print(f"\n📊 Résumé: {added} comptes ajoutés")
    
    await db.disconnect()

async def toggle_account(username: str, active: bool):
    """Activer/désactiver un compte"""
    await db.connect()
    
    username = username.lstrip('@')
    
    # Mettre à jour le statut
    query = """
    UPDATE twitter_accounts 
    SET is_active = $1, updated_at = NOW()
    WHERE username = $2
    """
    
    async with db.pool.acquire() as conn:
        result = await conn.execute(query, active, username)
    
    if result.split()[-1] == '1':
        status = "activé" if active else "désactivé"
        print(f"✅ @{username} {status}")
    else:
        print(f"❌ Compte @{username} non trouvé")
    
    await db.disconnect()

async def main():
    """Menu principal"""
    while True:
        print("\n🤖 GESTION DES COMPTES TWITTER")
        print("=" * 40)
        print("1. Voir tous les comptes")
        print("2. Ajouter plusieurs comptes")
        print("3. Désactiver un compte")
        print("4. Réactiver un compte")
        print("5. Quitter")
        
        choice = input("\nChoix: ").strip()
        
        if choice == '1':
            await show_accounts()
        elif choice == '2':
            await add_multiple_accounts()
        elif choice == '3':
            username = input("Username à désactiver (@): ").strip()
            if username:
                await toggle_account(username, False)
        elif choice == '4':
            username = input("Username à réactiver (@): ").strip()
            if username:
                await toggle_account(username, True)
        elif choice == '5':
            print("👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide")
        
        input("\nAppuyez sur Enter pour continuer...")

if __name__ == "__main__":
    asyncio.run(main())