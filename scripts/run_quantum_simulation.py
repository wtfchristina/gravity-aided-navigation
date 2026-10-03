from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gravity_nav import QuantumSimulationConfig, run_quantum_simulation


def main():
    df, metrics, _, _ = run_quantum_simulation(QuantumSimulationConfig())
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    df.to_csv(out / "quantum_simulation.csv", index=False)
    (out / "quantum_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
