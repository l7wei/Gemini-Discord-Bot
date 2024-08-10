import asyncio
import os
import re

import discord
from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger

from attachments import process_attachments
from chat_history import ChatHistory
from gemini import generate_response
from url import extract_url, process_url

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Initialize Discord bot
defaultIntents = discord.Intents.default()
defaultIntents.message_content = True
bot = commands.Bot(command_prefix="!", intents=defaultIntents)


@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    logger.info(f"目前登入身份: {bot.user}")
    logger.info(f"載入 {len(slash)} 個斜線指令")


@bot.tree.command(name="reset", description="Reset the chat history for the user.")
async def reset(interaction: discord.Interaction):
    channel_id = interaction.channel.id
    chat_history = ChatHistory(channel_id)
    chat_history.reset_history()
    await interaction.response.send_message("🧹 清除記憶囉！")


@bot.tree.command(name="ping", description="Ping the bot to check if it is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! 我在線上！")


@bot.event
async def on_message(message):
    # Start the coroutine
    asyncio.create_task(process_message(message))


async def process_message(message):
    logger.info(f"💬 Processing Message from {message.author}: {message.content}")
    if message.author == bot.user or message.mention_everyone:
        logger.info("🚫 Skipping bot messages and everyone mentions.")
        return
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        pass
    else:
        logger.info("🚫 Skipping non-mention messages in non-DM channels.")
        return

    async with message.channel.typing():
        channel_id = message.channel.id
        chat_history = ChatHistory(channel_id)
        cleaned_text = clean_discord_message(message.content)

        if extract_url(cleaned_text):
            cleaned_text = await process_url(cleaned_text)
            await message.add_reaction("🔗")

        parts = [cleaned_text]

        # Check for attachments
        if message.attachments:
            for attachment in message.attachments:
                cleaned_text += f" (Attachment: {attachment.filename})"
                try:
                    part = await process_attachments(attachment)
                    if isinstance(part, dict):
                        parts.append(part)
                        await message.add_reaction("🖼️")
                    elif isinstance(part, str):
                        parts.append(part)
                        await message.add_reaction("📄")
                except Exception as e:
                    logger.error(e)
                    await message.add_reaction("❌")

        chat_history.insert_user_reply(message.author.id, cleaned_text)
        prompt = chat_history.get_history_gemini_format()
        # change last user message to the current user message (in case of attachments)
        prompt[-1]["parts"] = parts
        response_text = await generate_response(prompt)
        await split_and_send_messages(message, response_text, 1700)
        chat_history.insert_bot_reply(message.author.id, response_text)


# ---------------------------------------------Message-------------------------------------------------


# cleans the discord message of any <@!123456789> tags
def clean_discord_message(input_string):
    # Create a regular expression pattern to match text between < and >
    bracket_pattern = re.compile(r"<[^>]+>")
    # Replace text between brackets with an empty string
    cleaned_content = bracket_pattern.sub("", input_string)
    return cleaned_content


async def split_and_send_messages(message_system, text, max_length):
    # Split the string into parts
    messages = []
    for i in range(0, len(text), max_length):
        sub_message = text[i : i + max_length]
        messages.append(sub_message)

    # Send each part as a separate message
    for string in messages:
        await message_system.channel.send(string)


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
