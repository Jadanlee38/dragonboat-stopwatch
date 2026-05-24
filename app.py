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
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #f59e0b;
        background-color: #0f172a;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🐉 GCD Boat Run Tracker")

# --- Initialize States ---
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "history" not in st.session_state:
    st.session_state.history = []  # List of dicts: {"type": "Kid"|"Coach", "abs_time": float}
if "coach_index" not in st.session_state:
    st.session_state.coach_index = None

# --- Live Stopwatch Logic ---
if st.session_state.start_time is not None and st.session_state.coach_index is None:
    # If timer started but coach hasn't finished, display an active counting clock
    elapsed_now = time.time() - st.session_state.start_time
    m_now = int(elapsed_now // 60)
    s_now = int(elapsed_now % 60)
    st.markdown(f'<div class="stopwatch-box">{m_now:02d}:{s_now:02d}</div>', unsafe_allow_html=True)
    # This button forces Streamlit to rerun the page immediately, creating a live ticking effect
    st.button("⏱️ Refresh Clock")
elif st.session_state.start_time is not None and st.session_state.coach_index is not None:
    st.markdown('<div class="stopwatch-box" style="color:#10b981;">Race Finalized</div>', unsafe_allow_html=True)

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
    # Disable coach button if race hasn't started or coach is already logged
    coach_disabled = (st.session_state.start_time is None) or (st.session_state.coach_index is not None)
    if st.button("⏱️ Log Coach", disabled=coach_disabled):
        current_clock = time.time()
        st.session_state.history.append({
            "type": "Coach",
            "abs_time": current_clock
        })
        # Keep track of where the coach sits in the list
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
                    # Kid beat or tied coach. Strict round up for rewards: 1 sec faster = 1 min reward (-5)
                    minutes_faster = math.ceil(abs(diff) / 60.0)
                    total_burpees -= (minutes_faster * 5)
                else:
                    # Kid lost to coach. Strict round up for penalties: 1 sec slower = 1 min penalty (+5)
                    minutes_slower = math.ceil(diff / 60.0)
                    total_burpees += (minutes_slower * 5)

    # --- Live Punishment Tally Display ---
    tally_color = "#34d399" if total_burpees <= 0 else "#f87171"
    st.markdown(f"""
    <div class="metric-box">
        <p style="margin:0; font-size:14px; color:#cbd5e1; font-weight:bold;">TOTAL TEAM BURPEE TALLY</p>
        <h1 style="margin:0; font-size:48px; color:{tally_color};">
            {total_burpees} Burpees
        </h1>
    </div>
    """, unsafe_allow_html=True)

    # --- Re-indexed Finish Feed ---
    st.subheader("📋 Official Finish Order")
    
    kid_counter = 1
    for item in st.session_state.history:
        # Standard display before coach arrives
        if coach_abs_time == None:
            rel_time = item["abs_time"] - st.session_state.start_time
            m = int(rel_time // 60)
            s = int(rel_time % 60)
            
            if item["type"] == "Coach":
                st.write(f"➡️ **COACH FINISHED:** {m:02d}:{s:02d} (Awaiting final calculations...)")
            else:
                st.write(f"🏃‍♂️ **Runner #{kid_counter}:** {m:02d}:{s:02d}")
                kid_counter += 1
        
        # Inverted display after coach arrives
        else:
            diff = item["abs_time"] - coach_abs_time
            m_diff = int(abs(diff) // 60)
            s_diff = int(abs(diff) % 60)
            time_str = f"{m_diff:02d}:{s_diff:02d}"
            
            if item["type"] == "Coach":
                st.markdown(f"⏱️ <span style='color:#10b981; font-weight:bold;'>[COACH FINISHED BASELINE]</span>", unsafe_allow_html=True)
            else:
                if diff <= 0:
                    # Faster than coach
                    mins_rounded = math.ceil(abs(diff) / 60.0)
                    st.write(f"🏃‍♂️ **Runner #{kid_counter}:** {time_str} ahead of coach ({mins_rounded}m faster) 🟢 **-{mins_rounded*5} Burpees**")
                else:
                    # Slower than coach
                    mins_rounded = math.ceil(diff / 60.0)
                    st.write(f"🏃‍♂️ **Runner #{kid_counter}:** {time_str} behind coach ({mins_rounded}m slower) 🔴 **+{mins_rounded*5} Burpees**")
                kid_counter += 1