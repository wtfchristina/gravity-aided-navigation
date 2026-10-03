.PHONY: install test baseline quantum symplectic figures app all

install:
	python -m pip install -e ".[dev]"

test:
	pytest -q

baseline:
	python scripts/run_simulation.py

quantum:
	python scripts/run_quantum_simulation.py

symplectic:
	python scripts/run_symplectic_benchmark.py

figures:
	python scripts/generate_figures.py
	python scripts/generate_quantum_figures.py

app:
	streamlit run app.py

all: test baseline quantum figures symplectic
