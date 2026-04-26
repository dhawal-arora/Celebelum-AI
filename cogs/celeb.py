import io
import asyncio
import discord
from discord.ext import commands, voice_recv
import PyPDF2

from services.ai import get_summary_and_quiz, generate_image
from services.tts import prepare_feedback_audio, say
from utils.quiz import parse_quiz, extract_quiz_section


CELEB_CHOICES = [
    discord.app_commands.Choice(name="Millie Bobby Brown", value="TM:edsa15q98zmy"),
    discord.app_commands.Choice(name="Donald Trump", value="TM:03690khwpsbz"),
    discord.app_commands.Choice(name="Andrew Tate", value="TM:43c7p13p3z5c"),
    discord.app_commands.Choice(name="MrBeast", value="TM:r1jbtkgnc6ep"),
]

SUBJECT_CHOICES = [
    discord.app_commands.Choice(name="Math", value="1S"),
    discord.app_commands.Choice(name="English", value="2S"),
    discord.app_commands.Choice(name="History", value="3S"),
    discord.app_commands.Choice(name="Biology", value="4S"),
]


class CelebCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _play_question(
        self,
        vc,
        question: int,
        quiz_list: list,
        gpt_text: str,
        celeb_token: str,
        subject: str,
    ):
        vc.stop_playing()
        if question >= len(quiz_list):
            vc.play(discord.FFmpegPCMAudio("thanks.wav"))
            return
        say(quiz_list[question]["question"], celeb_token, f"question{question}.wav")
        vc.play(
            discord.FFmpegPCMAudio(f"question{question}.wav"),
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self._run_quiz(vc, question, quiz_list, gpt_text, celeb_token, subject),
                self.bot.loop,
            ),
        )

    async def _run_quiz(
        self,
        vc,
        question: int,
        quiz_list: list,
        gpt_text: str,
        celeb_token: str,
        subject: str,
    ):
        vc.stop_playing()
        if question >= 10:
            vc.play(discord.FFmpegPCMAudio("thanks.wav"))
            return

        # Voice recognition was the intended input method.
        # Using console input as a placeholder until voice recognition is re-enabled.
        text = input("Enter true/false/start: ")

        if text.lower() == "start" and question == 0:
            say(quiz_list[0]["question"], celeb_token, "question1.wav")
            vc.play(
                discord.FFmpegPCMAudio("question1.wav"),
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self._run_quiz(vc, 1, quiz_list, gpt_text, celeb_token, subject),
                    self.bot.loop,
                ),
            )
        elif text.lower() in ("true", "false") and question >= 1:
            correct = str(quiz_list[question]["answer"]).lower() == text.lower()
            feedback_file = "true.wav" if correct else "false.wav"
            vc.play(
                discord.FFmpegPCMAudio(feedback_file),
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self._play_question(vc, question + 1, quiz_list, gpt_text, celeb_token, subject),
                    self.bot.loop,
                ),
            )

    async def _play_summary(self, vc, gpt_text: str, celeb_token: str, subject: str):
        summary_text = gpt_text.split("Quiz")[0]
        say(summary_text, celeb_token, "summary.wav")
        quiz_list = list(parse_quiz(extract_quiz_section(gpt_text)).values())
        vc.play(
            discord.FFmpegPCMAudio("summary.wav"),
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self._run_quiz(vc, 0, quiz_list, gpt_text, celeb_token, subject),
                self.bot.loop,
            ),
        )

    @discord.app_commands.command(
        name="celeb",
        description="Hear a PDF summary and quiz yourself in a celebrity's voice.",
    )
    @discord.app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @discord.app_commands.choices(celebs=CELEB_CHOICES, subject=SUBJECT_CHOICES)
    async def celeb(
        self,
        interaction: discord.Interaction,
        book: discord.Attachment,
        celebs: discord.app_commands.Choice[str],
        pagenumber: int,
        subject: discord.app_commands.Choice[str],
    ):
        await interaction.response.defer(ephemeral=True)

        if interaction.user.voice is None:
            await interaction.followup.send("You must be in a voice channel to use this command.", ephemeral=True)
            return

        prepare_feedback_audio(celebs.value)

        buffer = io.BytesIO()
        await book.save(buffer)
        buffer.seek(0)
        reader = PyPDF2.PdfReader(buffer)

        gpt_text = get_summary_and_quiz(reader, pagenumber)
        summary_text = gpt_text.split("Quiz")[0]
        quiz_dict = parse_quiz(extract_quiz_section(gpt_text))
        image_url = generate_image(gpt_text)

        embed = discord.Embed(title="Celebelum", description="Your Celebrity AI Assistant", color=0x00FF00)
        embed.add_field(name="Summary", value=summary_text, inline=False)
        questions_text = "Questions:\n" + "\n".join(q["question"] for q in quiz_dict.values())
        embed.add_field(name="Quiz", value=questions_text, inline=False)
        embed.set_image(url=image_url)

        vc = await interaction.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        vc.play(
            discord.FFmpegPCMAudio("intro.wav"),
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self._play_summary(vc, gpt_text, celebs.value, subject.name),
                self.bot.loop,
            ),
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CelebCog(bot))
