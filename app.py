
import streamlit as st
from google import genai
from supabase import create_client, Client
import json
from datetime import date
 
st.set_page_config(page_title="FitAI Buddy", page_icon="💪", layout="wide")
 
# =====================================================================
# SUPABASE – חיבור
# =====================================================================
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
 
supabase = get_supabase()
 
# =====================================================================
# DB FUNCTIONS
# =====================================================================
def load_profile():
    res = supabase.table("profile").select("*").eq("id", 1).execute()
    return res.data[0] if res.data else None
 
def save_profile_db(gender, age, weight, height, cal_t, prot_t, water_t):
    data = {
        "id": 1,
        "gender": gender,
        "age": age,
        "weight": weight,
        "height": height,
        "cal_target": cal_t,
        "prot_target": prot_t,
        "water_target": water_t,
    }
 
    try:
        supabase.table("profile").upsert(data).execute()
        st.success("הפרופיל נשמר!")
    except Exception as e:
        st.error(f"שגיאת Supabase מלאה: {e}")
        print(e)
 
def save_today_log(calories_in, burned, protein, water, workout_min, weight):
    today = date.today().isoformat()
    net   = calories_in - burned
    data  = {
        "log_date":       today,
        "calories_in":    calories_in,
        "calories_burned": burned,
        "net_calories":   net,
        "protein":        protein,
        "water":          float(water),
        "workout_min":    workout_min,
        "weight":         float(weight),
    }
    # בדיקה אם כבר קיימת שורה להיום
    existing = supabase.table("daily_log").select("id").eq("log_date", today).execute()
    if existing.data:
        supabase.table("daily_log").update(data).eq("log_date", today).execute()
    else:
        supabase.table("daily_log").insert(data).execute()
 
def load_history(days=30):
    res = supabase.table("daily_log") \
        .select("*") \
        .order("log_date", desc=True) \
        .limit(days) \
        .execute()
    return res.data  # רשימת dict-ים
 
