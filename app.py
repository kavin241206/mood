import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import base64
import os

# 1. Set page config
st.set_page_config(page_title="Our Little Space ❤️", page_icon="🥰", layout="centered")

# --- INITIALIZE SESSION STATE FOR FRONT PAGE ---
if 'unlocked' not in st.session_state:
    st.session_state.unlocked = False

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
            background-color: rgba(0, 0, 0, 0.45);
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
        
        /* Make the buttons green */
        div[data-testid="stButton"] button {{
            background-color: #4CAF50 !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
            padding: 15px 30px !important;
        }}
        div[data-testid="stButton"] button:hover {{
            background-color: #45a049 !important;
            color: white !important;
        }}
        
        /* CRAZY LOVE BAR CSS */
        .love-container {{
            width: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            border-radius: 25px;
            padding: 5px;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
            margin: 20px 0px;
        }}
        .love-bar {{
            height: 45px;
            background: linear-gradient(90deg, #ff1493, #ff69b4, #ff1493);
            background-size: 200% 200%;
            border-radius: 20px;
            text-align: center;
            line-height: 45px;
            color: white;
            font-weight: 900;
            font-size: 1.3rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            animation: pulse-glow 2s infinite, moving-gradient 3s infinite linear;
            white-space: nowrap;
            overflow: hidden;
        }}
        
        @keyframes pulse-glow {{
            0% {{ box-shadow: 0 0 10px #ff1493; }}
            50% {{ box-shadow: 0 0 25px #ff1493, 0 0 40px #ff69b4; }}
            100% {{ box-shadow: 0 0 10px #ff1493; }}
        }}
        @keyframes moving-gradient {{
            0% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
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
        return pd.DataFrame(columns=["Timestamp", "Mood", "Miss You Scale", "Love Counter", "Notes"])

def save_data(mood, miss_scale, love_scale, notes):
    df = load_data()
    new_entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Mood": mood,
        "Miss You Scale": miss_scale,
        "Love Counter": love_scale,
        "Notes": notes
    }
    if df.empty or df.dropna(how='all').empty:
        df = pd.DataFrame([new_entry])
    else:
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    conn.update(data=df)


# ==========================================
# --- APP INTERFACE ROUTING ---
# ==========================================

if not st.session_state.unlocked:
    # --- THE FRONT PAGE ---
    # Add some spacing to push everything to the middle of the screen
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem;'>Hello Beautiful ✨</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #e0e0e0; font-weight: normal; margin-bottom: 40px;'>Are you ready to enter our little space?</h3>", unsafe_allow_html=True)
    
    # Center the button using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Yes, take me there! ❤️", use_container_width=True):
            st.session_state.unlocked = True
            st.rerun() # This instantly refreshes the page to show the main app

else:
    # --- THE MAIN APP (Only shows if unlocked = True) ---
    st.markdown("<h1 style='text-align: center;'>💖 Our Daily Connection Hub 💖</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-bottom: 25px; color: #ff9fb6; font-weight: bold;'>✨ Keeping us close, no matter the distance ✨</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["✨ For Her", "📊 For You"])

    # --- TAB 1: HER INPUT ---
    with tab1:
        st.markdown("### How are you doing today? 🥰")
        
        mood_options = ["😊 Happy / Excited", "😴 Tired / Lazy", "😔 A bit low", "😡 Annoyed / Stressed", "🥰 Loved / Cozy"]
        selected_mood = st.selectbox("How is your mood today?", mood_options)
        
        st.markdown("---")
        st.markdown("#### Distance Check 🌸")
        miss_scale = st.slider("How much do you miss me today? (1 to 100)", min_value=1, max_value=100, value=75)
        
        st.markdown("---")
        st.markdown("#### The Love Meter 💘")
        love_scale = st.slider("Scale limit broken! How much do you love me?", min_value=1, max_value=3000, value=3000, step=10, help="I love you 3000! 🤖❤️")
        
        st.markdown("---")
        extra_notes = st.text_area("Anything else you want to tell me?", placeholder="Type a sweet note, a secret, or how your day went...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Send Updates ❤️", use_container_width=True):
            with st.spinner("Sending love to our sheet..."):
                save_data(selected_mood, miss_scale, love_scale, extra_notes)
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
            
            # Top Row: Mood and Miss Scale
            col1, col2 = st.columns(2)
            with col1:
                mood_val = str(latest["Mood"]).split(" ")[1] if " " in str(latest["Mood"]) else str(latest["Mood"])
                st.metric(label="Current Mood Status", value=mood_val)
                st.caption(f"Full status: {latest['Mood']}")
            with col2:
                st.metric(label="Misses You Scale", value=f"{int(latest['Miss You Scale'])} / 100")
            
            st.markdown("---")
            
            # Bottom Row: THE GLOWING LOVE BAR
            st.markdown("<h4 style='text-align: center;'>Love Power Level Detected:</h4>", unsafe_allow_html=True)
            
            # Extract the love value and calculate the percentage to fill the bar
            current_love = int(latest.get("Love Counter", 3000)) if pd.notna(latest.get("Love Counter")) else 3000
            percentage = min(100, max(5, int((current_love / 3000) * 100)))
            
            # Inject the custom HTML for the animated bar
            love_bar_html = f"""
            <div class="love-container">
                <div class="love-bar" style="width: {percentage}%;">
                    🚀 {current_love} / 3000
                </div>
            </div>
            """
            st.markdown(love_bar_html, unsafe_allow_html=True)
                
            if pd.notna(latest["Notes"]) and str(latest["Notes"]).strip() != "" and str(latest["Notes"]) != "nan":
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 💌 Message for you:")
                st.info(latest["Notes"])
                
            st.markdown(f"<div style='text-align: right; color: #e0e0e0; font-size: 0.8rem; margin-top: 15px;'>Last updated: {latest['Timestamp']}</div>", unsafe_allow_html=True)
            
        # Past Log Dropdown
        if not data.empty:
            with st.expander("📜 Walk Down Memory Lane (Past Logs)"):
                st.dataframe(data.sort_values(by="Timestamp", ascending=False), use_container_width=True)
