import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)

# Websites allowed to call this API
ALLOWED = [
    "https://vishwasmehra922-wq.github.io",
    "https://khoj-1-ogw8.onrender.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]
ALLOWED += [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
CORS(app, origins=ALLOWED)

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
client = genai.Client(api_key=API_KEY) if API_KEY else None

SYSTEM = (
    "You are KHOJ AI, the helpful assistant inside the KHOJ search website. "
    "Give clear, accurate and short answers (under 200 words). "
    "Use simple words. If you are not sure, say so."
)


@app.get("/")
def health():
    return jsonify({"status": "KHOJ AI backend is running"})


@app.post("/ask")
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    lang = data.get("lang", "en")

    if not question:
        return jsonify({"error": "Question required"}), 400
    if len(question) > 500:
        return jsonify({"error": "Question too long (max 500 characters)"}), 400
    if client is None:
        return jsonify({"error": "Server is missing GEMINI_API_KEY"}), 500

    system = SYSTEM + (" Answer in Hindi (Devanagari)." if lang == "hi" else "")
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=1500,
                thinking_config=types.ThinkingConfig(thinking_level="low"),
            ),
        )
        answer = (response.text or "").strip()
        if not answer:
            return jsonify({"error": "No answer generated"}), 502
        return jsonify({"answer": answer})
    except Exception:
        app.logger.exception("Gemini request failed")
        return jsonify({"error": "AI is busy right now, try again in a minute"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
