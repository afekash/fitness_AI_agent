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
water_target = st.sidebar.number_input("יעד מים יומי (ליטרים)", value=2.5, step=0.5)

# --- משתני מערכת (Session State) לשמירת המדדים והיסטוריית הצ'אט ---
if "current_calories" not in st.session_state:
    st.session_state.current_calories = 0
if "current_water" not in st.session_state:
    st.session_state.current_water = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- חיבור ל-Gemini באמצעות המפתח מהכספת ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- הצגת מדדי התקדמות (Progress Bars) במרכז המסך ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🍎 תזונה (קלוריות)")
    cal_progress = min(st.session_state.current_calories / calorie_target, 1.0) if calorie_target > 0 else 0.0
    st.progress(cal_progress)
    st.write(f"{st.session_state.current_calories} / {calorie_target} קק''ל")

with col2:
    st.subheader("💧 רוויה (מים)")
    water_progress = min(st.session_state.current_water / water_target, 1.0) if water_target > 0 else 0.0
    st.progress(water_progress)
    st.write(f"{st.session_state.current_water} / {water_target} ליטר")

st.divider()

# --- הצגת היסטוריית הצ'אט על המסך ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- אזור קלט מהמשתמש ---
user_input = st.chat_input("למשל: אכלתי עכשיו סלט יווני ושתיתי 2 כוסות מים...")

if user_input:
    # 1. מציג ושומר את הודעת המשתמש
    st.chat_message("user").write(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # 2. בניית ההוראות ל-AI
    system_instruction = f"""
    אתה מאמן כושר ותזונאי אישי חכם ומקצועי.
    המשתמשת מולך היא {gender} בגיל {age}, במשקל {weight} ק"ג ובגובה {height} ס"מ.
    עליך לנתח את מה שהיא אכלה או שתתה בהודעה האחרונה ולהחזיר אך ורק אובייקט JSON תקין.
    
    מבנה ה-JSON:
    {{
        "response": "תגובה קצרה ומעודדת בעברית על מה שהיא דיווחה",
        "added_calories": מספר קלוריות של האוכל (מספר שלם, או 0 אם לא אכלה),
        "added_water": כמות המים בליטרים (מספר עשרוני, למשל 0.5, או 0.0 אם לא שתתה)
    }}
    """
    
    try:
        # 3. פנייה ל-Gemini עם הגדרת חובה להחזרת JSON
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_input,
            config={
                'system_instruction': system_instruction,
                'response_mime_type': 'application/json' # מכריח את המודל לענות ב-JSON נקי
            }
        )
        
        # 4. פירוק ה-JSON
        result = json.loads(response.text.strip())
        
        # 5. עדכון המדדים
        st.session_state.current_calories += int(result.get("added_calories", 0))
        st.session_state.current_water += float(result.get("added_water", 0.0))
        
        # 6. הצגת תגובת ה-AI
        ai_response = result.get("response", "הנתונים עודכנו בהצלחה!")
        with st.chat_message("assistant"):
            st.write(ai_response)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # ריענון האפליקציה לעדכון המדים
        st.rerun()
        
    except Exception as e:
        with st.chat_message("assistant"):
            st.error("התרחשה שגיאה בתקשורת עם ה-AI:")
            st.exception(e) # מציג את השגיאה המלאה והמדויקת של פייתון במבנה אדום וברור
