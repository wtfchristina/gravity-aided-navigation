from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from gravity_nav import SimulationConfig, run_simulation
from gravity_nav.metrics import position_errors

st.set_page_config(page_title="Gravity-Aided Navigation", layout="wide")
st.title("Gravity-Aided Navigation in a GPS-Denied Environment")
st.caption("A RelativisticQ-PNT research demonstrator — synthetic simulation, not flight-test performance.")

with st.sidebar:
    st.header("Simulation controls")
    gravity_noise = st.slider("Gravity sensor noise", 0.5, 8.0, 2.0, 0.5)
    update_period = st.slider("Gravity update period (s)", 0.5, 10.0, 2.0, 0.5)
    accel_noise = st.slider("Accelerometer noise (m/s^2)", 0.005, 0.10, 0.03, 0.005)
    bias_rw = st.slider("Accel bias random walk", 0.0001, 0.0030, 0.0008, 0.0001, format="%.4f")
    seed = st.number_input("Random seed", min_value=0, value=7, step=1)

cfg = SimulationConfig(
    gravity_noise_std=gravity_noise,
    gravity_update_period=update_period,
    accel_noise_std=accel_noise,
    bias_rw_std=bias_rw,
    seed=int(seed),
)

df, metrics, gmap = run_simulation(cfg)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Distance", f"{metrics['distance_km']:.1f} km")
c2.metric("INS terminal error", f"{metrics['ins_terminal_m']:.0f} m")
c3.metric("Aided terminal error", f"{metrics['aided_terminal_m']:.0f} m")
c4.metric("RMSE improvement", f"{metrics['rmse_improvement_pct']:.1f}%")

fig = plt.figure(figsize=(10, 5))
plt.plot(df.truth_x_m/1000, df.truth_y_m/1000, label="Truth", linewidth=2)
plt.plot(df.ins_x_m/1000, df.ins_y_m/1000, label="INS only")
plt.plot(df.aided_x_m/1000, df.aided_y_m/1000, label="Gravity-aided EKF")
plt.xlabel("East (km)")
plt.ylabel("North (km)")
plt.title("Trajectory comparison")
plt.legend(); plt.grid(True, alpha=0.25); plt.tight_layout()
st.pyplot(fig)

truth = df[["truth_x_m","truth_y_m"]].to_numpy()
ins = df[["ins_x_m","ins_y_m"]].to_numpy()
aid = df[["aided_x_m","aided_y_m"]].to_numpy()
fig2 = plt.figure(figsize=(10, 5))
plt.plot(df.time_s, position_errors(truth, ins), label="INS only")
plt.plot(df.time_s, position_errors(truth, aid), label="Gravity-aided EKF")
plt.xlabel("Time (s)"); plt.ylabel("Position error (m)")
plt.title("Position error growth"); plt.legend(); plt.grid(True, alpha=0.25); plt.tight_layout()
st.pyplot(fig2)

with st.expander("Methodology and scope"):
    st.markdown("""
This demo uses a planar inertial model, a synthetic differentiable gravity-gradient map,
and a nonlinear Extended Kalman Filter. The gravity measurement is used as a spatial
map-matching observable. It is intended to demonstrate estimation architecture and
observability concepts, not operational cold-atom sensor performance.
""")
