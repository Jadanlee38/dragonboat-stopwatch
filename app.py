import streamlit as st
import time
import math

st.set_page_config(page_title="Dragon Boat Run Tracker", layout="centered")

# --- CSS Styling for Mobile Buttons & Visuals ---
st.markdown("""
<style>
    div.stButton > button {
        width: 100% !important;
        height: 65px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
    }
    .metric-box {
        background-color: #1e293b;
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 15px;
    }
    .stopwatch-box {
        font-family: 'Courier New', Courier, monospace;
        font-size: 52px;
        font-weight: bold;
        text-align: center;
        color: #f59e0b;
        background-color: #0f172a;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 2px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

st.title("🐉 GCD Run Tracker")

# --- Initialize States ---
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "history" not in st.session_state:
    st.session_state.history = []  # List of dicts: {"type": "Kid"|"Coach", "abs_time": float}
if "coach_index" not in st.session_state:
    st.session_state.coach_index = None

# --- Live-Ticking Stopwatch Fragment ---
# This decorator keeps the stopwatch ticking every 1 second without reloading the entire app layout
@st.fragment(run_every=1.0)
def render_live_stopwatch():
    if st.session_state.start_time is not None:
        current_now = time.time()
        
        # If coach hasn't finished, count up from the first runner
        if st.session_state.coach_index is None:
            elapsed_now = current_now - st.session_state.start_time
            m_now = int(elapsed_now // 60)
            s_now = int(elapsed_now % 60)
            st.markdown(f'<div class="stopwatch-box">⏱️ {m_now:02d}:{s_now:02d}</div>', unsafe_allow_html=True)
            
        # IF COACH FINISHED: Count up live from the coach's arrival time
        else:
            coach_abs_time = st.session_state.history[st.session_state.coach_index]["abs_time"]
            elapsed_since_coach = current_now - coach_abs_time
            m_since = int(elapsed_since_coach // 60)
            s_since = int(elapsed_since_coach % 60)
            st.markdown(f'<div class="stopwatch-box" style="color:#10b981; border-color:#10b981;">⏱️ {m_since:02d}:{s_since:02d} since Coach</div>', unsafe_allow_html=True)

# Run the stopwatch fragment
render_live_stopwatch()

# --- Action Buttons ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🏃‍♂️ Log Runner", type="primary"):
        current_clock = time.time()
        if st.session_state.start_time is None:
            st.session_state.start_time = current_clock
        
        st.session_state.history.append({
            "type": "Kid",
            "abs_time": current_clock
        })
        st.rerun()

with col2:
    coach_disabled = (st.session_state.start_time is None) or (st.session_state.coach_index is not None)
    if st.button("⏱️ Log Coach", disabled=coach_disabled):
        current_clock = time.time()
        st.session_state.history.append({
            "type": "Coach",
            "abs_time": current_clock
        })
        st.session_state.coach_index = len(st.session_state.history) - 1
        st.rerun()

# --- Reset Button ---
if st.button("🔄 Reset Entire Race"):
    st.session_state.start_time = None
    st.session_state.history = []
    st.session_state.coach_index = None
    st.rerun()

# --- Math & Dashboard Calculation ---
if st.session_state.start_time is not None:
    st.markdown("---")
    
    total_burpees = 0
    coach_abs_time = None
    
    if st.session_state.coach_index is not None:
        coach_abs_time = st.session_state.history[st.session_state.coach_index]["abs_time"]
        
        # Calculate burpees for all logged kids
        for item in st.session_state.history:
            if item["type"] == "Kid":
                diff = item["abs_time"] - coach_abs_time
                
                if diff <= 0:
                    minutes_faster = math.ceil(abs(diff) / 60.0)
                    total_burpees -= (minutes_faster * 5)
                else:
                    minutes_slower = math.ceil(diff / 60.0)
                    total_burpees += (minutes_slower * 5)

    # --- Live Punishment Tally Display ---
    tally_color = "#34d399" if total_burpees <= 0 else "#f87171"
    st.markdown(f"""
    <div class="metric-box">
        <p style="margin:0; font-size:14px; color:#cbd5e1; font-weight:bold;">TOTAL TEAM BURPEE TALLY</p>
        <h1 style="margin:0; font-size:48px; color:{tally_color};">
            {'+' if total_burpees > 0 else ''}{total_burpees} Burpees
        </h1>
    </div>
    """, unsafe_allow_html=True)

    # --- Re-indexed Finish Feed ---
    st.subheader("📋 Official Finish Order")
    
    kid_counter = 1
    for item in st.session_state.history:
        if coach_abs_time == None:
            rel_time = item["abs_time"] - st.session_state.start_time
            m = int(rel_time // 60)
            s = int(rel_time % 60)
            
            if item["type"] == "Coach":
                st.write(f"➡️ **COACH FINISHED:** {m:02d}:{s:02d} (Awaiting final calculations...)")
            else:
                st.write(f"🏃‍♂️ **Runner #{kid_counter}:** {m:02d}:{s:02d}")
                kid_counter += 1
        else:
            diff = item["abs_time"] - coach_abs_time
            m_diff = int(abs(diff) // 60)
            s_diff = int(abs(diff) % 60)
            time_str = f"{m_diff:02d}:{s_diff:02d}"
            
            if item["type"] == "Coach":
                st.markdown(f"⏱️ <span style='color:#10b981; font-weight:bold;'>[COACH FINISHED BASELINE]</span>", unsafe_allow_html=True)
            else:
                if diff <= 0:
                    mins_rounded = math.ceil(abs(diff) / 60.0)
                    st.write(f"🏃‍♂️ **Runner #{kid_counter}:** {time_str} ahead of coach ({mins_rounded}m faster) 🟢 **-{mins_rounded*5} Burpees**")
                else:
                    mins_rounded = math.ceil(diff / 60.0)
                    st.write(f"🏃‍♂️ **Runner #{kid_counter}:** {time_str} behind coach ({mins_rounded}m slower) 🔴 **+{mins_rounded*5} Burpees**")
                kid_counter += 1