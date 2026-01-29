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


# --- HELPERS ---
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE, dtype={'ID': str})
    return pd.DataFrame(columns=["Name", "ID", "Score", "Audit_Details", "Timestamp"])


def save_data(df):
    df.to_csv(DB_FILE, index=False)


def display_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        # PDF Viewer + Download button fallback for Chrome
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        with open(file_path, "rb") as file:
            st.download_button(label="📥 Download CV for viewing", data=file, file_name=os.path.basename(file_path),
                               mime="application/pdf")
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")


def perform_detailed_audit(u_file):
    with pdfplumber.open(u_file) as pdf:
        text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    t = " ".join(text.lower().split())
    criteria = {
        "Personal Profile": ["profile", "summary", "objective", "about me"],
        "Contact Info": ["email", "phone", "address", "mobile"],
        "Academic Qualification": ["academic", "education", "degree", "university"],
        "Professional Experience": ["experience", "employment", "internship"],
        "Technical Skills": ["computer", "literacy", "software", "excel", "it"],
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


# --- UI SETUP ---
st.set_page_config(page_title="SMS Nalanda University CV Portal", layout="wide")

# CSS for hiding Streamlit elements
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stAppDeployButton {display: none;}
    .footer-col {font-size: 14px; line-height: 1.6;}
    .footer-title {font-weight: bold; color: #1f77b4; margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_l, col_m, col_r = st.columns([1, 1, 1])
with col_m:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.info("Logo Placeholder (logo.png not found)")
st.markdown("<h1 style='text-align: center;'>School of Management Studies</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>NALANDA UNIVERSITY</h4>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📤 Student Submission", "🔒 Admin Dashboard"])

# --- STUDENT SECTION ---
with tab1:
    if 'id_verified' not in st.session_state: st.session_state.id_verified = False
    if 'current_id' not in st.session_state: st.session_state.current_id = ""

    # Return to first page button
    if st.session_state.id_verified:
        if st.button("⬅️ Return to ID Verification Page"):
            st.session_state.id_verified = False
            st.rerun()

    if not st.session_state.id_verified:
        st.subheader("Step 1: Verify Identity")
        v_id = st.text_input("Please enter your Student ID to proceed")
        if st.button("Verify ID"):
            if v_id in STUDENT_DATA:
                st.session_state.id_verified = True
                st.session_state.current_id = v_id
                st.rerun()
            else:
                st.error("Invalid Student ID. Please check and try again.")
    else:
        # ID is verified, show Information and Upload/Actions
        sid = st.session_state.current_id
        s_info = STUDENT_DATA[sid]
        df = load_data()
        already_submitted = sid in df['ID'].values

        st.success(f"Hello, {s_info['name']}! Your identity is verified.")

        # Display Student Info
        with st.expander("📝 Your Information Details", expanded=True):
            st.write(f"**Full Name:** {s_info['name']}")
            st.write(f"**Phone Number:** {s_info['phone']}")
            st.write(f"**School:** {s_info['school']}")
            st.write(f"**Year of Studies:** {s_info['year']}")
            st.info("💡 If this information is correct, you can upload your CV below.")

        st.divider()

        if not already_submitted:
            st.subheader("📤 Upload your CV")
            u_file = st.file_uploader("Select PDF CV", type=['pdf'])
            if st.button("Submit CV"):
                if u_file:
                    # Process Upload
                    path = os.path.join(SAVE_FOLDER, f"{sid}.pdf")
                    with open(path, "wb") as f:
                        f.write(u_file.getbuffer())

                    score, details = perform_detailed_audit(u_file)
                    new_row = pd.DataFrame([{"Name": s_info['name'], "ID": sid, "Score": score,
                                             "Audit_Details": details,
                                             "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")}])
                    save_data(pd.concat([df, new_row], ignore_index=True))
                    st.success("✅ CV Submitted Successfully!")
                    st.rerun()
                else:
                    st.error("Please select a file.")
        else:
            # Action Menu if already submitted
            st.subheader("📂 Manage Your Submission")
            st.warning("You have already submitted a CV. Choose an action below:")

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("👁️ View Submitted CV"):
                    display_pdf(os.path.join(SAVE_FOLDER, f"{sid}.pdf"))
            with c2:
                # Edit functionality (re-upload)
                new_edit_file = st.file_uploader("Re-upload CV to Edit", type=['pdf'], key="edit_up")
                if st.button("Confirm Edit/Update"):
                    if new_edit_file:
                        path = os.path.join(SAVE_FOLDER, f"{sid}.pdf")
                        with open(path, "wb") as f: f.write(new_edit_file.getbuffer())
                        score, details = perform_detailed_audit(new_edit_file)
                        df.loc[df['ID'] == sid, ['Score', 'Audit_Details', 'Timestamp']] = [score, details,
                                                                                            datetime.now().strftime(
                                                                                                "%Y-%m-%d %H:%M")]
                        save_data(df)
                        st.success("CV Updated Successfully!")
                        st.rerun()
            with c3:
                if st.button("🗑️ Delete My CV"):
                    df = df[df['ID'] != sid]
                    save_data(df)
                    f_path = os.path.join(SAVE_FOLDER, f"{sid}.pdf")
                    if os.path.exists(f_path): os.remove(f_path)
                    st.success("Submission deleted. You can now upload again.")
                    st.rerun()

# --- ADMIN SECTION ---
with tab2:
    if "admin_auth" not in st.session_state: st.session_state.admin_auth = False
    if not st.session_state.admin_auth:
        with st.form("admin_login"):
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if pw == ADMIN_PASSWORD:
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("Wrong password")
    else:
        st.subheader("Admin Management Console")
        df_adm = load_data()
        if not df_adm.empty:
            # Add Action Link placeholder for the dataframe
            st.write("### Submitted Student Records")
            st.dataframe(df_adm, use_container_width=True)

            st.divider()
            st.write("### 🛠️ Global Actions")
            if st.button("🗑️ DELETE ALL DATA (Reset System)", type="primary"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                shutil.rmtree(SAVE_FOLDER)
                os.makedirs(SAVE_FOLDER)
                st.success("All documents and scores have been wiped.")
                st.rerun()

            # Individual CV Audit viewer
            sel_student = st.selectbox("Select Student to Audit/View", options=df_adm["Name"].tolist())
            if sel_student:
                row = df_adm[df_adm["Name"] == sel_student].iloc[-1]
                st.write(f"**Audit Score:** {row['Score']}%")
                st.info(f"**Audit Report:** {row['Audit_Details']}")
                display_pdf(os.path.join(SAVE_FOLDER, f"{row['ID']}.pdf"))
        else:
            st.info("No submissions found.")

# --- FOOTER SIDE ---
st.divider()
f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("""
    <div class="footer-col">
        <div class="footer-title">QUICK LINKS</div>
        • About Our Logo<br>
        • Copyright and Privacy Policy<br>
        • Academic Calendar<br>
        • Events<br>
        • Contact Us
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="footer-col">
        <div class="footer-title">ADMISSION HELPLINE</div>
        <i>(Monday to Friday, 9:30 am to 6:30 pm IST)</i><br><br>
        <b>For Students:</b><br>
        admission@nalandauniv.edu.in
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class="footer-col">
        <div class="footer-title">CAMPUS ADDRESS</div>
        Nalanda University<br>
        Rajgir, Nalanda District<br>
        Bihar 803 116<br>
        Email: nalanda@nalandauniv.edu.in
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><hr><p style='text-align: center;'>Copyright 2025-2026 © SMS NALANDA UNIVERSITY</p>",
            unsafe_allow_html=True)