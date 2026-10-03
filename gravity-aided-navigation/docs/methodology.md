# Methodology

## Scope

This repository is a research simulation of gravity-aided inertial navigation. It is not a flight-qualified navigation system and does not claim operational cold-atom sensor performance.

## State model

The estimator state is

`x = [p_x, p_y, v_x, v_y, b_ax, b_ay]^T`

where `p` is planar position, `v` is velocity, and `b_a` is accelerometer bias.

The inertial propagation model uses measured acceleration minus estimated bias.

## Synthetic gravity map

The reference observable is a smooth scalar field constructed from several Gaussian anomalies. It acts as a stand-in for a gravity-gradient map:

`z = h(p_x, p_y) + noise`

The EKF linearizes this measurement using the spatial gradient of the map:

`H = [dh/dx, dh/dy, 0, 0, 0, 0]`

This is enough to demonstrate nonlinear environmental map matching.

## Why a synthetic field?

Using a synthetic map makes the demo self-contained, reproducible, and explicit about what is being tested: state estimation architecture. A later version can replace this with public gravity/geopotential data.

## Limitations

- 2D kinematics rather than full 6-DOF strapdown INS.
- No Earth rotation, transport rate, Coriolis, coning/sculling, or ellipsoidal frame transformations.
- Synthetic gravity observable rather than validated Eotvos-unit gravity-gradient data.
- Simplified accelerometer model and no gyroscope channel.
- No cold-atom dead time, vibration rejection, laser phase noise, or platform-coupling model.
- EKF only; no particle filter, factor graph, or batch smoother.

These limitations are deliberate and keep the first release focused on one testable concept: can an external spatial field constrain inertial drift in a reproducible simulation?
