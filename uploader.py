import os
import requests
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
UPLOAD_CHANNEL = os.getenv("UPLOAD_CHANNEL")  # e.g. -1001234567890

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)


def send_message(chat_id, text):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text})


def extract_media(msg):
    """Extract media info from user message."""
    if "video" in msg:
        return msg["video"], "video"
    if "document" in msg:
        return msg["document"], "document"
    if "animation" in msg:
        return msg["animation"], "animation"
    if "photo" in msg:
        return msg["photo"][-1], "photo"
    return None, None


@app.route("/")
def home():
    return "Uploader bot running!"


@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    data = request.json
    msg = data.get("message", {})

    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text")

    # 1️⃣ START COMMAND
    if text and text.lower() == "/start":
        send_message(chat_id,
                     "👋 *Welcome!*\n\n"
                     "Send me any *video / document*, and I will automatically upload it "
                     "to your channel.\n\n"
                     "Then your stream bot can generate a working stream link! 🔥")
        return "ok"

    # 2️⃣ MEDIA HANDLING
    media_obj, media_type = extract_media(msg)

    if not media_obj:
        send_message(chat_id, "📥 Send me a *video/document* and I will upload it to your channel.")
        return "ok"

    # 3️⃣ REAL UPLOAD USING copyMessage
    copy_res = requests.post(f"{API}/copyMessage", json={
        "chat_id": UPLOAD_CHANNEL,
        "from_chat_id": chat_id,
        "message_id": msg["message_id"]
    }).json()

    if not copy_res.get("ok"):
        send_message(chat_id, f"❌ Upload failed:\n{copy_res.get('description')}")
        return "ok"

    # 4️⃣ SUCCESS
    send_message(chat_id, "✅ Video successfully uploaded to your channel!")

    return "ok"


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
