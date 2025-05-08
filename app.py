import os
import datetime
import yfinance as yf
from flask import Flask
import os

app = Flask(__name__)

# 1. 確保 /mnt/data 資料夾存在
os.makedirs("/mnt/data", exist_ok=True)

# 2. 如果報告檔不存在，就先寫一個占位文字
file_path = "/mnt/data/daily_report.txt"
if not os.path.exists(file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("尚無今日報告，請稍後再試。")

@app.route('/')
def index():
    return "Service is live. Try /daily_report"

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
    lines.append("無法取得 GPT 新聞摘要。")

    lines.append("\n來源：Yahoo Finance, OpenAI GPT-4")

    # 儲存為 txt
    with open("/mnt/data/daily_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return "\n".join(lines)
