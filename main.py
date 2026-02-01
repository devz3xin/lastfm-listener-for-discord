import discord
from discord.ext import tasks
import requests
import datetime
import json

with open('config.json', 'r') as f:
    config = json.load(f)

LASTFM_API_KEY = config['LASTFM_API_KEY']
LASTFM_USER = config['LASTFM_USER']
DISCORD_TOKEN = config['DISCORD_TOKEN']

client = discord.Client()
last_status = ""

def get_lastfm_status():
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={LASTFM_USER}&api_key={LASTFM_API_KEY}&format=json&limit=1"
    now = datetime.datetime.now().strftime("%H:%M:%S")
    try:
        print(f"[{now}] Tentativo di fetch da Last.fm...")
        r = requests.get(url).json()
        track = r['recenttracks']['track'][0]
        artist = track['artist']['#text']
        song = track['name']
        is_playing = track.get('@attr', {}).get('nowplaying') == 'true'
        
        print(f"[{now}] Dati ricevuti: {song} | {artist} | In riproduzione: {is_playing}")
        return song, artist, is_playing
    except Exception as e:
        print(f"[{now}] Errore durante il fetch: {e}")
        return None, None, False

@tasks.loop(seconds=15)
async def update_presence():
    global last_status
    song, artist, is_playing = get_lastfm_status()
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    if song and artist:
        current_id = f"{song}{artist}{is_playing}"
        
        if current_id != last_status:
            if is_playing:
                activity = discord.Activity(
                    type=discord.ActivityType.listening,
                    name=song,
                    details=song,
                    state=f"di {artist}"
                )
                print(f"[{now}] Aggiornamento Presence: In ascolto di {song} - {artist}")
            else:
                activity = discord.CustomActivity(name=f"📜 Ascoltato: {song} - {artist}")
                print(f"[{now}] Aggiornamento Presence: Ultimo brano {song}")

            await client.change_presence(activity=activity)
            last_status = current_id
        else:
            print(f"[{now}] Nessun cambiamento rilevato nel brano. Skipping update.")

@client.event
async def on_ready():
    print(f"--- Selfbot Online come {client.user} ---")
    if not update_presence.is_running():
        update_presence.start()

client.run(DISCORD_TOKEN)