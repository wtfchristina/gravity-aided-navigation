from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gravity_nav import SimulationConfig, run_simulation


def main():
    df, metrics, _ = run_simulation(SimulationConfig())
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    df.to_csv(out / "simulation.csv", index=False)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
