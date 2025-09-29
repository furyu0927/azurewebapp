from flask import Flask, render_template, request, jsonify, Response
import openai
import os
from dotenv import load_dotenv
from functools import wraps

# --- .env を読み込む ---
load_dotenv()

app = Flask(__name__)

# --- ベーシック認証 ---
def check_auth(username, password):
    return username == os.environ.get("BASIC_USER") and password == os.environ.get("BASIC_PASS")

def authenticate():
    return Response(
        'ログインが必要です', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# --- Azure OpenAI 設定 ---
openai.api_type = "azure"
openai.api_version = "2025-01-01-preview"
openai.azure_endpoint = os.environ.get("OPENAI_ENDPOINT")
openai.api_key = os.environ.get("OPENAI_API_KEY")
DEPLOYMENT_NAME = os.environ.get("DEPLOYMENT_NAME", "gpt-5-chat-Mika")

# --- 会話履歴（簡易保持） ---
chat_history = []

@app.route("/")
@requires_auth
def index():
    return render_template("index.html", chat_history=chat_history)

@app.route("/chat", methods=["POST"])
@requires_auth
def chat():
    user_input = request.form["user_input"]
    chat_history.append({"role": "user", "content": user_input})

    try:
        response = openai.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": m["role"], "content": m["content"]} for m in chat_history]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"エラーが発生しました: {e}"

    chat_history.append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply})

# --- 履歴クリア用 ---
@app.route("/clear", methods=["POST"])
@requires_auth
def clear():
    global chat_history
    chat_history = []
    return jsonify({"status": "cleared"})
