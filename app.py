import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ------------------ PAGE SETTINGS ------------------
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="/Assets/meteorology.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set theme colors
THEME_COLOR = "#00d4ff"
DARK_BG = "#0a0e27"
CARD_BG = "#1a1f3a"
TEXT_PRIMARY = "#ffffff"
ACCENT_COLOR = "#ff6b9d"

# Configure matplotlib style
plt.style.use('dark_background')
sns.set_palette("husl")

# ------------------ CUSTOM CSS ------------------
st.markdown(f"""
<style>
:root {{
    --primary-color: {THEME_COLOR};
    --dark-bg: {DARK_BG};
    --card-bg: {CARD_BG};
    --text-primary: {TEXT_PRIMARY};
    --accent-color: {ACCENT_COLOR};
}}

* {{
    margin: 0;
    padding: 0;
}}

body {{
    background: linear-gradient(135deg, {DARK_BG} 0%, #1a2847 100%);
    color: {TEXT_PRIMARY};
}}

.stApp {{
    background: linear-gradient(135deg, {DARK_BG} 0%, #1a2847 100%);
}}

.nav-title {{
    /* reduced margins and left-align so it sits close to the image */
    font-size: 42px;
    font-weight: 700;
    text-align: left;
    display: inline-block;
    background: linear-gradient(135deg, {THEME_COLOR} 0%, {ACCENT_COLOR} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 6px 0;         /* reduced vertical margin */
    letter-spacing: 1px;
    line-height: 1.1;      /* tighter line height to reduce gap */
}}

.card {{
    padding: 25px;
    border-radius: 15px;
    background: linear-gradient(135deg, {CARD_BG} 0%, rgba(26, 31, 58, 0.8) 100%);
    border: 1px solid rgba(0, 212, 255, 0.2);
    box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
    margin: 10px 0;
    transition: all 0.3s ease;
}}

.card:hover {{
    border-color: rgba(0, 212, 255, 0.5);
    box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
    transform: translateY(-5px);
}}

.metric-value {{
    font-size: 32px;
    font-weight: 700;
    color: {THEME_COLOR};
    margin: 10px 0;
}}

.metric-label {{
    font-size: 14px;
    color: rgba(255, 255, 255, 0.7);
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.metric-subtitle {{
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
    margin-top: 8px;
}}

[data-testid="stMetricValue"] {{
    color: {THEME_COLOR};
}}

.stSubheader {{
    border-bottom: 2px solid {THEME_COLOR};
    padding-bottom: 10px;
}}

.stDataFrame {{
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 10px;
}}

.dataframe {{
    background: {CARD_BG} !important;
}}

.stDownloadButton > button {{
    background: linear-gradient(135deg, {THEME_COLOR} 0%, {ACCENT_COLOR} 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 10px 20px;
}}

.stDownloadButton > button:hover {{
    transform: scale(1.05);
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {CARD_BG} 0%, {DARK_BG} 100%);
    border-right: 1px solid rgba(0, 212, 255, 0.2);
}}

.stTextInput > div > div > input {{
    background-color: rgba(255, 255, 255, 0.1);
    color: {TEXT_PRIMARY};
    border: 1px solid {THEME_COLOR};
    border-radius: 8px;
}}

.stButton > button {{
    background: linear-gradient(135deg, {THEME_COLOR} 0%, {ACCENT_COLOR} 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    width: 100%;
    padding: 10px;
}}

.stButton > button:hover {{
    transform: scale(1.02);
}}

.stError {{
    background: rgba(255, 107, 157, 0.2);
    border: 1px solid {ACCENT_COLOR};
    border-radius: 8px;
}}

h1, h2, h3 {{
    color: {TEXT_PRIMARY};
}}
</style>
""", unsafe_allow_html=True)

# ------------------ API KEY ------------------
API_KEY = "67b92f0af5416edbfe58458f502b0a31"

# ------------------ WEATHER FUNCTION ------------------
def current_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url).json()
    if r.get("cod") != 200:
        return None
    return r

def forecast_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url).json()
    if r.get("cod") != "200":
        return None
    return r

def apply_chart_theme(fig, ax):
    """Apply custom theme to charts"""
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(THEME_COLOR)
    ax.spines['bottom'].set_color(THEME_COLOR)
    ax.tick_params(colors=TEXT_PRIMARY)
    ax.xaxis.label.set_color(TEXT_PRIMARY)
    ax.yaxis.label.set_color(TEXT_PRIMARY)
    ax.title.set_color(TEXT_PRIMARY)
    # Safe for axes without line objects (e.g. pie)
    for line in getattr(ax, "lines", []):
        line.set_linewidth(2.5)
    return fig, ax

