import os
import asyncio
from flask import Flask, request, jsonify, render_template
import httpx
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, template_folder="templates")

# Get Azure values from environment
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_KEY")


@app.route("/", methods=["GET"])
def read_root():
    return render_template("index.html")


# Async function to call Azure OpenAI
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
        # Flask is sync, so run async call manually
        result = asyncio.run(call_azure(user_input))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": {"message": str(e)}})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
