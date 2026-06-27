import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Set page config
st.set_page_config(page_title="Our Mood Tracker", page_icon="❤️", layout="centered")

# Establish connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper function to load data safely
def load_data():
    try:
        # Read existing data from the sheet
        return conn.read(ttl=0)  # ttl=0 ensures it fetches fresh data every time
    except Exception:
        # Fallback if the sheet is completely empty or can't be read yet
        return pd.DataFrame(columns=["Timestamp", "Mood", "Miss You Scale", "Notes"])

# Helper function to save data
def save_data(mood, miss_scale, notes):
    df = load_data()
    new_entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Mood": mood,
        "Miss You Scale": miss_scale,
        "Notes": notes
    }
    
    # Clean up empty dataframes if needed, then append
    if df.empty or df.dropna(how='all').empty:
        df = pd.DataFrame([new_entry])
    else:
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    
    # Update the Google Sheet
    conn.update(data=df)

# --- APP INTERFACE ---

st.title("❤️ Daily Connection Hub")

tab1, tab2 = st.tabs(["✨ For Her", "📊 For You"])

# --- TAB 1: HER INPUT ---
with tab1:
    st.header("Hey beautiful, how are you doing today?")
    
    mood_options = ["😊 Happy / Excited", "😴 Tired / Lazy", "😔 A bit low", "😡 Annoyed / Stressed", "🥰 Loved / Cozy"]
    selected_mood = st.selectbox("How is your mood today?", mood_options)
    
    miss_scale = st.slider("How much do you miss me today? (1 to 100)", min_value=1, max_value=100, value=50)
    extra_notes = st.text_area("Anything else you want to tell me?", placeholder="Type here...")
    
    if st.button("Send Updates ❤️"):
        with st.spinner("Sending to our sheet..."):
            save_data(selected_mood, miss_scale, extra_notes)
        st.balloons()
        st.success("Sent! Go check the 'For You' tab to see it updated!")

# --- TAB 2: YOUR VIEW ---
with tab2:
    st.header("How she's doing")
    
    data = load_data()
    
    # Clean out any completely empty rows from the dataframe row check
    data = data.dropna(how='all')
    
    if data.empty:
        st.info("No updates yet today. Check back later!")
    else:
        # Get the latest entry
        latest = data.iloc[-1]
        
        col1, col2 = st.columns(2)
        with col1:
            # Safely handle string splitting if the data formatting shifts
            mood_val = str(latest["Mood"]).split(" ")[1] if " " in str(latest["Mood"]) else str(latest["Mood"])
            st.metric(label="Current Mood", value=mood_val)
            st.caption(f"Icon/Type: {latest['Mood']}")
        with col2:
            st.metric(label="Misses You Scale", value=f"{int(latest['Miss You Scale'])}/100")
            
        if pd.notna(latest["Notes"]) and str(latest["Notes"]).strip() != "" and str(latest["Notes"]) != "nan":
            st.subheader("Message for you:")
            st.info(latest["Notes"])
            
        st.caption(f"Last updated at: {latest['Timestamp']}")
        
        with st.expander("See Past History Log"):
            st.dataframe(data.sort_values(by="Timestamp", ascending=False), use_container_width=True)
