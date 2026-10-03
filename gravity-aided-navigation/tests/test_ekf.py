from gravity_nav import run_simulation


def test_gravity_aiding_improves_rmse_default_case():
    _, metrics, _ = run_simulation()
    assert metrics["aided_rmse_m"] < metrics["ins_rmse_m"]
