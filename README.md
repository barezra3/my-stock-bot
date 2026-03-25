📈 StockAI Telegram Bot
An intelligent Telegram bot that provides real-time stock market analysis, financial news summaries, and AI-driven insights using the Groq LPU (Language Processing Unit) and NewsAPI.

🚀 Features
Real-time Data: Fetches live stock performance and technical data.

AI Insights: Uses advanced LLMs (via Groq) to analyze market trends and provide context.

News Integration: Automatically retrieves and summarizes the latest financial headlines for any ticker.

Bilingual Support: Interface available in both English and Hebrew.

Cloud Ready: Optimized for 24/7 deployment on cloud platforms (Render/VPS).

🛠️ Tech Stack
Language: Python 3.x

Framework: python-telegram-bot

AI Engine: Groq API (Llama 3 / Mixtral)

Data Sources: Yahoo Finance (yfinance) & NewsAPI

Environment: Dotenv for secure secret management

📦 Installation & Setup
Clone the repository:

Bash
git clone https://github.com/barezra3/my-stock-bot.git
cd my-stock-bot
Install dependencies:

Bash
pip install -r requirements.txt
Set up Environment Variables:
Create a .env file in the root directory and add your keys:

קטע קוד
TELEGRAM_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
NEWS_API_KEY=your_news_api_key
Run the bot:

Bash
python telegram_bot.py
📝 Disclaimer
This project is for educational purposes only. The information provided by the bot does not constitute financial advice. Always consult with a professional before making investment decisions.
