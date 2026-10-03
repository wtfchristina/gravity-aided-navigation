from __future__ import annotations

import numpy as np

from .gravity_tensor import SyntheticGravityTensorMap


class TensorGravityAidedEKF:
    """EKF state [x, y, vx, vy, bax, bay] with tensor-map measurements."""

    def __init__(self, x0: np.ndarray, P0: np.ndarray, gravity_map: SyntheticGravityTensorMap,
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
            x + vx * dt + 0.5 * ax * dt**2,
            y + vy * dt + 0.5 * ay * dt**2,
            vx + ax * dt,
            vy + ay * dt,
            bax, bay,
        ])

        F = np.eye(6)
        F[0, 2] = dt; F[1, 3] = dt
        F[0, 4] = -0.5 * dt**2; F[1, 5] = -0.5 * dt**2
        F[2, 4] = -dt; F[3, 5] = -dt

        G = np.zeros((6, 4))
        G[0, 0] = 0.5 * dt**2; G[1, 1] = 0.5 * dt**2
        G[2, 0] = dt; G[3, 1] = dt
        G[4, 2] = np.sqrt(dt); G[5, 3] = np.sqrt(dt)
        q = np.diag([
            self.accel_noise_std**2,
            self.accel_noise_std**2,
            self.bias_rw_std**2,
            self.bias_rw_std**2,
        ])
        self.P = F @ self.P @ F.T + G @ q @ G.T

    def update_component(self, component: str, z_e: float, noise_std_e: float):
        px, py = float(self.x[0]), float(self.x[1])
        h = float(self.map.component(component, px, py))
        grad = self.map.jacobian_component(component, px, py)
        H = np.zeros((1, 6))
        H[0, :2] = grad
        R = np.array([[noise_std_e**2]])
        innov = np.array([z_e - h])
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + (K @ innov).ravel()
        I = np.eye(6)
        self.P = (I - K @ H) @ self.P @ (I - K @ H).T + K @ R @ K.T
