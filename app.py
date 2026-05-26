import streamlit as st
from google import genai
import json
import os

# הגדרת כותרת האפליקציה
st.set_page_config(page_title="FitAI Buddy", page_icon="💪", layout="wide")

# --- פונקציות שמירה וטעינה (זיכרון קבוע) ---
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # נתונים התחלתיים
    return {"calories": 0, "protein": 0, "burned": 0, "water": 0}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

st.title("💪 FitAI – סוכן הבריאות והכושר האישי שלך")

# --- הגדרות צד (היעדים שלך) ---
st.sidebar.title("🎯 הגדרות ויעדים")
calorie_target = st.sidebar.number_input("יעד קלוריות יומי", value=1800, step=50)
water_target = st.sidebar.number_input("יעד מים יומי (ליטרים)", value=2.5, step=0.1)

# --- חיבור ל-Gemini ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- תצוגת מדדים ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.subheader("🍎 קלוריות"); st.write(f"{data['calories']} / {calorie_target}")
with col2:
    st.subheader("🔥 שריפה"); st.write(f"{data['burned']} קק\"ל")
with col3:
    st.subheader("🥩 חלבון"); st.write(f"{data['protein']} גרם")
with col4:
    st.subheader("💧 מים"); st.write(f"{data['water']} / {water_target} ליטר")

st.divider()

user_input = st.chat_input("מה אכלת או איזה אימון עשית?")

if user_input:
    system_instruction = "אתה מאמן. החזר JSON עם: response, added_calories (מספר), added_protein (מספר), calories_burned (מספר), added_water (מספר)."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_input,
            config={'system_instruction': system_instruction, 'response_mime_type': 'application/json'}
        )
        result = json.loads(response.text.strip())
        
        # עדכון ושמירה
        data['calories'] += int(result.get("added_calories", 0))
        data['protein'] += int(result.get("added_protein", 0))
        data['burned'] += int(result.get("calories_burned", 0))
        data['water'] += float(result.get("added_water", 0.0))
        save_data(data)
        
        st.success(result.get("response"))
        st.rerun()
    except Exception as e:
        st.error("הייתה שגיאה, נסי שוב")
