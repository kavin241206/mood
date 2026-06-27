import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import base64
import os

# 1. Set page config
st.set_page_config(page_title="Our Little Space ❤️", page_icon="🥰", layout="centered")

# 2. Function to safely encode local image for CSS background
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# Matches your file name exactly from GitHub
IMG_FILENAME = "background.jpg.jpeg" 
img_base64 = get_base64_image(IMG_FILENAME)

# 3. Inject Custom CSS for Background and Theme Styling
if img_base64:
    st.markdown(
        f"""
        <style>
        /* Main background image setup */
        .stApp {{
            background-image: url("data:image/jpg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* Semi-transparent dark overlay to make white text pop against the selfie */
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.45); /* Darkened so white text is readable */
            backdrop-filter: blur(3px);
            z-index: -1;
        }}
        
        /* Make all standard text, labels, and spans white */
        .stApp, p, label, span, .stMarkdown, .stText {{
            color: #ffffff !important;
        }}
        
        /* Make headers soft pink with a shadow for readability */
        h1, h2, h3, h4 {{
            color: #ff9fb6 !important; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        }}
        
        /* Style the tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(0, 0, 0, 0.3);
            border-radius: 10px 10px 0px 0px;
            padding: 10px 20px;
            color: #ffffff;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: rgba(0, 0, 0, 0.6);
            color: #ff9fb6 !important;
        }}
        
        /* Make Streamlit metrics (the big numbers) white */
        [data-testid="stMetricValue"] {{
            color: #ffffff !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    # Fallback cozy color scheme
    st.markdown("<style>.stApp {background-color: #1a1a1a; color: #fff;}</style>", unsafe_allow_html=True)


# 4. Establish connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(ttl=0)
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Mood", "Miss You Scale", "Notes"])

def save_data(mood, miss_scale, notes):
    df = load_data()
    new_entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Mood": mood,
        "Miss You Scale": miss_scale,
        "Notes": notes
    }
    if df.empty or df.dropna(how='all').empty:
        df = pd.DataFrame([new_entry])
    else:
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    conn.update(data=df)


# --- APP INTERFACE ---

st.markdown("<h1 style='text-align: center;'>💖 Our Daily Connection Hub 💖</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; margin-bottom: 25px; color: #ff9fb6; font-weight: bold;'>✨ Keeping us close, no matter the distance ✨</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✨ For Her", "📊 For You"])

# --- TAB 1: HER INPUT ---
with tab1:
    st.markdown("### Hey beautiful, how are you doing today? 🥰")
    
    mood_options = ["😊 Happy / Excited", "😴 Tired / Lazy", "😔 A bit low", "😡 Annoyed / Stressed", "🥰 Loved / Cozy"]
    selected_mood = st.selectbox("How is your mood today?", mood_options)
    
    st.markdown("---")
    st.markdown("#### Distance Check 🌸")
    miss_scale = st.slider("How much do you miss me today? (1 to 100)", min_value=1, max_value=100, value=75)
    
    st.markdown("---")
    extra_notes = st.text_area("Anything else you want to tell me?", placeholder="Type a sweet note, a secret, or how your day went...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Send Updates ❤️", use_container_width=True):
        with st.spinner("Sending love to our sheet..."):
            save_data(selected_mood, miss_scale, extra_notes)
        st.balloons()
        st.success("Sent! Go check the 'For You' tab to see it updated!")

# --- TAB 2: YOUR VIEW ---
with tab2:
    st.markdown("### How she's doing today 💭")
    
    data = load_data().dropna(how='all')
    
    if data.empty:
        st.info("No updates yet today. Check back later, handsome!")
    else:
        latest = data.iloc[-1]
        
        col1, col2 = st.columns(2)
        with col1:
            mood_val = str(latest["Mood"]).split(" ")[1] if " " in str(latest["Mood"]) else str(latest["Mood"])
            st.metric(label="Current Mood Status", value=mood_val)
            st.caption(f"Full status: {latest['Mood']}")
        with col2:
            st.metric(label="Misses You Scale", value=f"{int(latest['Miss You Scale'])} / 100")
            
        if pd.notna(latest["Notes"]) and str(latest["Notes"]).strip() != "" and str(latest["Notes"]) != "nan":
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 💌 Message for you:")
            st.info(latest["Notes"])
            
        st.markdown(f"<div style='text-align: right; color: #e0e0e0; font-size: 0.8rem; margin-top: 15px;'>Last updated: {latest['Timestamp']}</div>", unsafe_allow_html=True)
        
    # Past Log Dropdown
    if not data.empty:
        with st.expander("📜 Walk Down Memory Lane (Past Logs)"):
            st.dataframe(data.sort_values(by="Timestamp", ascending=False), use_container_width=True)
