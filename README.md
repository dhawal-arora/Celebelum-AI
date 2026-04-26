# Celebelum

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fdhawal-arora%2FCelebelum-AI&count_bg=%23FD9801&title_bg=%23270A0A&icon=&icon_color=%23A64141&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)

A Discord bot that makes studying fun by reading your PDFs and quizzing you — in a celebrity's voice.

Built for **Hacklytics 2024**.

---

## What It Does

- Upload any PDF and pick a page to study
- GPT-4 summarizes the content and generates a 10-question true/false quiz
- A celebrity voice (MrBeast, Donald Trump, Millie Bobby Brown, Andrew Tate) reads the summary and quiz aloud in your voice channel via FakeYou TTS
- DALL-E 3 generates a visual summary image
- `/translate` reads a translated version of the summary using OpenAI TTS
- `/report` displays performance charts

## Commands

| Command | Description |
|---|---|
| `/celeb` | Upload a PDF, choose a celebrity and subject, and get quizzed aloud |
| `/translate` | Upload a PDF and hear the summary translated into another language |
| `/report` | View quiz performance and leaderboard charts |
| `/help` | Show all available commands |

## Setup

### Prerequisites

- Python 3.10+
- FFmpeg installed and on your PATH
- A Discord bot token with Message Content and Voice intents enabled
- Accounts / API keys for: OpenAI, FakeYou, AWS, MySQL

### Installation

```bash
git clone https://github.com/dhawal-arora/Celebelum-AI.git
cd Celebelum-AI
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Your Discord bot token |
| `OPENAI_API_KEY` | OpenAI API key (GPT-4 + DALL-E 3 + TTS) |
| `FAKEYOU_USERNAME` | FakeYou account username |
| `FAKEYOU_PASSWORD` | FakeYou account password |
| `MYSQL_HOST` | MySQL server host |
| `MYSQL_USER` | MySQL username |
| `MYSQL_PASSWORD` | MySQL password |
| `MYSQL_DATABASE` | Database name (default: `celebelum`) |
| `AWS_ACCESS_KEY_ID` | AWS access key (for Translate) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_REGION` | AWS region (default: `us-east-1`) |
| `TRANSLATE_TARGET_LANGUAGE` | ISO 639-1 language code (default: `hi` for Hindi) |
| `OPUS_LIB_PATH` | Path to libopus (only needed on some systems) |

### Running

```bash
python bot.py
```

### Report Images

The `/report` command displays performance charts. Place your chart images in `assets/reports/`:

```
assets/reports/quiz_performance.jpeg
assets/reports/subject_performance.jpeg
assets/reports/leaderboard.jpeg
```

## Project Structure

```
Celebelum-AI/
├── bot.py                  # Entry point — starts the bot and loads cogs
├── config.py               # Loads all configuration from environment variables
├── database.py             # MySQL connection helper
├── cogs/
│   ├── celeb.py            # /celeb command — celebrity voice quiz
│   ├── translate.py        # /translate command — translated summary
│   ├── report.py           # /report command — performance charts
│   └── help.py             # /help command
├── services/
│   ├── ai.py               # OpenAI (GPT-4, DALL-E 3, TTS)
│   ├── tts.py              # FakeYou celebrity voice synthesis
│   └── translation.py      # AWS Translate
├── utils/
│   └── quiz.py             # Quiz text parser
└── assets/
    └── reports/            # Place report chart images here
```

## Challenges

Speech recognition through a Discord voice channel proved extremely difficult — processing raw audio bytes, handling packet loss, and running recognition fast enough to stay responsive. The quiz currently uses a console fallback while voice recognition is being improved.

## License

MIT
