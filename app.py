import streamlit as st
import os
import re
from src.proposal_engine import ProposalEngine

# Page Configuration for Premium UI/UX
st.set_page_config(
    page_title="Apex Proposal Automation Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics and clean layouts
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 0.3rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin-bottom: 0.8rem;
    }
    .metric-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1F2937;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
""", unsafe_allow_html=True)

# Resolve DB paths dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
proposals_db = os.path.join(BASE_DIR, "data", "past_proposals.json")
emails_db = os.path.join(BASE_DIR, "data", "client_emails.json")

# Initialize proposal engine and cache it in session state
if "engine" not in st.session_state:
    st.session_state.engine = ProposalEngine(
        proposals_db_path=proposals_db,
        emails_db_path=emails_db
    )

engine = st.session_state.engine

# Sidebar Configuration
st.sidebar.markdown("### 🏢 APEX SALES AUTOMATION")
st.sidebar.markdown("---")

# API Key config
api_key_input = st.sidebar.text_input(
    "🔑 Gemini API Key (Optional)",
    value=os.environ.get("GEMINI_API_KEY", ""),
    type="password",
    help="Enter your Google Gemini API Key. If left blank, the app will fall back to high-fidelity local simulation mode."
)

# Set the API key in the engine
if api_key_input:
    engine.api_key = api_key_input
    import google.generativeai as genai
    genai.configure(api_key=api_key_input)
else:
    engine.api_key = None

st.sidebar.markdown("---")

# Preloaded client emails selection
st.sidebar.markdown("### 📥 Lead Qualification Inbox")
emails = engine.get_emails()
email_options = [f"{idx}. {e['sender_name']} ({e['company']})" for idx, e in enumerate(emails, 1)]
email_options.append("Write Custom Email...")

selected_option = st.sidebar.selectbox(
    "Select an incoming client email to load:",
    options=email_options,
    index=0
)

# Main Title Header
st.markdown('<div class="main-title">🤖 Sales Proposal Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Automated B2B Lead Qualification & Semantic Proposal Generation</div>', unsafe_allow_html=True)

# Determine prefilled email details
prefilled_body = ""
prefilled_sender = "Valued Customer"
prefilled_company = "Prospect Corporation"
prefilled_subject = "Custom Development Services"
prefilled_email = "client@prospect.com"

if selected_option != "Write Custom Email...":
    idx = int(selected_option.split(".")[0]) - 1
    selected_email_data = emails[idx]
    prefilled_body = selected_email_data["body"]
    prefilled_sender = selected_email_data["sender_name"]
    prefilled_company = selected_email_data["company"]
    prefilled_subject = selected_email_data["subject"]
    prefilled_email = selected_email_data["sender"]

# Set up form columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-header">1. Client Request Email</div>', unsafe_allow_html=True)
    
    # Metadata fields
    client_name = st.text_input("Client Contact Name", value=prefilled_sender)
    company_name = st.text_input("Company Name", value=prefilled_company)
    sender_email = st.text_input("Sender Email", value=prefilled_email)
    project_subject = st.text_input("Inquiry Subject Line", value=prefilled_subject)
    
    # Raw Email text area
    email_body = st.text_area(
        "Raw Email Contents",
        value=prefilled_body,
        height=320,
        help="Paste the raw client inquiry email here."
    )
    
    run_pipeline = st.button("🚀 Run Proposal Pipeline", type="primary", use_container_width=True)

# Keep track of states
if run_pipeline and email_body:
    # 1. Parse client details using regex/heuristics (and populate text fields)
    temp_email_dict = {
        "body": email_body,
        "sender_name": client_name,
        "company": company_name,
        "sender": sender_email,
        "subject": project_subject
    }
    details = engine.parse_client_details(temp_email_dict)
    
    # 2. Semantic matching against historical proposals DB
    matched_prop, match_score = engine.match_proposal(email_body)
    
    st.session_state.pipeline_run = {
        "details": details,
        "matched_prop": matched_prop,
        "match_score": match_score,
        "email_dict": temp_email_dict
    }

with col2:
    st.markdown('<div class="section-header">2. Ingestion & Analysis Results</div>', unsafe_allow_html=True)
    
    if "pipeline_run" in st.session_state:
        run_data = st.session_state.pipeline_run
        details = run_data["details"]
        matched_prop = run_data["matched_prop"]
        match_score = run_data["match_score"]
        
        # Display extracted parameters
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Extracted Budget</div>
                    <div class="metric-value">{details['extracted_budget']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Expected Timeline</div>
                    <div class="metric-value">{details['extracted_timeline']}</div>
                </div>
            """, unsafe_allow_html=True)
        with p_col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Best Historical Match</div>
                    <div class="metric-value">{matched_prop['title'] if matched_prop else 'None'}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Semantic Match Score</div>
                    <div class="metric-value">{match_score:.1%}</div>
                </div>
            """, unsafe_allow_html=True)
            
        if matched_prop:
            st.info(f"💡 matched with standard project configuration: **{matched_prop['category']}** (Base price: ${matched_prop['cost_usd']:,} USD)")
        else:
            st.warning("⚠️ No matching reference project found in the past proposals database.")
            
        # Step 3: Synthesis
        st.markdown('<div class="section-header">3. Synthesis Output</div>', unsafe_allow_html=True)
        
        with st.spinner("Synthesizing custom proposal..."):
            proposal_md, used_api = engine.generate_proposal(
                run_data["email_dict"],
                matched_prop,
                details
            )

        # Store in session state for proposal preview section below
        st.session_state.pipeline_run["proposal_md"] = proposal_md
            
        source = "Gemini 1.5 Flash API" if used_api else "High-Fidelity Local Simulator"
        st.success(f"✅ Proposal draft generated via **{source}**!")
        
        # Try to save locally (works on local machine, skipped gracefully on cloud)
        client_clean = details["company_name"].lower().replace(" ", "_")
        md_filename = f"proposal_{client_clean}.md"
        try:
            output_dir = os.path.join(BASE_DIR, "output")
            os.makedirs(output_dir, exist_ok=True)
            md_path = os.path.join(output_dir, md_filename)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(proposal_md)
        except OSError:
            pass  # Read-only filesystem on Streamlit Cloud — download button still works
        
        # Download button
        st.download_button(
            label="💾 Download Proposal (.md)",
            data=proposal_md,
            file_name=md_filename,
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.markdown("<p style='color: #6B7280; font-style: italic;'>Submit the client request on the left to see the ingestion, matching, and synthesis results here.</p>", unsafe_allow_html=True)

# Display Generated Proposal Preview below both columns
if "pipeline_run" in st.session_state and "proposal_md" in st.session_state.pipeline_run:
    st.markdown("---")
    st.markdown('<div class="section-header">4. Live Proposal Preview</div>', unsafe_allow_html=True)
    st.markdown(st.session_state.pipeline_run["proposal_md"])
