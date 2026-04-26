import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
FAKEYOU_USERNAME = os.getenv("FAKEYOU_USERNAME", "")
FAKEYOU_PASSWORD = os.getenv("FAKEYOU_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "celebelum")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TRANSLATE_TARGET_LANGUAGE = os.getenv("TRANSLATE_TARGET_LANGUAGE", "hi")
OPUS_LIB_PATH = os.getenv("OPUS_LIB_PATH", "")
