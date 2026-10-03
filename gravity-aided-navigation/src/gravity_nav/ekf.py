from __future__ import annotations

import numpy as np

from .gravity_map import SyntheticGravityMap


class GravityAidedEKF:
    """EKF state: [x, y, vx, vy, bax, bay]."""

    def __init__(self, x0: np.ndarray, P0: np.ndarray, gravity_map: SyntheticGravityMap,
                 accel_noise_std: float = 0.03, bias_rw_std: float = 8e-4):
        self.x = np.array(x0, dtype=float)
        self.P = np.array(P0, dtype=float)
        self.map = gravity_map
        self.accel_noise_std = accel_noise_std
        self.bias_rw_std = bias_rw_std

    def predict(self, imu_accel: np.ndarray, dt: float):
        x, y, vx, vy, bax, bay = self.x
        ax = imu_accel[0] - bax
        ay = imu_accel[1] - bay

        self.x = np.array([
            x + vx * dt + 0.5 * ax * dt * dt,
            y + vy * dt + 0.5 * ay * dt * dt,
            vx + ax * dt,
            vy + ay * dt,
            bax,
            bay,
        ])

        F = np.eye(6)
        F[0, 2] = dt
        F[1, 3] = dt
        F[0, 4] = -0.5 * dt * dt
        F[1, 5] = -0.5 * dt * dt
        F[2, 4] = -dt
        F[3, 5] = -dt

        G = np.zeros((6, 4))
        G[0, 0] = 0.5 * dt * dt
        G[1, 1] = 0.5 * dt * dt
        G[2, 0] = dt
        G[3, 1] = dt
        G[4, 2] = np.sqrt(dt)
        G[5, 3] = np.sqrt(dt)
        q = np.diag([
            self.accel_noise_std**2,
            self.accel_noise_std**2,
            self.bias_rw_std**2,
            self.bias_rw_std**2,
        ])
        self.P = F @ self.P @ F.T + G @ q @ G.T

    def update_gravity(self, z: float, noise_std: float):
        px, py = self.x[0], self.x[1]
        h = float(self.map.value(px, py))
        grad = self.map.gradient(px, py)

        H = np.zeros((1, 6))
        H[0, 0] = grad[0]
        H[0, 1] = grad[1]

        R = np.array([[noise_std**2]])
        innovation = np.array([z - h])
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + (K @ innovation).ravel()

        I = np.eye(6)
        KH = K @ H
        self.P = (I - KH) @ self.P @ (I - KH).T + K @ R @ K.T
