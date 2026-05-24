import streamlit as st
import time
import math

# Force a mobile-friendly wide layout configuration
st.set_page_config(page_title="Dragon Boat Run Tracker", layout="centered")

# --- CSS to make buttons massive and easy to tap on a phone screen ---
st.markdown("""
<style>
    div.stButton > button {
        width: 100% !important;
        height: 60px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🐉 Celestial Run Tracker")
st.write("Tap buttons as they cross the finish line. Timer starts automatically on the first kid.")

# --- Initialize Session States ---
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "runner_times" not in st.session_state:
    st.session_state.runner_times = []  # List of floats (seconds from start)
if "coach_time" not in st.session_state:
    st.session_state.coach_time = None

# --- Action Buttons ---
col1, col2 = st.columns(2)

with col1:
    # Green button for logging kids
    if st.button("🏃‍♂️ Log Runner", type="primary"):
        current_clock = time.time()
        
        # If this is the very first person crossing, they set the baseline (00:00)
        if st.session_state.start_time is None:
            st.session_state.start_time = current_clock
            st.session_state.runner_times.append(0.0)
        else:
            elapsed = current_clock - st.session_state.start_time
            st.session_state.runner_times.append(elapsed)

with col2:
    # Red button for logging the coach
    if st.button("⏱️ Log Coach", disabled=st.session_state.start_time is None or st.session_state.coach_time is not None):
        st.session_state.coach_time = time.time() - st.session_state.start_time

# --- Reset Button ---
if st.button("🔄 Reset Timer & Data"):
    st.session_state.start_time = None
    st.session_state.runner_times = []
    st.session_state.coach_time = None
    st.rerun()

# --- Calculations & Live Dashboard ---
if st.session_state.start_time is not None:
    st.markdown("---")
    
    total_burpees = 0
    coach_display = "Running..."
    
    if st.session_state.coach_time is not None:
        c_min = int(st.session_state.coach_time // 60)
        c_sec = int(st.session_state.coach_time % 60)
        coach_display = f"{c_min:02d}:{c_sec:02d}"
        
        # Calculate burpees for every runner logged so far
        for r_time in st.session_state.runner_times:
            # Time difference in seconds
            diff = r_time - st.session_state.coach_time
            
            if diff <= 0:
                # Kid beat or tied coach: calculate whole minutes faster
                # Use absolute value to see how many full minutes ahead they were
                minutes_faster = int(abs(diff) // 60)
                total_burpees -= (minutes_faster * 5)
            else:
                # Kid was slower: strict ceiling rounding (1 second late = 1 full minute late)
                minutes_slower = math.ceil(diff / 60.0)
                total_burpees += (minutes_slower * 5)

    # --- Mobile Display Cards ---
    st.markdown(f"""
    <div class="metric-box">
        <p style="margin:0; font-size:14px; color:#555;">CURRENT PUNISHMENT TALLY</p>
        <h1 style="margin:0; font-size:42px; color:{'#2e7d32' if total_burpees <= 0 else '#d32f2f'};">
            {total_burpees} Burpees
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    d_col1, d_col2 = st.columns(2)
    d_col1.metric("Runners Logged", len(st.session_state.runner_times))
    d_col2.metric("Coach Time", coach_display)

    # --- Detailed Runner Feed ---
    st.subheader("Finish Order")
    for i, r_time in enumerate(st.session_state.runner_times):
        m = int(r_time // 60)
        s = int(r_time % 60)
        
        # Contextual labeling based on coach status
        status_label = ""
        if st.session_state.coach_time is not None:
            diff = r_time - st.session_state.coach_time
            if diff <= 0:
                status_label = f" ({int(abs(diff)//60)}m faster) -> -{int(abs(diff)//60)*5} Burpees"
            else:
                status_label = f" ({math.ceil(diff/60.0)}m slower) -> +{math.ceil(diff/60.0)*5} Burpees"
                
        st.write(f"**Runner #{i+1}:** {m:02d}:{s:02d}{status_label}")