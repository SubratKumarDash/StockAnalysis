from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import uvicorn

app = FastAPI()

# -------------------------------------------------
# CORS
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# STOCK LIST
# -------------------------------------------------

NIFTY_STOCKS = [

    # -------------------------------------------------
    # LARGE CAP / NIFTY LEADERS
    # -------------------------------------------------

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "ITC.NS",
    "LT.NS",
    "BHARTIARTL.NS",
    "AXISBANK.NS",
    "MARUTI.NS",
    "BAJFINANCE.NS",
    "HCLTECH.NS",
    "WIPRO.NS",
    "SUNPHARMA.NS",
    "POWERGRID.NS",
    "NTPC.NS",
    "TITAN.NS",
    "ADANIPORTS.NS",
    "ONGC.NS",
    "ULTRACEMCO.NS",
    "ASIANPAINT.NS",
    "NESTLEIND.NS",
    "KOTAKBANK.NS",
    "TECHM.NS",
    "TATAMOTORS.NS",
    "M&M.NS",
    "BAJAJFINSV.NS",
    "INDUSINDBK.NS",
    "HINDUNILVR.NS",

    # -------------------------------------------------
    # BANKING & FINANCE
    # -------------------------------------------------

    "BANKBARODA.NS",
    "PNB.NS",
    "CANBK.NS",
    "FEDERALBNK.NS",
    "IDFCFIRSTB.NS",
    "AUBANK.NS",
    "BANDHANBNK.NS",
    "CHOLAFIN.NS",
    "LICHSGFIN.NS",
    "MUTHOOTFIN.NS",
    "SHRIRAMFIN.NS",
    "RECLTD.NS",
    "PFC.NS",

    # -------------------------------------------------
    # IT / SOFTWARE
    # -------------------------------------------------

    "PERSISTENT.NS",
    "COFORGE.NS",
    "LTIM.NS",
    "MPHASIS.NS",
    "OFSS.NS",
    "KPITTECH.NS",
    "TATAELXSI.NS",
    "CYIENT.NS",
    "SONATSOFTW.NS",

    # -------------------------------------------------
    # DEFENCE / RAILWAY
    # -------------------------------------------------

    "HAL.NS",
    "BEL.NS",
    "BDL.NS",
    "MAZDOCK.NS",
    "GRSE.NS",
    "COCHINSHIP.NS",
    "PARAS.NS",
    "RVNL.NS",
    "IRFC.NS",
    "RAILTEL.NS",
    "IRCON.NS",
    "TITAGARH.NS",

    # -------------------------------------------------
    # PHARMA
    # -------------------------------------------------

    "CIPLA.NS",
    "DIVISLAB.NS",
    "DRREDDY.NS",
    "LUPIN.NS",
    "AUROPHARMA.NS",
    "TORNTPHARM.NS",
    "ZYDUSLIFE.NS",
    "GLENMARK.NS",
    "ALKEM.NS",
    "BIOCON.NS",

    # -------------------------------------------------
    # POWER / ENERGY
    # -------------------------------------------------

    "ADANIGREEN.NS",
    "ADANIPOWER.NS",
    "TATAPOWER.NS",
    "JSWENERGY.NS",
    "NHPC.NS",
    "SJVN.NS",
    "SUZLON.NS",
    "IOC.NS",
    "BPCL.NS",
    "HINDPETRO.NS",

    # -------------------------------------------------
    # AUTO / EV
    # -------------------------------------------------

    "EICHERMOT.NS",
    "HEROMOTOCO.NS",
    "TVSMOTOR.NS",
    "ASHOKLEY.NS",
    "EXIDEIND.NS",
    "MOTHERSON.NS",

    # -------------------------------------------------
    # MIDCAP MOMENTUM
    # -------------------------------------------------

    "POLYCAB.NS",
    "DIXON.NS",
    "BSE.NS",
    "CGPOWER.NS",
    "KEI.NS",
    "APLAPOLLO.NS",
    "KAYNES.NS",
    "CLEAN.NS",
    "ZENTECH.NS",
    "IDEAFORGE.NS",

    # -------------------------------------------------
    # CHEMICAL / INDUSTRIAL
    # -------------------------------------------------

    "DEEPAKNTR.NS",
    "PIDILITIND.NS",
    "SRF.NS",
    "AARTIIND.NS",
    "NAVINFLUOR.NS",

    # -------------------------------------------------
    # FMCG / CONSUMPTION
    # -------------------------------------------------

    "DABUR.NS",
    "GODREJCP.NS",
    "MARICO.NS",
    "COLPAL.NS",
    "BRITANNIA.NS"

]

# -------------------------------------------------
# EMA
# -------------------------------------------------

def calculate_ema(prices, period):

    ema_values = []

    multiplier = 2 / (period + 1)

    ema = prices[0]

    for price in prices:

        ema = (price * multiplier) + (ema * (1 - multiplier))

        ema_values.append(round(ema, 2))

    return ema_values

