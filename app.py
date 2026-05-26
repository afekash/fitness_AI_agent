import streamlit as st
from google import genai
import json
import requests


# הגדרת כותרת האפליקציה
st.set_page_config(page_title="FitAI Buddy", page_icon="💪", layout="wide")


# --- פונקציה לשליחת נתונים לאקסל ---
def log_to_sheets(user_input, ai_response, calories, protein, water):
    url = "https://script.google.com/macros/s/AKfycby-nC3OyBcKLjho8h3kHxz4DUBED6Amne1VjdZO9ypDaC_woPFek_g9EMpqQV2C754v2w/exec"
    data = {
        "input": user_input,
        "response": ai_response,
        "calories": calories,
        "protein": protein,
        "water": water
    }
    try:
        requests.post(url, json=data)
    except:
        pass


st.title("💪 FitAI – סוכן הבריאות והכושר האישי שלך")


# --- הגדרות צד ---
st.sidebar.title("🎯 הגדרות ויעדים")
gender = st.sidebar.selectbox("מגדר", ["אישה", "גבר"])
age = st.sidebar.number_input("גיל", min_value=10, max_value=100, value=22, step=1)
weight = st.sidebar.number_input("משקל נוכחי (ק״ג)", min_value=30.0, max_value=200.0, value=65.0, step=0.1)
calorie_target = st.sidebar.number_input("יעד קלוריות יומי", value=1800, step=50)
protein_target = int(weight * 2)


# --- משתני מערכת ---
if "current_calories" not in st.session_state: st.session_state.current_calories = 0
if "current_protein" not in st.session_state: st.session_state.current_protein = 0
if "current_water" not in st.session_state: st.session_state.current_water = 0
if "chat_history" not in st.session_state: st.session_state.chat_history = []


# --- חיבור ל-Gemini ---
# מוודאים שמשתמשים בשם הנכון של המפתח שהגדרת ב-Secrets
client = genai.Client(api_key=st.secrets["[Credentials]"])


# --- תצוגת מדדים ---
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("🍎 קלוריות"); st.write(f"{st.session_state.current_calories} / {calorie_target}")
with col2:
    st.subheader("🥩 חלבון"); st.write(f"{st.session_state.current_protein} / {protein_target}")
with col3:
    st.subheader("💧 מים"); st.write(f"{st.session_state.current_water} / 2.5")


st.divider()


user_input = st.chat_input("למשל: אכלתי קוטג' וטונה ושתיתי כוס מים...")


if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    system_instruction = "אתה מאמן תזונה. עליך לנתח את הקלט. החזר JSON עם: response, added_calories (מספר), added_protein (מספר), added_water (מספר)."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_input,
            config={'system_instruction': system_instruction, 'response_mime_type': 'application/json'}
        )
        result = json.loads(response.text.strip())
        
        # עדכון המשתנים
        cal = int(result.get("added_calories", 0))
        prot = int(result.get("added_protein", 0))
        wat = float(result.get("added_water", 0.0))
        
        st.session_state.current_calories += cal
        st.session_state.current_protein += prot
        st.session_state.current_water += wat
        
        # שליחה לאקסל
        log_to_sheets(user_input, result.get("response"), cal, prot, wat)
        
        st.session_state.chat_history.append({"role": "assistant", "content": result.get("response")})
        st.rerun()
    except Exception as e:
        st.error(f"שגיאה: {e}")
