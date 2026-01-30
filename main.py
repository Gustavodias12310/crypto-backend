from fastapi import FastAPI
from binance.client import Client
import pandas as pd
import ta
import threading
import time

app = FastAPI()
client = Client()

TIMEFRAMES = ["5m", "15m", "30m", "1h", "4h", "1d"]
SCAN_INTERVAL = 60
signals = []

exchange_info = client.get_exchange_info()
SYMBOLS = [
    s["symbol"] for s in exchange_info["symbols"]
    if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"
]

def analyze(symbol, interval):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=100)
    df = pd.DataFrame(klines, columns=[
        "time","open","high","low","close","volume",
        "_","_","_","_","_","_"
    ])
    df["close"] = df["close"].astype(float)

    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["ema9"] = ta.trend.EMAIndicator(df["close"], window=9).ema_indicator()
    df["ema21"] = ta.trend.EMAIndicator(df["close"], window=21).ema_indicator()

    last = df.iloc[-1]
    if last["rsi"] < 30 and last["ema9"] > last["ema21"]:
        return "BUY"
    if last["rsi"] > 70 and last["ema9"] < last["ema21"]:
        return "SELL"
    return None

def scanner():
    while True:
        for s in SYMBOLS:
            for tf in TIMEFRAMES:
                try:
                    r = analyze(s, tf)
                    if r:
                        signals.append({
                            "symbol": s,
                            "timeframe": tf,
                            "signal": r
                        })
                except:
                    pass
        time.sleep(SCAN_INTERVAL)

threading.Thread(target=scanner, daemon=True).start()

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/signals")
def get_signals():
    return signals[-20:]
