from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gravity_nav import run_simulation
from gravity_nav.metrics import position_errors


def main():
    df, metrics, gmap = run_simulation()
    figdir = ROOT / "figures"
    figdir.mkdir(exist_ok=True)

    # Trajectory comparison
    plt.figure(figsize=(10, 5.8))
    plt.plot(df.truth_x_m/1000, df.truth_y_m/1000, label="Truth", linewidth=2)
    plt.plot(df.ins_x_m/1000, df.ins_y_m/1000, label="INS only", alpha=0.85)
    plt.plot(df.aided_x_m/1000, df.aided_y_m/1000, label="Gravity-aided EKF", alpha=0.9)
    plt.xlabel("East position (km)")
    plt.ylabel("North position (km)")
    plt.title("GPS-Denied Navigation: Truth vs INS vs Gravity-Aided EKF")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(figdir / "trajectory_comparison.png", dpi=180)
    plt.close()

    # Error plot
    truth = df[["truth_x_m","truth_y_m"]].to_numpy()
    ins = df[["ins_x_m","ins_y_m"]].to_numpy()
    aid = df[["aided_x_m","aided_y_m"]].to_numpy()
    e_ins = position_errors(truth, ins)
    e_aid = position_errors(truth, aid)
    plt.figure(figsize=(10, 5.8))
    plt.plot(df.time_s, e_ins, label="INS only")
    plt.plot(df.time_s, e_aid, label="Gravity-aided EKF")
    plt.xlabel("Time (s)")
    plt.ylabel("Position error (m)")
    plt.title("Position Error Growth")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(figdir / "position_error.png", dpi=180)
    plt.close()

    # Gravity map
    xx, yy, zz = gmap.grid()
    plt.figure(figsize=(10, 5.8))
    cs = plt.contourf(xx/1000, yy/1000, zz, levels=24)
    plt.colorbar(cs, label="Synthetic gravity-gradient observable")
    plt.plot(df.truth_x_m/1000, df.truth_y_m/1000, linewidth=2, label="Truth trajectory")
    plt.xlabel("East position (km)")
    plt.ylabel("North position (km)")
    plt.title("Synthetic Gravity-Gradient Map and Vehicle Trajectory")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figdir / "gravity_map.png", dpi=180)
    plt.close()

    print(metrics)


if __name__ == "__main__":
    main()
