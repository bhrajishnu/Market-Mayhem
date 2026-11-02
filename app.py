
import streamlit as st
import pandas as pd
import plotly.express as px
import random
import time

st.set_page_config(
    page_title="MARKET MAYHEM",
    page_icon="📈",
    layout="wide"
)

STARTING_CASH = 10000
GOAL = 20000
MAX_DAYS = 30
DAY_LENGTH = 90

COMPANIES = {
    "Apple": {"ticker": "AAPL", "price": 190, "volatility": 0.035},
    "Microsoft": {"ticker": "MSFT", "price": 420, "volatility": 0.030},
    "NVIDIA": {"ticker": "NVDA", "price": 135, "volatility": 0.055},
    "Amazon": {"ticker": "AMZN", "price": 215, "volatility": 0.040},
    "Tesla": {"ticker": "TSLA", "price": 330, "volatility": 0.065},
    "Google": {"ticker": "GOOGL", "price": 175, "volatility": 0.035},
    "Meta": {"ticker": "META", "price": 600, "volatility": 0.045},
    "Coca-Cola": {"ticker": "KO", "price": 70, "volatility": 0.025},
    "Walmart": {"ticker": "WMT", "price": 95, "volatility": 0.025},
    "Disney": {"ticker": "DIS", "price": 110, "volatility": 0.040},
    "Netflix": {"ticker": "NFLX", "price": 950, "volatility": 0.050},
    "JPMorgan": {"ticker": "JPM", "price": 250, "volatility": 0.035},
}

POSITIVE_NEWS = [
    "{company} reports record-breaking earnings!",
    "{company} announces an exciting new product!",
    "Analysts upgrade {company} after impressive growth.",
    "{company} secures a major business partnership!",
    "Investors are excited about {company}'s future.",
    "{company} announces record-breaking sales!",
    "Demand for {company}'s products is increasing.",
    "{company} expands into a promising new market!",
]

NEGATIVE_NEWS = [
    "{company} misses its earnings expectations!",
    "{company} faces an unexpected investigation.",
    "Investors worry about {company}'s future growth.",
    "{company} announces disappointing sales.",
    "{company} loses an important business partnership.",
    "A competitor threatens {company}'s market share.",
    "{company} faces unexpected production problems.",
    "Analysts downgrade {company} after weak results.",
]

GENERAL_NEWS = [
    ("🏦", "Federal Reserve keeps interest rates unchanged."),
    ("🌎", "Global markets react to economic uncertainty."),
    ("📊", "Investors await the latest inflation report."),
    ("💰", "Wall Street sees increased trading activity."),
    ("📉", "Market analysts warn of possible volatility."),
    ("📈", "Investor confidence improves across the market."),
    ("⚡", "Technology stocks attract major investor attention."),
    ("💼", "Major investment funds adjust their portfolios."),
]

ACHIEVEMENT_LIST = [
    {
        "id": "first_trade",
        "name": "First Trade",
        "description": "Complete your first stock trade.",
        "reward": 100,
        "emoji": "🤝",
    },
    {
        "id": "ten_shares",
        "name": "Big Investor",
        "description": "Purchase 10 total shares.",
        "reward": 150,
        "emoji": "📦",
    },
    {
        "id": "five_trades",
        "name": "Active Trader",
        "description": "Complete 5 stock trades.",
        "reward": 200,
        "emoji": "⚡",
    },
    {
        "id": "wealth_15k",
        "name": "Rising Star",
        "description": "Reach $15,000 total wealth.",
        "reward": 250,
        "emoji": "🌟",
    },
    {
        "id": "wealth_20k",
        "name": "Wall Street Legend",
        "description": "Reach $20,000 total wealth.",
        "reward": 500,
        "emoji": "🏆",
    },
]

if "started" not in st.session_state:
    st.session_state.started = False

if "cash" not in st.session_state:
    st.session_state.cash = STARTING_CASH
    st.session_state.day = 0
    st.session_state.prices = {
        n: d["price"] for n, d in COMPANIES.items()
    }
    st.session_state.holdings = {
        n: 0 for n in COMPANIES
    }
    st.session_state.history = {
        n: [d["price"]] for n, d in COMPANIES.items()
    }
    st.session_state.news = [
        {
            "day": 0,
            "headline": "🏦 WALL STREET IS OPEN!",
            "details": "Your investing career starts now. You have $10,000."
        }
    ]
    st.session_state.next_update = None
    st.session_state.last_job_day = -1
    st.session_state.researched_day = -1
    st.session_state.research_report = None
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.trade_history = []

