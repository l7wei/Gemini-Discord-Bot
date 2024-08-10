# Description: Code for the Gemini model, to generate responses to user messages in the chatbot.

import os

import google.generativeai as genai
from dotenv import load_dotenv
from loguru import logger
from opencc import OpenCC

load_dotenv()
GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT") or "你是一個有幫助的聊天助手。"
logger.info(f"🤖 System Prompt: {SYSTEM_PROMPT}")

# Configure the generative AI model
genai.configure(api_key=GOOGLE_AI_KEY)
text_generation_config = {
    "temperature": 2,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 4096,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

gemini_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=text_generation_config,
    safety_settings=safety_settings,
    system_instruction=SYSTEM_PROMPT,
)


async def generate_response(prompt):
    logger.debug(f"🤖 Gemini Prompt: {prompt}")
    try:
        response = gemini_model.generate_content(prompt)
        if response._error:
            return "❌" + str(response._error)
        text = response.text
        text = s2twp_converter(text)
        return text
    except Exception as e:
        logger.error(f"Exception: {e}")
        return "❌ Exception: " + str(e)


def s2twp_converter(simplified_text):
    # 創建 OpenCC 物件，指定簡體到臺灣繁體的轉換
    cc = OpenCC("s2twp")
    # 使用 convert 方法進行轉換
    traditional_text = cc.convert(simplified_text)
    return traditional_text
