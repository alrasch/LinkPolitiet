import os
import discord
from dotenv import load_dotenv

from urlextract import URLExtract
from urllib.parse import urlparse

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()


def findUrls(string):
    extractor = URLExtract()
    urls = extractor.find_urls(string)
    return urls


def checkIfWhitelisted(url):
    whitelist = [
        "udl.no",
        "download.udl.no",
        "youtube.com",
        "youtu.be",
        "github.com",
        "udir.no",
        "ndla.no",
        "matematikk.net",
        "en.wikipedia.org",
        "www.csn.edu",
        "catalog.csn.edu"
    ]

    parsed_url = urlparse(url)
    location = parsed_url.netloc

    if len(location) == 0:
        return True

    if location.replace("www.", "") in whitelist:
        print(parsed_url, "totally in whitelist")
        return True
    print(parsed_url, "not whitelisted")
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
            whitelisted = checkIfWhitelisted(url)
            if whitelisted is False:
                print("Suppressing message. {name}: {post}".format(name=message.author, post=message.content))
                await message.delete()
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
