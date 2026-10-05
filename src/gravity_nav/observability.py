from __future__ import annotations
import numpy as np


def scalar_information(field, noise_std: float, x, y, step_m: float = 25.0):
    """Approximate local position information ||grad h||^2 / sigma^2."""
    xa=np.asarray(x,dtype=float); ya=np.asarray(y,dtype=float)
    gx=(field.value(xa+step_m,ya)-field.value(xa-step_m,ya))/(2*step_m)
    gy=(field.value(xa,ya+step_m)-field.value(xa,ya-step_m))/(2*step_m)
    return (gx*gx+gy*gy)/max(float(noise_std)**2,1e-18)


def combined_information(fields_and_noise, x, y, step_m: float = 25.0):
    out=np.zeros(np.broadcast(np.asarray(x),np.asarray(y)).shape,dtype=float)
    for field,noise in fields_and_noise:
        out += scalar_information(field,noise,x,y,step_m)
    return out


def normalized_score(info):
    a=np.asarray(info,dtype=float)
    lo=float(np.nanpercentile(a,5)); hi=float(np.nanpercentile(a,95))
    if hi<=lo: return np.zeros_like(a)
    return np.clip((a-lo)/(hi-lo),0,1)
