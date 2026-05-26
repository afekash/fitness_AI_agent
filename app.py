import streamlit as st
from google import genai
import json

# הגדרת כותרת האפליקציה ואייקון לשונית בדפדפן
st.set_page_config(page_title="FitAI Buddy", page_icon="💪", layout="wide")

st.title("💪 FitAI – סוכן הבריאות והכושר האישי שלך")
st.write("ה-AI מחובר! נסי לכתוב לו מה אכלת, שתית או איזה אימון עשית והמדדים יתעדכנו אוטומטית.")

# --- יצירת סרגל הצד (Sidebar) להגדרות ---
st.sidebar.title("🎯 הגדרות ויעדים")
gender = st.sidebar.selectbox("מגדר", ["אישה", "גבר"])
age = st.sidebar.number_input("גיל", min_value=10, max_value=100, value=22, step=1)
weight = st.sidebar.number_input("משקל נוכחי (ק״ג)", min_value=30.0, max_value=200.0, value=65.0, step=0.1)
height = st.sidebar.number_input("גובה (ס״מ)", min_value=100, max_value=250, value=170, step=1)
calorie_target = st.sidebar.number_input("יעד קלוריות יומי (נטו)", value=1800, step=50)
protein_target = int(weight * 2)
water_target = st.sidebar.number_input("יעד מים יומי (ליטרים)", value=2.5, step=0.5)

# --- משתני מערכת ---
if "current_calories" not in st.session_state: st.session_state.current_calories = 0
if "current_protein" not in st.session_state: st.session_state.current_protein = 0
if "current_water" not in st.session_state: st.session_state.current_water = 0
if "calories_burned" not in st.session_state: st.session_state.calories_burned = 0 # חדש
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- חיבור ל-Gemini ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- הצגת מדדים ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.subheader("🍎 קלוריות שנאכלו")
    st.write(f"{st.session_state.current_calories} קק\"ל")
with col2:
    st.subheader("🔥 קלוריות שנשרפו")
    st.write(f"{st.session_state.calories_burned} קק\"ל")
with col3:
    st.subheader("🥩 חלבון")
    st.write(f"{st.session_state.current_protein} ג׳")
with col4:
    st.subheader("💧 מים")
    st.write(f"{st.session_state.current_water} ליטר")

st.divider()

# --- היסטוריה ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("למשל: אכלתי קוטג', או: רצתי 30 דקות...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    system_instruction = f"""
    אתה מאמן כושר ותזונאי אישי חכם.
    המשתמשת: {gender}, בת {age}, שוקלת {weight} ק"ג.
    נתח את הקלט: אם זה אוכל - חשב קלוריות וחלבון. אם זו פעילות גופנית - חשב קלוריות שנשרפו.
    החזר JSON בלבד עם:
    {{
        "response": "תגובה מעודדת קצרה",
        "added_calories": מספר,
        "added_protein": מספר,
        "added_water": מספר,
        "calories_burned": מספר
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', # עדכנתי ל-2.0, הוא יותר יציב
            contents=user_input,
            config={'system_instruction': system_instruction, 'response_mime_type': 'application/json'}
        )
        
        result = json.loads(response.text.strip())
        
        # עדכון המדדים
        st.session_state.current_calories += int(result.get("added_calories", 0))
        st.session_state.current_protein += int(result.get("added_protein", 0))
        st.session_state.current_water += float(result.get("added_water", 0.0))
        st.session_state.calories_burned += int(result.get("calories_burned", 0))
        
        st.session_state.chat_history.append({"role": "assistant", "content": result.get("response")})
        st.rerun()
    except Exception as e:
        st.error("התרחשה שגיאה בתקשורת עם ה-AI")
