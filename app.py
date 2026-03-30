"""
app.py — Main Streamlit UI & Orchestration for Big Red Group.
Now structured into Provider Onboarding and Listing Management pages.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from agents import run_onboarding_audit, ValidationResult
from utils import extract_and_detect_type

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Big Red Group — Partner Portal",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Header gradient */
    .main-header {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 50%, #7F1D1D 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(220, 38, 38, 0.25);
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.85);
        font-size: 1.05rem;
        margin: 0.5rem 0 0 0;
    }

    /* Cards */
    .result-card {
        background: linear-gradient(145deg, #1E1E2E, #2A2A3D);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    }
    .result-card h3 {
        color: #F1F5F9;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .result-card p, .result-card li {
        color: #CBD5E1;
        line-height: 1.7;
    }

    /* Compliance badges */
    .badge-pass {
        display: inline-block;
        background: linear-gradient(135deg, #059669, #10B981);
        color: #FFFFFF;
        padding: 0.4rem 1.2rem;
        border-radius: 999px;
        font-weight: 700;
    }
    .badge-fail {
        display: inline-block;
        background: linear-gradient(135deg, #DC2626, #EF4444);
        color: #FFFFFF;
        padding: 0.4rem 1.2rem;
        border-radius: 999px;
        font-weight: 700;
    }

    /* Sidebar Navigation */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1A2E 0%, #16213E 100%);
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
        color: #FFFFFF;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2.5rem;
        box-shadow: 0 4px 16px rgba(220, 38, 38, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🛡️ Big Red Group")
    st.markdown("### Partner Operations")
    
    selected_page = st.selectbox(
        "Navigation",
        ["Provider Onboarding", "Listing Management"],
        label_visibility="collapsed",
    )
    
    st.markdown("---")
    st.info("🤖 **Engine**: GPT-4o (Vision Enabled)")
    st.markdown("---")
    st.markdown(
        "<p style='color:#64748B; font-size:0.85rem;'>"
        "Self-Correction Portal v1.2<br>"
        "Powered by OpenAI GPT-4o"
        "</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Shared State for Navigation
# ---------------------------------------------------------------------------
if 'description' not in st.session_state:
    st.session_state.description = ""

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
header_subtitle = (
    "Compliance Audit & Insurance Verification" 
    if selected_page == "Provider Onboarding" 
    else "SEO Audit & Quality Control"
)

st.markdown(
    f"""
    <div class="main-header">
        <h1>🔴 Big Red Group — {selected_page}</h1>
        <p>{header_subtitle}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Page Logic: Provider Onboarding
# ---------------------------------------------------------------------------
if selected_page == "Provider Onboarding":
    col_l, col_r = st.columns([1, 1], gap="large")
    
    with col_l:
        st.markdown("### 📄 Insurance Certificate (PDF)")
        st.write("Upload your certificate of currency (Standard or Scanned).")
        uploaded_file = st.file_uploader(
            "Certificate Upload",
            type=["pdf"],
            label_visibility="collapsed",
        )
        
        if uploaded_file:
            st.success(f"📎 {uploaded_file.name} loaded.", icon="📄")

    with col_r:
        st.markdown("### 💡 What we audit")
        st.markdown(
            """
            - **Liability Amount**: Must be $\ge$ $10,000,000 AUD.
            - **Expiry Date**: Today's date is **2026-03-30**. Expired policies will be rejected.
            - **Insurance Type**: Must mentions 'Public Liability' or 'General Liability'.
            """
        )

    st.markdown("---")
    if st.button("🛡️ Verify Insurance Compliance", use_container_width=True):
        if not uploaded_file:
            st.error("Please upload an insurance PDF first.", icon="❌")
        else:
            with st.spinner("🤖 Extracting & Analyzing Policy..."):
                try:
                    file_bytes = uploaded_file.read()
                    ins_text, ins_images = extract_and_detect_type(file_bytes)
                    
                    if ins_images:
                        st.info("📸 No text layer found. Switching to **Vision OCR** fallback.", icon="🔎")
                    
                    # Call specialized insurance audit
                    from agents import run_insurance_audit
                    result: ValidationResult = run_insurance_audit(
                        insurance_text=ins_text,
                        insurance_images=ins_images,
                    )
                    
                    # Display Result
                    res_col_l, res_col_r = st.columns(2)
                    
                    with res_col_l:
                        badge = "badge-pass" if result.is_compliant else "badge-fail"
                        status = "✅ COMPLIANT" if result.is_compliant else "❌ NON-COMPLIANT"
                        st.markdown(
                            f"""
                            <div class="result-card">
                                <h3>Audit Status</h3>
                                <div style="text-align:center; padding:1rem;">
                                    <span class="{badge}">{status}</span>
                                </div>
                                <p><strong>Expiry Extracted:</strong> {result.insurance_expiry}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    
                    with res_col_r:
                        st.markdown(
                            f"""
                            <div class="result-card">
                                <h3>Reasoning</h3>
                                <p>{result.compliance_reasoning}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        
                    if result.missing_elements:
                        st.warning(f"⚠️ Missing Elements: {', '.join(result.missing_elements)}")

                except Exception as e:
                    st.error(f"Error: {e}")

# ---------------------------------------------------------------------------
# Page Logic: Listing Management
# ---------------------------------------------------------------------------
elif selected_page == "Listing Management":
    col_l, col_r = st.columns([1, 1], gap="large")
    
    with col_l:
        st.markdown("### 📝 Listing Description")
        st.session_state.description = st.text_area(
            "Paste description here",
            value=st.session_state.description,
            height=350,
            label_visibility="collapsed",
        )

    with col_r:
        st.markdown("### 💡 SEO Strategy")
        st.markdown(
            """
            - **Vibe**: Tone should be 'High-Octane' or 'Memorable'.
            - **Structure**: Must have 'What to expect' and 'What's included'.
            - **Formatting**: Use bullet points and clear sections.
            """
        )

    st.markdown("---")
    if st.button("🚀 Audit Listing SEO", use_container_width=True):
        if not st.session_state.description.strip():
            st.error("Please enter a listing description.", icon="❌")
        else:
            with st.spinner("🤖 Analyzing SEO & Tone..."):
                try:
                    from agents import run_seo_audit
                    result: ValidationResult = run_seo_audit(
                        description=st.session_state.description,
                    )
                    
                    res_col_l, res_col_r = st.columns(2)
                    
                    with res_col_l:
                        st.markdown(
                            f"""
                            <div class="result-card">
                                <h3>SEO Score</h3>
                                <div style="text-align:center; font-size:3rem; font-weight:800; color:#DC2626;">
                                    {result.seo_score}/100
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    
                    with res_col_r:
                        st.markdown(
                            f"""
                            <div class="result-card">
                                <h3>SEO Feedback</h3>
                                <p>{result.seo_feedback}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                except Exception as e:
                    st.error(f"Error: {e}")