DEFAULTS = {
    "crate_day": -1,
    "wheel_day": -1,
    "tip_day": -1,
    "insider_tip": None,
    "daily_challenge": None,
    "challenge_day": -1,
    "trades_today": 0,
    "total_trades": 0,
    "total_shares_bought": 0,
    "achievements": [],
    "achievement_log": [],
    "trade_notice": None,
    "new_day_popup": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, list) else value

dark = True

bg = "#10121C"
panel = "#191D2B"
text = "#F4F4F8"
muted = "#A4A9BC"
accent = "#9B72FF"
secondary = "#252B3D"

st.markdown(f"""
<style>
.stApp {{
    background-color: {bg};
    color: {text};
}}
[data-testid="stSidebar"] {{
    background-color: {panel};
}}
h1, h2, h3, p, label {{
    color: {text};
}}
.stMetric {{
    background-color: {panel};
    border: 1px solid {secondary};
    padding: 14px;
    border-radius: 12px;
}}
.stButton > button {{
    border-radius: 10px;
    border: 1px solid {accent};
    font-weight: bold;
    min-height: 42px;
}}
div[data-testid="stProgressBar"] > div > div {{
    background-color: {accent};
}}
.news-card {{
    background-color: {panel};
    padding: 15px;
    border-radius: 12px;
    border-left: 4px solid {accent};
    margin-bottom: 12px;
}}
.hero {{
    background: linear-gradient(120deg, #5426B8, #A33CEB, #F05A91);
    padding: 45px 30px;
    border-radius: 22px;
    text-align: center;
    color: white;
    margin-bottom: 25px;
}}
.hero h1 {{
    color: white;
    font-size: 58px;
    font-weight: 900;
}}
.hero p {{
    color: white;
    font-size: 19px;
}}
.hub-card {{
    background-color: {panel};
    border: 1px solid {secondary};
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 12px;
}}
.research-card {{
    background-color: {panel};
    border: 1px solid {secondary};
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
}}
</style>
""", unsafe_allow_html=True)


def money(amount):
    return f"${amount:,.2f}"


def portfolio_value():
    return sum(
        st.session_state.holdings[n] * st.session_state.prices[n]
        for n in COMPANIES
    )


def total_wealth():
    return st.session_state.cash + portfolio_value()


def add_news(headline, details):
    st.session_state.news.insert(
        0,
        {
            "day": st.session_state.day,
            "headline": headline,
            "details": details
        }
    )
    st.session_state.news = st.session_state.news[:30]


def ensure_daily_challenge():
    if st.session_state.challenge_day == st.session_state.day:
        return

    options = [
        {
            "kind": "trades",
            "description": "Complete 2 stock trades today.",
            "target": 2,
            "reward": 175,
        },
        {
            "kind": "buy",
            "company": random.choice(list(COMPANIES.keys())),
            "description": "",
            "target": 3,
            "reward": 200,
        },
        {
            "kind": "sell",
            "company": random.choice(list(COMPANIES.keys())),
            "description": "",
            "target": 1,
            "reward": 175,
        },
    ]

    challenge = random.choice(options)

    if challenge["kind"] == "buy":
        challenge["description"] = (
            f"Buy 3 shares of {challenge['company']} today."
        )
    elif challenge["kind"] == "sell":
        challenge["description"] = (
            f"Sell 1 share of {challenge['company']} today."
        )

    challenge["progress"] = 0
    challenge["completed"] = False

    st.session_state.daily_challenge = challenge
    st.session_state.challenge_day = st.session_state.day
    st.session_state.trades_today = 0


def check_achievements():
    for achievement in ACHIEVEMENT_LIST:
        aid = achievement["id"]

        if aid in st.session_state.achievements:
            continue

        unlocked = False

        if aid == "first_trade":
            unlocked = st.session_state.total_trades >= 1
        elif aid == "ten_shares":
            unlocked = st.session_state.total_shares_bought >= 10
        elif aid == "five_trades":
            unlocked = st.session_state.total_trades >= 5
        elif aid == "wealth_15k":
            unlocked = total_wealth() >= 15000
        elif aid == "wealth_20k":
            unlocked = total_wealth() >= 20000

        if unlocked:
            st.session_state.achievements.append(aid)
            st.session_state.cash += achievement["reward"]

            st.session_state.achievement_log.insert(
                0,
                f"{achievement['emoji']} {achievement['name']} unlocked! "
                f"Bonus: {money(achievement['reward'])}"
            )


