import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime

# הגדרת ה-API של Gemini (תשאירי את זה כפי שהיה לך)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# פונקציית ה"צינור" לאקסל
def log_to_sheets(user_input, ai_response, calories, protein, water):
    # הכתובת שהעתקת מ-Apps Script
    url = "https://script.google.com/macros/s/AKfycbx1IjiqAA2p7Gai4aAM2FsPYR3YV7-IXljcwJqDEsdakKhdj5377EwVnnt1lI4ITxCvqQ/exec"
    data = {
        "input": user_input,
        "response": ai_response,
        "calories": calories,
        "protein": protein,
        "water": water
    }
    try:
        requests.post(url, json=data)
    except Exception as e:
        st.error(f"שגיאה בשמירה לאקסל: {e}")

# ממשק המשתמש
st.title("FitAI Tracker 🥗")
user_input = st.text_input("מה אכלת היום?")

if st.button("שלח"):
    if user_input:
        model = genai.GenerativeModel('gemini-pro')
        # הנחיה לבוט להוציא נתונים מסודרים
        prompt = f"נתח את האוכל הבא: {user_input}. תחזיר תשובה בפורמט: קלוריות (מספר), חלבון (מספר), מים (מספר), והמלצה קצרה."
        
        response = model.generate_content(prompt)
        ai_response = response.text
        
        # כאן אנחנו "מנחשים" את המספרים (זה תלוי איך ה-Gemini עונה לך)
        # בואי נניח לבינתיים ערכים בסיסיים כדי שהקוד יעבוד
        calories, protein, water = 0, 0, 0 
        
        st.write(ai_response)
        
        # עדכון האקסל
        log_to_sheets(user_input, ai_response, calories, protein, water)
        st.success("המידע נשמר באקסל!")
