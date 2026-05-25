import streamlit as st
import time
import math

st.set_page_config(page_title="GCD Boat Run Tracker", layout="centered")

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
    .stopwatch-display {
        font-family: 'Courier New', Courier, monospace;
        font-size: 52px;
        font-weight: bold;
        text-align: center;
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
    st.session_state.history = []  
if "coach_index" not in st.session_state:
    st.session_state.coach_index = None

# --- HTML/JavaScript Local Stopwatch (Zero Network Lag) ---
if st.session_state.start_time is not None:
    current_time_now = time.time()
    
    if st.session_state.coach_index is None:
        # Count UP from start_time
        elapsed_baseline = current_time_now - st.session_state.start_time
        js_timer_html = f"""
        <div class="stopwatch-display" id="local-clock" style="color: #f59e0b;">00:00</div>
        <script>
            let elapsed = {elapsed_baseline};
            const clockDiv = document.getElementById('local-clock');
            setInterval(() => {{
                elapsed += 1;
                let m = Math.floor(elapsed / 60);
                let s = Math.floor(elapsed % 60);
                clockDiv.innerText = "⏱️ " + String(m).padStart(2, '0') + ":" + String(s).padStart(2, '0');
            }}, 1000);
        </script>
        """
    else:
        # Coach finished: Count UP from coach timestamp
        coach_abs_time = st.session_state.history[st.session_state.coach_index]["abs_time"]
        elapsed_since_coach = current_time_now - coach_abs_time
        js_timer_html = f"""
        <div class="stopwatch-display" id="local-clock" style="color: #10b981; border-color: #10b981;">00:00 since Coach</div>
        <script>
            let elapsed = {elapsed_since_coach};
            const clockDiv = document.getElementById('local-clock');
            setInterval(() => {{
                elapsed += 1;
                let m = Math.floor(elapsed / 60);
                let s = Math.floor(elapsed % 60);
                clockDiv.innerText = "⏱️ " + String(m).padStart(2, '0') + ":" + String(s).padStart(2, '0') + " since Coach";
            }}, 1000);
        </script>
        """
    st.components.v1.html(js_timer_html, height=100)

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

# --- Calculations & Display Feed ---
if st.session_state.start_time is not None:
    st.markdown("---")
    total_burpees = 0
    coach_abs_time = None
    
    if st.session_state.coach_index is not None:
        coach_abs_time = st.session_state.history[st.session_state.coach_index]["abs_time"]
        for item in st.session_state.history:
            if item["type"] == "Kid":
                diff = item["abs_time"] - coach_abs_time
                if diff <= 0:
                    minutes_faster = math.ceil(abs(diff) / 60.0)
                    total_burpees -= (minutes_faster * 5)
                else:
                    minutes_slower = math.ceil(diff / 60.0)
                    total_burpees += (minutes_slower * 5)

    tally_color = "#34d399" if total_burpees <= 0 else "#f87171"
    st.markdown(f"""
    <div class="metric-box">
        <p style="margin:0; font-size:14px; color:#cbd5e1; font-weight:bold;">TOTAL TEAM BURPEE TALLY</p>
        <h1 style="margin:0; font-size:48px; color:{tally_color};">
            {'+' if total_burpees > 0 else ''}{total_burpees} Burpees
        </h1>
    </div>
    """, unsafe_allow_html=True)

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