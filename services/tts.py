from typing import Optional
import fakeyou
import config

_fy: Optional[fakeyou.FakeYou] = None


def _get_client() -> fakeyou.FakeYou:
    global _fy
    if _fy is None:
        _fy = fakeyou.FakeYou()
        _fy.login(config.FAKEYOU_USERNAME, config.FAKEYOU_PASSWORD)
    return _fy


def prepare_feedback_audio(celeb_token: str) -> None:
    fy = _get_client()
    clips = [
        ("Correct", "true.wav"),
        ("Wrong. Try Next Question", "false.wav"),
        ("Thanks For Participating", "thanks.wav"),
    ]
    for text, path in clips:
        fy.say(text=text, ttsModelToken=celeb_token).save(path)


def say(text: str, celeb_token: str, output_path: str) -> None:
    _get_client().say(text=text, ttsModelToken=celeb_token).save(output_path)
