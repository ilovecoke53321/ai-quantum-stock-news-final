from flask import Flask
from datetime import datetime
import os
import yfinance as yf

app = Flask(__name__)

@app.route("/")
def home():
    return "AI & QC 股市追蹤報告系統已啟動，請使用 /daily_report 存取每日報告。"

@app.route("/daily_report")
def daily_report():
    ai_stocks = {
        "國內": ["3661.TW", "3443.TW", "3035.TW"],
        "國外": ["NVDA", "AMD", "PLTR"]
    }
    qc_stocks = {
        "國內": ["2454.TW", "2301.TW", "3105.TW"],
        "國外": ["IONQ", "RGTI", "QBTS"]
    }

    report_lines = [f"[{datetime.now().strftime('%Y/%m/%d')} 股市追蹤]\n", "【AI 領域】"]
    for region, tickers in ai_stocks.items():
        report_lines.append(f"{region}：")
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                todays_data = stock.history(period='1d')
                price = todays_data['Close'].iloc[0]
                volume = todays_data['Volume'].iloc[0]
                report_lines.append(f"{ticker}： 股價 {price:.2f}, 成交量 {int(volume/1e6)}M")
            except:
                report_lines.append(f"{ticker}： 無法取得資料")
    report_lines.append("\n【QC 領域】")
    for region, tickers in qc_stocks.items():
        report_lines.append(f"{region}：")
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                todays_data = stock.history(period='1d')
                price = todays_data['Close'].iloc[0]
                volume = todays_data['Volume'].iloc[0]
                report_lines.append(f"{ticker}： 股價 {price:.2f}, 成交量 {int(volume/1e6)}M")
            except:
                report_lines.append(f"{ticker}： 無法取得資料")
    report_lines.append("\n【每日新聞摘要】\n無法取得 GPT 新聞摘要。")
    report_lines.append("\n來源：Yahoo Finance, OpenAI GPT-4")

    txt_content = "\n".join(report_lines)
    file_path = "/mnt/data/daily_report.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(txt_content)

    return txt_content