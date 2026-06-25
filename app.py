from flask import Flask, render_template, request, jsonify
from chatbot import FAQChatbot

app = Flask(__name__)

# create bot instance ONCE
bot = FAQChatbot()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    user_text = request.json.get("message", "")

    response, tag, score = bot.get_response(user_text)

    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(debug=True)