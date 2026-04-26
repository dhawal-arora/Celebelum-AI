import io
import asyncio
import discord
from discord.ext import commands, voice_recv
import PyPDF2

from services.ai import get_summary_and_quiz, generate_speech


class TranslateCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _play_translated_summary(self, vc, gpt_text: str):
        generate_speech(gpt_text, "output.wav")
        vc.play(discord.FFmpegPCMAudio("output.wav"))

    @discord.app_commands.command(
        name="translate",
        description="Hear a translated PDF summary read aloud in your voice channel.",
    )
    @discord.app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def translate(
        self,
        interaction: discord.Interaction,
        book: discord.Attachment,
        pagenumber: int,
    ):
        await interaction.response.defer(ephemeral=True)

        if interaction.user.voice is None:
            await interaction.followup.send("You must be in a voice channel to use this command.", ephemeral=True)
            return

        buffer = io.BytesIO()
        await book.save(buffer)
        buffer.seek(0)
        reader = PyPDF2.PdfReader(buffer)

        gpt_text = get_summary_and_quiz(reader, pagenumber, translated=True)
        vc = await interaction.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)

        vc.play(
            discord.FFmpegPCMAudio("intro.wav"),
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self._play_translated_summary(vc, gpt_text),
                self.bot.loop,
            ),
        )

        embed = discord.Embed(
            title="Celebelum",
            description="Translated summary is playing in your voice channel.",
            color=0x00FF00,
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(TranslateCog(bot))
