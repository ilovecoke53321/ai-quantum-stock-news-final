from flask import Flask, Response
import yfinance as yf
from datetime import datetime
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

ai_stocks = {
    "TW": ["3661.TW", "3443.TW", "3035.TW"],
    "US": ["NVDA", "AMD", "PLTR"]
}

qc_stocks = {
    "TW": ["2454.TW", "2301.TW", "3105.TW"],
    "US": ["IONQ", "RGTI", "QBTS"]
}

def fetch_stock_data(tickers):
    data = {}
    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            price = info.get("regularMarketPrice", "無法取得資料")
            volume = info.get("volume", "無法取得資料")
            data[symbol] = f"股價 {price}，成交量 {volume if isinstance(volume, str) else str(round(volume / 1e6)) + 'M'}"
        except:
            data[symbol] = "無法取得資料"
    return data

def generate_news_summary():
    try:
        messages = [{
            "role": "user",
            "content": "請用繁體中文簡要摘要今日 AI 與量子電腦領域的三則重要新聞，適合放在每日股市追蹤報告中。"
        }]
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"無法取得 GPT 新聞摘要。錯誤：{str(e)}"

@app.route("/")
def stock_summary():
    today = datetime.now().strftime("%Y/%m/%d")
    text = f"[{today} 股市追蹤]\n\n"

    text += "【AI 領域】\n國內：\n"
    ai_tw = fetch_stock_data(ai_stocks["TW"])
    for symbol, result in ai_tw.items():
        text += f"{symbol}：{result}\n"

    text += "\n國外：\n"
    ai_us = fetch_stock_data(ai_stocks["US"])
    for symbol, result in ai_us.items():
        text += f"{symbol}：{result}\n"

    text += "\n【QC 領域】\n國內：\n"
    qc_tw = fetch_stock_data(qc_stocks["TW"])
    for symbol, result in qc_tw.items():
        text += f"{symbol}：{result}\n"

    text += "\n國外：\n"
    qc_us = fetch_stock_data(qc_stocks["US"])
    for symbol, result in qc_us.items():
        text += f"{symbol}：{result}\n"

    text += "\n【每日新聞摘要】\n"
    text += generate_news_summary()
    text += "\n\n來源：Yahoo Finance, OpenAI GPT-4"

    with open("stock_summary.txt", "w", encoding="utf-8") as f:
        f.write(text)

    return Response(text, mimetype="text/plain")