def update_daily_challenge(action, company, quantity):
    ensure_daily_challenge()
    challenge = st.session_state.daily_challenge

    if challenge["completed"]:
        return

    if challenge["kind"] == "trades":
        challenge["progress"] += 1
    elif challenge["kind"] == "buy" and action == "buy":
        if company == challenge["company"]:
            challenge["progress"] += quantity
    elif challenge["kind"] == "sell" and action == "sell":
        if company == challenge["company"]:
            challenge["progress"] += quantity

    if challenge["progress"] >= challenge["target"]:
        challenge["completed"] = True
        st.session_state.cash += challenge["reward"]

        st.session_state.achievement_log.insert(
            0,
            f"🎯 Daily Challenge completed! Bonus: {money(challenge['reward'])}"
        )


def advance_market():
    st.session_state.day += 1
    st.session_state.new_day_popup = True

    news_company = None
    news_impact = 0

    if random.random() < 0.45:
        news_company = random.choice(list(COMPANIES.keys()))
        positive = random.choice([True, False])

        if positive:
            headline = random.choice(POSITIVE_NEWS).format(
                company=news_company
            )
            news_impact = random.uniform(0.01, 0.05)
            add_news(
                "🟢 " + headline,
                f"Investors react positively. {news_company} experiences increased buying interest."
            )
        else:
            headline = random.choice(NEGATIVE_NEWS).format(
                company=news_company
            )
            news_impact = -random.uniform(0.01, 0.05)
            add_news(
                "🔴 " + headline,
                f"Investors become concerned. {news_company} experiences increased selling pressure."
            )

    for name, data in COMPANIES.items():
        direction = random.choice([-1, 1])
        movement = abs(random.gauss(0, data["volatility"]))
        change = direction * movement

        if name == news_company:
            change += news_impact

        change = max(-0.15, min(0.15, change))
        new_price = st.session_state.prices[name] * (1 + change)
        new_price = max(1, round(new_price, 2))

        st.session_state.prices[name] = new_price
        st.session_state.history[name].append(new_price)

    if random.random() < 0.40:
        emoji, headline = random.choice(GENERAL_NEWS)
        add_news(
            emoji + " " + headline,
            "Markets continue trading as investors react to the latest developments."
        )

    st.session_state.researched_day = -1
    st.session_state.research_report = None

    ensure_daily_challenge()
    check_achievements()

    if st.session_state.day >= MAX_DAYS:
        st.session_state.game_over = True
        st.session_state.won = total_wealth() >= GOAL


def open_mystery_crate():
    if st.session_state.crate_day == st.session_state.day:
        return "You already opened today's crate!"

    if st.session_state.cash < 100:
        return "You need at least $100 to open a crate."

    st.session_state.cash -= 100
    prize = random.choice([0, 50, 150, 300, 500])
    st.session_state.cash += prize
    st.session_state.crate_day = st.session_state.day

    net = prize - 100

    if prize == 0:
        message = "💀 The crate was empty! You lost $100."
    elif net > 0:
        message = f"🎉 JACKPOT! You received {money(prize)}. Net profit: {money(net)}!"
    else:
        message = f"📦 You received {money(prize)}. Net result: {money(net)}."

    check_achievements()
    return message


def spin_investor_wheel():
    if st.session_state.wheel_day == st.session_state.day:
        return "You've already spun the wheel today!"

    outcomes = [
        ("💸 Lost $100", -100),
        ("😐 Nothing happened", 0),
        ("💵 Won $100", 100),
        ("🎉 Won $250", 250),
        ("🚀 MEGA WIN! Won $500", 500),
    ]

    result, amount = random.choice(outcomes)

    if amount < 0 and st.session_state.cash < abs(amount):
        amount = 0
        result = "😐 You avoided a loss because you had insufficient cash."

    st.session_state.cash += amount
    st.session_state.wheel_day = st.session_state.day

    check_achievements()
    return result


