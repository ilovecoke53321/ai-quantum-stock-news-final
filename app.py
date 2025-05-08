from flask import Flask
import openai
import datetime
import yfinance as yf

app = Flask(__name__)

openai.api_key = '你的API金鑰'

@app.route('/')
def index():
    return 'Welcome to AI & QC Stock Tracker'

@app.route('/daily_report')
def daily_report():
    # 定義 AI 與量子電腦股票代碼
    ai_stocks = {
        '台股': ['3661.TW', '3443.TW', '3035.TW'],
        '美股': ['NVDA', 'AMD', 'PLTR']
    }
    qc_stocks = {
        '台股': ['2454.TW', '2301.TW', '3105.TW'],
        '美股': ['IONQ', 'RGTI', 'QBTS']
    }

    def get_stock_info(ticker):
        try:
            stock = yf.Ticker(ticker)
            todays_data = stock.history(period='1d')
            price = todays_data['Close'].iloc[0]
            volume = todays_data['Volume'].iloc[0]
            return f'股價 {price:.2f}，成交量 {int(volume / 1000000)}M'
        except:
            return '無法取得資料'

    today = datetime.date.today().strftime('%Y/%m/%d')
    text = f"[{today} 股市追蹤]\n\n【AI 領域】\n"

    for region, stocks in ai_stocks.items():
        text += f"{region}：\n"
        for stock in stocks:
            info = get_stock_info(stock)
            text += f"{stock}：{info}\n"

    text += "\n【QC 領域】\n"
    for region, stocks in qc_stocks.items():
        text += f"{region}：\n"
        for stock in stocks:
            info = get_stock_info(stock)
            text += f"{stock}：{info}\n"

    # 新聞摘要
    try:
        news = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "請以中文撰寫摘要。"},
                {"role": "user", "content": "請用繁體中文提供一段今天 AI 與量子電腦領域的新聞摘要。"}
            ]
        )
        news_summary = news.choices[0].message.content
    except Exception as e:
        news_summary = f"無法取得 GPT 新聞摘要：{str(e)}"

    text += f"\n【每日新聞摘要】\n{news_summary}\n\n來源：Yahoo Finance, OpenAI GPT-4"

    return f"<pre>{text}</pre>"
