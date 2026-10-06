from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class AffineMapError:
    base_map: object
    bias: float = 0.0
    scale_error: float = 0.0
    noise_std: float = 0.0
    seed: int = 0
    @property
    def name(self): return f'{getattr(self.base_map,"name","field")}_perturbed'
    @property
    def units(self): return getattr(self.base_map,'units','arb')
    def value(self,x,y):
        v=np.asarray(self.base_map.value(x,y),float)
        # deterministic pseudo-map error as a smooth spatial field, not per-call white noise
        if self.noise_std:
            perturb=self.noise_std*np.sin(np.asarray(x,float)/3500.0+0.31*self.seed)*np.cos(np.asarray(y,float)/2700.0-0.17*self.seed)
        else: perturb=0.0
        out=(1+self.scale_error)*v+self.bias+perturb
        return float(out) if np.ndim(out)==0 else out
    def gradient(self,x,y,step_m=25.0):
        h=float(step_m)
        return np.array([(self.value(x+h,y)-self.value(x-h,y))/(2*h),(self.value(x,y+h)-self.value(x,y-h))/(2*h)],float)
