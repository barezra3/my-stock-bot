import os
import yfinance as yf
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from groq import Groq  # ייבוא הספרייה של ה-AI

# טעינת המפתחות מהכספת
load_dotenv()

# שליפת המפתחות
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# יצירת הלקוח של Groq
groq_client = Groq(api_key=GROQ_API_KEY)

def get_analysis_keyboard(ticker):
    keyboard = [
        [
            InlineKeyboardButton("📊 נתונים טכניים", callback_data=f"tech_{ticker}"),
            InlineKeyboardButton("🇮🇱 תרגם לעברית", callback_data=f"translate_{ticker}")
        ],
        [InlineKeyboardButton("📰 עוד חדשות", callback_data=f"news_{ticker}")]
    ]
    return InlineKeyboardMarkup(keyboard)

# פונקציית עזר למשיכת חדשות וניתוח
def analyze_stock(ticker, user_text):
    # --- שלב 1: משיכת מחיר (yfinance) ---
    try:
        stock = yf.Ticker(ticker)
        price_data = stock.history(period="1d")
        if not price_data.empty:
            current_price = price_data['Close'].iloc[-1]
            prev_close = stock.info.get('previousClose', current_price)
            change_pct = ((current_price - prev_close) / prev_close) * 100
            price_string = f"💰 Price: ${current_price:.2f} ({'+' if change_pct > 0 else ''}{change_pct:.2f}%)"
        else:
            price_string = "Price data unavailable."
    except Exception:
        price_string = "Could not fetch price."

    # --- שלב 2: משיכת חדשות ---
    url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&pageSize=3&apiKey={NEWS_API_KEY}"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    articles = res.json().get('articles', [])

    if not articles:
        return f"{price_string}\n\nNo news found for {ticker}."

    titles = [a['title'] for a in articles]

    #  שלב 3: בדיקת שפה  ---
    is_hebrew = "עברית" in user_text.lower()
    language_instruction = "Respond entirely in Hebrew" if is_hebrew else "Respond in English"

    #  שלב 4: ה-Prompt ל-Groq ---
    prompt = f"""
    Analyze these news for {ticker}: {titles}. 
    Current status: {price_string}.

    Instruction: {language_instruction}.
    Provide a 3-sentence summary, sentiment (Bullish/Bearish), and a score (1-10).

    IMPORTANT: Always end with this disclaimer in Hebrew:
    "---
    ⚠️ הבהרה: סיכום זה בוצע על ידי בינה מלאכותית ומבוסס על כותרות חדשות בלבד. 
    אין לראות במידע זה המלצה למסחר או ייעוץ פיננסי
    Bar Ezra."
    """

    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    # מחזירים את המחיר + התשובה של ה-AI
    return f"{price_string}\n\n{completion.choices[0].message.content}"

    # ניתוח AI
    prompt = f"Analyze these news for {ticker}: {context}. Provide a 3-sentence summary in English: Sentiment, Impact, and Score (1-10)."
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content


# פונקציה שמופעלת כשכותבים /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a stock ticker (e.g., NVDA) and I'll analyze it for you!")


# פונקציה שמטפלת בהודעות טקסט (שמות של מניות)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    ticker = user_text.split()[0].upper()

    await update.message.reply_text(f"Analyzing {ticker}... 🔍")

    try:
        report = analyze_stock(ticker, user_text)
        # שים לב להוספת ה-reply_markup
        await update.message.reply_text(report, reply_markup=get_analysis_keyboard(ticker))
    except Exception as e:
        await update.message.reply_text("שגיאה בניתוח המניה. וודא שהסימול נכון.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # מאשר לטלגרם שהלחיצה התקבלה (מפסיק את השעון המסתובב על הכפתור)

    data = query.data
    action, ticker = data.split('_')  # מפרק ל-action (כמו tech) ו-ticker (כמו NVDA)

    if action == "tech":
        await query.message.reply_text(f"מחלץ נתונים טכניים עבור {ticker}... 📈")
        stock = yf.Ticker(ticker)
        info = stock.info

        # שליפת נתונים מעניינים
        pe = info.get('forwardPE', 'N/A')
        mkt_cap = info.get('marketCap', 'N/A')
        day_high = info.get('dayHigh', 'N/A')

        tech_msg = (
            f"📊 **Technical Data: {ticker}**\n"
            f"• P/E Ratio: {pe}\n"
            f"• Market Cap: {mkt_cap:,} if isinstance(mkt_cap, int) else mkt_cap\n"
            f"• Day High: ${day_high}\n"
            f"---"
        )
        await query.message.reply_text(tech_msg)

    elif action == "news":
        # משיכה של יותר חדשות (למשל 5 במקום 3)
        await query.message.reply_text(f"מחפש כותרות נוספות עבור {ticker}... 📰")
        url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        articles = res.json().get('articles', [])

        news_list = "\n\n".join([f"• {a['title']}" for a in articles])
        await query.message.reply_text(f"📰 **More News for {ticker}:**\n\n{news_list}")

    elif action == "translate":
        await query.message.reply_text(f"מתרגם את הניתוח לעברית... 🇮🇱")
        report = analyze_stock(ticker, "עברית")
        await query.message.reply_text(report)
# הרצת הבוט
if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # הפקודות הרגילות
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # השורה החדשה שחייבת להיות כאן:
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is starting...")
    app.run_polling()
