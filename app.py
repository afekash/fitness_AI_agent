import streamlit as st
from google import genai
import json

# הגדרת כותרת האפליקציה
st.set_page_config(page_title="FitAI Buddy", page_icon="💪", layout="wide")

st.title("💪 FitAI – סוכן הבריאות והכושר האישי שלך")

# --- משתני מערכת ---
if "current_calories" not in st.session_state: st.session_state.current_calories = 0
if "current_protein" not in st.session_state: st.session_state.current_protein = 0
if "calories_burned" not in st.session_state: st.session_state.calories_burned = 0
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- חיבור ל-Gemini ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- תצוגת מדדים ---
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("🍎 קלוריות")
    st.write(f"{st.session_state.current_calories} קק\"ל")
with col2:
    st.subheader("🔥 שריפה")
    st.write(f"{st.session_state.calories_burned} קק\"ל")
with col3:
    st.subheader("🥩 חלבון")
    st.write(f"{st.session_state.current_protein} גרם")

st.divider()

user_input = st.chat_input("מה עשית היום? (אכלתי... או עשיתי אימון...)")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # הוראות פשוטות ששומרות על המבנה שעבד לך
    system_instruction = """
    אתה עוזר כושר. נתח את הקלט. 
    החזר JSON עם: 
    response (תגובה), added_calories (מספר), added_protein (מספר), calories_burned (מספר).
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_input,
            config={'system_instruction': system_instruction, 'response_mime_type': 'application/json'}
        )
        
        result = json.loads(response.text.strip())
        
        # עדכון המדדים הישירים
        st.session_state.current_calories += int(result.get("added_calories", 0))
        st.session_state.current_protein += int(result.get("added_protein", 0))
        st.session_state.calories_burned += int(result.get("calories_burned", 0))
        
        st.session_state.chat_history.append({"role": "assistant", "content": result.get("response")})
        st.rerun()
    except Exception as e:
        st.error("הייתה שגיאה בעיבוד. נסי שוב.")

# הצגת היסטוריה
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
