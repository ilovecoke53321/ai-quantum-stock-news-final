import os
import datetime
import yfinance as yf
from flask import Flask, Response
from openai import OpenAI

# 建立初始報告檔案
file_path = "daily_report.txt"
if not os.path.exists(file_path):
    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write("尚無今日報告，請稍後再試。")

app = Flask(__name__)

@app.route('/')
def index():
    return "Service is live. Try /daily_report or /text_report"

@app.route('/daily_report')
def daily_report():
    ai_stocks = {
        "國內": ["3661.TW", "3443.TW", "3035.TW"],
        "國外": ["NVDA", "AMD", "PLTR"]
    }
    qc_stocks = {
        "國內": ["2454.TW", "2301.TW", "3105.TW"],
        "國外": ["IONQ", "RGTI", "QBTS"]
    }

    def fetch_stock_data(symbols):
        result = []
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                todays_data = stock.history(period="1d")
                price = todays_data['Close'].iloc[0]
                volume = todays_data['Volume'].iloc[0]
                result.append((symbol, price, volume))
            except Exception:
                result.append((symbol, '無法取得資料', ''))
        return result

    now = datetime.datetime.now().strftime('%Y/%m/%d')
    lines = [f"[{now} 股市追蹤]\n"]

    lines.append("【AI 領域】")
    for region, symbols in ai_stocks.items():
        lines.append(region + "：")
        for symbol, price, volume in fetch_stock_data(symbols):
            lines.append(f"{symbol}：股價 {price}，成交量 {volume}")

    lines.append("\n【QC 領域】")
    for region, symbols in qc_stocks.items():
        lines.append(region + "：")
        for symbol, price, volume in fetch_stock_data(symbols):
            lines.append(f"{symbol}：股價 {price}，成交量 {volume}")

    lines.append("\n【每日新聞摘要】")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "請以簡短方式摘要今天 AI 和量子電腦產業的重要新聞"},
                {"role": "user", "content": "請列出重點"}
            ]
        )
        summary = response.choices[0].message.content
        lines.append(summary)
    except Exception as e:
        lines.append("無法取得 GPT 新聞摘要。")
        lines.append(str(e))  # 可選：除錯用

    lines.append("\n來源：Yahoo Finance, OpenAI GPT-4")

    with open("daily_report.txt", "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines))

    return "\n".join(lines)

@app.route("/text_report")
def text_report():
    with open("daily_report.txt", "r", encoding="utf-8-sig") as f:
        content = f.read()
    return Response(content, mimetype="text/plain; charset=utf-8")
