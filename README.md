# 🤖 Systematic NSE Index Options Algos

A collection of 6 automated intraday options-selling and real-time MTM monitoring bots built in **Python** for Indian index derivatives (**NIFTY**, **BANKNIFTY**, and **FINNIFTY**). The suite implements two systematic strategy frameworks—**Directional/Non-Directional (DND) Regime Switching** and **Dynamic Rolling Straddles**—complete with live option-chain parsing, automated Telegram alerts, intraday MTM charting, and end-of-day CSV trade logs.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-MTM%20Charts-11557c)
![Telegram](https://img.shields.io/badge/Telegram-Live%20Alerts-26A5E4?logo=telegram&logoColor=white)

---

## 📌 Strategy Suite Overview

| Strategy Family | Underlying | Entry Time | Exit Time | Core Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **DND Setup** | NIFTY | 09:20 IST | 15:25 IST | PDH/PDL regime switching (`Neutral` ↔ `Bullish` ↔ `Bearish`) via premium-matched strikes |
| **DND Setup** | BANKNIFTY | 09:20 IST | 15:25 IST | PDH/PDL regime switching (`Neutral` ↔ `Bullish` ↔ `Bearish`) via premium-matched strikes |
| **DND Setup** | FINNIFTY | 09:20 IST | 15:25 IST | PDH/PDL regime switching (`Neutral` ↔ `Bullish` ↔ `Bearish`) via premium-matched strikes |
| **Rolling Straddle** | NIFTY | 09:16 IST | 15:25 IST | Short ATM straddle; rolls to new ATM when spot shifts by 1 strike (±5 pts) or skips >106 pts |
| **Rolling Straddle** | BANKNIFTY | 09:16 IST | 15:25 IST | Short ATM straddle; rolls to new ATM when spot shifts by 1 strike (±5 pts) or skips >106 pts |
| **Rolling Straddle** | FINNIFTY | 09:16 IST | 15:25 IST | Short ATM straddle; rolls to new ATM when spot shifts by 1 strike (±5 pts) or skips >106 pts |

---

## ⚙️ How the Strategies Work

### 1. DND Setup (Directional / Non-Directional)
- Pulls Previous Day High (**PDH**), Previous Day Low (**PDL**), and Today's Open from TradingView (`tvDatafeed`).
- Classifies the market at **09:20 IST** into one of three regimes:
  - **Neutral** (`PDL < Spot < PDH`): Sells both a Call and a Put nearest to the target premium.
  - **Bullish** (`Spot > PDH` and `Spot > Open`): Sells Put legs only.
  - **Bearish** (`Spot < PDL` and `Spot < Open`): Sells Call legs only.
- Continuously monitors spot price at 5-minute intervals and dynamically exits the tested leg / enters the new regime leg whenever price breaks out of or re-enters the PDH/PDL range.

### 2. Rolling Straddle (RS)
- Waits until spot is within `±5` points of the nearest At-The-Money (ATM) strike after **09:16 IST** and sells the ATM CE + PE straddle.
- Tracks real-time combined straddle premium and MTM P&L every 10 seconds.
- Automatically squares off the current straddle and rolls to the new ATM strike whenever the underlying moves to a new ATM (within `±5` points) or gaps past `±106` points, carrying realized P&L into the adjusted cost basis.

---

## ✨ Key System Features

- **Dynamic Option-Chain Strike Selection:** Queries live NFO option chains to automatically resolve trading symbols by nearest target premium or ATM strike.
- **Automated Telegram Reporting:**
  - Instant entry, adjustment, and exit notifications.
  - **Every 30 minutes:** Generates and sends a shaded Matplotlib intraday MTM P&L chart annotated with `Max`, `Min`, and `Avg` P&L.
  - **Every 5 minutes:** Snapshots intraday MTM history to CSV.
  - **15:25 IST Square-Off:** Closes all open legs, exports the complete intraday trade log (`tradelog_YYYY-MM-DD.csv`), and dispatches the final P&L chart and CSV file to Telegram.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python |
| **Market Data** | Broker REST API (`login_flow`), `tvDatafeed` (TradingView) |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib |
| **Notifications** | Telegram Bot API (`tg_bot`) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- A supported broker API session module (`login_flow.py` exposing an authenticated `api` object)
- A Telegram bot helper module (`tg_bot.py` exposing `telegram_send_message`, `telegram_send_photo_caption`, and `telegram_send_file`)

### Setup

1. **Clone the repository**
   ```bash
   git clone [https://github.com/shubhamharwani/](https://github.com/shubhamharwani/)<repo-name>.git
   cd <repo-name>
   ```

2. **Install dependencies**
   ```bash
   pip install pandas numpy matplotlib tvDatafeed
   ```

3. **Configure credentials & output folder**
   - Create an `output/` directory in the project root.
   - Replace `"YOUR_TELEGRAM_CHAT_ID"` in the strategy script you want to run with your Telegram channel/group chat ID.
   - Provide your local `login_flow.py` and `tg_bot.py` modules (excluded from version control for security).

4. **Run a strategy**
   ```bash
   python dnd_nifty.py
   ```

---

## ⚠️ Disclaimer

These scripts are shared strictly for educational and portfolio demonstration purposes. Derivatives trading involves substantial risk of loss. This repository does not constitute financial or investment advice.

---

## 👤 Author

**Shubham Harwani**  
- GitHub: [@shubhamharwani](https://github.com/shubhamharwani)
