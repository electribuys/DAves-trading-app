import tkinter as tk
from tkinter import ttk
import customtkinter as ctk  # Modern UI for Tkinter
from PIL import Image, ImageTk
import yfinance as yf
import numpy as np
import talib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import matplotlib.dates as mdates

# ----------------- CustomTkinter Setup ----------------- #
ctk.set_appearance_mode("dark")  # Cyberpunk dark mode
ctk.set_default_color_theme("blue")

# Create the main app window
tk_app = ctk.CTk()
tk_app.title("Cyberpunk Trade Signal Dashboard")
tk_app.geometry("1400x900")
tk_app.configure(bg="#0d0221")  # Deep space purple for cyberpunk aesthetic

# Font Styling
cyber_font = ("Orbitron", 22, "bold")
info_font = ("Arial", 18, "bold")

# Layout Frames
top_frame = ctk.CTkFrame(tk_app, fg_color="#1a052f", corner_radius=15)
top_frame.pack(pady=10, padx=20, fill="x")

info_frame = ctk.CTkFrame(tk_app, fg_color="#1a052f", corner_radius=15)
info_frame.pack(pady=10, padx=20, fill="both", expand=True)

chart_frame = ctk.CTkFrame(tk_app, fg_color="#1a052f", corner_radius=15,
                           border_width=2, border_color="#ff007f")
chart_frame.pack(fill="both", expand=True, padx=20, pady=20)

# ----------------- Timeframe Configuration ----------------- #
timeframe_map = {
    "1 Day": "1d",
    "7 Days": "7d",
    "30 Days": "30d",
    "1 Year": "1y"
}
timeframe_var = tk.StringVar(value="7 Days")  # default timeframe

# ----------------- Indicator Checkboxes ----------------- #
# Each checkbox toggles whether we plot that indicator on the chart
indicator_vars = {
    "MA10": tk.BooleanVar(value=True),
    "MA20": tk.BooleanVar(value=True),
    "MACD": tk.BooleanVar(value=True),
    "RSI": tk.BooleanVar(value=True),
}

# ----------------- Widgets in the Top Frame ----------------- #
# Ticker
ticker_label = ctk.CTkLabel(top_frame, text="Enter Ticker:", font=cyber_font, text_color="cyan")
ticker_label.grid(row=0, column=0, padx=10, pady=5)

ticker_entry = ctk.CTkEntry(top_frame, font=cyber_font, text_color="white", fg_color="black", 
                            corner_radius=10, border_width=2, border_color="cyan")
ticker_entry.grid(row=0, column=1, padx=10, pady=5)

# Timeframe Dropdown
timeframe_label = ctk.CTkLabel(top_frame, text="Select Timeframe:", font=cyber_font, text_color="cyan")
timeframe_label.grid(row=0, column=2, padx=10, pady=5)

timeframe_menu = ctk.CTkOptionMenu(
    top_frame,
    values=list(timeframe_map.keys()),
    variable=timeframe_var,
    font=cyber_font,
    text_color="white",
    fg_color="black",
    button_color="#ff007f",
    button_hover_color="#ff00ff"
)
timeframe_menu.grid(row=0, column=3, padx=10, pady=5)

# Checkboxes for Indicators
ma10_checkbox = ctk.CTkCheckBox(
    top_frame, text="10MA", variable=indicator_vars["MA10"],
    onvalue=True, offvalue=False, font=("Arial", 14, "bold")
)
ma10_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky="w")

ma20_checkbox = ctk.CTkCheckBox(
    top_frame, text="20MA", variable=indicator_vars["MA20"],
    onvalue=True, offvalue=False, font=("Arial", 14, "bold")
)
ma20_checkbox.grid(row=1, column=1, padx=10, pady=5, sticky="w")

macd_checkbox = ctk.CTkCheckBox(
    top_frame, text="MACD", variable=indicator_vars["MACD"],
    onvalue=True, offvalue=False, font=("Arial", 14, "bold")
)
macd_checkbox.grid(row=1, column=2, padx=10, pady=5, sticky="w")

rsi_checkbox = ctk.CTkCheckBox(
    top_frame, text="RSI", variable=indicator_vars["RSI"],
    onvalue=True, offvalue=False, font=("Arial", 14, "bold")
)
rsi_checkbox.grid(row=1, column=3, padx=10, pady=5, sticky="w")

# Status Label
status_label = ctk.CTkLabel(top_frame, text="", font=cyber_font, text_color="white")
status_label.grid(row=2, column=0, columnspan=4, padx=10, pady=5)

