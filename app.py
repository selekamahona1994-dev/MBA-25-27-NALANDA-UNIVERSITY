import streamlit as st
import pandas as pd
import os
import pdfplumber
import base64
import zipfile
import shutil
from io import BytesIO
from datetime import datetime

# --- CONFIG ---
DB_FILE = "cv_database.csv"
SAVE_FOLDER = "cv_files"
ADMIN_PASSWORD = "admin123"

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# --- STUDENT DATABASE ---
STUDENT_DATA = {
    "040425001": {"name": "Stuti Mishra", "phone": "+916201494101", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425002": {"name": "Deepak Kumar", "phone": "+917488251470", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425004": {"name": "Claireshelmith MwendeMacharia", "phone": "+918434931097", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425005": {"name": "Shreya", "phone": "+919528388257", "school": "Management Studies", "year": "2025-2027"},
    "040425006": {"name": "Emmanuel Armah", "phone": "+233247802748", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425007": {"name": "Raghubir PrasadTharu", "phone": "+919120052250", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425008": {"name": "Arpita Dey", "phone": "+919831916200", "school": "Management Studies", "year": "2025-2027"},
    "040425010": {"name": "Sumit Kumar", "phone": "+919708839740", "school": "Management Studies", "year": "2025-2027"},
    "040425011": {"name": "Viraj Ranjan", "phone": "+917677901112", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425012": {"name": "Aman Kumar", "phone": "+918252108719", "school": "Management Studies", "year": "2025-2027"},
    "040425013": {"name": "Abhishek Kumar", "phone": "+917547015502", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425014": {"name": "Surbhi Mishra", "phone": "+9779806838945", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425015": {"name": "Daniel Bafan Tau", "phone": "+26771761784", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425016": {"name": "Belhadj Moussa Gabra", "phone": "+918434931544", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425017": {"name": "Bounthanom Santiphab", "phone": "+8562096320151", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425018": {"name": "Seleka Mahona Kisusi", "phone": "+255763971285", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425019": {"name": "Khine Thazin Thein", "phone": "+917584815507", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425029": {"name": "Prince Kumar Tiwari", "phone": "+9779824768000", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425031": {"name": "Krishna Kushwaha", "phone": "+919304722114", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425033": {"name": "Rajan Chaudhary", "phone": "+917257938005", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425030": {"name": "Raviranjan Kumar", "phone": "+918709164388", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425034": {"name": "Polash Kumar Deb", "phone": "+919365934294", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425035": {"name": "Yasudha Mukhia", "phone": "+97517711419", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425037": {"name": "Maikay Sandaroo", "phone": "+959977792380", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425039": {"name": "Manghku Sinram", "phone": "+959441937793", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425036": {"name": "Phyu Thar Tin Aung", "phone": "+959793384761", "school": "Management Studies",
                  "year": "2025-2027"},
    "040425038": {"name": "Zin Thin Oo", "phone": "+959448544961", "school": "Management Studies", "year": "2025-2027"},
}


# --- DETECTION ENGINE ---
def perform_detailed_audit(text):
    t = " ".join(text.lower().split())
    criteria = {
        "Personal Profile": ["profile", "summary", "objective", "about me", "career"],
        "Personal Details": ["nationality", "date of birth", "gender", "id number"],
        "Contact Info": ["email", "phone", "address", "contact"],
        "Language Proficiency": ["language", "english", "proficiency"],
        "Academic Qualification": ["academic", "education", "degree", "university"],
        "Professional Experience": ["experience", "employment", "work history"],
        "Technical Skills": ["computer", "software", "ict", "excel", "word"],
        "Referees": ["referees", "references"]
    }
    audit_results = {}
    found_count = 0
    for label, keywords in criteria.items():
        is_found = any(key in t for key in keywords)
        audit_results[label] = "✅ Found" if is_found else "❌ Missing"
        if is_found: found_count += 1
    score = int((found_count / len(criteria)) * 100)
    detailed_report = " | ".join([f"{k}: {v}" for k, v in audit_results.items()])
    return score, detailed_report


# --- HELPERS ---
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={'ID': str})
    return pd.DataFrame(columns=["Name", "ID", "Score", "Audit_Details", "Timestamp"])


def save_submission(u_name, u_id, u_file):
    path = os.path.join(SAVE_FOLDER, f"{u_id}.pdf")
    with open(path, "wb") as f:
        f.write(u_file.getbuffer())
    with pdfplumber.open(u_file) as pdf:
        raw_text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    score, details = perform_detailed_audit(raw_text)
    df = load_data()
    # Remove existing record if editing
    df = df[df['ID'] != u_id]
    new_row = pd.DataFrame([{"Name": u_name, "ID": u_id, "Score": score, "Audit_Details": details,
                             "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")}])
    pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False)


def delete_submission(u_id):
    df = load_data()
    df = df[df['ID'] != u_id]
    df.to_csv(DB_FILE, index=False)
    f_path = os.path.join(SAVE_FOLDER, f"{u_id}.pdf")
    if os.path.exists(f_path): os.remove(f_path)


def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# --- UI SETUP ---
st.set_page_config(page_title="SMS Nalanda CV Portal", layout="wide")

hide_style = """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- HEADER ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.info("Centered Logo (logo.png)")
st.markdown("<h2 style='text-align: center; color: #800000;'>School of Management Studies</h2>", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if 'verified_id' not in st.session_state: st.session_state.verified_id = None

tab1, tab2 = st.tabs(["📤 Student Submission", "🔒 Admin Dashboard"])

with tab1:
    if st.session_state.verified_id is None:
        st.subheader("Verify Student Identity")
        input_id = st.text_input("Enter Student ID to continue:")
        if st.button("Verify ID"):
            if input_id in STUDENT_DATA:
                st.session_state.verified_id = input_id
                st.rerun()
            else:
                st.error("Invalid Student ID. Please contact administration.")
    else:
        # User is Verified
        s_id = st.session_state.verified_id
        info = STUDENT_DATA[s_id]
        df = load_data()
        has_submitted = s_id in df['ID'].values

        # Information Display
        st.success(f"ID Verified: {s_id}. If this information is correct, you can upload your CV.")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"**Full Name:** {info['name']}")
            st.write(f"**Phone:** {info['phone']}")
        with col_b:
            st.write(f"**School:** {info['school']}")
            st.write(f"**Year:** {info['year']}")

        st.divider()

        if not has_submitted:
            # Upload Mode
            st.subheader("Upload Your CV")
            u_file = st.file_uploader("Select PDF File", type=['pdf'])
            if st.button("Submit CV"):
                if u_file:
                    save_submission(info['name'], s_id, u_file)
                    st.success("CV Submitted successfully!")
                    st.rerun()
                else:
                    st.error("Please select a file.")
        else:
            # Management Mode
            st.info("You have already submitted a CV. Choose an action below:")
            act_col1, act_col2, act_col3 = st.columns(3)

            with act_col1:
                if st.button("👁️ View My CV"):
                    st.session_state.view_cv = True
            with act_col2:
                if st.button("✏️ Edit / Re-upload"):
                    st.session_state.edit_mode = True
            with act_col3:
                if st.button("🗑️ Delete Submission", type="primary"):
                    delete_submission(s_id)
                    st.warning("Submission deleted.")
                    st.rerun()

            if st.session_state.get('edit_mode'):
                new_file = st.file_uploader("Upload New Version (PDF)", type=['pdf'])
                if st.button("Update CV"):
                    if new_file:
                        save_submission(info['name'], s_id, new_file)
                        st.session_state.edit_mode = False
                        st.success("CV Updated!")
                        st.rerun()

            if st.session_state.get('view_cv'):
                f_path = os.path.join(SAVE_FOLDER, f"{s_id}.pdf")
                display_pdf(f_path)
                if st.button("Close Preview"):
                    st.session_state.view_cv = False
                    st.rerun()

        if st.button("🔙 Return to First Page"):
            st.session_state.verified_id = None
            st.rerun()

with tab2:
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated:
        with st.form("admin_login"):
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if pw == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Wrong password.")
    else:
        st.subheader("Admin Dashboard")
        admin_df = load_data()
        st.dataframe(admin_df, use_container_width=True)
        if st.button("Logout Admin"):
            st.session_state.authenticated = False
            st.rerun()

# --- FOOTER ---
st.markdown("---")
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("""
    **QUICK LINKS**
    * [About Our Logo](#)
    * [Copyright & Privacy Policy](#)
    * [Academic Calendar](#)
    * [Events](#)
    * [Contact Us](#)
    """)
with f2:
    st.markdown("""
    **Admission Helpline**
    (Mon to Fri, 9:30 am to 6:30 pm IST)

    *For Students:*
    admission@nalandauniv.edu.in
    """)
with f3:
    st.markdown("""
    **Campus Address**
    Nalanda University
    Rajgir, Nalanda District
    Bihar 803 116
    nalanda@nalandauniv.edu.in
    """)
st.markdown("<p style='text-align: center; font-size: 12px;'>Copyright 2025-2026 © SMS NALANDA UNIVERSITY</p>",
            unsafe_allow_html=True)