from flask import Flask
import yfinance as yf
from openai import OpenAI
from datetime import datetime

app = Flask(__name__)

client = OpenAI()

@app.route('/')
def index():
    return 'AI & QC 股市追蹤服務啟動成功。請使用 /daily_report 存取每日報告。'

@app.route('/daily_report')
def daily_report():
    today = datetime.now().strftime('%Y/%m/%d')
    stocks = {
        'AI': {
            'TW': {'世芯-KY': '3661.TW', '創意': '3443.TW', '智原': '3035.TW'},
            'US': {'NVIDIA': 'NVDA', 'AMD': 'AMD', 'Palantir': 'PLTR'}
        },
        'QC': {
            'TW': {'聯發科': '2454.TW', '光寶科': '2301.TW', '穩懋': '3105.TW'},
            'US': {'IonQ': 'IONQ', 'Rigetti': 'RGTI', 'D-Wave': 'QBTS'}
        }
    }

    output = [f"[{today} 股市追蹤]"]
    for field, region_data in stocks.items():
        output.append(f"\n【{field} 領域】")
        for region, companies in region_data.items():
            output.append(f"\n{('國內' if region == 'TW' else '國外')}：")
            for name, symbol in companies.items():
                try:
                    data = yf.Ticker(symbol).history(period="1d")
                    price = data['Close'][0]
                    volume = data['Volume'][0]
                    volume_str = f"{int(volume / 1_000_000)}M" if volume > 1_000_000 else f"{int(volume / 1_000)}K"
                    output.append(f"{name}({symbol})： 股價 {round(price, 2)}，成交量 {volume_str}")
                except:
                    output.append(f"{name}({symbol})： 無法取得資料")

    # GPT 新聞摘要
    try:
        gpt_news = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一位財經記者，請根據今天的 AI 與量子運算領域股市，生成 2~3 行精簡摘要。"},
                {"role": "user", "content": "\n".join(output)}
            ]
        ).choices[0].message.content
    except Exception as e:
        gpt_news = "無法取得 GPT 新聞摘要。"

    output.append("\n【每日新聞摘要】\n" + gpt_news)
    output.append("\n來源：Yahoo Finance, OpenAI GPT-4")
    return "\n".join(output)
