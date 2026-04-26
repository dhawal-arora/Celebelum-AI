import os
import discord
from discord.ext import commands

REPORT_ASSETS = {
    "1R": ("assets/reports/quiz_performance.jpeg", "quiz_performance.jpeg"),
    "2R": ("assets/reports/subject_performance.jpeg", "subject_performance.jpeg"),
    "3R": ("assets/reports/leaderboard.jpeg", "leaderboard.jpeg"),
}

REPORT_CHOICES = [
    discord.app_commands.Choice(name="Quiz Performance", value="1R"),
    discord.app_commands.Choice(name="Overall Performance In Different Subjects", value="2R"),
    discord.app_commands.Choice(name="Leaderboard", value="3R"),
]


class ReportCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="report", description="View compiled performance reports.")
    @discord.app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @discord.app_commands.choices(reports=REPORT_CHOICES)
    async def report(self, interaction: discord.Interaction, reports: discord.app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)

        file_path, filename = REPORT_ASSETS[reports.value]
        if not os.path.exists(file_path):
            await interaction.followup.send(
                "Report image not found. Please generate performance reports first.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(title="Celebelum", description="Your Celebrity AI Assistant", color=0x00FF00)
        embed.set_image(url=f"attachment://{filename}")
        file = discord.File(file_path, filename=filename)
        await interaction.followup.send(file=file, embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReportCog(bot))
