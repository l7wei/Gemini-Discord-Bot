# Description: Used to send messages to the discord channel.
import re


async def split_and_send_messages(message_system, text, max_length):
    # Split the string into parts
    messages = []
    for i in range(0, len(text), max_length):
        sub_message = text[i : i + max_length]
        messages.append(sub_message)

    # Send each part as a separate message
    for string in messages:
        await message_system.channel.send(string)


# cleans the discord message of any <@!123456789> tags
def clean_discord_message(input_string):
    # Create a regular expression pattern to match text between < and >
    bracket_pattern = re.compile(r"<[^>]+>")
    # Replace text between brackets with an empty string
    cleaned_content = bracket_pattern.sub("", input_string)
    return cleaned_content