# =====================================================================
# CSS
# =====================================================================
st.markdown("""
<style>
    .net-calories {
        background: linear-gradient(135deg, #0f3460, #533483);
        border-radius: 12px; padding: 16px;
        text-align: center; margin: 10px 0;
    }
    .net-calories h2 { margin: 0; font-size: 2.5rem; color: white; }
    .net-calories p  { margin: 4px 0 0; color: rgba(255,255,255,0.7); font-size: 0.85rem; }
    .saved-badge {
        background: #22c55e; color: white;
        border-radius: 20px; padding: 4px 14px;
        font-size: 0.8rem; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
 
st.title("💪 FitAI – סוכן הבריאות והכושר האישי שלך")
 
# =====================================================================
# SESSION STATE
# =====================================================================
defaults = {
    "current_calories": 0,
    "current_protein":  0,
    "current_water":    0.0,
    "burned_calories":  0,
    "workout_minutes":  0,
    "chat_history":     [],
    "saved_gender":     "גבר",
    "saved_age":        25,
    "saved_weight":     75.0,
    "saved_height":     175,
    "calorie_target":   2200,
    "protein_target":   150,
    "water_target":     3.0,
    "profile_saved":    False,
    "db_loaded":        False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
 
# טעינת פרופיל מ-Supabase בפעם הראשונה
if not st.session_state.db_loaded:
    row = load_profile()
    if row:
        st.session_state.saved_gender   = str(row["gender"])
        st.session_state.saved_age      = int(row["age"])
        st.session_state.saved_weight   = float(row["weight"])
        st.session_state.saved_height   = int(row["height"])
        st.session_state.calorie_target = int(row["cal_target"])
        st.session_state.protein_target = int(row["prot_target"])
        st.session_state.water_target   = float(row["water_target"])
        st.session_state.profile_saved  = True
    st.session_state.db_loaded = True
 
# =====================================================================
# פונקציה: חישוב יעדים (Harris-Benedict)
# =====================================================================
def calculate_targets(gender, age, weight, height):
    bmr = (10*weight + 6.25*height - 5*age + 5) if gender == "גבר" \
          else (10*weight + 6.25*height - 5*age - 161)
    return int(bmr * 1.55), int(weight * 2), round(weight * 0.035, 1)
 
# =====================================================================
# SIDEBAR – פרופיל
# =====================================================================
st.sidebar.title("🎯 הגדרות ויעדים")
st.sidebar.markdown("### 👤 פרופיל אישי")
 
gender_input = st.sidebar.selectbox("מגדר", ["גבר", "אישה"],
                   index=["גבר","אישה"].index(st.session_state.saved_gender))
age_input    = st.sidebar.number_input("גיל", 10, 100, st.session_state.saved_age, 1)
weight_input = st.sidebar.number_input('משקל (ק"ג)', 30.0, 200.0, st.session_state.saved_weight, 0.1)
height_input = st.sidebar.number_input('גובה (ס"מ)', 100, 250, st.session_state.saved_height, 1)
 
preview_cal, preview_prot, preview_water = calculate_targets(
    gender_input, age_input, weight_input, height_input)
st.sidebar.info(f"📊 תצוגה מקדימה:\n🔥 {preview_cal} קק\"ל | 🥩 {preview_prot}ג' | 💧 {preview_water}ל'")
 
if st.sidebar.button("💾 שמור פרופיל", use_container_width=True, type="primary"):
    st.session_state.saved_gender   = gender_input
    st.session_state.saved_age      = age_input
    st.session_state.saved_weight   = weight_input
    st.session_state.saved_height   = height_input
    st.session_state.calorie_target = preview_cal
    st.session_state.protein_target = preview_prot
    st.session_state.water_target   = preview_water
    st.session_state.profile_saved  = True
    save_profile_db(gender_input, age_input, weight_input, height_input,
                    preview_cal, preview_prot, preview_water)
    st.rerun()
 
if st.session_state.profile_saved:
    st.sidebar.markdown('<span class="saved-badge">✅ פרופיל נשמר!</span>', unsafe_allow_html=True)
 
st.sidebar.markdown("---")
 
# =====================================================================
# SIDEBAR – שמירה ואיפוס
# =====================================================================
st.sidebar.markdown("### 📅 יומן")
 
if st.sidebar.button("💿 שמור נתוני היום", use_container_width=True, type="primary"):
    save_today_log(
        st.session_state.current_calories,
        st.session_state.burned_calories,
        st.session_state.current_protein,
        st.session_state.current_water,
        st.session_state.workout_minutes,
        st.session_state.saved_weight,
    )
    st.sidebar.success(f"✅ נשמר ל-{date.today().isoformat()}")
 
if st.sidebar.button("🔄 אפס נתוני היום", use_container_width=True):
    for k in ("current_calories","current_protein","burned_calories","workout_minutes"):
        st.session_state[k] = 0
    st.session_state.current_water = 0.0
    st.session_state.chat_history  = []
    st.rerun()
 
# =====================================================================
# TABS
# =====================================================================
tab_today, tab_history = st.tabs(["📊 היום", "📈 היסטוריה"])
 
# ------------------------------------------------------------------
with tab_today:
 
    net_cal   = st.session_state.current_calories - st.session_state.burned_calories
    remaining = st.session_state.calorie_target - net_cal
    color_net = "#22c55e" if remaining >= 0 else "#ef4444"
 
    st.markdown(f"""
    <div class="net-calories">
        <p>קלוריות נטו היום · {date.today().strftime('%d/%m/%Y')}</p>
        <h2 style="color:{color_net}">{net_cal:,}</h2>
        <p>{"נותרו" if remaining >= 0 else "חרגת ב"} {abs(remaining):,} קק"ל מהיעד ({st.session_state.calorie_target:,})</p>
    </div>
    """, unsafe_allow_html=True)
 
    c1, c2, c3, c4 = st.columns(4)
    cal_t   = st.session_state.calorie_target
    prot_t  = st.session_state.protein_target
    water_t = st.session_state.water_target
 
    with c1:
        st.subheader("🍎 קלוריות שנאכלו")
        st.progress(min(st.session_state.current_calories / cal_t, 1.0) if cal_t else 0)
        st.write(f"{st.session_state.current_calories:,} / {cal_t:,} קק\"ל")
 
    with c2:
        st.subheader("🔥 קלוריות נשרפות")
        st.progress(min(st.session_state.burned_calories / 800, 1.0))
        st.write(f"{st.session_state.burned_calories} קק\"ל ({st.session_state.workout_minutes} דק')")
 
    with c3:
        st.subheader("🥩 חלבון")
        st.progress(min(st.session_state.current_protein / prot_t, 1.0) if prot_t else 0)
        st.write(f"{st.session_state.current_protein} / {prot_t} ג'")
 
    with c4:
        st.subheader("💧 מים")
        st.progress(min(st.session_state.current_water / water_t, 1.0) if water_t else 0)
        st.write(f"{st.session_state.current_water:.1f} / {water_t:.1f} ל'")
 
    st.divider()
 
    # צ'אט
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
 
    user_input = st.chat_input("למשל: אכלתי 2 ביצים וקוטג׳, שתיתי כוס מים, רצתי 30 דקות...")
 
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
 
        system_instruction = f"""
אתה מאמן כושר ותזונאי אישי חכם ומקצועי.
המשתמש: {st.session_state.saved_gender}, גיל {st.session_state.saved_age},
משקל {st.session_state.saved_weight} ק"ג, גובה {st.session_state.saved_height} ס"מ.
נתח את ההודעה: מה אכל/שתה/אילו אימונים עשה.
אם מוזכר אימון – חשב קלוריות שנשרפו ודקות אימון.
החזר אך ורק JSON תקין:
{{
    "response": "תגובה קצרה ומעודדת בעברית",
    "added_calories": מספר שלם,
    "added_protein":  מספר שלם,
    "added_water":    מספר עשרוני,
    "burned_calories": מספר שלם,
    "workout_minutes": מספר שלם
}}"""
 
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_input,
                config={'system_instruction': system_instruction,
                        'response_mime_type': 'application/json'}
            )
            result = json.loads(response.text.strip())
 
            st.session_state.current_calories  += int(result.get("added_calories", 0))
            st.session_state.current_protein   += int(result.get("added_protein", 0))
            st.session_state.current_water     += float(result.get("added_water", 0.0))
            st.session_state.burned_calories   += int(result.get("burned_calories", 0))
            st.session_state.workout_minutes   += int(result.get("workout_minutes", 0))
 
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result.get("response", "הנתונים עודכנו!")
            })
 
            save_today_log(
                st.session_state.current_calories,
                st.session_state.burned_calories,
                st.session_state.current_protein,
                st.session_state.current_water,
                st.session_state.workout_minutes,
                st.session_state.saved_weight,
            )
            st.rerun()
 
        except Exception as e:
            st.error("שגיאה בתקשורת עם ה-AI:")
            st.exception(e)
 
# ------------------------------------------------------------------
with tab_history:
    st.subheader("📈 היסטוריית 30 ימים אחרונים")
 
    rows = load_history(30)
 
    if not rows:
        st.info("עדיין אין נתונים היסטוריים. התחילי לתעד!")
    else:
        import pandas as pd
 
        df = pd.DataFrame(rows)
        df["log_date"] = pd.to_datetime(df["log_date"])
        df = df.sort_values("log_date")
 
        # סיכום מהיר
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("ממוצע קלוריות נטו/יום", f"{int(df['net_calories'].mean()):,}")
        with s2:
            st.metric("ממוצע שריפה/יום", f"{int(df['calories_burned'].mean()):,} קק\"ל")
        with s3:
            st.metric("ממוצע חלבון/יום", f"{int(df['protein'].mean())} ג'")
        with s4:
            st.metric("סה\"כ דקות אימון", f"{int(df['workout_min'].sum())} דק'")
 
        st.divider()
 
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**🔥 קלוריות נאכלו vs נשרפו**")
            st.line_chart(df[["log_date","calories_in","calories_burned"]].set_index("log_date").rename(
                columns={"calories_in":"נאכלו","calories_burned":"נשרפו"}))
        with col_g2:
            st.markdown("**⚖️ קלוריות נטו יומי**")
            st.bar_chart(df[["log_date","net_calories"]].set_index("log_date").rename(
                columns={"net_calories":"נטו"}))
 
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            st.markdown("**🥩 חלבון יומי**")
            st.line_chart(df[["log_date","protein"]].set_index("log_date").rename(
                columns={"protein":"חלבון (ג')"}))
        with col_g4:
            st.markdown("**🏃 דקות אימון יומי**")
            st.bar_chart(df[["log_date","workout_min"]].set_index("log_date").rename(
                columns={"workout_min":"דקות"}))
 
        st.divider()
 
        # טבלה מפורטת
        st.markdown("**📋 טבלה מלאה**")
        df_table = df.sort_values("log_date", ascending=False).copy()
        df_table["log_date"] = df_table["log_date"].dt.strftime("%d/%m/%Y")
        df_table = df_table.rename(columns={
            "log_date":"תאריך", "calories_in":'קק"ל נאכלו',
            "calories_burned":'קק"ל נשרפו', "net_calories":"נטו",
            "protein":"חלבון (ג')", "water":"מים (ל')",
            "workout_min":"אימון (דק')", "weight":'משקל (ק"ג)'
        })
        cols_show = ["תאריך",'קק"ל נאכלו','קק"ל נשרפו',"נטו","חלבון (ג')","מים (ל')","אימון (דק')",'משקל (ק"ג)']
        st.dataframe(df_table[cols_show], use_container_width=True, hide_index=True)
 
        csv = df_table[cols_show].to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ ייצא ל-CSV", csv, "fitai_history.csv", "text/csv")
