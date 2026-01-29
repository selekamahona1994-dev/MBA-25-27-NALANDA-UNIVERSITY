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
# This dictionary stores the pre-filled information based on Student ID
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
        "Personal Profile": ["profile", "summary", "objective", "about me", "career", "biography", "statement"],
        "Personal Details": ["nationality", "date of birth", "gender", "marital status", "id number", "dob", "bio"],
        "Contact Info": ["email", "phone", "address", "contact", "cell", "telephone"],
        "Language Proficiency": ["language", "english", "swahili", "proficiency", "speak"],
        "Academic Qualification": ["academic", "education", "degree", "university", "school", "institution"],
        "Professional Experience": ["experience", "employment", "work history", "internship"],
        "Technical & Computer Literacy": ["computer", "literacy", "software", "ict", "digital", "excel", "word"],
        "Referees": ["referees", "references", "recommendation", "referee"]
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
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def create_zip_of_cvs(folder_path):
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".pdf"):
                    z.write(os.path.join(root, file), file)
    return buf.getvalue()


def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Name", "ID", "Score", "Audit_Details", "Timestamp"])


# --- UI SETUP ---
st.set_page_config(page_title="CV Management System", layout="wide")

# CSS to clean UI
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stAppDeployButton {display: none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- HEADER WITH LOGO ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    # Ensure logo.png is in the same directory as the script
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.info("Logo Placeholder (logo.png not found)")
st.markdown("<h2 style='text-align: center;'>School of Management Studies</h2>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📤 Student Submission", "🔒 Admin Dashboard"])

with tab1:
    st.info("### 📝 Instructions\nEnter your Student ID to auto-fill your details, then upload your PDF CV.")

    # Input for Student ID
    input_id = st.text_input("Enter Student ID (e.g., 040425001)")

    # Auto-fill Logic
    student_info = STUDENT_DATA.get(input_id, {"name": "", "phone": "", "school": "", "year": ""})

    with st.form("student_form", clear_on_submit=True):
        st.subheader("Your Information")
        # These fields auto-populate based on the ID entered above
        u_name = st.text_input("Full Name:", value=student_info["name"])
        u_phone = st.text_input("Phone Number:", value=student_info["phone"])
        u_school = st.text_input("School:", value=student_info["school"])
        u_year = st.text_input("Year of Studies:", value=student_info["year"])

        u_file = st.file_uploader("Upload CV (PDF)", type=['pdf'])

        submit = st.form_submit_button("Submit CV")

        if submit:
            if u_name and input_id and u_file:
                path = os.path.join(SAVE_FOLDER, f"{input_id}.pdf")
                with open(path, "wb") as f:
                    f.write(u_file.getbuffer())

                with pdfplumber.open(u_file) as pdf:
                    raw_text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])

                score, details = perform_detailed_audit(raw_text)
                df = load_data()
                new_row = pd.DataFrame([{"Name": u_name, "ID": input_id, "Score": score, "Audit_Details": details,
                                         "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")}])
                pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False)
                st.success(f"✅ CV for {u_name} received and audited!")
            else:
                st.error("⚠️ Please provide a valid ID and upload a PDF file.")

with tab2:
    if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        with st.form("login"):
            pw = st.text_input("Admin Password", type="password")
            if st.form_submit_button("Login"):
                if pw == ADMIN_PASSWORD:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Access Denied")
    else:
        st.subheader("Admin Audit Dashboard")
        df_admin = load_data()
        if not df_admin.empty:
            st.dataframe(df_admin, use_container_width=True)

            # Individual Viewer
            sel = st.selectbox("View Student CV", options=df_admin["Name"].tolist())
            rec = df_admin[df_admin["Name"] == sel].iloc[-1]

            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Audit Score", f"{rec['Score']}%")
                st.write("**Audit Details:**")
                st.write(rec['Audit_Details'].replace(" | ", "\n\n"))
            with c2:
                f_path = os.path.join(SAVE_FOLDER, f"{rec['ID']}.pdf")
                if os.path.exists(f_path): display_pdf(f_path)
        else:
            st.info("No records yet.")