# ----------------- Info Labels (middle frame) ----------------- #
data_labels = [
    ("Trend", "lime"),
    ("Price", "white"),
    ("Pre-Market Price", "cyan"),
    ("RSI", "cyan"),
    ("MACD Signal", "magenta"),
    ("Volume Trend", "yellow"),
    ("Volatility", "orange"),
    ("Trade Length", "cyan"),
    ("Trade Confidence", "lime"),
    ("Support/Resistance", "cyan"),
    ("Market Trend", "yellow")
]

info_labels = {}
for i, (label_text, color) in enumerate(data_labels):
    row = i // 2
    col = i % 2
    label = ctk.CTkLabel(info_frame, text=f"{label_text}: --", font=info_font, text_color=color)
    label.grid(row=row, column=col, padx=20, pady=5, sticky="w")
    info_labels[label_text] = label

# ----------------- CHART UPDATE FUNCTION ----------------- #
def update_chart(ticker, data):
    """
    Create a single chart with multiple y-axes:
      - Primary y-axis: Price, (optionally) 10MA, 20MA
      - Secondary y-axis: (optionally) MACD
      - Tertiary y-axis: (optionally) RSI
    """
    # Prepare the figure
    fig, ax_price = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('#0d0221')
    ax_price.set_facecolor('#0d0221')
    
    # Plot Price
    ax_price.plot(data.index, data["Close"], label="Close Price", color="cyan")
    
    # Plot 10MA if checked
    if indicator_vars["MA10"].get() and "10MA" in data.columns:
        ax_price.plot(data.index, data["10MA"], label="10-day MA", color="magenta")
    
    # Plot 20MA if checked
    if indicator_vars["MA20"].get() and "20MA" in data.columns:
        ax_price.plot(data.index, data["20MA"], label="20-day MA", color="orange")
    
    ax_price.set_ylabel("Price", color="white")
    ax_price.tick_params(axis='y', colors='white')
    ax_price.tick_params(axis='x', colors='white')
    
    # We'll create additional axes as needed
    ax_macd = None
    ax_rsi = None
    
    # Plot MACD if checked
    if indicator_vars["MACD"].get():
        macd, signal, _ = talib.MACD(data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
        ax_macd = ax_price.twinx()
        ax_macd.set_facecolor('#0d0221')
        ax_macd.plot(data.index, macd, label="MACD", color="green")
        ax_macd.plot(data.index, signal, label="Signal", color="red")
        ax_macd.bar(data.index, macd - signal, label="Histogram", color="gray", alpha=0.5)
        ax_macd.set_ylabel("MACD", color="white")
        ax_macd.tick_params(axis='y', colors='white')
    
    # Plot RSI if checked
    if indicator_vars["RSI"].get():
        # If not already computed in get_trade_signal, do it here:
        if "RSI" not in data.columns:
            data["RSI"] = talib.RSI(data["Close"], timeperiod=14)
        ax_rsi = ax_price.twinx()
        ax_rsi.spines["right"].set_position(("axes", 1.1))
        ax_rsi.set_facecolor('#0d0221')
        ax_rsi.plot(data.index, data["RSI"], label="RSI", color="yellow")
        ax_rsi.axhline(70, color="red", linestyle="--", linewidth=1)
        ax_rsi.axhline(30, color="green", linestyle="--", linewidth=1)
        ax_rsi.set_ylabel("RSI", color="white")
        ax_rsi.tick_params(axis='y', colors='white')
    
    # Format the x-axis for dates
    ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    
    # Combine legends from all axes
    lines_labels = []
    def gather_legend(ax):
        if ax is not None:
            lines, labels = ax.get_legend_handles_labels()
            return list(zip(lines, labels))
        return []
    
    lines_labels += gather_legend(ax_price)
    lines_labels += gather_legend(ax_macd)
    lines_labels += gather_legend(ax_rsi)
    
    if lines_labels:
        handles, lbls = zip(*lines_labels)
        ax_price.legend(handles, lbls, loc="upper left")
    
    # Clear any previous chart in the chart_frame
    for widget in chart_frame.winfo_children():
        widget.destroy()
    
    # Embed the Matplotlib figure into the Tkinter frame
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# ----------------- GET TRADE SIGNAL FUNCTION ----------------- #
def get_trade_signal():
    # Update status label to show processing message
    status_label.configure(text="Processing...")
    tk_app.update_idletasks()  # Force UI update
    
    # Get the ticker and timeframe
    ticker = ticker_entry.get().upper()
    selected_timeframe_label = timeframe_var.get()  # e.g. "7 Days"
    selected_timeframe = timeframe_map[selected_timeframe_label]  # e.g. "7d"
    
    if not ticker:
        status_label.configure(text="")
        return
    
    stock = yf.Ticker(ticker)
    data = stock.history(period=selected_timeframe)
    
    if data.empty:
        info_labels["Trend"].configure(text="Invalid Ticker", text_color="red")
        status_label.configure(text="")
        return
    
    # Fetch Live Data for Pre-Market Price
    premarket_price = stock.fast_info.get("preMarketPrice", "N/A")
    
    # Calculate Indicators (MAs, RSI, etc.) up front
    data["10MA"] = talib.SMA(data["Close"], timeperiod=10)
    data["20MA"] = talib.SMA(data["Close"], timeperiod=20)
    data["RSI"] = talib.RSI(data["Close"], timeperiod=14)
    
    macd, signal, _ = talib.MACD(data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
    rsi_val = round(data["RSI"].iloc[-1], 2) if not np.isnan(data["RSI"].iloc[-1]) else "--"
    macd_signal = round(macd.iloc[-1] - signal.iloc[-1], 2) if not np.isnan(macd.iloc[-1]) else "--"
    
    # Trend Logic
    price = round(data["Close"].iloc[-1], 2)
    trend = ("BEARISH (Buy Inverse ETF, Puts, Or Sell Calls)"
             if price < data["10MA"].iloc[-1]
             else "BULLISH (Buy Stock, Calls or Sell Puts)")
    trend_color = "red" if "BEARISH" in trend else "lime"
    
    # Volume Trend
    if len(data) >= 10:
        avg_volume = data["Volume"].rolling(10).mean().iloc[-1]
        volume_trend = "HIGH" if data["Volume"].iloc[-1] > avg_volume else "LOW"
    else:
        volume_trend = "--"
    
    # Volatility Calculation
    log_returns = np.log(data["Close"] / data["Close"].shift(1))
    volatility = round(np.std(log_returns.dropna()) * np.sqrt(252), 2) if not data.empty else 0
    
    # Support & Resistance
    if len(data) >= 10:
        support = round(data["Low"].rolling(10).min().iloc[-1], 2)
        resistance = round(data["High"].rolling(10).max().iloc[-1], 2)
    else:
        support = round(data["Low"].min(), 2)
        resistance = round(data["High"].max(), 2)
    
    # Trade Confidence
    confidence = round((100 - abs(50 - float(rsi_val))) if rsi_val != "--" else 0, 1)
    trade_confidence = f"{confidence}%" if confidence != 0 else "--"
    
    # Market Trend
    market_tickers = {"S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Bitcoin": "BTC-USD"}
    trends = []
    for name, symbol in market_tickers.items():
        market_data = yf.Ticker(symbol).history(period=selected_timeframe)
        if not market_data.empty:
            idx = min(10, len(market_data))
            trend_type = ("Bullish"
                          if market_data["Close"].iloc[-1] > market_data["Close"].iloc[-idx]
                          else "Bearish")
            trends.append(f"{name}: {trend_type}")
        else:
            trends.append(f"{name}: --")
    market_trend = " | ".join(trends)
    
    # ----------------- Update Info Labels ----------------- #
    info_labels["Trend"].configure(text=f"Trend: {trend}", text_color=trend_color)
    info_labels["Price"].configure(text=f"Price: {price}")
    info_labels["Pre-Market Price"].configure(text=f"Pre-Market Price: {premarket_price}")
    info_labels["RSI"].configure(text=f"RSI: {rsi_val}")
    info_labels["MACD Signal"].configure(text=f"MACD Signal: {macd_signal}")
    info_labels["Volume Trend"].configure(text=f"Volume Trend: {volume_trend}")
    info_labels["Volatility"].configure(text=f"Volatility: {volatility}")
    info_labels["Trade Length"].configure(text=f"Trade Length: {selected_timeframe_label}")
    info_labels["Trade Confidence"].configure(text=f"Trade Confidence: {trade_confidence}")
    info_labels["Support/Resistance"].configure(text=f"Support: {support}, Resistance: {resistance}")
    info_labels["Market Trend"].configure(text=f"Market Trend: {market_trend}")
    
    # ----------------- Update Chart ----------------- #
    update_chart(ticker, data)
    
    # Clear the processing message once done
    status_label.configure(text="")

# ----------------- End of Function Definitions ----------------- #

# Bind the Return/Enter key to trigger get_trade_signal
ticker_entry.bind("<Return>", lambda event: get_trade_signal())

# Create the Cyberpunk Button after function definitions
get_signal_btn = ctk.CTkButton(
    top_frame,
    text="Get Trade Signal",
    font=cyber_font,
    fg_color="#ff007f",
    hover_color="#ff00ff",
    corner_radius=10,
    command=get_trade_signal
)
get_signal_btn.grid(row=0, column=4, padx=10, pady=5)

# Run the App
tk_app.mainloop()
