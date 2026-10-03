from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gravity_nav import run_quantum_simulation
from gravity_nav.metrics import position_errors


def main():
    df, metrics, gmap, _ = run_quantum_simulation()
    figdir = ROOT / "figures"; figdir.mkdir(exist_ok=True)

    truth = df[["truth_x_m","truth_y_m"]].to_numpy()
    ins = df[["ins_x_m","ins_y_m"]].to_numpy()
    aid = df[["aided_x_m","aided_y_m"]].to_numpy()

    plt.figure(figsize=(10, 5.8))
    plt.plot(df.truth_x_m/1000, df.truth_y_m/1000, label="Truth", linewidth=2)
    plt.plot(df.ins_x_m/1000, df.ins_y_m/1000, label="INS only")
    plt.plot(df.aided_x_m/1000, df.aided_y_m/1000, label="Cold-atom gravity-aided EKF")
    plt.xlabel("East position (km)"); plt.ylabel("North position (km)")
    plt.title("Cold-Atom Gravity-Gradient Aided Navigation")
    plt.legend(); plt.grid(True, alpha=0.25); plt.tight_layout()
    plt.savefig(figdir / "quantum_trajectory_comparison.png", dpi=180); plt.close()

    plt.figure(figsize=(10, 5.8))
    plt.plot(df.time_s, position_errors(truth, ins), label="INS only")
    plt.plot(df.time_s, position_errors(truth, aid), label="Cold-atom gravity-aided EKF")
    plt.xlabel("Time (s)"); plt.ylabel("Position error (m)")
    plt.title("Position Error: INS vs Cold-Atom Gravity Aiding")
    plt.legend(); plt.grid(True, alpha=0.25); plt.tight_layout()
    plt.savefig(figdir / "quantum_position_error.png", dpi=180); plt.close()

    xx, yy, zz = gmap.grid("Tzz")
    plt.figure(figsize=(10, 5.8))
    cs = plt.contourf(xx/1000, yy/1000, zz, levels=24)
    plt.colorbar(cs, label="Synthetic Tzz (E)")
    plt.plot(df.truth_x_m/1000, df.truth_y_m/1000, linewidth=2, label="Truth trajectory")
    plt.xlabel("East position (km)"); plt.ylabel("North position (km)")
    plt.title("Synthetic Tzz Gravity-Gradient Map")
    plt.legend(); plt.tight_layout()
    plt.savefig(figdir / "tzz_map.png", dpi=180); plt.close()

    mask = np.isfinite(df.cai_phase_rad.to_numpy())
    plt.figure(figsize=(10, 5.8))
    plt.plot(df.time_s[mask], df.cai_phase_rad[mask])
    plt.xlabel("Time (s)"); plt.ylabel("Measured differential phase (rad)")
    plt.title("Synthetic Cold-Atom Differential Phase")
    plt.grid(True, alpha=0.25); plt.tight_layout()
    plt.savefig(figdir / "cold_atom_phase.png", dpi=180); plt.close()

    print(metrics)


if __name__ == "__main__":
    main()