def purchase_insider_tip():
    if st.session_state.tip_day == st.session_state.day:
        return "You've already purchased today's insider tip."

    if st.session_state.cash < 150:
        return "You need $150 to purchase an insider tip."

    st.session_state.cash -= 150
    company = random.choice(list(COMPANIES.keys()))
    prices = st.session_state.history[company]

    if len(prices) >= 3:
        trend = (prices[-1] - prices[-3]) / prices[-3]
    else:
        trend = 0

    if trend > 0.015:
        prediction = "🟢 Recent momentum is positive."
    elif trend < -0.015:
        prediction = "🔴 Recent momentum is negative."
    else:
        prediction = "🟡 Recent movement has been relatively neutral."

    tip = (
        f"🔍 Rumor about {company} ({COMPANIES[company]['ticker']}): "
        f"{prediction} Analysts are watching this company closely."
    )

    st.session_state.insider_tip = tip
    st.session_state.tip_day = st.session_state.day

    check_achievements()
    return tip


def create_research_report(company):
    prices = st.session_state.history[company]
    current_price = prices[-1]
    shares_owned = st.session_state.holdings[company]
    position_value = current_price * shares_owned

    recent_prices = prices[-6:]

    if len(recent_prices) >= 2:
        recent_change = (
            (recent_prices[-1] - recent_prices[0])
            / recent_prices[0]
        ) * 100

        daily_change = (
            (prices[-1] - prices[-2])
            / prices[-2]
        ) * 100
    else:
        recent_change = 0
        daily_change = 0

    average_price = sum(recent_prices) / len(recent_prices)
    highest_price = max(recent_prices)
    lowest_price = min(recent_prices)

    range_percentage = (
        (highest_price - lowest_price) / lowest_price
    ) * 100 if lowest_price > 0 else 0

    daily_returns = pd.Series(recent_prices).pct_change().dropna()

    if len(daily_returns) >= 2:
        volatility = daily_returns.std() * 100
    else:
        volatility = 0

    average_difference = (
        (current_price - average_price) / average_price
    ) * 100 if average_price > 0 else 0

    if recent_change > 3:
        momentum = "Positive"
        momentum_description = (
            f"{company} has shown strong upward momentum, gaining "
            f"{recent_change:.2f}% over the recent trading period. "
            "Investors have generally been willing to pay higher prices."
        )
    elif recent_change > 0.5:
        momentum = "Slightly Positive"
        momentum_description = (
            f"{company} is showing a modest upward trend, gaining "
            f"{recent_change:.2f}% recently. The movement is positive, "
            "although it has not yet developed into a particularly strong rally."
        )
    elif recent_change < -3:
        momentum = "Negative"
        momentum_description = (
            f"{company} has experienced a noticeable decline of "
            f"{abs(recent_change):.2f}% over the recent trading period. "
            "Selling pressure has been stronger than buying interest."
        )
    elif recent_change < -0.5:
        momentum = "Slightly Negative"
        momentum_description = (
            f"{company} has slipped {abs(recent_change):.2f}% recently. "
            "The trend is somewhat negative, but the decline is relatively modest."
        )
    else:
        momentum = "Neutral"
        momentum_description = (
            f"{company} has moved relatively sideways, changing "
            f"{recent_change:+.2f}% over the recent trading period. "
            "There is not yet a clear upward or downward trend."
        )

    if volatility >= 4:
        risk_level = "High"
        volatility_description = (
            "Price swings have been relatively large. This stock may offer "
            "larger opportunities, but sudden losses are also possible."
        )
    elif volatility >= 2:
        risk_level = "Moderate"
        volatility_description = (
            "The stock has experienced moderate price movement. "
            "It has some noticeable swings, but recent trading has not been extremely volatile."
        )
    else:
        risk_level = "Low"
        volatility_description = (
            "Recent price movement has been relatively calm compared with "
            "the other volatility levels in this game."
        )

    if average_difference > 1:
        average_description = (
            f"The current price is {average_difference:.2f}% above its recent average, "
            "meaning the stock is currently trading higher than its typical price "
            "during this period."
        )
    elif average_difference < -1:
        average_description = (
            f"The current price is {abs(average_difference):.2f}% below its recent average, "
            "meaning the stock is currently trading below its typical price "
            "during this period."
        )
    else:
        average_description = (
            "The current price is very close to its recent average, "
            "suggesting relatively balanced movement."
        )

    if daily_change > 0.5:
        daily_description = (
            f"The latest market day was positive, with the share price rising "
            f"{daily_change:.2f}%."
        )
    elif daily_change < -0.5:
        daily_description = (
            f"The latest market day was negative, with the share price falling "
            f"{abs(daily_change):.2f}%."
        )
    else:
        daily_description = (
            f"The latest market day saw relatively little movement "
            f"({daily_change:+.2f}%)."
        )

    company_news = None

    for item in st.session_state.news:
        if company.lower() in (
            item["headline"] + " " + item["details"]
        ).lower():
            company_news = item
            break

    if company_news:
        news_description = (
            f"**{company_news['headline']}**\n\n"
            f"{company_news['details']}"
        )
    else:
        news_description = (
            f"There are currently no recent company-specific headlines "
            f"for {company} in the financial news feed."
        )

    if len(prices) > 1:
        period_description = (
            f"Based on the latest {len(recent_prices) - 1} completed "
            "market day(s)."
        )
    else:
        period_description = (
            "This company has not completed a market update yet. "
            "More price history will become available as the game progresses."
        )

    if momentum in ["Positive", "Slightly Positive"]:
        takeaway = (
            "The recent trend is encouraging. Investors looking for upward "
            "momentum may want to keep this company on their watchlist. "
            "However, a rising price does not guarantee that it will continue."
        )
    elif momentum in ["Negative", "Slightly Negative"]:
        takeaway = (
            "The recent trend is weak. Investors may want to watch for signs "
            "of stabilization before buying. A falling price can continue falling."
        )
    else:
        takeaway = (
            "The stock has not established a strong direction. Waiting for "
            "a clearer trend or watching upcoming news may provide more information."
        )

    if risk_level == "High":
        takeaway += (
            " Be especially careful with position size because recent price swings "
            "have been large."
        )

    report = f"""
### 📊 {company} ({COMPANIES[company]['ticker']}) — Research Report

*{period_description}*

#### 💹 Current Market Overview

| Indicator | Result |
|---|---:|
| Current Share Price | {money(current_price)} |
| Latest Daily Change | {daily_change:+.2f}% |
| Recent Price Change | {recent_change:+.2f}% |
| Recent Average Price | {money(average_price)} |
| Recent High | {money(highest_price)} |
| Recent Low | {money(lowest_price)} |
| Recent Price Range | {range_percentage:.2f}% |
| Estimated Recent Volatility | {volatility:.2f}% |

#### 📈 Trend Analysis

**Momentum: {momentum}**

{momentum_description}

{daily_description}

{average_description}

#### ⚠️ Risk Assessment

**Recent Volatility: {risk_level}**

{volatility_description}

The recent high-to-low price range is {range_percentage:.2f}%. This shows how far apart the highest and lowest prices have been during the recent observation period.

#### 📰 Company News

{news_description}

#### 💼 Your Investment Position

- Shares currently owned: **{shares_owned}**
- Current value of your position: **{money(position_value)}**

#### 🧠 Research Takeaway

{takeaway}

*This report is generated from simulated game prices and fictional news. It is not a real financial forecast or a guarantee of future stock performance.*
"""

    return report


