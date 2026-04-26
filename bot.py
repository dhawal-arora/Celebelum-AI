import asyncio
import discord
from discord.ext import commands
import config

if config.OPUS_LIB_PATH:
    discord.opus.load_opus(config.OPUS_LIB_PATH)

COGS = [
    "cogs.celeb",
    "cogs.translate",
    "cogs.report",
    "cogs.help",
]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["Ptz.", "ptz.", "p.", "P."], intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="/help")
    )
    await bot.tree.sync()


async def main():
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
