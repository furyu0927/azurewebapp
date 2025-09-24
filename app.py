from flask import Flask, render_template, request, jsonify
import openai
import os  # 追加
from dotenv import load_dotenv  # ← 追加

# --- .env を読み込む ---
load_dotenv()

app = Flask(__name__)

# --- Azure OpenAI の設定 ---
openai.api_type = "azure"
openai.api_version = "2025-01-01-preview"
openai.azure_endpoint = os.environ.get("OPENAI_ENDPOINT")  # 環境変数から取得
openai.api_key = os.environ.get("OPENAI_API_KEY")          # 環境変数から取得
DEPLOYMENT_NAME = os.environ.get("DEPLOYMENT_NAME", "gpt-5-chat-Mika")  # デフォルト値付き

@app.route("/")
def index():
    return render_template("index.html", response="")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form["user_input"]

    response = openai.chat.completions.create(
        model=DEPLOYMENT_NAME,  # デプロイ名
        messages=[{"role": "user", "content": user_input}]
    )

    reply = response.choices[0].message.content
    return render_template("index.html", response=reply)

if __name__ == "__main__":
    app.run(debug=True)
