
import streamlit as st
from google import genai
import json
 
st.set_page_config(page_title="FitAI Buddy", page_icon="💪", layout="wide")
 
# --- CSS מותאם אישית ---
st.markdown("""
<style>
    /* כרטיס פרופיל */
    .profile-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 10px;
    }
    /* מדד קלוריות נטו */
    .net-calories {
        background: linear-gradient(135deg, #0f3460, #533483);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 10px 0;
    }
    .net-calories h2 {
        margin: 0;
        font-size: 2.5rem;
        color: white;
    }
    .net-calories p {
        margin: 4px 0 0;
        color: rgba(255,255,255,0.7);
        font-size: 0.85rem;
    }
    /* תגית SAVED */
    .saved-badge {
        background: #22c55e;
        color: white;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
 
st.title("💪 FitAI – סוכן הבריאות והכושר האישי שלך")
 
# =====================================================================
# SESSION STATE – אתחול
# =====================================================================
defaults = {
    "current_calories": 0,
    "current_protein": 0,
    "current_water": 0.0,
    "burned_calories": 0,       # קלוריות שנשרפו באימון
    "workout_minutes": 0,       # דקות אימון
    "chat_history": [],
    # פרופיל שמור
    "saved_gender": "גבר",
    "saved_age": 25,
    "saved_weight": 75.0,
    "saved_height": 175,
    "calorie_target": 2200,
    "protein_target": 150,
    "water_target": 3.0,
    "profile_saved": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
 
 
# =====================================================================
# פונקציה: חישוב יעדים לפי פרופיל (נוסחת Harris-Benedict)
# =====================================================================
def calculate_targets(gender, age, weight, height):
    """מחשב BMR ויעד קלוריות ביסיים לפי פרופיל."""
    if gender == "גבר":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    # רמת פעילות ממוצעת (1.55 = פעיל מדי)
    cal_target = int(bmr * 1.55)
    # 2 גרם חלבון לכל ק"ג
    prot_target = int(weight * 2)
    # מים: 35 מ"ל לכל ק"ג
    water_t = round(weight * 0.035, 1)
    return cal_target, prot_target, water_t
 
 
# =====================================================================
# סרגל צד – פרופיל + SAVE
# =====================================================================
st.sidebar.title("🎯 הגדרות ויעדים")
st.sidebar.markdown("### 👤 פרופיל אישי")
 
gender_input  = st.sidebar.selectbox("מגדר", ["גבר", "אישה"],
                    index=["גבר", "אישה"].index(st.session_state.saved_gender))
age_input     = st.sidebar.number_input("גיל", 10, 100, st.session_state.saved_age, 1)
weight_input  = st.sidebar.number_input("משקל (ק\"ג)", 30.0, 200.0, st.session_state.saved_weight, 0.1)
height_input  = st.sidebar.number_input("גובה (ס\"מ)", 100, 250, st.session_state.saved_height, 1)
 
# חישוב preview בזמן אמת
preview_cal, preview_prot, preview_water = calculate_targets(
    gender_input, age_input, weight_input, height_input
)
st.sidebar.info(
    f"📊 תצוגה מקדימה:\n"
    f"🔥 {preview_cal} קק\"ל | 🥩 {preview_prot}ג' | 💧 {preview_water}ל'"
)
 
if st.sidebar.button("💾 שמור פרופיל", use_container_width=True, type="primary"):
    st.session_state.saved_gender  = gender_input
    st.session_state.saved_age     = age_input
    st.session_state.saved_weight  = weight_input
    st.session_state.saved_height  = height_input
    st.session_state.calorie_target = preview_cal
    st.session_state.protein_target = preview_prot
    st.session_state.water_target   = preview_water
    st.session_state.profile_saved  = True
    st.rerun()
 
if st.session_state.profile_saved:
    st.sidebar.markdown(
        '<span class="saved-badge">✅ פרופיל נשמר!</span>', unsafe_allow_html=True
    )
    st.sidebar.caption(
        f"יעד קלוריות: **{st.session_state.calorie_target}** קק\"ל | "
        f"חלבון: **{st.session_state.protein_target}** ג'"
    )
 
st.sidebar.markdown("---")
 
# =====================================================================
# סרגל צד – אפס נתוני יום
# =====================================================================
if st.sidebar.button("🔄 אפס נתוני היום", use_container_width=True):
    for key in ("current_calories","current_protein","current_water",
                "burned_calories","workout_minutes","chat_history"):
        st.session_state[key] = 0 if key != "current_water" else 0.0
        if key == "chat_history":
            st.session_state[key] = []
    st.rerun()
 
# =====================================================================
# גוף ראשי – מדדים
# =====================================================================
 
# -- קלוריות נטו (מה שנאכל פחות מה שנשרף) --
net_cal = st.session_state.current_calories - st.session_state.burned_calories
remaining = st.session_state.calorie_target - net_cal
color_net = "#22c55e" if remaining >= 0 else "#ef4444"
 
st.markdown(f"""
<div class="net-calories">
    <p>קלוריות נטו היום</p>
    <h2 style="color:{color_net}">{net_cal:,}</h2>
    <p>{"נותרו" if remaining >= 0 else "חרגת ב"} {abs(remaining):,} קק"ל מהיעד ({st.session_state.calorie_target:,})</p>
</div>
""", unsafe_allow_html=True)
 
col1, col2, col3, col4 = st.columns(4)
 
with col1:
    st.subheader("🍎 קלוריות שנאכלו")
    cal_t = st.session_state.calorie_target
    cal_p = min(st.session_state.current_calories / cal_t, 1.0) if cal_t > 0 else 0.0
    st.progress(cal_p)
    st.write(f"{st.session_state.current_calories:,} / {cal_t:,} קק\"ל")
 
with col2:
    st.subheader("🔥 קלוריות נשרפות")
    # מציגים כמה שרפת ביחס ל-800 (מקסימום ויזואלי)
    burn_max = 800
    burn_p = min(st.session_state.burned_calories / burn_max, 1.0)
    st.progress(burn_p)
    st.write(f"{st.session_state.burned_calories} קק\"ל נשרפו ({st.session_state.workout_minutes} דק')")
 
with col3:
    st.subheader("🥩 חלבון")
    prot_t = st.session_state.protein_target
    prot_p = min(st.session_state.current_protein / prot_t, 1.0) if prot_t > 0 else 0.0
    st.progress(prot_p)
    st.write(f"{st.session_state.current_protein} / {prot_t} ג'")
 
with col4:
    st.subheader("💧 מים")
    water_t = st.session_state.water_target
    water_p = min(st.session_state.current_water / water_t, 1.0) if water_t > 0 else 0.0
    st.progress(water_p)
    st.write(f"{st.session_state.current_water:.1f} / {water_t:.1f} ל'")
 
st.divider()
 
# =====================================================================
# צ'אט
# =====================================================================
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
 
user_input = st.chat_input(
    "למשל: אכלתי 2 ביצים וקוטג׳, שתיתי כוס מים, רצתי 30 דקות..."
)
 
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
 
    system_instruction = f"""
אתה מאמן כושר ותזונאי אישי חכם ומקצועי.
המשתמש: {st.session_state.saved_gender}, גיל {st.session_state.saved_age},
משקל {st.session_state.saved_weight} ק"ג, גובה {st.session_state.saved_height} ס"מ.
 
נתח את ההודעה: מה אכל/שתה/אילו אימונים עשה.
אם מוזכר אימון (ריצה/אופניים/כוח/שחייה וכו') – חשב קלוריות שנשרפו ודקות אימון.
 
החזר אך ורק JSON תקין במבנה הבא:
{{
    "response": "תגובה קצרה ומעודדת בעברית (מקסימום 2 משפטים)",
    "added_calories": קלוריות שנאכלו (מספר שלם, 0 אם לא אכל),
    "added_protein": גרמי חלבון (מספר שלם, 0 אם אין),
    "added_water": ליטרים (עשרוני, 0.0 אם לא שתה),
    "burned_calories": קלוריות שנשרפו באימון (מספר שלם, 0 אם לא אמן),
    "workout_minutes": דקות אימון (מספר שלם, 0 אם לא אמן)
}}
"""
 
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
 
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_input,
            config={
                'system_instruction': system_instruction,
                'response_mime_type': 'application/json'
            }
        )
 
        result = json.loads(response.text.strip())
 
        st.session_state.current_calories  += int(result.get("added_calories", 0))
        st.session_state.current_protein   += int(result.get("added_protein", 0))
        st.session_state.current_water     += float(result.get("added_water", 0.0))
        st.session_state.burned_calories   += int(result.get("burned_calories", 0))
        st.session_state.workout_minutes   += int(result.get("workout_minutes", 0))
 
        ai_response = result.get("response", "הנתונים עודכנו בהצלחה!")
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
 
        st.rerun()
 
    except Exception as e:
        st.error("שגיאה בתקשורת עם ה-AI:")
        st.exception(e)
