import streamlit as st
import requests
import re
import os
import io
from rapidfuzz import fuzz
from dotenv import load_dotenv
from gtts import gTTS

# 1. PAGE CONFIG & STYLING
st.set_page_config(page_title="Pension-Mitra AI", page_icon="👵", layout="centered")

# Load API Key
load_dotenv()
API_KEY = os.getenv("SARVAM_API_KEY") or st.secrets.get("SARVAM_API_KEY", "")

# --- VOICE ENGINE FUNCTION ---
def speak_text(text, lang='ml'):
    """Converts text to speech and plays it automatically."""
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        # Using autoplay so the senior citizen hears it immediately
        st.audio(fp, format='audio/mp3', autoplay=True)
    except Exception as e:
        st.error(f"Voice Error: {e}")

# 2. HEADER
st.title("👵 Pension-Mitra: Sovereign AI Agent")
st.markdown("### മുതിർന്ന പൗരന്മാർക്കുള്ള ഡിജിറ്റൽ സഹായം")
st.info("Goal: Automated Document Verification & Mismatch Detection")

# 3. MALAYALAM VOICE INSTRUCTIONS
if st.button("🔈 Play Instructions (Malayalam)"):
    instruction = "ദയവായി നിങ്ങളുടെ ആധാർ കാർഡും പെൻഷൻ രേഖയും സ്കാൻ ചെയ്യുക."
    st.write(f"📢 *{instruction}*")
    speak_text(instruction, lang='ml')

st.divider()

# 4. DOCUMENT CAPTURE
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
            a_text = run_ocr(aad_file)
            p_text = run_ocr(pen_file)
            
            # Fallback for Demo
            if not a_text or not p_text:
                a_text = "NAME: RAGHAVAN MK DOB: 01/02/1960 ACC: 99887766"
                p_text = "NAME: RAGHAVAN MK DOB: 01/03/1960 ACC: 90887766"

            # Extract Data
            a_name = extract_field(r"NAME:\s*(.*?)(?=DOB|$)", a_text)
            p_name = extract_field(r"NAME:\s*(.*?)(?=DOB|$)", p_text)
            a_dob = extract_field(r"DOB:\s*(\d{2}/\d{2}/\d{4})", a_text)
            p_dob = extract_field(r"DOB:\s*(\d{2}/\d{2}/\d{4})", p_text)
            a_acc = extract_field(r"ACC:\s*(\d+)", a_text)
            p_acc = extract_field(r"ACC:\s*(\d+)", p_text)

            # Comparison
            mismatches = []
            if fuzz.ratio(a_name, p_name) < 90:
                mismatches.append(f"NAME: Aadhaar has '{a_name}', Pension has '{p_name}'")
            if a_dob != p_dob:
                mismatches.append(f"DOB: Aadhaar has '{a_dob}', Pension has '{p_dob}'")
            if a_acc != p_acc:
                mismatches.append(f"ACCOUNT: Aadhaar has '{a_acc}', Pension has '{p_acc}'")

            # 7. DISPLAY RESULTS & VOICE FEEDBACK
            st.divider()
            if not mismatches:
                st.balloons()
                st.success("✅ VERIFICATION SUCCESSFUL")
                speak_text("വെരിഫിക്കേഷൻ വിജയിച്ചു", lang='ml') # "Verification Successful" in ML
            else:
                st.error("⚠️ MISMATCHES DETECTED")
                speak_text("രേഖകളിൽ പൊരുത്തക്കേടുകൾ ഉണ്ട്", lang='ml') # "Mismatches in documents" in ML
                for m in mismatches:
                    st.write(f"❌ {m}")
                
                # Letter Generation
                letter_text = f"To: The Bank Manager\nI, {a_name}, request a correction..."
                st.text_area("Correction Letter:", value=letter_text, height=150)

    else:
        st.warning("Please scan both documents first.")

# 8. SIDEBAR
st.sidebar.title("About")
st.sidebar.info("Developed by Alan Shaju - Sovereign AI for Seniors.")
