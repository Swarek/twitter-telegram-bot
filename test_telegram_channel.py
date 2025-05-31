#!/usr/bin/env python3
"""Tester la connexion à un canal Telegram"""
import asyncio
import sys
sys.path.insert(0, 'src')

from publisher import TelegramPublisher
from config import settings

async def test_channel(channel_id: str = None):
    """Tester si le bot peut publier dans un canal"""
    
    if not channel_id:
        channel_id = settings.telegram_channel_id
    
    print(f"🔍 Test du canal: {channel_id}")
    
    publisher = TelegramPublisher(settings.telegram_bot_token)
    
    try:
        # Essayer d'envoyer un message de test
        message = await publisher.bot.send_message(
            chat_id=channel_id,
            text="✅ Test réussi ! Le bot peut publier dans ce canal."
        )
        
        print(f"✅ Succès ! Message envoyé (ID: {message.message_id})")
        print(f"   Le bot peut publier dans {channel_id}")
        
        # Supprimer le message de test après 5 secondes
        await asyncio.sleep(5)
        await publisher.bot.delete_message(
            chat_id=channel_id,
            message_id=message.message_id
        )
        print("🧹 Message de test supprimé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        
        if "Chat not found" in str(e):
            print("\n💡 Solutions:")
            print("   1. Vérifiez que le nom du canal est correct")
            print("   2. Pour un canal privé, utilisez l'ID numérique")
            
        elif "bot is not a member" in str(e) or "need administrator rights" in str(e):
            print("\n💡 Solution:")
            print(f"   1. Ajoutez @{(await publisher.bot.get_me()).username} comme admin du canal")
            print("   2. Donnez-lui la permission de publier des messages")
            
        elif "bot was kicked" in str(e):
            print("\n💡 Le bot a été banni de ce canal. Débannissez-le d'abord.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", "-c", help="Canal à tester (ex: @moncanal)")
    args = parser.parse_args()
    
    asyncio.run(test_channel(args.channel))