@st.fragment(run_every=1)
def live_market_clock():
    if not st.session_state.started or st.session_state.game_over:
        return

    if st.session_state.next_update is None:
        st.session_state.next_update = time.time() + DAY_LENGTH

    advanced = False

    while (
        time.time() >= st.session_state.next_update
        and not st.session_state.game_over
    ):
        advance_market()
        st.session_state.next_update += DAY_LENGTH
        advanced = True

    if advanced:
        st.rerun(scope="app")

    time_remaining = max(
        0,
        int(st.session_state.next_update - time.time())
    )

    minutes = time_remaining // 60
    seconds = time_remaining % 60

    st.markdown(
        f"""
        <div style="
            background:{panel};
            border:1px solid {secondary};
            border-radius:12px;
            padding:12px 18px;
            margin-bottom:15px;
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">
            <span style="color:{text};font-weight:bold;">
                ⏰ NEXT MARKET UPDATE
            </span>
            <span style="
                color:{accent};
                font-size:26px;
                font-weight:900;
            ">
                {minutes:02d}:{seconds:02d}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


if not st.session_state.started:
    st.markdown("""
    <div class="hero">
        <h1>📈 MARKET MAYHEM</h1>
        <p>Buy low. Sell high. Become a Wall Street legend.</p>
        <h2 style="color:white;">$10,000 → $20,000</h2>
        <p>Can you double your money in just 30 days?</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🎮 Welcome, Investor!")

    col1, col2, col3 = st.columns(3)

    col1.metric("Starting Cash", "$10,000")
    col2.metric("Target Wealth", "$20,000")
    col3.metric("Time Limit", "30 Days")

    st.divider()
    st.subheader("📜 How to Play")

    st.markdown("""
    - Buy and sell shares in 12 different companies.
    - Stock prices automatically update every 90 seconds.
    - Each 90 seconds represents one trading day.
    - Read breaking news to spot opportunities.
    - Visit the Investor Hub for bonus activities.
    - Complete daily challenges and unlock achievements.
    - Reach $20,000 before the end of Day 30!
    """)

    if st.button(
        "🚀 START GAME",
        type="primary",
        use_container_width=True
    ):
        st.session_state.started = True
        st.session_state.next_update = time.time() + DAY_LENGTH
        ensure_daily_challenge()
        st.rerun()

    st.stop()


if st.session_state.game_over:
    if st.session_state.new_day_popup:
        st.toast("A New Day Has Dawned", icon="🌅")
        st.session_state.new_day_popup = False

    st.markdown("""
    <div class="hero">
        <h1>MARKET MAYHEM</h1>
        <p>THE FINAL BELL HAS RUNG!</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.won:
        st.balloons()
        st.success("🏆 YOU WON! YOU ARE A WALL STREET LEGEND!")
    else:
        st.error("📉 GAME OVER! YOU DIDN'T REACH YOUR TARGET.")

    st.metric("Final Wealth", money(total_wealth()))
    st.metric("Starting Money", money(STARTING_CASH))
    st.metric("Total Profit / Loss", money(total_wealth() - STARTING_CASH))

    st.write("Your 30 trading days are complete.")

    st.subheader("🏆 Your Achievements")

    for achievement in ACHIEVEMENT_LIST:
        if achievement["id"] in st.session_state.achievements:
            st.write(f"{achievement['emoji']} {achievement['name']}")

    if st.button("🔄 PLAY AGAIN", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.stop()


st.title("📈 MARKET MAYHEM")
st.caption("Your 30-day race to $20,000 starts now.")

ensure_daily_challenge()
live_market_clock()

if st.session_state.new_day_popup:
    st.toast("A New Day Has Dawned", icon="🌅")
    st.session_state.new_day_popup = False

if st.session_state.trade_notice:
    st.success(st.session_state.trade_notice)
    st.session_state.trade_notice = None

st.sidebar.title("💰 YOUR ACCOUNT")

st.sidebar.metric("Available Cash", money(st.session_state.cash))
st.sidebar.metric("Portfolio Value", money(portfolio_value()))

wealth = total_wealth()

st.sidebar.metric(
    "Total Wealth",
    money(wealth),
    delta=money(wealth - STARTING_CASH)
)

st.sidebar.metric(
    "Trading Day",
    f"{st.session_state.day}/{MAX_DAYS}"
)

st.sidebar.progress(
    min(wealth / GOAL, 1.0),
    text="Goal: $20,000"
)

st.sidebar.divider()

if st.sidebar.button("🔄 Restart Game", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

c1, c2, c3, c4 = st.columns(4)

c1.metric("💵 Cash", money(st.session_state.cash))
c2.metric("📊 Investments", money(portfolio_value()))
c3.metric("🏆 Total Wealth", money(wealth))
c4.metric("📅 Days Remaining", MAX_DAYS - st.session_state.day)

st.divider()

left, right = st.columns([1.7, 1])

with left:
    st.subheader("🏢 STOCK MARKET")

    company = st.selectbox(
        "Choose a company",
        list(COMPANIES.keys())
    )

    price = st.session_state.prices[company]
    starting_price = COMPANIES[company]["price"]

    change = ((price - starting_price) / starting_price) * 100

    col1, col2, col3 = st.columns(3)

    col1.metric("Stock Price", money(price), f"{change:+.2f}%")
    col2.metric("Shares Owned", st.session_state.holdings[company])
    col3.metric(
        "Position Value",
        money(price * st.session_state.holdings[company])
    )

    chart_data = pd.DataFrame({
        "Day": range(len(st.session_state.history[company])),
        "Price": st.session_state.history[company]
    })

    fig = px.line(
        chart_data,
        x="Day",
        y="Price",
        title=f"{company} ({COMPANIES[company]['ticker']})",
        markers=True
    )

    fig.update_traces(
        line=dict(color="#00CC96", width=4),
        marker=dict(size=6)
    )

    fig.update_layout(
        height=420,
        template="plotly_dark",
        paper_bgcolor=panel,
        plot_bgcolor=panel,
        font=dict(color=text),
        hovermode="x unified",
        xaxis_title="Trading Day",
        yaxis_title="Stock Price ($)"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("💸 TRADE STOCKS")
    st.write(f"**{company}**")
    st.write(f"Current price: **{money(price)}**")

    quantity = st.number_input(
        "Number of shares",
        min_value=1,
        max_value=10000,
        value=1,
        step=1
    )

    st.metric("Estimated Trade Value", money(price * quantity))

    if st.button(
        "🟢 BUY STOCK",
        type="primary",
        use_container_width=True
    ):
        if price * quantity > st.session_state.cash:
            st.error("Not enough cash!")
        else:
            cost = price * quantity
            st.session_state.cash -= cost
            st.session_state.holdings[company] += quantity

            st.session_state.trade_history.insert(
                0,
                f"Bought {quantity} {company} shares for {money(cost)}"
            )

            st.session_state.total_trades += 1
            st.session_state.total_shares_bought += quantity
            st.session_state.trades_today += 1

            update_daily_challenge("buy", company, quantity)
            check_achievements()

            st.session_state.trade_notice = (
                f"Successfully bought {quantity} shares of {company}!"
            )
            st.rerun()

    if st.button(
        "🔴 SELL STOCK",
        use_container_width=True
    ):
        if quantity > st.session_state.holdings[company]:
            st.error("You don't own enough shares!")
        else:
            revenue = price * quantity
            st.session_state.cash += revenue
            st.session_state.holdings[company] -= quantity

            st.session_state.trade_history.insert(
                0,
                f"Sold {quantity} {company} shares for {money(revenue)}"
            )

            st.session_state.total_trades += 1
            st.session_state.trades_today += 1

            update_daily_challenge("sell", company, quantity)
            check_achievements()

            st.session_state.trade_notice = (
                f"Successfully sold {quantity} shares of {company}!"
            )
            st.rerun()

st.divider()
st.subheader("📋 COMPANY DIRECTORY")

company_data = []

for name, data in COMPANIES.items():
    current = st.session_state.prices[name]
    change = ((current - data["price"]) / data["price"]) * 100

    company_data.append({
        "Company": name,
        "Ticker": data["ticker"],
        "Price": current,
        "Change": change,
        "Owned Shares": st.session_state.holdings[name]
    })

df = pd.DataFrame(company_data)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Price": st.column_config.NumberColumn(format="$%.2f"),
        "Change": st.column_config.NumberColumn(format="%.2f%%")
    }
)

st.divider()
st.header("🎮 INVESTOR HUB")

st.caption(
    "Take a break from trading, test your luck, "
    "complete challenges, and earn bonus rewards."
)

st.subheader("🎯 Daily Market Challenge")

challenge = st.session_state.daily_challenge

challenge_col1, challenge_col2 = st.columns([2, 1])

with challenge_col1:
    st.markdown(
        f"""
        <div class="hub-card">
            <h3>📋 Today's Objective</h3>
            <p>{challenge['description']}</p>
            <p>Reward: <b>{money(challenge['reward'])}</b></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    progress = min(challenge["progress"] / challenge["target"], 1.0)
    st.progress(progress)
    st.caption(
        f"Progress: {challenge['progress']} / {challenge['target']}"
    )

with challenge_col2:
    if challenge["completed"]:
        st.success("🏆 CHALLENGE COMPLETE!")
    else:
        st.info("Keep trading to complete today's challenge.")

st.divider()
st.subheader("🎁 Mystery Crate")

crate_col1, crate_col2 = st.columns([2, 1])

with crate_col1:
    st.write("Spend $100 to open a mystery crate. You could win up to $500!")
    st.caption("Possible prizes: $0, $50, $150, $300, or $500.")

with crate_col2:
    if st.session_state.crate_day == st.session_state.day:
        st.info("Today's crate has been opened.")
    else:
        if st.button("🎁 OPEN CRATE — $100", use_container_width=True):
            result = open_mystery_crate()
            st.success(result)

st.divider()
st.subheader("🎡 Investor Wheel")

wheel_col1, wheel_col2 = st.columns([2, 1])

with wheel_col1:
    st.write("Spin the wheel for a random cash reward. But be careful!")
    st.markdown("**Possible results:** -$100, $0, +$100, +$250, or +$500.")

with wheel_col2:
    if st.session_state.wheel_day == st.session_state.day:
        st.info("You've already spun today.")
    else:
        if st.button("🎡 SPIN THE WHEEL", use_container_width=True):
            result = spin_investor_wheel()
            st.success(result)

st.divider()
st.subheader("🕵️ Insider Tips")

st.write("Pay $150 to receive a rumor about a randomly selected company.")
st.caption("Tips are based on recent stock movement, not guaranteed predictions.")

tip_col1, tip_col2 = st.columns([2, 1])

with tip_col1:
    if st.session_state.insider_tip:
        st.info(st.session_state.insider_tip)
    else:
        st.write("You haven't purchased today's tip yet.")

with tip_col2:
    if st.session_state.tip_day == st.session_state.day:
        st.info("Today's tip has been purchased.")
    else:
        if st.button("🔍 BUY INSIDER TIP — $150", use_container_width=True):
            result = purchase_insider_tip()

            if result.startswith("You need") or result.startswith("You've"):
                st.error(result)
            else:
                st.success("Insider tip purchased!")
                st.info(result)

st.divider()
st.subheader("🏆 Achievement Collection")

st.write(
    "Unlock achievements as you build your investing career. "
    "Every achievement gives you bonus cash!"
)

for achievement in ACHIEVEMENT_LIST:
    unlocked = achievement["id"] in st.session_state.achievements

    ach_col1, ach_col2 = st.columns([3, 1])

    with ach_col1:
        if unlocked:
            st.success(
                f"{achievement['emoji']} **{achievement['name']}** — "
                f"{achievement['description']}"
            )
        else:
            st.write(
                f"🔒 **{achievement['name']}** — "
                f"{achievement['description']}"
            )

    with ach_col2:
        if unlocked:
            st.write("✅ UNLOCKED")
        else:
            st.write(f"Reward: {money(achievement['reward'])}")

if st.session_state.achievement_log:
    st.divider()
    st.subheader("🎉 Recent Rewards")

    for message in st.session_state.achievement_log[:8]:
        st.write("• " + message)

st.divider()
st.header("🔍 COMPANY RESEARCH")

research_company = st.selectbox(
    "Research a company",
    list(COMPANIES.keys()),
    key="research_company"
)

if st.session_state.researched_day == st.session_state.day:
    st.info("You already used today's research report.")

    if st.session_state.research_report:
        st.markdown(
            f"""
            <div class="research-card">
                {st.session_state.research_report.replace(chr(10), '<br>')}
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    st.write(
        "Generate a detailed report covering price trends, volatility, "
        "recent news, and your current investment position."
    )

    if st.button("📊 GENERATE RESEARCH REPORT", use_container_width=True):
        report = create_research_report(research_company)

        st.session_state.researched_day = st.session_state.day
        st.session_state.research_report = report

        st.success("Research report generated!")

        st.markdown(
            f"""
            <div class="research-card">
                {report.replace(chr(10), '<br>')}
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()
st.header("📰 BREAKING FINANCIAL NEWS")
st.caption("Stay informed. News can move stock prices!")

for item in st.session_state.news:
    st.markdown(
        f"""
        <div class="news-card">
            <b>{item['headline']}</b>
            <p>{item['details']}</p>
            <small>Trading Day {item['day']}</small>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()
st.header("💼 YOUR INVESTMENT PORTFOLIO")

portfolio_data = []

for name, shares in st.session_state.holdings.items():
    if shares > 0:
        current = st.session_state.prices[name]

        portfolio_data.append({
            "Company": name,
            "Shares": shares,
            "Share Price": current,
            "Total Value": shares * current
        })

if portfolio_data:
    st.dataframe(
        pd.DataFrame(portfolio_data),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Share Price": st.column_config.NumberColumn(format="$%.2f"),
            "Total Value": st.column_config.NumberColumn(format="$%.2f")
        }
    )
else:
    st.info("You haven't invested in any companies yet!")

st.divider()
st.header("📜 YOUR TRADING HISTORY")

if st.session_state.trade_history:
    for trade in st.session_state.trade_history[:15]:
        st.write("• " + trade)
else:
    st.info("Your trading history will appear here.")

st.divider()

st.caption(
    "MARKET MAYHEM | 30-Day Challenge | "
    "All stock prices and news are simulated. "
    "No real money is involved."
)
