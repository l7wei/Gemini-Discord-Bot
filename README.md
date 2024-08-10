# Gemini Discord Bot

Discord bot that leverages the power of Google's Gemini-Pro API to interact with users in both text and image formats. It processes messages and images sent to it, generating creative and engaging responses.

## Features

- **AI-Driven Text Responses:** Generates text responses using Google's generative AI.
- **Image Processing:** Responds to images, combining text and visual inputs for a more engaging interaction.
- **User Message History Management:** Maintains a history of user interactions using SQLite, allowing for context-aware conversations.

## Setup

### Requirements

- aiohttp
- discord.py
- google-generativeai
- python-dotenv
- youtube-transcript-api
- PyMuPDF
- requests
- beautifulsoup4

### Installation

1. Clone the repository to your local machine.
2. Install the required Python libraries:
   ```sh
   pip install -U -r requirements.txt
    ```

### Configuration
1. Create a .env file and copy the contents of .env.example into it.
   ```sh
   cp .env.example .env
   ```
2. Fill in the following values:
  - `GOOGLE_AI_KEY`: Your Google API key.
  - `DISCORD_BOT_TOKEN`: Your Discord bot token.
  - `SYSTEM_PROMPT`: The prompt to use for the AI model.
  - `LOGURU_LEVEL`: The logging level to use (e.g., DEBUG, INFO, WARNING, ERROR).
3. Run the bot:
   ```sh
   python main.py
   ```
The bot will start listening to messages in your Discord server. It responds to direct mentions or direct messages.

## How to get API keys (and set up permissions)
### Discord Bot Token
1. Create a new application on the [Discord Developer Portal](https://discord.com/developers/applications/).
2. Get your bot token from the "Bot" tab and add it to your .env file.
3. Set up bot permissions by going to the "OAuth2" tab and selecting the "bot" scope. Add the following permissions:
   - View Channels
   - Send Messages
   - Read Message History
   - Attach Files
4. Copy the generated URL and paste it into your browser to add the bot to your server.
### Google AI API Key
1. Go to the [Google AI Studio](https://aistudio.google.com/app/).
2. Get your API key from the "Get API Key" button and add it to your .env file.

## Commands
- Mention or DM the bot to activate: History only works on pure text input.
- Send an Image: The bot will respond with an AI-generated interpretation or related content.
- Type 'CLEAN': Clears the message history for the user.

## Additional Items
- Youtube URLs: Reads the transcript from a YouTube video and you can ask a question about it.
- PDF / TXT: PDF or TXT will be added into your prompt.
- Web URL: Scrapes the text off a URL (as well as it can).

## Thanks
Inspired by the [Echoshard/Gemini_Discordbot](https://github.com/Echoshard/Gemini_Discordbot).