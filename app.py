
import os
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "Question required"}), 400

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question
    )

    return jsonify({"answer": response.text})

if __name__ == "__main__":
    app.run()
