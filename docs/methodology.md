# Methodology

## Scope

This repository is a research simulation of gravity-aided inertial navigation and structure-preserving dynamics. It is **not** flight-qualified navigation software and does not claim operational cold-atom sensor performance.

## Navigation state

The estimator state is:

`x = [p_x, p_y, v_x, v_y, b_ax, b_ay]^T`

where `p` is planar position, `v` velocity, and `b_a` accelerometer bias.

## Baseline scalar map

The original v0.1 demo uses a smooth scalar spatial field constructed from Gaussian anomalies:

`z = h(p_x, p_y) + noise`

The EKF linearizes the field with:

`H = [dh/dx, dh/dy, 0, 0, 0, 0]`

This baseline remains in the repository for comparison and teaching.

## Synthetic gravity-gradient tensor

Version 0.2 adds a synthetic gravitational potential formed from Gaussian perturbations. Analytic second derivatives produce `Txx`, `Txy`, and `Tyy`; `Tzz = -(Txx + Tyy)` is imposed as a local source-free Laplace constraint.

Tensor values are reported in Eotvos:

`1 E = 1e-9 s^-2`

This is a self-contained synthetic field, not a validated Earth gravity model.

## Cold-atom gradiometer model

The cold-atom demonstrator uses the simplified differential phase model:

`DeltaPhi ~= k_eff * Gamma * L * T^2`

where `Gamma` is the selected gravity-gradient component, `L` is the interferometer baseline, and `T` is interrogation time. Independent phase and vibration-noise terms are added before phase is converted back to an inferred gradient measurement.

The model intentionally omits many real-system effects, including wavefront aberrations, Coriolis coupling, contrast loss, atom-cloud temperature effects, laser-frequency noise, platform vibration transfer functions, dead-time aliasing, and detailed pulse dynamics.

## Gravity-aided EKF

At each sensor update, the EKF predicts the tensor component from the reference map at the current estimated position. A numerical spatial Jacobian converts the field residual into a position-sensitive measurement update.

This demonstrates environmental map matching; it does not establish observability for every terrain, route, map resolution, or sensor configuration.

## Structure-preserving dynamics benchmark

A separate two-body Kepler test compares classical fourth-order Runge-Kutta with the implicit midpoint method. The implicit midpoint method is symplectic. It does **not** guarantee exact conservation of the original Hamiltonian, but its geometric structure can give favorable long-horizon energy behavior.

## Reproducibility

Random seeds are fixed in default configurations. Generated CSV/JSON results and figures are derived from code rather than hard-coded.

## Limitations

- 2D kinematics rather than full 6-DOF strapdown INS.
- No gyroscope channel, attitude error state, Earth rotation, transport rate, Coriolis, coning/sculling, or ellipsoidal frame transformations.
- Synthetic gravity field rather than validated airborne/marine gravity maps.
- Simplified cold-atom phase/noise model.
- EKF only; no particle filter, factor graph, smoother, or integrity monitor.
- No hardware-in-the-loop or flight-test validation.

These limitations are deliberate: the repository is meant to expose the architecture and numerical assumptions clearly enough to be inspected and extended.
