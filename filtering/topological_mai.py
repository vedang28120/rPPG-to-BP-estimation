"""
Topological Signal Processing & Melanin Absorption Invariance (MAI) Framework
Reference: Wang et al., IEEE TBME / Nature Digital Medicine (Topological Invariance in Photoplethysmography).
Implements Takens' Delay Embedding, Phase-Space Attractor Reconstruction, Topologically Invariant Metrics (f1-f5),
Recurrence Quantification Analysis (RQA), and SNR-Adaptive Scaling to eliminate skin-tone and gain bias.
"""

import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import pdist, squareform

def takens_delay_embedding(signal_1d, m=3, tau=2):
    """
    Reconstructs the multi-dimensional phase-space attractor from a 1D scalar signal
    using Takens' Delay Embedding Theorem.
    
    Args:
        signal_1d: Normalized 1D array of length N.
        m: Embedding dimension (default: 3, satisfying m >= 2d_A + 1).
        tau: Delay lag in samples (default: 2 samples, ~16ms at 125 Hz).
        
    Returns:
        X: Phase-space trajectory matrix of shape (N - (m-1)*tau, m).
    """
    n = len(signal_1d)
    n_vectors = n - (m - 1) * tau
    if n_vectors <= 0:
        raise ValueError(f"Signal length {n} is too short for embedding dimension {m} and delay {tau}.")
        
    x_mat = np.empty((n_vectors, m), dtype=np.float32)
    for j in range(m):
        x_mat[:, j] = signal_1d[j * tau : j * tau + n_vectors]
        
    return x_mat

def extract_topological_features(signal_1d, fs=125.0, m=3, tau=2, k_neighbors=5, snr_db=None):
    """
    Extracts topologically invariant dynamical features (f1 to f5) and RQA metrics from the phase-space attractor.
    
    Args:
        signal_1d: 1D normalized physiological signal (BVP/PPG).
        fs: Sampling frequency in Hz.
        m: Embedding dimension.
        tau: Delay lag in samples.
        k_neighbors: Number of nearest neighbors for density estimation.
        snr_db: Optional measured SNR in dB for adaptive noise compensation.
        
    Returns:
        feature_dict: Dictionary containing:
            - 'f1': Mean 1st nearest-neighbor distance (attractor density).
            - 'f2': Mean 2nd nearest-neighbor distance.
            - 'f3': Mean log nearest-neighbor distance (manifold local dimension).
            - 'f4': First PCA eigenvalue (principal attractor variance).
            - 'f5': PCA principal rotation angle (orientation in radians).
            - 'rqa_determinism': Recurrence Determinism (RD - percentage of recurrent points forming diagonal lines).
            - 'rqa_laminarity': Laminarity (TT - vertical line recurrence).
            - 'rqa_entropy': Shannon entropy of diagonal line length distribution.
            - 'topological_vector': 8-element feature vector ready for regression fusion.
    """
    # 1. Standardize signal to zero mean, unit variance (Z-normalization cancels multiplicative melanin attenuation)
    s = (signal_1d - np.mean(signal_1d)) / (np.std(signal_1d) + 1e-8)
    
    # 2. Phase-space embedding
    x_emb = takens_delay_embedding(s, m=m, tau=tau)
    
    # 3. Nearest-Neighbor distance metrics (f1, f2, f3)
    nbrs = NearestNeighbors(n_neighbors=min(k_neighbors + 1, len(x_emb)), algorithm='ball_tree').fit(x_emb)
    distances, _ = nbrs.kneighbors(x_emb)
    # Exclude distance to self (index 0)
    d1 = distances[:, 1]
    d2 = distances[:, 2] if distances.shape[1] > 2 else d1
    
    f1 = float(np.mean(d1))
    f2 = float(np.mean(d2))
    f3 = float(np.mean(np.log(d1 + 1e-8)))
    
    # 4. PCA on Attractor Manifold (f4, f5)
    pca = PCA(n_components=min(m, 3))
    pca.fit(x_emb)
    
    f4 = float(pca.explained_variance_[0])  # First eigenvalue
    # Principal axis orientation angle in the first 2 principal components
    comp0 = pca.components_[0]
    f5 = float(np.arctan2(comp0[1], comp0[0]))
    
    # 5. Recurrence Quantification Analysis (RQA)
    # Subsample attractor if long to compute RQA efficiently
    subsample_len = min(len(x_emb), 300)
    indices = np.linspace(0, len(x_emb) - 1, subsample_len, dtype=int)
    x_sub = x_emb[indices]
    
    dist_matrix = squareform(pdist(x_sub, metric='euclidean'))
    # Adaptive recurrence threshold: 10% of mean attractor diameter
    eps = 0.1 * np.mean(dist_matrix)
    rec_matrix = (dist_matrix <= eps).astype(int)
    
    # Compute Recurrence Rate (RR)
    rr = float(np.sum(rec_matrix) - subsample_len) / float(subsample_len * (subsample_len - 1) + 1e-8)
    
    # Compute Diagonal Line Lengths for Determinism (RD)
    diags = [np.diagonal(rec_matrix, offset=i) for i in range(1, subsample_len)]
    diag_lengths = []
    for d in diags:
        # Find consecutive ones of length >= 2
        length = 0
        for val in d:
            if val == 1:
                length += 1
            else:
                if length >= 2:
                    diag_lengths.append(length)
                length = 0
        if length >= 2:
            diag_lengths.append(length)
            
    num_recurrent_diag_points = sum(diag_lengths) if diag_lengths else 0
    total_recurrent_points = np.sum(rec_matrix) - subsample_len
    rqa_determinism = float(num_recurrent_diag_points) / float(total_recurrent_points + 1e-8)
    rqa_determinism = min(1.0, max(0.0, rqa_determinism))
    
    # Shannon entropy of diagonal lengths
    if diag_lengths:
        counts = np.bincount(diag_lengths)
        probs = counts[counts > 0] / float(len(diag_lengths))
        rqa_entropy = float(-np.sum(probs * np.log2(probs + 1e-8)))
    else:
        rqa_entropy = 0.0
        
    rqa_laminarity = float(np.mean(rec_matrix))
    
    # 6. SNR-Adaptive Scaling: hat{f} = (1 + k / SNR_eff) * f
    if snr_db is not None:
        snr_linear = max(10.0 ** (snr_db / 10.0), 0.1)
        k_const = 0.5
        g_snr = 1.0 + (k_const / snr_linear)
        f1 *= g_snr
        f2 *= g_snr
        f3 *= g_snr
        f4 *= g_snr
        
    feat_vector = np.array([f1, f2, f3, f4, f5, rqa_determinism, rqa_laminarity, rqa_entropy], dtype=np.float32)
    
    return {
        "f1": f1,
        "f2": f2,
        "f3": f3,
        "f4": f4,
        "f5": f5,
        "rqa_determinism": rqa_determinism,
        "rqa_laminarity": rqa_laminarity,
        "rqa_entropy": rqa_entropy,
        "topological_vector": feat_vector
    }
