import streamlit as st
import subprocess
import json
import os
from pypdf import PdfReader

# --- Page Config ---
st.set_page_config(
    page_title="DebugSteller",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Session State Initialization ---
if 'execution_done' not in st.session_state:
    st.session_state.execution_done = False

# --- Custom CSS (The "Hackathon Winning" Look) ---
st.markdown("""
<style>
    /* Hide Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    /* Modern Fonts */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Code Editor Font */
    .stTextArea textarea {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }
    .stCode {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }
    
    /* Gradient Header */
    .gradient-text {
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    /* Custom Button Styling */
    div.stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #FF2B2B;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }
    
    /* Hide Anchor Links */
    .css-15zrgzn {display: none;}
    .css-10trblm {display: none;}
    a.anchor-link {display: none;}
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def parse_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error parsing PDF: {e}")
        return None

def run_debugger(code_content, description=None):
    # Save to temp file
    with open("temp_source.py", "w") as f:
        f.write(code_content)
    
    # Build command
    cmd = ["python3", "main.py", "temp_source.py", "--model", "qwen2.5-coder:7b"]
    
    # Add description if provided
    if description and description.strip():
        cmd.extend(["--description", description.strip()])
    
    # Run backend
    with st.spinner("Debugging & Optimizing... (This may take a minute)"):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            return result
        except Exception as e:
            st.error(f"Execution Error: {e}")
            return None

def load_report():
    if os.path.exists("debug_report.json"):
        with open("debug_report.json", "r") as f:
            return json.load(f)
    return None

# --- Header ---
st.markdown('<h1 class="gradient-text">DebugSteller</h1>', unsafe_allow_html=True)
st.markdown("### AI-Powered Autonomous Debugging & Optimization Engine")
st.markdown("---")

left_col, right_col = st.columns([1, 1], gap="large")

# --- Left Column: Input ---
with left_col:
    st.subheader("Input Zone")
    
    input_method = st.radio("Source", ["Paste Code", "Upload File"], horizontal=True, label_visibility="collapsed")
    
    code_input = ""
    
    if input_method == "Paste Code":
        code_input = st.text_area(
            "Code Editor", 
            height=400, 
            placeholder="Paste your buggy Python code here... (e.g., a function that crashes or gives wrong output)"
        )
    else:
        uploaded_file = st.file_uploader("Upload .py or .pdf", type=["py", "pdf"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".pdf"):
                code_input = parse_pdf(uploaded_file)
                if code_input:
                    st.info("Extracted text from PDF. Please verify code structure below.")
                    code_input = st.text_area("Extracted Code", value=code_input, height=300)
            else:
                # .py file
                stringio = uploaded_file.getvalue().decode("utf-8")
                code_input = st.text_area("File Content", value=stringio, height=300)

    # Bug Description Input
    st.markdown("### Bug Description (Optional)")
    bug_description = st.text_input(
        "Describe the issue", 
        placeholder='e.g., "Output should be ..."',
        label_visibility="collapsed"
    )
    
    st.markdown("###") # Spacer
    run_btn = st.button("Run Debugger", type="primary")
    
    # Handle button click
    if run_btn and code_input:
        result = run_debugger(code_input, bug_description)
        if result:
            st.session_state.execution_done = True
            st.rerun()

# --- Right Column: Output ---
with right_col:
    st.subheader("Output Zone")
    
    # Only show results if execution was done in this session
    if st.session_state.execution_done:
        report = load_report()
        
        if report:
            tab1, tab2, tab3 = st.tabs(["Code Diff", "Analysis & Insights", "Raw Trace"])
            
            with tab1:
                st.caption("Original vs. Fixed Code")
                col_orig, col_fixed = st.columns(2)
                with col_orig:
                    st.markdown("**Original**")
                    st.code(report.get("original_code", ""), language="python")
                with col_fixed:
                    st.markdown("**Fixed/Optimized**")
                    st.code(report.get("repaired_code", ""), language="python")
            
            with tab2:
                st.caption("Optimization & Educational Notes")
                
                traces = report.get("traces", [])
                opt_report = report.get("optimization_report")
                original_code = report.get("original_code", "").strip()
                repaired_code = report.get("repaired_code", "").strip()
                
                # Check for Rejection (Scenario A)
                rejected_trace = next((t for t in traces if "Rejected" in t.get("status", "") or "REJECTED" in t.get("status", "").upper()), None)
                
                if rejected_trace:
                    # Scenario A: Optimization Rejected
                    st.error("🔴 Optimization Rejected by Safety Guard")
                    
                    full_reason = rejected_trace.get("status", "").replace("Rejected: ", "")
                    
                    # Attempt to split traceback for better readability
                    if "Traceback" in full_reason:
                        summary, traceback_part = full_reason.split("Traceback", 1)
                        st.markdown(f"**Reason:** {summary.strip()}")
                        st.markdown("🚨 **Traceback (Error in LLM Patch):**")
                        st.code(f"Traceback{traceback_part}", language="bash")
                    else:
                        st.markdown(f"**Reason:** {full_reason}")
                    
                    st.markdown("**Detailed Summary:** The system detected that the optimized code produced different output/side-effects than the original. The optimization was discarded to ensure correctness.")
                    
                    st.markdown("---")
                    st.markdown("### Final Code")
                    st.caption("ℹ️ The code below is the **Original, Unmodified Code** saved after the rejection.")
                    st.code(repaired_code, language="python")
                    
                elif original_code == repaired_code:
                    # Scenario B: Code Already Optimal (No Change)
                    st.info("✨ Code Already Optimal")
                    st.markdown("No logic changes were needed. The code is already efficient.")
                    
                    st.markdown("### Final Code")
                    st.code(repaired_code, language="python")
                    
                else:
                    # Scenario C: Code Changed
                    # Check if it's optimization or logic repair
                    is_optimization = False
                    if opt_report:
                        changes = opt_report.get("changes_summary", [])
                        changes_text = " ".join(changes).lower()
                        if "complexity" in changes_text or "o(n" in changes_text:
                            is_optimization = True
                    
                    # Check traces for logic repair
                    logic_repair_trace = next((t for t in traces if "Logic Repair" in t.get("error_type", "")), None)
                    
                    if is_optimization:
                        st.success("🚀 Optimization Applied")
                        if opt_report:
                            orig_comp = opt_report.get('original_complexity', '')
                            opt_comp = opt_report.get('optimized_complexity', '')
                            
                            if orig_comp and opt_comp and orig_comp != opt_comp:
                                st.markdown(f"**Complexity Improvement:** `{orig_comp}` ➝ `{opt_comp}`")
                            
                            changes = opt_report.get("changes_summary", [])
                            if changes:
                                with st.expander("Detailed Improvements", expanded=True):
                                    for change in changes:
                                        st.markdown(f"- {change}")
                    else:
                        st.success("🚀 Refactoring & Logic Repair Complete")
                        st.markdown("Code improvements and bug fixes were applied successfully.")

                    st.markdown("### Final Code")
                    st.code(repaired_code, language="python")

            with tab3:
                st.caption("Execution Trace")
                traces = report.get("traces", [])
                for trace in traces:
                    status_icon = "✅" if trace.get("success") else "❌"
                    status_text = trace.get("status", "Attempted")
                    
                    with st.expander(f"{status_icon} Iteration {trace.get('iteration')}: {trace.get('error_type')} ({status_text})"):
                        st.write(f"**Strategy:** {trace.get('strategy')}")
                        st.write(f"**Patch:**")
                        st.code(trace.get('patch'), language="python")

            # Download Button
            st.markdown("---")
            fixed_code = report.get("repaired_code", "")
            if fixed_code:
                st.download_button(
                    label="⬇️ Download Fixed Code",
                    data=fixed_code,
                    file_name="fixed_code.py",
                    mime="text/x-python"
                )
        else:
            st.error("Failed to load debug report.")
            
    else:
        # Welcome State (before first run)
        st.markdown("### 👈 Ready to Debug?")
        st.markdown("---")
        
        st.markdown("""
        **How to use DebugSteller:**
        
        1. **Paste or upload** your Python code on the left
        2. **Describe the bug** (optional) - e.g., "Output should be [1,2,3]"
        3. **Click** the "Run Debugger" button
        4. **Review** the automatic fixes and optimizations here
        
        """)
        
        st.info("💡 **Waiting for input...** The system will analyze your code for bugs and performance issues.")
        
        st.markdown("---")
        st.markdown("**What DebugSteller does:**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Auto-Fix**")
            st.caption("Detects and repairs runtime errors")
        with col2:
            st.markdown("**Optimize**")
            st.caption("Improves time complexity")
        with col3:
            st.markdown("**Verify**")
            st.caption("Ensures logic integrity")
