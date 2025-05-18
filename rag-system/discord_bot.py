import discord, os, requests

# Make sure you have a Discord server already
# visit here to get the token (https://discord.com/developers/applications)
# get the channel ID by enabling "developer mode" then right click on a channel to copy the "channel id"
TOKEN = os.getenv("DISCORD_TOKEN", 'replace-with-your-discord-token')
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "123456789012345678"))  # replace with actual

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

BANNED_WORDS = {"sexy", "nudes", "violence", "xxx"}
RAG_API = "http://localhost:8000/predict"

@client.event
async def on_message(message):
    if message.author.bot or message.channel.id != CHANNEL_ID:
        return

    print(f'message received: {message.content}')
    if any(word in message.content.lower() for word in BANNED_WORDS):
        print('⚠️ Message removed due to inappropriate content.')
        await message.delete()
        await message.channel.send(f"⚠️ Message removed due to inappropriate content.")
        return
    try:
        resp = requests.post(RAG_API, json={"query": message.content}).json()
        print(f"RAG answer: {resp['answer']}")
        await message.channel.send(resp["answer"])
    except requests.exceptions.RequestException as e:
        await message.channel.send(f"Request error: {e}")
    except Exception as e:
        await message.channel.send(f"General error: {e}")

if __name__ == "__main__":
    client.run(TOKEN)
