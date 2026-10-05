from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from gravity_nav import SimulationConfig, QuantumSimulationConfig, run_simulation, run_quantum_simulation, AssuredPNTConfig, run_assured_pnt
from gravity_nav.metrics import position_errors
from gravity_nav.symplectic import benchmark
from gravity_nav.requirements import MissionRequirement, solve_sensor_requirements
from gravity_nav.integrity import IntegrityConfig, single_run_integrity

st.set_page_config(page_title="RelativisticQ-PNT Research Demonstrator", layout="wide")
st.title("Gravity-Aided Navigation in a GPS-Denied Environment")
st.caption("RelativisticQ-PNT research demonstrator — synthetic simulations, not flight-test or operational performance.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Baseline gravity-aided INS", "Cold-atom Tzz aiding", "Symplectic dynamics", "Assured PNT trade study", "Mission requirements & integrity"])

with tab1:
    with st.sidebar:
        st.header("Baseline controls")
        gravity_noise = st.slider("Scalar-map sensor noise", 0.5, 8.0, 2.0, 0.5)
        update_period = st.slider("Scalar-map update period (s)", 0.5, 10.0, 2.0, 0.5)
        accel_noise = st.slider("Accelerometer noise (m/s^2)", 0.005, 0.10, 0.03, 0.005)
        bias_rw = st.slider("Accel bias random walk", 0.0001, 0.0030, 0.0008, 0.0001, format="%.4f")
        seed = st.number_input("Baseline random seed", min_value=0, value=7, step=1)

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
    plt.xlabel("East (km)"); plt.ylabel("North (km)"); plt.title("Baseline trajectory comparison")
    plt.legend(); plt.grid(True, alpha=0.25); plt.tight_layout(); st.pyplot(fig)

with tab2:
    st.subheader("Synthetic cold-atom gravity-gradiometer navigation")
    st.write("The sensor model converts a synthetic Tzz gravity-gradient field into a differential matter-wave phase, adds phase/vibration noise, and converts the measured phase back to an inferred gradient for EKF map matching.")

    c1, c2, c3 = st.columns(3)
    with c1:
        q_phase_noise = st.slider("Phase noise std (rad)", 0.0, 0.02, 0.004, 0.001)
    with c2:
        q_vib_noise = st.slider("Vibration phase std (rad)", 0.0, 0.02, 0.003, 0.001)
    with c3:
        q_update = st.slider("CAI update period (s)", 0.5, 5.0, 2.0, 0.5)

    qcfg = QuantumSimulationConfig(
        phase_noise_std_rad=q_phase_noise,
        vibration_phase_std_rad=q_vib_noise,
        cai_update_period_s=q_update,
    )
    qdf, qm, qmap, cai = run_quantum_simulation(qcfg)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Distance", f"{qm['distance_km']:.1f} km")
    m2.metric("INS terminal error", f"{qm['ins_terminal_m']:.0f} m")
    m3.metric("CAI-aided terminal error", f"{qm['aided_terminal_m']:.0f} m")
    m4.metric("Equivalent Tzz noise", f"{qm['cai_equivalent_gradient_noise_std_E']:.1f} E")

    fig = plt.figure(figsize=(10, 5))
    plt.plot(qdf.truth_x_m/1000, qdf.truth_y_m/1000, label="Truth", linewidth=2)
    plt.plot(qdf.ins_x_m/1000, qdf.ins_y_m/1000, label="INS only")
    plt.plot(qdf.aided_x_m/1000, qdf.aided_y_m/1000, label="Cold-atom Tzz-aided EKF")
    plt.xlabel("East (km)"); plt.ylabel("North (km)"); plt.title("High-speed synthetic navigation demonstration")
    plt.legend(); plt.grid(True, alpha=0.25); plt.tight_layout(); st.pyplot(fig)

    mask = np.isfinite(qdf.cai_phase_rad.to_numpy())
    fig2 = plt.figure(figsize=(10, 4.5))
    plt.plot(qdf.time_s[mask], qdf.cai_phase_rad[mask])
    plt.xlabel("Time (s)"); plt.ylabel("Differential phase (rad)"); plt.title("Synthetic cold-atom phase observations")
    plt.grid(True, alpha=0.25); plt.tight_layout(); st.pyplot(fig2)

with tab3:
    st.subheader("Structure-preserving orbital propagation benchmark")
    st.write("A planar Kepler problem compares classical RK4 with the symplectic implicit-midpoint method. The point is not that one method always has lower instantaneous error; it is to expose long-horizon energy behavior under matched step size.")
    duration_days = st.slider("Benchmark duration (days)", 1, 14, 7, 1)
    dt_s = st.select_slider("Step size (s)", options=[30, 60, 120, 180, 300], value=120)
    t, rk, mp, rk_e, mp_e = benchmark(duration_s=duration_days*86400.0, dt=float(dt_s))

    e1, e2 = st.columns(2)
    e1.metric("RK4 terminal |dH/H|", f"{abs(rk_e[-1]):.3e}")
    e2.metric("Midpoint terminal |dH/H|", f"{abs(mp_e[-1]):.3e}")

    fig3 = plt.figure(figsize=(10, 5))
    plt.plot(t/86400.0, np.abs(rk_e), label="RK4")
    plt.plot(t/86400.0, np.abs(mp_e), label="Implicit midpoint")
    plt.yscale("log"); plt.xlabel("Time (days)"); plt.ylabel("Absolute relative Hamiltonian error")
    plt.title("Long-horizon Kepler energy behavior"); plt.legend(); plt.grid(True, alpha=0.25); plt.tight_layout(); st.pyplot(fig3)

