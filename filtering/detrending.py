"""
Smoothness Priors Approach (SPA) Detrending Module
Removes low-frequency baseline drift and respiration wander without distorting the optical AC pulsatile component.
"""

import numpy as np
from scipy import sparse
import scipy.sparse.linalg

def detrend_smoothness_priors(signal_1d, lambda_param=100):
    """
    Applies the Smoothness Priors Approach (Tarvainen et al., 2002) using sparse linear system solvers.
    
    Args:
        signal_1d: 1D signal vector.
        lambda_param: Regularization smoothing parameter (default: 100).
        
    Returns:
        Detrended stationary 1D signal.
    """
    t_len = len(signal_1d)
    if t_len < 3:
        return signal_1d
        
    i_mat = sparse.eye(t_len, format='csr')
    d2_mat = sparse.diags([1, -2, 1], [0, 1, 2], shape=(t_len - 2, t_len), format='csr')
    
    # Solve (I + lambda^2 * D2.T * D2) * z_trend = signal
    a_mat = i_mat + (lambda_param ** 2) * (d2_mat.T.dot(d2_mat))
    trend = scipy.sparse.linalg.spsolve(a_mat, signal_1d)
    
    return signal_1d - trend
