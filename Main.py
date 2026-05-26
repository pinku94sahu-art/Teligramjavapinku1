import os
import telebot
from flask import Flask, request
from openai import OpenAI

# Fetch Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')
# Render automatically provides RENDER_EXTERNAL_URL for web services
WEBHOOK_URL = os.environ.get('RENDER_EXTERNAL_URL') 

# Initialize Flask App
app = Flask(__name__)

# Initialize Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize Hugging Face / OpenAI Client
hf_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# Handle incoming Telegram messages
@bot.message_handler(func=lambda message: True)
def handle_chat(message):
    user_text = message.text
    
    try:
        # Show a "typing..." status in Telegram
        bot.send_chat_action(message.chat.id, 'typing')

        # Call Hugging Face API
        chat_completion = hf_client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V4-Pro:novita",
            messages=[
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
        )

        # Get response and send back to user
        bot_reply = chat_completion.choices[0].message.content
        bot.reply_to(message, bot_reply)

    except Exception as e:
        bot.reply_to(message, f"Oops! Something went wrong: {str(e)}")

# Flask route to receive webhooks from Telegram
@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# Basic route for Render Health Check
@app.route('/')
def index():
    return "Bot is running perfectly!", 200

if __name__ == "__main__":
    # Setup Webhook when the script starts
    if WEBHOOK_URL:
        bot.remove_webhook()
        # Set the webhook URL to point to the Render domain + bot token route
        bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    else:
        print("Warning: RENDER_EXTERNAL_URL not found. Webhook might not be set.")

    # Render dynamically assigns a port, default to 10000 if not found
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
