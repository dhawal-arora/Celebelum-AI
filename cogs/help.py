import discord
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="help", description="Show available commands.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Celebelum",
            description=(
                "**CELEBRITY-AI STUDY TOOL**\n\n"
                "Learn From Celebrity 🍎: `/celeb`\n"
                "Learn In Foreign Language 🌍: `/translate`\n"
                "Report & Leaderboard 🏆: `/report`"
            ),
            color=0x00FF00,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
