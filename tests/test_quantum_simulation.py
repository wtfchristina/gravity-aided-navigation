from gravity_nav import run_quantum_simulation


def test_cold_atom_gravity_aiding_improves_default_rmse():
    _, metrics, _, _ = run_quantum_simulation()
    assert metrics["aided_rmse_m"] < metrics["ins_rmse_m"]
    assert metrics["cai_equivalent_gradient_noise_std_E"] > 0.0
