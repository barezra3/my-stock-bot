import requests
from groq import Groq

GROQ_API_KEY = "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"
NEWS_API_KEY = "beffd522bd2e485cb9975488a82a54b2"

# יצירת החיבור ל-AI
client = Groq(api_key=GROQ_API_KEY)


def run_simple_agent(ticker):
    print(f"--- בודק את מניית {ticker} ---")

    # 1. משיכת חדשות
    news_url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    news_res = requests.get(news_url, headers={'User-Agent': 'Mozilla/5.0'})

    if news_res.status_code != 200:
        print(f"שגיאה בחדשות: {news_res.json().get('message')}")
        return

    titles = [a['title'] for a in news_res.json().get('articles', [])]
    if not titles:
        print("לא מצאתי חדשות.")
        return

    print(f"מצאתי חדשות: {titles[0]}...")

    # 2. ניתוח AI
    print("--- ה-AI מנתח עכשיו... ---")
    # ה-Prompt החדש והמפורט שלך
    prompt = f"""
        Analyze the following news headlines for the company {ticker}:
        {titles}

        Please provide a professional financial analyst report in English:
        1. **Market Sentiment**: (Bullish / Bearish / Neutral)
        2. **Key Findings**: Summarize the main points from the news.
        3. **Short-Term Price Impact**: How might this affect the stock in the next 5-10 days?
        4. **Long-Term Strategic Outlook**: Why is this significant for the company's future?
        5. **Investment Score**: 1-10 (1 = Strong Sell, 10 = Strong Buy).

        Format the output with clear headers and bullet points.
        """
    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    print("\n" + "=" * 20)
    print(f"התוצאה עבור {ticker}:")
    print(chat.choices[0].message.content)
    print("=" * 20)


# הפעלה
run_simple_agent("NVIDIA")