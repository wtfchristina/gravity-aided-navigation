# LinkedIn Showcase Copy

## Suggested project title

**Gravity-Aided Navigation for GPS-Denied Systems — A RelativisticQ-PNT Research Demonstrator**

## Suggested LinkedIn post

I built a gravity-aided navigation research demonstrator to explore a simple question: can an environmental gravity reference constrain inertial drift after GNSS loss?

The repository now includes:

- INS-only dead reckoning with accelerometer bias/noise
- synthetic gravity-gradient tensor maps (`Txx`, `Txy`, `Tyy`, `Tzz`)
- Extended Kalman Filter map matching
- a simplified cold-atom gradiometer phase model
- high-speed `Tzz`-aided navigation simulation
- an RK4 vs implicit-midpoint symplectic orbit benchmark
- an interactive Streamlit dashboard
- reproducible plots, metrics, tests, and CI

In the default high-speed synthetic run, the vehicle travels ~54.8 km. INS-only terminal position error is ~436 m, while the cold-atom gravity-aided estimate finishes at ~98 m.

These are synthetic simulation results—not flight-test or operational hardware claims. The point of the project is to make the architecture inspectable and reproducible: physics -> sensing -> estimation -> navigation.

GitHub: https://github.com/wtfchristina/gravity-aided-navigation

#AssuredPNT #QuantumSensing #GPSDenied #Navigation #GNC #AtomInterferometry #Aerospace #Python

## Suggested GitHub repository description

Gravity-aided GPS-denied navigation research demonstrator with INS, EKF map matching, synthetic gravity-gradient tensors, cold-atom phase sensing, and symplectic dynamics.
