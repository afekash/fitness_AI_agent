

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
    url = st.secrets["[Credentials]"]
    key = st.secrets["[Credentials]"]
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
        # זה החלק החשוב - זה ידפיס את השגיאה המלאה למסך
        st.error(f"שגיאת Supabase מלאה: {e}")
        # נוסיף גם הדפסה ללוגים למקרה הצורך
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
