import streamlit as st
import requests
import re
import os
from rapidfuzz import fuzz
from dotenv import load_dotenv

# 1. PAGE CONFIG & STYLING
st.set_page_config(page_title="Pension-Mitra AI", page_icon="👵", layout="centered")

# Load API Key from .env (Local) or Secrets (Streamlit Cloud)
load_dotenv()
API_KEY = os.getenv("SARVAM_API_KEY") or st.secrets.get("SARVAM_API_KEY", "")

# 2. HEADER
st.title("👵 Pension-Mitra: Sovereign AI Agent")
st.markdown("### മുതിർന്ന പൗരന്മാർക്കുള്ള ഡിജിറ്റൽ സഹായം")
st.info("Goal: Automated Document Verification & Mismatch Detection")

# 3. MALAYALAM VOICE INSTRUCTION (Simulated for Web)
if st.button("🔈 Play Instructions (Malayalam)"):
    # This represents the Voice-First nature of your project
    st.write("📢 *'ദയവായി നിങ്ങളുടെ ആധാർ കാർഡും പെൻഷൻ രേഖയും സ്കാൻ ചെയ്യുക.'*")
    st.caption("Voice instructions help senior citizens navigate without reading small text.")

st.divider()

# 4. DOCUMENT CAPTURE (Using Browser Camera)
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Aadhaar Card")
    aad_file = st.camera_input("Scan Aadhaar Front")

with col2:
    st.subheader("2. Pension Document")
    pen_file = st.camera_input("Scan PPO/Pension Record")

# 5. CORE LOGIC FUNCTIONS
def run_ocr(uploaded_file):
    if not API_KEY:
        return None
    url = "https://api.sarvam.ai/extract"
    headers = {"api-subscription-key": API_KEY}
    files = {'file': uploaded_file}
    data = {'feature': 'document-digitization', 'language_code': 'en-IN'}
    try:
        res = requests.post(url, headers=headers, files=files, data=data)
        if res.status_code == 200:
            return res.json().get('text', "").upper()
    except:
        return None
    return None

def extract_field(pattern, text):
    match = re.search(pattern, text)
    return match.group(1).strip() if match else "NOT FOUND"

# 6. VERIFICATION PROCESS
if st.button("🚀 RUN FULL VERIFICATION"):
    if aad_file and pen_file:
        with st.spinner("AI Analyzing Documents..."):
            # Step 1: Run OCR
            a_text = run_ocr(aad_file)
            p_text = run_ocr(pen_file)
            
            # Step 2: Fallback to Mock Data if OCR fails (For Demo Purposes)
            if not a_text or not p_text:
                st.warning("Using Demo Data for evaluation purposes.")
                a_text = "NAME: RAGHAVAN MK DOB: 01/02/1960 ACC: 99887766"
                p_text = "NAME: RAGHAVAN MK DOB: 01/03/1960 ACC: 90887766"

            # Step 3: Extract Data
            a_name = extract_field(r"NAME:\s*(.*?)(?=DOB|$)", a_text)
            p_name = extract_field(r"NAME:\s*(.*?)(?=DOB|$)", p_text)
            
            a_dob = extract_field(r"DOB:\s*(\d{2}/\d{2}/\d{4})", a_text)
            p_dob = extract_field(r"DOB:\s*(\d{2}/\d{2}/\d{4})", p_text)
            
            a_acc = extract_field(r"ACC:\s*(\d+)", a_text)
            p_acc = extract_field(r"ACC:\s*(\d+)", p_text)

            # Step 4: Comparison Logic
            mismatches = []
            if fuzz.ratio(a_name, p_name) < 90:
                mismatches.append(f"NAME: Aadhaar has '{a_name}', Pension has '{p_name}'")
            if a_dob != p_dob:
                mismatches.append(f"DOB: Aadhaar has '{a_dob}', Pension has '{p_dob}'")
            if a_acc != p_acc:
                mismatches.append(f"ACCOUNT: Aadhaar has '{a_acc}', Pension has '{p_acc}'")

            # 7. DISPLAY RESULTS
            st.divider()
            if not mismatches:
                st.balloons()
                st.success("✅ VERIFICATION SUCCESSFUL: Documents Match!")
                st.write("Data is ready to be synced with the Pension Portal.")
            else:
                st.error("⚠️ MISMATCHES DETECTED")
                for m in mismatches:
                    st.write(f"❌ {m}")
                
                # Correction Letter Generation
                st.subheader("📝 Generated Correction Letter")
                letter_text = f"""
To: The Bank Manager / Pension Officer
Subject: Request for Record Correction

I, {a_name}, am submitting this request to correct my official records. 
My Aadhaar documents verify my DOB as {a_dob}, while current pension records show {p_dob}. 
Please update my bank account information to match my Aadhaar-linked account ({a_acc}).

Sincerely,
{a_name}
                """
                st.text_area("Copy/Print Letter:", value=letter_text, height=200)
                st.info("Feature: This letter can be printed and submitted to the bank.")

    else:
        st.warning("Please scan both documents using the cameras above.")

# 8. FOOTER FOR INTERNSHIP PORTFOLIO
st.sidebar.title("About")
st.sidebar.info("Developed by Alan Shaju as a Sovereign AI solution for senior citizen accessibility.")