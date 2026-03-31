import streamlit as st
import datetime
from database import create_tables, add_user, login_user, add_record, get_user_logs
from processor import extract_profile_text, generate_technical_modules, analyze_performance_data
from streamlit_mic_recorder import speech_to_text 

create_tables()
st.set_page_config(page_title="Ai Resume Builder", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0F19 !important; }
    
    /* Sidebar Visibility */
    [data-testid="stSidebar"] { background-color: #161B22 !important; border-right: 1px solid #1E293B; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }

    /* Upload Text & Labels (Visible Text Fix) */
    .stFileUploader label, .stSelectbox label, .stTextArea label, .stTextInput label {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    /* Final Report ( Black on White) */
    .performance-report {
        background-color: #FFFFFF !important;
        padding: 40px;
        border-radius: 12px;
        border: 4px solid #3B82F6;
    }
    .performance-report * { color: #000000 !important; }

    /* Question Display */
    .module-display {
        background-color: #1E293B !important;
        padding: 25px;
        border-radius: 12px;
        border-left: 10px solid #3B82F6;
        color: #FFFFFF !important;
        margin-bottom: 20px;
    }

    /* Buttons */
    .stButton>button { background: #3B82F6 !important; color: white !important; font-weight: bold !important; width: 100%; }
    .stTextArea textarea { background-color: #FFFFFF !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTICATION ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>AI<span style='color:#3B82F6;'>Resume Builder</span></h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        t1, t2 = st.tabs(["System Login", "Register Profile"])
        with t1:
            u_id = st.text_input("Username", key="l_u")
            p_id = st.text_input("Access Key", type="password", key="l_p")
            if st.button("LOG IN"):
                user = login_user(u_id, p_id)
                if user:
                    st.session_state.auth, st.session_state.uid, st.session_state.uname = True, user[0], user[1]
                    st.rerun()
        with t2:
            # Separated inputs to prevent unpack error
            nu = st.text_input("Create Username", key="r_u")
            np = st.text_input("Create Access Key", type="password", key="r_p")
            if st.button("ACTIVATE PROFILE"):
                if nu and np:
                    try: 
                        add_user(nu, np)
                        st.success("Account Created! Use Login Tab.")
                    except: st.error("Username already taken.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.subheader(f"User: {st.session_state.uname}")
    if st.button("Logout"): st.session_state.auth = False; st.rerun()
    st.divider()
    st.markdown("### History")
    for log in get_user_logs(st.session_state.uid):
        st.markdown(f'<div style="background:#1E293B; padding:10px; border-radius:8px; margin-bottom:8px; border:1px solid #3B82F6;"><b>{log[0]}</b><br>Score: {log[1]}</div>', unsafe_allow_html=True)

# --- WORKFLOW ---
if 'step' not in st.session_state: st.session_state.step = "init"
if 'q_ptr' not in st.session_state: st.session_state.q_ptr = 0
if 'transcript' not in st.session_state: st.session_state.transcript = ""

# THE FULL 22 LANGUAGE LIST
lang_options = {
    "Assamese": "as-IN", "Bengali": "bn-IN", "Bodo": "brx-IN", "Dogri": "doi-IN",
    "English": "en-US", "Gujarati": "gu-IN", "Hindi": "hi-IN", "Kannada": "kn-IN",
    "Kashmiri": "ks-IN", "Konkani": "gom-IN", "Maithili": "mai-IN", "Malayalam": "ml-IN",
    "Manipuri": "mni-IN", "Marathi": "mr-IN", "Nepali": "ne-NP", "Odia": "or-IN",
    "Punjabi": "pa-IN", "Sanskrit": "sa-IN", "Santali": "sat-IN", "Sindhi": "sd-IN",
    "Tamil": "ta-IN", "Telugu": "te-IN", "Urdu": "ur-IN"
}

if st.session_state.step == "init":
    st.markdown("### Configuration")
    target_lang = st.selectbox("Language Specification", sorted(lang_options.keys()))
    pdf_up = st.file_uploader("Upload Profile Documentation (PDF)", type="pdf")
    req_tx = st.text_area("Requirements Specification")
    
    if st.button("LAUNCH ASSESSMENT"):
        if pdf_up and req_tx:
            st.session_state.modules = generate_technical_modules(extract_profile_text(pdf_up), req_tx, target_lang)
            st.session_state.active_lang, st.session_state.step = target_lang, "running"
            st.rerun()

elif st.session_state.step == "running":
    curr_q = st.session_state.modules[st.session_state.q_ptr]
    st.markdown(f'<div class="module-display"><b>Module {st.session_state.q_ptr+1}:</b> {curr_q}</div>', unsafe_allow_html=True)

    v_rec = speech_to_text(language=lang_options.get(st.session_state.active_lang, "en-US"), start_prompt="🎤 Record", stop_prompt="🛑 Stop", key=f"v_{st.session_state.q_ptr}")
    if v_rec: st.session_state[f"tmp_{st.session_state.q_ptr}"] = v_rec

    ans_tx = st.text_area("Response Entry:", value=st.session_state.get(f"tmp_{st.session_state.q_ptr}", ""), key=f"t_{st.session_state.q_ptr}", height=150)

    if st.button("SUBMIT MODULE"):
        st.session_state.transcript += f"Q: {curr_q}\nA: {ans_tx}\n\n"
        if st.session_state.q_ptr < 2:
            st.session_state.q_ptr += 1
            st.rerun()
        else:
            st.session_state.step = "summary"
            st.rerun()

elif st.session_state.step == "summary":
    final_rep = analyze_performance_data(st.session_state.transcript, st.session_state.active_lang)
    
    score = "Processed"
    if "OVERALL_SCORE:" in final_rep:
        score = final_rep.split("OVERALL_SCORE:")[-1].strip()
    
    if 'is_saved' not in st.session_state:
        add_record(st.session_state.uid, st.session_state.active_lang, score, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        st.session_state.is_saved = True

    st.markdown(f"""
        <div class="performance-report">
            <h2 style="text-align:center;">PERFORMANCE EVALUATION SHEET</h2>
            <hr style="border:1px solid #000;">
            <div style="white-space: pre-wrap;">{final_rep}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("NEW ASSESSMENT"):
        for key in list(st.session_state.keys()): 
            if key not in ['auth', 'uid', 'uname']: del st.session_state[key]
        st.rerun()