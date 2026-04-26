def extract_quiz_section(gpt_text: str) -> str:
    """Return the text after 'Quiz:' or an empty string if the marker is missing."""
    parts = gpt_text.split("Quiz:", 1)
    return parts[1].strip() if len(parts) > 1 else ""


def parse_quiz(quiz_text: str) -> dict:
    """Parse GPT quiz output into {question_number: {question, answer}} dict."""
    quiz_dict = {}
    for line in quiz_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            question_part, answer_part = line.rsplit(" (", 1)
            number = int(question_part.split(". ", 1)[0])
            question_text = question_part.split(". ", 1)[1]
            answer_str = answer_part.replace(")", "").strip()
            quiz_dict[number] = {
                "question": question_text,
                "answer": answer_str.lower() == "true",
            }
        except (ValueError, IndexError):
            continue
    return quiz_dict
