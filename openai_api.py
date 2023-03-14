import config
import openai
from io import BytesIO

openai.api_key = config.OPENAI_API_KEY


def chat_complete(context: list, text: str) -> tuple[list, str]:
    new_context = context.copy()
    new_context.append({"role": "user", "content": config.ENHANCE_PROMPT + text})
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=config.INITIAL_CONTEXT + new_context
        )
        message = completion["choices"][0]["message"]["content"]
        new_context.append({"role": "assistant", "content": message})
        return (new_context, message)
    except:
        return context, ""


def transcript(audio: BytesIO, language: str) -> str:
    try:
        if language == "ja":
            transcript = openai.Audio.transcribe(
                "whisper-1",
                audio,
                language=language,
                prompt=config.TRANSCRIPT_PROMPT.get(language, ""),
            )
        elif language == "zh":
            transcript = openai.Audio.transcribe(
                "whisper-1",
                audio,
                language=language,
                prompt=config.TRANSCRIPT_PROMPT.get(language, ""),
            )
        else:
            transcript = openai.Audio.transcribe("whisper-1", audio)
    except openai.InvalidRequestError:
        return {"code": 1}
    except:
        return {"code": -1}
    return {"code": 0, "result": transcript["text"]}
