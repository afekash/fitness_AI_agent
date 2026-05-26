import streamlit as st

# הגדרת כותרת האפליקציה ואייקון לשונית בדפדפן
st.set_page_config(page_title="FitAI Buddy", page_icon="💪", layout="wide")

st.title("💪 FitAI – סוכן הבריאות והכושר האישי שלך")
st.write("הממשק מוכן! בשלב הבא נחבר את ה-AI שינתח את מה שאת כותבת.")

# --- יצירת סרגל הצד (Sidebar) להגדרות ---
st.sidebar.title("🎯 הגדרות ויעדים")

# ------ כאן אנחנו מוסיפים את הפרופיל האישי החדש ------
st.sidebar.markdown("### 👤 פרופיל אישי")
gender = st.sidebar.selectbox("מגדר", ["אישה", "גבר"])
age = st.sidebar.number_input("גיל", min_value=10, max_value=100, value=22, step=1)
weight = st.sidebar.number_input("משקל נוכחי (ק״ג)", min_value=30.0, max_value=200.0, value=65.0, step=0.1)
height = st.sidebar.number_input("גובה (ס״מ)", min_value=100, max_value=250, value=170, step=1)

st.sidebar.markdown("---") # קו מפריד

# יעדים יומיים
st.sidebar.markdown("### 📅 יעדים יומיים")
calorie_target = st.sidebar.number_input("יעד קלוריות יומי", value=1800, step=50)
water_target = st.sidebar.number_input("יעד מים יומי (ליטרים)", value=2.5, step=0.5)

# --- משתני מערכת (Session State) לשמירת המדדים של המשתמש בזמן ריצה ---
if "current_calories" not in st.session_state:
    st.session_state.current_calories = 0
if "current_water" not in st.session_state:
    st.session_state.current_water = 0

# --- הצגת מדדי התקדמות (Progress Bars) במרכז המסך ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🍎 תזונה (קלוריות)")
    # תיקון: שימוש ב-calorie_target שהוגדר בסיידבר
    cal_progress = min(st.session_state.current_calories / calorie_target, 1.0) if calorie_target > 0 else 0.0
    st.progress(cal_progress)
    st.write(f"{st.session_state.current_calories} / {calorie_target} קק''ל")

with col2:
    st.subheader("💧 רוויה (מים)")
    # תיקון: שימוש ב-water_target שהוגדר בסיידבר
    water_progress = min(st.session_state.current_water / water_target, 1.0) if water_target > 0 else 0.0
    st.progress(water_progress)
    st.write(f"{st.session_state.current_water} / {water_target} ליטר")

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
