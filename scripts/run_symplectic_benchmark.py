from pathlib import Path
import json
import sys
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gravity_nav.symplectic import benchmark


def main():
    t, rk, mp, rk_e, mp_e = benchmark()
    figdir = ROOT / "figures"; figdir.mkdir(exist_ok=True)
    out = ROOT / "results"; out.mkdir(exist_ok=True)

    plt.figure(figsize=(10, 5.8))
    plt.plot(t, np.abs(rk_e), label="RK4")
    plt.plot(t, np.abs(mp_e), label="Implicit midpoint")
    plt.yscale("log")
    plt.xlabel("Time (s)")
    plt.ylabel("Absolute relative Hamiltonian error")
    plt.title("Kepler Propagation: Hamiltonian Error")
    plt.legend(); plt.grid(True, alpha=0.25); plt.tight_layout()
    plt.savefig(figdir / "symplectic_energy_error.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 7))
    plt.plot(rk[:,0]/1000, rk[:,1]/1000, label="RK4")
    plt.plot(mp[:,0]/1000, mp[:,1]/1000, label="Implicit midpoint")
    plt.xlabel("x (km)"); plt.ylabel("y (km)")
    plt.title("Planar Kepler Orbit Benchmark")
    plt.axis("equal"); plt.legend(); plt.grid(True, alpha=0.25); plt.tight_layout()
    plt.savefig(figdir / "symplectic_orbit.png", dpi=180)
    plt.close()

    metrics = {
        "duration_s": float(t[-1]),
        "dt_s": float(t[1]-t[0]),
        "rk4_max_abs_relative_energy_error": float(np.max(np.abs(rk_e))),
        "midpoint_max_abs_relative_energy_error": float(np.max(np.abs(mp_e))),
        "rk4_terminal_abs_relative_energy_error": float(abs(rk_e[-1])),
        "midpoint_terminal_abs_relative_energy_error": float(abs(mp_e[-1])),
    }
    (out / "symplectic_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
