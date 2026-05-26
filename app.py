import streamlit as st

# הגדרת כותרת האפליקציה ואייקון לשונית בדפדפן
st.set_page_config(page_title="FitAI Buddy", page_icon="💪", layout="wide")

st.title("💪 FitAI – סוכן הבריאות והכושר האישי שלך")
st.write("הממשק מוכן! בשלב הבא נחבר את ה-AI שינתח את מה שאת כותבת.")

# --- יצירת סרגל הצד (Sidebar) להגדרות ---
st.sidebar.header("🎯 היעדים היומיים שלך")
target_calories = st.sidebar.number_input("יעד קלוריות יומי", value=2000, step=100)
target_water = st.sidebar.number_input("יעד מים יומי (מ''ל)", value=2500, step=250)

# --- משתני מערכת (Session State) לשמירת המדדים של המשתמש בזמן ריצה ---
if "current_calories" not in st.session_state:
    st.session_state.current_calories = 0
if "current_water" not in st.session_state:
    st.session_state.current_water = 0

# --- הצגת מדדי התקדמות (Progress Bars) במרכז המסך ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🍎 תזונה (קלוריות)")
    # חישוב אחוז ההתקדמות (ערך בין 0.0 ל-1.0 עבור הציור של המד)
    cal_progress = min(st.session_state.current_calories / target_calories, 1.0) if target_calories > 0 else 0.0
    st.progress(cal_progress)
    st.write(f"{st.session_state.current_calories} / {target_calories} קק''ל")

with col2:
    st.subheader("💧 רוויה (מים)")
    water_progress = min(st.session_state.current_water / target_water, 1.0) if target_water > 0 else 0.0
    st.progress(water_progress)
    st.write(f"{st.session_state.current_water} / {target_water} מ''ל")

# --- אזור הצ'אט ---
st.divider()
st.subheader("💬 דברי עם סוכן הכושר שלך")
user_input = st.chat_input("למשל: אכלתי עכשיו סלט יווני ושתיתי 2 כוסות מים...")

if user_input:
    # מציג את מה שהמשתמש כתב בצ'אט
    st.chat_message("user").write(user_input)
    
    # תגובה זמנית קבועה רק כדי לראות שהממשק מגיב
    with st.chat_message("assistant"):
        st.write("היי! הממשק שלנו עובד מעולה. בשלב הבא נחבר את ה-AI כדי שיפרק את המשפט שלך לקלוריות ומים אמיתיים! 😉")