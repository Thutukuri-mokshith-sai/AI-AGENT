import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx
from dotenv import load_dotenv

# Load env vars
load_dotenv()

app = Flask(__name__)

# ✅ Enable CORS for frontend domain
CORS(app, resources={r"/*": {"origins": "*"}})
# For production replace "*" with your blob URL

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_KEY")


# Async Azure OpenAI call
async def call_azure(user_input):
    payload = {
        "messages": [{"role": "user", "content": user_input}],
        "temperature": 0.7
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            AZURE_ENDPOINT,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    try:
        result = asyncio.run(call_azure(user_input))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500


@app.route("/", methods=["GET"])
def health():
    return {"status": "AI backend running"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