# -------------------------------------------------
# RSI
# -------------------------------------------------

def calculate_rsi(prices, period=14):

    gains = []
    losses = []

    for i in range(1, len(prices)):

        diff = prices[i] - prices[i - 1]

        if diff >= 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period if gains else 0
    avg_loss = sum(losses[-period:]) / period if losses else 1

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss

    return round(100 - (100 / (1 + rs)), 2)

# -------------------------------------------------
# ATR
# -------------------------------------------------

def calculate_atr(df, period=14):

    high = df['High'].values.flatten()
    low = df['Low'].values.flatten()
    close = df['Close'].values.flatten()

    trs = []

    for i in range(1, len(close)):

        tr = max(

            high[i] - low[i],

            abs(high[i] - close[i - 1]),

            abs(low[i] - close[i - 1])

        )

        trs.append(tr)

    atr = sum(trs[-period:]) / period

    return round(float(atr), 2)

# -------------------------------------------------
# MACD
# -------------------------------------------------

def calculate_macd(prices):

    ema12 = calculate_ema(prices, 12)

    ema26 = calculate_ema(prices, 26)

    macd_line = []

    for i in range(len(prices)):

        macd_line.append(

            ema12[i] - ema26[i]

        )

    signal_line = calculate_ema(macd_line, 9)

    return round(macd_line[-1], 2), round(signal_line[-1], 2)

# -------------------------------------------------
# ADX
# -------------------------------------------------

def calculate_adx(df, period=14):

    high = df['High'].values.flatten()
    low = df['Low'].values.flatten()
    close = df['Close'].values.flatten()

    plus_dm = []
    minus_dm = []
    tr_list = []

    for i in range(1, len(close)):

        up_move = high[i] - high[i - 1]
        down_move = low[i - 1] - low[i]

        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0)

        tr = max(
            high[i] - low[i],
            abs(high[i] - close[i - 1]),
            abs(low[i] - close[i - 1])
        )

        tr_list.append(tr)

    atr = sum(tr_list[-period:])

    plus_di = (sum(plus_dm[-period:]) / atr) * 100 if atr != 0 else 0
    minus_di = (sum(minus_dm[-period:]) / atr) * 100 if atr != 0 else 0

    dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) != 0 else 0

    return round(dx, 2)

# -------------------------------------------------
# ANALYSIS ENGINE
# -------------------------------------------------

def analyze_logic(stock):

    try:

        df = yf.download(
            stock,
            period="6mo",
            progress=False,
            auto_adjust=False
        )

        if df.empty:
            return {"error": "Invalid Stock"}

        close_prices = [
            float(x)
            for x in df['Close'].values.flatten().tolist()
        ]

        volumes = [
            float(x)
            for x in df['Volume'].values.flatten().tolist()
        ]

        latest_price = close_prices[-1]

        ema20 = calculate_ema(close_prices, 20)
        ema50 = calculate_ema(close_prices, 50)

        latest_ema20 = ema20[-1]
        latest_ema50 = ema50[-1]

        rsi = calculate_rsi(close_prices)

        atr = calculate_atr(df)

        macd, signal_line = calculate_macd(close_prices)

        adx = calculate_adx(df)

        latest_volume = volumes[-1]

        avg_volume = sum(volumes) / len(volumes)

        rvol = round(latest_volume / avg_volume, 2)

        # -------------------------------------------------
        # BREAKOUT ENGINE
        # -------------------------------------------------

        recent_resistance = max(close_prices[-20:-1])

        breakout_status = "NO BREAKOUT"

        if latest_price > recent_resistance and rvol > 1.5:

            breakout_status = "CONFIRMED BREAKOUT"

        elif latest_price > recent_resistance:

            breakout_status = "WEAK BREAKOUT"

        # -------------------------------------------------
        # MARKET TREND
        # -------------------------------------------------

        market_trend = "BULLISH"

        if latest_price < latest_ema50:

            market_trend = "BEARISH"

        # -------------------------------------------------
        # TRADE SCORE
        # -------------------------------------------------

        trade_score = 0

        analysis = []

        if latest_ema20 > latest_ema50:

            trade_score += 20
            analysis.append("EMA20 above EMA50 bullish trend")

        if latest_price > latest_ema20:

            trade_score += 15
            analysis.append("Price trading above EMA20")

        if rsi > 60:

            trade_score += 15
            analysis.append("RSI momentum strong")

        if macd > signal_line:

            trade_score += 15
            analysis.append("MACD bullish crossover")

        if rvol > 1.5:

            trade_score += 15
            analysis.append("High relative volume breakout")

        if adx > 25:

            trade_score += 10
            analysis.append("Strong trend detected using ADX")

        if breakout_status == "CONFIRMED BREAKOUT":

            trade_score += 10
            analysis.append("Confirmed resistance breakout")

        # -------------------------------------------------
        # SIGNAL
        # -------------------------------------------------

        signal = "AVOID"

        if trade_score >= 80:
            signal = "STRONG BUY"

        elif trade_score >= 65:
            signal = "BUY"

        elif trade_score >= 50:
            signal = "WATCHLIST"

        # -------------------------------------------------
        # TARGETS
        # -------------------------------------------------

        target1 = round(latest_price + atr, 2)

        target2 = round(latest_price + (atr * 2), 2)

        stop_loss = round(latest_price - atr, 2)

        # -------------------------------------------------
        # RISK REWARD
        # -------------------------------------------------

        risk = latest_price - stop_loss

        reward = target2 - latest_price

        rr = round(reward / risk, 2) if risk != 0 else 0

        # -------------------------------------------------
        # DURATION
        # -------------------------------------------------

        duration = "AVOID"

        if signal == "STRONG BUY":
            duration = "1-3 Weeks"

        elif signal == "BUY":
            duration = "1-2 Months"

        elif signal == "WATCHLIST":
            duration = "Wait for Breakout"

        # -------------------------------------------------
        # MOMENTUM SCORE
        # -------------------------------------------------

        momentum_score = round(
            trade_score + rsi + (rvol * 10),
            2
        )

        return {

            "stock": stock.replace(".NS", ""),

            "price": round(latest_price, 2),

            "rsi": rsi,

            "ema20": latest_ema20,

            "ema50": latest_ema50,

            "atr": atr,

            "macd": macd,

            "adx": adx,

            "rvol": rvol,

            "tradeScore": trade_score,

            "signal": signal,

            "target1": target1,

            "target2": target2,

            "stopLoss": stop_loss,

            "riskReward": rr,

            "duration": duration,

            "marketTrend": market_trend,

            "breakoutStatus": breakout_status,

            "momentumScore": momentum_score,

            "analysis": analysis,

            "chartData": {

                "labels": [
                    str(i.date())
                    for i in df.index
                ],

                "prices": close_prices,

                "ema20": ema20,

                "ema50": ema50
            }
        }

    except Exception as e:

        return {"error": str(e)}

