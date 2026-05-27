
        print(e)

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
 
        client = genai.Client(api_key=st.secrets["[Credentials]"])
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
