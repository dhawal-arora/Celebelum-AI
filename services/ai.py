from openai import OpenAI
import config
from services.translation import translate_text

_client = OpenAI(api_key=config.OPENAI_API_KEY)

_SYSTEM_PROMPT = (
    "You are a master tutor whose students always get great grades. "
    "Summarize the given text concisely, keeping all important facts and details. "
    "Then provide exactly 10 true/false quiz questions with the answer in parentheses after each. "
    "Format the quiz section with a 'Quiz:' header followed by numbered questions. "
    "Example: 'Quiz:\n1. Statement here. (True)\n2. Statement here. (False)'\n"
    "Keep the full response under 500 characters."
)


def get_summary_and_quiz(reader, page_number: int, translated: bool = False) -> str:
    page_text = reader.pages[page_number].extract_text()
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": f"Text: {page_text}\n\nProvide the summary and quiz."},
    ]
    response = _client.chat.completions.create(model="gpt-4", messages=messages)
    text = response.choices[0].message.content

    if translated:
        text = translate_text(text, config.TRANSLATE_TARGET_LANGUAGE) or text
    return text


def generate_image(prompt: str) -> str:
    response = _client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url


def generate_speech(text: str, output_path: str = "output.wav") -> None:
    response = _client.audio.speech.create(model="tts-1", voice="alloy", input=text)
    response.write_to_file(output_path)
