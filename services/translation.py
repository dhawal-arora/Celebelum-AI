from typing import Optional
import boto3
import config


def translate_text(text: str, target_language: str, source_language: str = "en") -> Optional[str]:
    try:
        client = boto3.client(
            service_name="translate",
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION,
        )
        result = client.translate_text(
            Text=text,
            SourceLanguageCode=source_language,
            TargetLanguageCode=target_language,
        )
        return result.get("TranslatedText")
    except Exception as e:
        print(f"Translation error: {e}")
        return None