# New helper functions: render charts with consistent sizing and theme
def render_hourly_chart(hours, temps, city):
    fig, ax = plt.subplots(figsize=(9, 4), dpi=100, constrained_layout=True)
    x = range(len(hours))
    ax.plot(x, temps, marker="o", linewidth=3, markersize=7, color=THEME_COLOR, label="Temp (°C)")
    ax.fill_between(x, temps, alpha=0.18, color=THEME_COLOR)
    ax.set_xticks(x)
    ax.set_xticklabels(hours, rotation=0)
    # title moved to Streamlit column header for better alignment
    # ax.set_title removed
    ax.set_ylabel("Temperature (°C)", fontsize=11)
    ax.set_xlabel("Time", fontsize=11)
    ax.grid(True, alpha=0.18, color=THEME_COLOR)
    ax.legend(loc='upper left', frameon=True, facecolor='none', framealpha=0.25)
    fig.patch.set_alpha(0)
    fig, ax = apply_chart_theme(fig, ax)
    return fig

def render_donut_chart(conditions_counts):
    labels = list(conditions_counts.keys())
    sizes = list(conditions_counts.values())
    colors = [THEME_COLOR, ACCENT_COLOR, "#00ff88", "#ff9500", "#a78bfa"][:len(labels)]
    fig, ax = plt.subplots(figsize=(5, 5), dpi=100, constrained_layout=True)
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        wedgeprops={'width': 0.45, 'edgecolor': 'none'},
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        pctdistance=0.75
    )
    centre_circle = plt.Circle((0, 0), 0.55, fc=CARD_BG, linewidth=0)
    ax.add_artist(centre_circle)
    ax.axis('equal')
    # title moved to Streamlit column header for better alignment
    for t in texts:
        t.set_color(TEXT_PRIMARY)
        t.set_fontsize(10)
        t.set_fontweight('bold')
    for at in autotexts:
        at.set_color('white')
        at.set_fontsize(9)
        at.set_fontweight('bold')
    fig.patch.set_alpha(0)
    fig, ax = apply_chart_theme(fig, ax)
    return fig

# ------------------ SIDEBAR ------------------
st.sidebar.header("🔍 Search City")
city = st.sidebar.text_input("Enter City Name", "Mumbai")
search = st.sidebar.button("Search Weather")

# replace single title markdown with a tighter image + title header
with st.container():
    # tighter ratio and small gap
    col_img, col_title = st.columns([0.06, 0.94], gap="small")
    with col_img:
        st.image("Assets/meteorology.png", width=800)  # smaller width
    with col_title:
        # no leading space and nav-title left-aligned now
        st.markdown("<h1 class='nav-title'>Weather Dashboard</h1>", unsafe_allow_html=True)