# -------------------------------------------------
# ANALYZE API
# -------------------------------------------------

@app.get("/analyze/{stock}")

def analyze_stock(stock: str):

    return analyze_logic(stock.upper() + ".NS")

# -------------------------------------------------
# WATCHLIST API
# -------------------------------------------------

@app.get("/watchlist")

def watchlist():

    results = []

    for stock in NIFTY_STOCKS:

        data = analyze_logic(stock)

        if "error" not in data:

            if data['signal'] in ['BUY', 'STRONG BUY']:

                results.append(data)

    results = sorted(
        results,
        key=lambda x: x['momentumScore'],
        reverse=True
    )

    return results[:10]

# -------------------------------------------------
# UI
# -------------------------------------------------

@app.get("/", response_class=HTMLResponse)

def home():

    return """

<!DOCTYPE html>

<html>

<head>

<title>AI Smart Stock Screening Agent By Subrat Dash</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body{
background:#0f172a;
color:white;
font-family:Arial;
padding:20px;
}

.container{
max-width:1500px;
margin:auto;
}

h1{
text-align:center;
color:#38bdf8;
margin-bottom:20px;
}

.search-box{
display:flex;
gap:10px;
margin-bottom:30px;
}

input{
flex:1;
padding:15px;
border:none;
border-radius:10px;
font-size:18px;
}

button{
padding:15px 30px;
border:none;
border-radius:10px;
background:#22c55e;
color:white;
font-size:18px;
cursor:pointer;
}

.dashboard{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
gap:20px;
}

.card{
background:#1e293b;
padding:20px;
border-radius:15px;
}

.card h3{
color:#94a3b8;
}

.card p{
font-size:24px;
font-weight:bold;
}

.chart-box{
margin-top:30px;
background:white;
padding:20px;
border-radius:15px;
}

.analysis-box{
margin-top:30px;
background:#1e293b;
padding:20px;
border-radius:15px;
}

table{
width:100%;
margin-top:20px;
border-collapse:collapse;
}

th,td{
padding:15px;
border:1px solid #334155;
text-align:center;
}

th{
background:#1e293b;
}

tr{
background:#111827;
}

</style>

</head>

<body>

<div class="container">

<h1>AI Smart Stock Screening Agent By Subrat Dash</h1>

<div class="search-box">

<input
id="stockInput"
type="text"
placeholder="Enter Stock Example: RELIANCE"
>

<button onclick="analyzeStock()">
Analyze
</button>

</div>

<div class="dashboard">

<div class="card"><h3>Stock</h3><p id="stock">-</p></div>
<div class="card"><h3>Price</h3><p id="price">-</p></div>
<div class="card"><h3>RSI</h3><p id="rsi">-</p></div>
<div class="card"><h3>ADX</h3><p id="adx">-</p></div>
<div class="card"><h3>MACD</h3><p id="macd">-</p></div>
<div class="card"><h3>RVOL</h3><p id="rvol">-</p></div>
<div class="card"><h3>Trade Score</h3><p id="tradeScore">-</p></div>
<div class="card"><h3>Signal</h3><p id="signal">-</p></div>
<div class="card"><h3>Breakout</h3><p id="breakout">-</p></div>
<div class="card"><h3>Market Trend</h3><p id="marketTrend">-</p></div>
<div class="card"><h3>Target 1</h3><p id="target1">-</p></div>
<div class="card"><h3>Target 2</h3><p id="target2">-</p></div>
<div class="card"><h3>Stop Loss</h3><p id="stoploss">-</p></div>
<div class="card"><h3>Risk Reward</h3><p id="rr">-</p></div>
<div class="card"><h3>Duration</h3><p id="duration">-</p></div>

</div>

<div class="chart-box">

<canvas id="chart"></canvas>

</div>

<div class="analysis-box">

<h2>AI Technical Analysis</h2>

<div id="analysis"></div>

</div>

<h2 style="margin-top:40px;color:#38bdf8;">

Top 10 High Momentum Stocks

</h2>

<table>

<thead>

<tr>

<th>Stock</th>
<th>Price</th>
<th>RSI</th>
<th>ADX</th>
<th>Breakout</th>
<th>Trade Score</th>
<th>Signal</th>

</tr>

</thead>

<tbody id="watchlistBody">

</tbody>

</table>

</div>

<script>

let stockChart;

async function analyzeStock(){

const stock =
document.getElementById("stockInput").value;

const response =
await fetch("/analyze/" + stock);

const data =
await response.json();

if(data.error){

alert(data.error);

return;
}

document.getElementById("stock").innerHTML = data.stock;
document.getElementById("price").innerHTML = "₹" + data.price;
document.getElementById("rsi").innerHTML = data.rsi;
document.getElementById("adx").innerHTML = data.adx;
document.getElementById("macd").innerHTML = data.macd;
document.getElementById("rvol").innerHTML = data.rvol;
document.getElementById("tradeScore").innerHTML = data.tradeScore;
document.getElementById("signal").innerHTML = data.signal;
document.getElementById("breakout").innerHTML = data.breakoutStatus;
document.getElementById("marketTrend").innerHTML = data.marketTrend;
document.getElementById("target1").innerHTML = "₹" + data.target1;
document.getElementById("target2").innerHTML = "₹" + data.target2;
document.getElementById("stoploss").innerHTML = "₹" + data.stopLoss;
document.getElementById("rr").innerHTML = data.riskReward;
document.getElementById("duration").innerHTML = data.duration;

let analysisHTML = "";

data.analysis.forEach(function(item){

analysisHTML += "<p>✔ " + item + "</p>";

});

document.getElementById("analysis").innerHTML =
analysisHTML;

const ctx =
document.getElementById("chart");

if(stockChart){

stockChart.destroy();
}

stockChart = new Chart(ctx, {

type:'line',

data:{

labels:data.chartData.labels,

datasets:[

{
label:'Price',
data:data.chartData.prices
},

{
label:'EMA20',
data:data.chartData.ema20
},

{
label:'EMA50',
data:data.chartData.ema50
}

]
}
});
}

async function loadWatchlist(){

const response =
await fetch("/watchlist");

const data =
await response.json();

let html = "";

data.forEach(function(stock){

html +=

"<tr>" +

"<td>" + stock.stock + "</td>" +

"<td>₹" + stock.price + "</td>" +

"<td>" + stock.rsi + "</td>" +

"<td>" + stock.adx + "</td>" +

"<td>" + stock.breakoutStatus + "</td>" +

"<td>" + stock.tradeScore + "</td>" +

"<td style='color:#22c55e;font-weight:bold;'>" +

stock.signal +

"</td>" +

"</tr>";

});

document.getElementById("watchlistBody").innerHTML =
html;
}

loadWatchlist();

</script>

</body>

</html>

"""

# -------------------------------------------------
# RUN
# -------------------------------------------------

if __name__ == "__main__":

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )
#------------------------------------------------
#-------- System Flow----------------------------
#-----------------------------------------------
# Browser UI
#   ↓
# FastAPI Backend
#    ↓
#  yfinance Library
#    ↓
#Yahoo Finance
#   ↓
#Historical Market Data
#   ↓
#Your Technical Engine
#   ↓
#AI Trade Analysis

#-----------------------------------
# Latest Agent To Run: uvicorn SSSAgent:app --reload
#------------------------------------