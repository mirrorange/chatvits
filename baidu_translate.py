import config
import requests
import hashlib
from uuid import uuid4


def translate(text: str):
    text = text.replace("\n", "")
    salt = str(uuid4())
    sign = hashlib.md5(
        (
            config.BAIDU_TRANSLATE_APPID + text + salt + config.BAIDU_TRANSLATE_KEY
        ).encode("utf-8")
    ).hexdigest()
    params = {
        "q": text,
        "from": "auto",
        "to": "zh",
        "appid": config.BAIDU_TRANSLATE_APPID,
        "salt": salt,
        "sign": sign,
    }
    response = requests.get(config.BAIDU_TRANSLATE_URL, params=params)
    result = response.json()
    if "error_code" in result:
        return {"code": result["error_code"]}
    else:
        return {"code": 0, "result": replace_words(result["trans_result"][0]["dst"])}


def replace_words(text: str):
    for key, value in config.REPLACEMENTS.items():
        text = text.replace(key, value)
    return text