# ------------------ MAIN LOGIC ------------------
if search:
    cw = current_weather(city)
    fc = forecast_weather(city)

    if cw:
        st.subheader(f"📍 Current Weather in {city.title()}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class='card'>
                <div class='metric-label'>Temperature</div>
                <div class='metric-value'>{cw['main']['temp']}°C</div>
                <div class='metric-subtitle'>Feels like {cw['main']['feels_like']}°C</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class='card'>
                <div class='metric-label'>Humidity</div>
                <div class='metric-value'>{cw['main']['humidity']}%</div>
                <div class='metric-subtitle'>Pressure: {cw['main']['pressure']} hPa</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class='card'>
                <div class='metric-label'>Wind Speed</div>
                <div class='metric-value'>{cw['wind']['speed']} m/s</div>
                <div class='metric-subtitle'>{cw['weather'][0]['description'].title()}</div>
            </div>
            """, unsafe_allow_html=True)

        # ------------------ HOURLY FORECAST GRAPH ------------------
        if fc:
            # prepare data
            hours = []
            temps = []
            for data in fc["list"][:8]:
                hour = datetime.fromtimestamp(data["dt"]).strftime("%I %p")
                hours.append(hour)
                temps.append(data["main"]["temp"])

            # prepare condition counts for donut
            from collections import Counter
            conditions = [d["weather"][0]["main"] for d in fc["list"][:40]]
            cond_counts = Counter(conditions)

            # render both charts in the same row and place titles at column level for perfect alignment
            with st.container():
                col_chart, col_donut = st.columns([2, 1], gap="large")
                with col_chart:
                    st.markdown("### ⏳ Hourly Temperature Forecast (Next 24 Hours)", unsafe_allow_html=True)
                    fig_line = render_hourly_chart(hours, temps, city)
                    st.pyplot(fig_line, use_container_width=True)
                with col_donut:
                    st.markdown("### ⛅Weather Distribution", unsafe_allow_html=True)
                    fig_donut = render_donut_chart(cond_counts)
                    st.pyplot(fig_donut, use_container_width=True)

        # ------------------ 7 DAY FORECAST ------------------
        st.subheader("📅 5-Day Forecast Summary")

        dates = []
        min_temp = []
        max_temp = []

        for item in fc["list"]:
            dt = item["dt_txt"].split(" ")[0]
            if dt not in dates:
                dates.append(dt)
                min_temp.append(item["main"]["temp_min"])
                max_temp.append(item["main"]["temp_max"])

        df_forecast = pd.DataFrame({
            "Date": dates[:5],
            "Min Temp": min_temp[:5],
            "Max Temp": max_temp[:5]
        })

        # Prepare a separate DataFrame for display/download that includes units
        df_csv = df_forecast.copy()
        df_csv = df_csv.rename(columns={
            "Min Temp": "Min Temp (°C)",
            "Max Temp": "Max Temp (°C)"
        })
        df_csv["Current Temp (°C)"] = cw["main"]["temp"]
        df_csv["Current Humidity (%)"] = cw["main"]["humidity"]
        df_csv["Current Wind Speed (m/s)"] = cw["wind"]["speed"]

        # show the CSV-ready table (with units)
        st.dataframe(df_csv, use_container_width=True)

        # Forecast graph
        fig2, ax2 = plt.subplots(figsize=(12, 5))
        ax2.plot(df_forecast["Date"], df_forecast["Min Temp"], label="Min Temp", marker="o", linewidth=2.5, markersize=8, color="#00d4ff")
        ax2.plot(df_forecast["Date"], df_forecast["Max Temp"], label="Max Temp", marker="s", linewidth=2.5, markersize=8, color="#ff6b9d")
        ax2.fill_between(range(len(df_forecast)), df_forecast["Min Temp"], df_forecast["Max Temp"], alpha=0.2, color=THEME_COLOR)
        ax2.set_title("5-Day Temperature Trend", fontsize=16, fontweight='bold')
        ax2.set_ylabel("Temperature (°C)", fontsize=12)
        ax2.set_xlabel("Date", fontsize=12)
        ax2.legend(loc='upper left', framealpha=0.9)
        ax2.grid(True, alpha=0.2, color=THEME_COLOR)
        fig2, ax2 = apply_chart_theme(fig2, ax2)
        st.pyplot(fig2)

        # ------------------ CORRELATION HEATMAP ------------------
        # Build metrics DataFrame from forecast entries
        metrics = []
        for item in fc["list"][:40]:
            metrics.append({
                "Temperature": item["main"].get("temp"),
                "Pressure": item["main"].get("pressure"),
                "Humidity": item["main"].get("humidity"),
                "Wind Speed": item.get("wind", {}).get("speed")
            })
        df_metrics = pd.DataFrame(metrics)

        if not df_metrics.empty:
            import matplotlib.colors as mcolors
            # create a smooth theme colormap from THEME_COLOR -> CARD_BG -> ACCENT_COLOR
            cmap = mcolors.LinearSegmentedColormap.from_list(
                "theme_cmap", [THEME_COLOR, CARD_BG, ACCENT_COLOR]
            )

            # Center heatmap using columns for professional alignment
            corr = df_metrics.corr()
            with st.container():
                st.subheader("🔎 Metric Correlations")
                left_col, mid_col, right_col = st.columns([1, 2, 1])
                with mid_col:
                    fig_h, ax_h = plt.subplots(figsize=(6.5, 4.5), dpi=100, constrained_layout=True)
                    sns.heatmap(
                        corr,
                        annot=True,
                        fmt=".2f",
                        cmap=cmap,
                        vmin=-1,
                        vmax=1,
                        annot_kws={"color": "white", "weight": "bold", "size": 10},
                        cbar_kws={"shrink": 0.6, "label": "Correlation", "pad": 0.02},
                        linewidths=0.6,
                        linecolor=(1, 1, 1, 0.03),
                        square=True,
                        ax=ax_h
                    )
                    ax_h.set_title("Correlation Matrix — Temp · Pressure · Humidity · Wind", fontsize=13, fontweight='bold', pad=10)
                    # Tidy tick labels and colors
                    ax_h.set_xticklabels(ax_h.get_xticklabels(), rotation=45, ha="right")
                    ax_h.set_yticklabels(ax_h.get_yticklabels(), rotation=0)
                    ax_h.tick_params(colors=TEXT_PRIMARY, labelsize=11)

                    # Style colorbar ticks to match theme
                    cbar = ax_h.collections[0].colorbar
                    cbar.ax.yaxis.set_tick_params(color=TEXT_PRIMARY)
                    plt.setp(cbar.ax.get_yticklabels(), color=TEXT_PRIMARY)

                    # Transparent background and apply theme to axes
                    fig_h.patch.set_alpha(0)
                    ax_h.set_facecolor("none")
                    fig_h, ax_h = apply_chart_theme(fig_h, ax_h)

                    st.pyplot(fig_h, use_container_width=True)

        # ------------------ CSV DOWNLOAD ------------------
        st.subheader("📥 Download Data")
        csv = df_csv.to_csv(index=False).encode("utf-8")
        st.download_button("Download 5-Day Forecast CSV", csv, "forecast.csv", "text/csv")

    else:
        st.error("City Not Found! Try a valid city name.")