with tab4:
    st.subheader("Multi-modal passive navigation trade study")
    st.write("Compare INS-only, gravity-only, magnetic-only, and fused environmental map aiding under a common deterministic IMU realization.")
    mode = st.selectbox("Aiding mode", ["fused", "gravity", "magnetic", "ins"], index=0)
    c1, c2 = st.columns(2)
    with c1:
        gnoise = st.slider("Gravity map observation noise", 0.5, 8.0, 2.0, 0.5)
    with c2:
        mnoise = st.slider("Magnetic observation noise (nT)", 2.0, 40.0, 8.0, 2.0)
    acfg = AssuredPNTConfig(mode=mode, gravity_noise_std=gnoise, magnetic_noise_std_nt=mnoise)
    adf, am, _, _ = run_assured_pnt(acfg)
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("INS terminal error", f"{am['ins_terminal_m']:.0f} m")
    a2.metric("Selected terminal error", f"{am['aided_terminal_m']:.0f} m")
    a3.metric("RMSE improvement", f"{am['rmse_improvement_pct']:.1f}%")
    a4.metric("Distance", f"{am['distance_km']:.1f} km")
    fig4 = plt.figure(figsize=(10, 5))
    plt.plot(adf.truth_x_m/1000, adf.truth_y_m/1000, label="Truth", linewidth=2)
    plt.plot(adf.ins_x_m/1000, adf.ins_y_m/1000, label="INS only")
    if mode != "ins":
        plt.plot(adf.aided_x_m/1000, adf.aided_y_m/1000, label=f"{mode.title()} aided")
    plt.xlabel("East (km)"); plt.ylabel("North (km)"); plt.title("Environmental navigation trade study")
    plt.legend(); plt.grid(True, alpha=0.25); plt.tight_layout(); st.pyplot(fig4)

with tab5:
    st.subheader("Mission requirements and integrity screening")
    st.write("Turn a navigation target into a sensor trade study, then inspect a transparent integrity proxy against an alert limit. Results are synthetic engineering-screening outputs, not certification evidence.")
    c1,c2,c3=st.columns(3)
    with c1:
        terminal_limit=st.number_input("Terminal error limit (m)",min_value=10.0,value=150.0,step=10.0)
    with c2:
        rmse_limit=st.number_input("RMSE limit (m)",min_value=10.0,value=250.0,step=10.0)
    with c3:
        alert_limit=st.number_input("Alert limit (m)",min_value=10.0,value=300.0,step=10.0)
    req=MissionRequirement(terminal_error_limit_m=terminal_limit,rmse_limit_m=rmse_limit,success_probability=0.8,alert_limit_m=alert_limit)
    base=AssuredPNTConfig(mode="fused")
    if st.button("Run compact requirements sweep"):
        tdf=solve_sensor_requirements(base,req,gravity_noise=(1.0,2.0,4.0),magnetic_noise=(4.0,8.0,16.0),update_period=(1.0,2.0),runs=5)
        st.dataframe(tdf.head(12),use_container_width=True)
    idf,_,_,_=run_assured_pnt(base)
    trace,im=single_run_integrity(idf,IntegrityConfig(alert_limit_m=alert_limit))
    i1,i2,i3=st.columns(3)
    i1.metric("Availability proxy",f"{100*im['availability_fraction']:.1f}%")
    i2.metric("Max position error",f"{im['max_position_error_m']:.0f} m")
    i3.metric("Max protection proxy",f"{im['max_protection_level_proxy_m']:.0f} m")
    fig5=plt.figure(figsize=(10,4.5))
    plt.plot(trace.time_s,trace.position_error_m,label="Position error")
    plt.plot(trace.time_s,trace.protection_level_proxy_m,label="Protection-level proxy")
    plt.axhline(alert_limit,linestyle="--",label="Alert limit")
    plt.xlabel("Time (s)"); plt.ylabel("Meters"); plt.title("Integrity screening proxy")
    plt.legend(); plt.grid(True,alpha=0.25); plt.tight_layout(); st.pyplot(fig5)

with st.expander("Scope and limitations"):
    st.markdown("""
This repository intentionally uses synthetic gravity fields, planar kinematics, and simplified cold-atom measurement equations. It demonstrates software architecture, map matching, estimator behavior, and numerical methods. It is not a flight-qualified navigation system, hardware-in-the-loop result, or claim of operational quantum-sensor performance.
""")
