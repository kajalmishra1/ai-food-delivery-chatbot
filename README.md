# 🤖 OrderBuddy – AI-Powered Food Delivery Chatbot

AI-powered conversational assistant for food delivery support, built using TF-IDF vectorization and cosine similarity, deployed with a Flask web application for real-time user interaction.

---

## 📌 Overview

OrderBuddy is an intelligent food delivery support chatbot designed to handle user queries related to orders, refunds, payments, delivery status, coupons, and account management.

It uses classical NLP techniques (TF-IDF + Cosine Similarity) to understand user input and return the most relevant response from predefined intents.

---

# 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![scikit-learn](https://img.shields.io/badge/scikit--learn-NLP-orange?logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green)


| Layer        | Technology |
|-------------|------------|
| NLP Engine   | Python, scikit-learn (TF-IDF + Cosine Similarity) |
| Backend      | Flask |
| Frontend     | HTML, CSS, JavaScript |
| Dataset      | Custom `intents.json` (18 intents, 400+ patterns) |


---

# 🚀 Features

- 💬 Natural language understanding via classical NLP
- 🎯 Confidence threshold — avoids wrong answers by falling back gracefully
- ⚡ Lightweight and fast — no GPU, no API keys, no internet dependency
- 🌐 Flask REST API backend
- 🖥️ Premium responsive web UI (works on mobile too)
- 🔒 XSS-safe message rendering
  

---

# 🧠 How It Works

1. User enters a message in chat interface  
2. Text is cleaned and preprocessed  
3. TF-IDF converts text into numerical vectors  
4. Cosine similarity is calculated between input and stored patterns  
5. Best matching intent is selected  
6. Response is returned from `intents.json`  

---

# 📁 Project Structure

Food Delivery Chatbot/
│
├── app.py # Flask backend
├── chatbot.py # NLP logic (TF-IDF + cosine similarity)
├── intents.json # Dataset of intents and responses
├── requirements.txt # Dependencies
│
├── templates/
│ └── index.html # Frontend UI
│
└── static/
├── style.css # Styling
└── script.js # Frontend logic


---


# ⚙️ Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/kajalmishra1/ai-food-delivery-chatbot.git
cd ai-food-delivery-chatbot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

# 4. Open in browser
http://127.0.0.1:5000
```

# 📌 Future Improvements

- 🔥 Add deep learning / transformer-based NLP model  
- 🎤 Voice-based chatbot interaction  
- 📊 Analytics dashboard for user queries  
- ☁️ Deploy on cloud (Render / AWS / Railway)  

---

# 👨‍💻 About the Project

This project demonstrates end-to-end development of an NLP-powered chatbot — from intent design and text vectorization to REST API deployment and a production-styled web UI.

Designed as a portfolio project showcasing practical machine learning, backend development, and frontend design skills.

---

# 📄 License

This project is open-source and available for learning and educational purposes.

---

# ✨ Author

**Kajal Mishra**
⭐ If you found this useful, consider starring the repo!
