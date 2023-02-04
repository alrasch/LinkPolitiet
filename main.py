import os
import discord
from dotenv import load_dotenv

from urlextract import URLExtract
from urllib.parse import urlparse

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def findUrls(string):
    extractor = URLExtract()
    urls = extractor.find_urls(string)
    return urls

def checkIfBlacklisted(url):
    with open("blacklist", "r") as f:
        blacklist = f.read().splitlines()

    parsed_url = urlparse(url)
    location = parsed_url.netloc

    if location.replace("www.", "") in blacklist:
        return True
    return False


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print("{}: {}".format(message.author, message.content))

    if message.author.name == os.getenv("ADMIN_NAME") and \
            message.author.discriminator == os.getenv("ADMIN_DISCRIMINATOR"):
        return

    urls = findUrls(message.content)

    try:
        for url in urls:
            with open("linked_links.log", "a") as file:
                file.write(f'\n{message.author.name} in {message.channel.name}:\n{message.content}\n{url}\n')

            blacklisted = checkIfBlacklisted(url)
            if blacklisted is True:
                with open("suppressed.log", "a") as f:
                    f.write("\nSuppressing message. {name} in {channel}: {post}\n".format(
                        name=message.author,
                        channel=message.channel.name,
                        post=message.content)
                    )
                await message.delete()
                await message.channel.send(content="Fjerna ei melding som inneholdt en link.")

    except discord.Forbidden as ex:
        print("Failed to delete message due to permissions.")
        print(ex.text)
        print(ex.response)
    except discord.NotFound as ex:
        print("Failed to find message.")
        print(ex.text)
    except discord.HTTPException as ex:
        print("Failed to delete message.")
        print(ex.text)


client.run(TOKEN)
