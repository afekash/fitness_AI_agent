import streamlit as st
from google import genai
import json

# הגדרת כותרת האפליקציה ואייקון לשונית בדפדפן
st.set_page_config(page_title="FitAI Buddy", page_icon="💪", layout="wide")

st.title("💪 FitAI – סוכן הבריאות והכושר האישי שלך")
st.write("ה-AI מחובר! נסי לכתוב לו מה אכלת או שתית היום והמדים יתעדכנו אוטומטית.")

# --- יצירת סרגל הצד (Sidebar) להגדרות ---
st.sidebar.title("🎯 הגדרות ויעדים")

st.sidebar.markdown("### 👤 פרופיל אישי")
gender = st.sidebar.selectbox("מגדר", ["אישה", "גבר"])
age = st.sidebar.number_input("גיל", min_value=10, max_value=100, value=22, step=1)
weight = st.sidebar.number_input("משקל נוכחי (ק״ג)", min_value=30.0, max_value=200.0, value=65.0, step=0.1)
height = st.sidebar.number_input("גובה (ס״מ)", min_value=100, max_value=250, value=170, step=1)

st.sidebar.markdown("---") 

# יעדים יומיים
st.sidebar.markdown("### 📅 יעדים יומיים")
calorie_target = st.sidebar.number_input("יעד קלוריות יומי", value=1800, step=50)

# חישוב אוטומטי: 2 גרם חלבון לכל קילו משקל גוף (הופך למספר שלם)
protein_target = int(weight * 2)
st.sidebar.info(f"🎯 יעד חלבון מחושב: {protein_target} גרם")

water_target = st.sidebar.number_input("יעד מים יומי (ליטרים)", value=2.5, step=0.5)

# --- משתני מערכת (Session State) לשמירת המדדים והיסטוריית הצ'אט ---
if "current_calories" not in st.session_state:
    st.session_state.current_calories = 0
if "current_protein" not in st.session_state:
    st.session_state.current_protein = 0
if "current_water" not in st.session_state:
    st.session_state.current_water = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- חיבור ל-Gemini באמצעות המפתח מהכספת ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- הצגת מדדי התקדמות (Progress Bars) במרכז המסך ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🍎 תזונה (קלוריות)")
    cal_progress = min(st.session_state.current_calories / calorie_target, 1.0) if calorie_target > 0 else 0.0
    st.progress(cal_progress)
    st.write(f"{st.session_state.current_calories} / {calorie_target} קק''ל")

with col2:
    st.subheader("🥩 חלבון (גרם)")
    protein_progress = min(st.session_state.current_protein / protein_target, 1.0) if protein_target > 0 else 0.0
    st.progress(protein_
