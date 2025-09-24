from flask import Flask, render_template, request, Response, session
import openai
import os
from dotenv import load_dotenv
from functools import wraps

# --- .env を読み込む ---
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")  # セッション用

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
openai.api_base = os.environ.get("OPENAI_ENDPOINT")
openai.api_key = os.environ.get("OPENAI_API_KEY")
DEPLOYMENT_NAME = os.environ.get("DEPLOYMENT_NAME", "gpt-5-chat-Mika")

# --- ルート ---
@app.route("/", methods=["GET"])
@requires_auth
def index():
    history = session.get("history", [])
    return render_template("index.html", history=history)

@app.route("/chat", methods=["POST"])
@requires_auth
def chat():
    user_input = request.form["user_input"]

    response = openai.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": user_input}]
    )

    reply = response.choices[0].message.content

    # セッションに履歴を保存
    if "history" not in session:
        session["history"] = []
    session["history"].append({"user": user_input, "bot": reply})

    return render_template("index.html", history=session["history"])

# --- セッションリセット用（任意） ---
@app.route("/reset")
@requires_auth
def reset():
    session.pop("history", None)
    return "チャット履歴をリセットしました。<a href='/'>戻る</a>"

if __name__ == "__main__":
    app.run(debug=True)
