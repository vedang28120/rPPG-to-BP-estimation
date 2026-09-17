"""
report_sections/chapter2.py
===========================
Chapter 02: Vocational Training Curriculum & Theoretical Foundations
"""

import docx
from docx.shared import Inches, Pt, RGBColor

def build_chapter2(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p, add_table_custom):
    add_heading_chapter(doc, "CHAPTER-02", "VOCATIONAL TRAINING CURRICULUM & THEORETICAL FOUNDATIONS")
    
    add_body_p(doc, "During the intensive Vocational Training on 'AI with Python' conducted under the supervision of Dr. Anurag Singh at IIIT Naya Raipur, a comprehensive theoretical and practical curriculum was completed. This chapter provides a rigorous academic, mathematical, and algorithmic synthesis of the computational principles, statistical machine learning models, deep neural network architectures, and modern agentic artificial intelligence frameworks mastered during the training period.")

    # ---------------------------------------------------------
    # 2.1 Scientific Computing Foundations in Python
    # ---------------------------------------------------------
    add_heading_sub1(doc, "2.1 Scientific Computing Foundations in Python")
    add_body_p(doc, "Python has established itself as the lingua franca of modern scientific computing and artificial intelligence owing to its elegant syntax, dynamic typing model, and mature ecosystem of high-performance C-accelerated numerical libraries. Biomedical signal processing and computer vision pipelines demand high-throughput data structures capable of executing multi-dimensional tensor operations with minimal computational overhead.")

    add_heading_sub2(doc, "2.1.1 The NumPy Numerical Architecture")
    add_body_p(doc, "NumPy (Numerical Python) forms the foundational layer for numerical computing. Central to NumPy is the N-dimensional array object (ndarray), which encapsulates contiguous blocks of homogeneous data in memory. Unlike standard Python lists that store pointers to boxed objects, NumPy arrays provide direct, strided memory access that enables Single Instruction, Multiple Data (SIMD) hardware acceleration.")
    add_body_p(doc, "Key mathematical mechanisms in NumPy include:")
    add_bullet_p(doc, "Vectorization: Vectorized execution replaces explicit iterative loops in Python with highly optimized C-level loops, executing element-wise arithmetic across large arrays orders of magnitude faster.", bold_prefix="• ")
    add_bullet_p(doc, "Broadcasting Rules: Broadcasting defines how NumPy handles arithmetic operations between arrays of differing shapes. An array of shape (N, 1) can be seamlessly combined with an array of shape (1, M) to yield an (N, M) matrix without explicit memory duplication, governed by dimension compatibility checks from trailing dimensions.", bold_prefix="• ")
    add_bullet_p(doc, "Linear Algebra (numpy.linalg): Provides optimized BLAS/LAPACK bindings for matrix inversion, singular value decomposition (SVD), eigenvalue decomposition, and Fourier transforms.", bold_prefix="• ")

    add_heading_sub2(doc, "2.1.2 Pandas for Biomedical Time-Series Data")
    add_body_p(doc, "Pandas provides high-level data structures—namely the 1D Series and 2D DataFrame—specifically designed for structured, labeled, and multi-rate time-series datasets. In physiological sensing, different sensors operate at asynchronous sampling frequencies (e.g., video at 30 FPS, reference contact PPG at 125 Hz, and Continuous Glucose Monitoring at 5-minute intervals).")
    add_body_p(doc, "Core operations include:")
    add_bullet_p(doc, "Datetime Indexing and Temporal Alignment: DatetimeIndex enables millisecond-precision alignment, nearest-neighbor timestamp matching, and synchronized multi-sensor joining.", bold_prefix="• ")
    add_bullet_p(doc, "Resampling and Frequency Conversion: The .resample() method permits upsampling (with cubic spline or linear interpolation) and downsampling (with anti-aliasing aggregations).", bold_prefix="• ")
    add_bullet_p(doc, "Rolling Window Transformations: The .rolling(window=W) construct allows continuous computation of rolling statistics (mean, variance, standard deviation) essential for baseline drift tracking.", bold_prefix="• ")

    add_heading_sub2(doc, "2.1.3 Matplotlib and Seaborn for Biomedical Visualization")
    add_body_p(doc, "Visualizing complex multidimensional physiological signals is critical for diagnostic validation. Matplotlib’s object-oriented API (Figure and Axes objects) enables precise layout customization, multi-panel waveform plots, and publication-ready vector rendering. Seaborn builds upon Matplotlib to provide statistical data visualization, including correlation heatmaps, kernel density estimation (KDE) distributions, and categorical regression plots.")

    # ---------------------------------------------------------
    # 2.2 Data Preprocessing, Cleaning & Statistical Conditioning
    # ---------------------------------------------------------
    add_heading_sub1(doc, "2.2 Data Preprocessing, Cleaning & Statistical Conditioning")
    add_body_p(doc, "Raw biomedical data is inherently non-stationary, contaminated by ambient sensor drift, motion artifacts, missing records, and high-frequency electronic noise. Preprocessing transforms raw sensory measurements into clean, normalized signals suitable for machine learning.")

    add_heading_sub2(doc, "2.2.1 Missing Value Imputation and Outlier Detection")
    add_body_p(doc, "Missing sensor records are addressed through forward/backward filling for short gaps or piecewise cubic Hermite interpolating polynomials (PCHIP) for physiological continuity. Outliers caused by sensor detachment are detected using statistical thresholds:")
    add_bullet_p(doc, "Z-Score Gating: Samples where |z| > 3, where z = (x - μ) / σ, are flagged and replaced or suppressed.", bold_prefix="• ")
    add_bullet_p(doc, "Tukey’s Interquartile Range (IQR): Values falling outside [Q1 - 1.5·IQR, Q3 + 1.5·IQR] are bounded to prevent gradient explosion during neural training.", bold_prefix="• ")

    add_heading_sub2(doc, "2.2.2 Feature Scaling and Normalization")
    add_body_p(doc, "To prevent features with large numeric ranges from dominating gradient updates, scaling transformations are applied:")
    add_bullet_p(doc, "Min-Max Normalization: Rescales values to the interval [0, 1]:\n   X_norm = (X - X_min) / (X_max - X_min)", bold_prefix="• ")
    add_bullet_p(doc, "Standardization (Z-Score): Centers data to zero mean and unit variance:\n   X_std = (X - μ) / σ", bold_prefix="• ")

    add_heading_sub2(doc, "2.2.3 Digital Filtering & The Savitzky-Golay Polynomial Smoothing Filter")
    add_body_p(doc, "Traditional low-pass infinite impulse response (IIR) filters (such as Butterworth filters) reduce high-frequency noise but often distort peak amplitudes and broaden sharp morphological transitions. The Savitzky-Golay filter addresses this by fitting a local polynomial of degree k across a moving window of length 2m + 1 points using linear least-squares regression.")
    add_body_p(doc, "Mathematically, the smoothed output g_i at point i is expressed as a convolution with precomputed coefficients c_n:\n   g_i = ∑_{n = -m}^{m} c_n · x_{i+n}")
    add_body_p(doc, "Because the convolution weights c_n correspond directly to the least-squares polynomial solution, the Savitzky-Golay filter preserves higher-order moments (peak height, pulse width, and inflection points). This property is vital in optical hemodynamics, where preserving the dicrotic notch and systolic upstroke gradient is essential for accurate blood pressure estimation.")

    # ---------------------------------------------------------
    # 2.3 Machine Learning Taxonomy & Mathematical Core
    # ---------------------------------------------------------
    add_heading_sub1(doc, "2.3 Machine Learning Taxonomy & Mathematical Core")
    add_body_p(doc, "Machine learning models learn functional mappings f: X → Y from empirical training data without being explicitly programmed.")

    add_heading_sub2(doc, "2.3.1 Paradigms of Machine Learning")
    add_bullet_p(doc, "Supervised Learning: The algorithm learns from paired input-target instances (x_i, y_i). Tasks include continuous regression (e.g., blood pressure, blood glucose) and discrete classification (e.g., normotensive vs. hypertensive).", bold_prefix="1. ")
    add_bullet_p(doc, "Unsupervised Learning: The algorithm discovers latent structures, clusters, or lower-dimensional representations from unlabeled inputs x_i (e.g., Principal Component Analysis, Independent Component Analysis, K-Means clustering).", bold_prefix="2. ")
    add_bullet_p(doc, "Semi-Supervised Learning: Leverages a large volume of unlabeled data combined with a small subset of labeled data to enhance representation learning.", bold_prefix="3. ")
    add_bullet_p(doc, "Reinforcement Learning: An autonomous agent interacts with an environment through a Markov Decision Process (MDP), learning an optimal policy π(a|s) to maximize cumulative discounted rewards R = ∑ γ^t r_t.", bold_prefix="4. ")

    add_heading_sub2(doc, "2.3.2 The Bias-Variance Tradeoff and Generalization")
    add_body_p(doc, "In statistical learning theory, the expected test mean squared error of a regression estimator f̂(x) decomposes into three distinct components:\n   E[(y - f̂(x))^2] = Bias^2[f̂(x)] + Var[f̂(x)] + σ_ε^2")
    add_body_p(doc, "where Bias[f̂(x)] = E[f̂(x)] - f(x) represents the error from erroneous model assumptions (leading to underfitting), Var[f̂(x)] = E[(f̂(x) - E[f̂(x)])^2] represents sensitivity to small fluctuations in the training set (leading to overfitting), and σ_ε^2 is the irreducible noise floor. The objective of hyperparameter tuning and model regularization is to locate the optimal capacity that minimizes total generalization error.")

    add_heading_sub2(doc, "2.3.3 Validation Strategies & Leave-One-Subject-Out (LOSO)")
    add_body_p(doc, "Evaluating models on biomedical signals requires strict partitioning protocols to prevent data leakage. In K-Fold Cross-Validation, the dataset is split into K equal partitions, iteratively training on K-1 folds and testing on the remaining fold. However, when multiple windows originate from the same subject, standard K-Fold causes severe subject leakage. To establish genuine clinical generalizability, Leave-One-Subject-Out (LOSO) cross-validation is employed, wherein all records from a given individual are strictly withheld from training.")

    add_heading_sub2(doc, "2.3.4 Regression Algorithms and Regularization")
    add_body_p(doc, "Regression models estimate continuous physiological variables:")
    add_bullet_p(doc, "Linear Regression (Ordinary Least Squares): Models y = Xw + b by minimizing ||y - Xw||_2^2, solved via normal equations w = (X^T X)^{-1} X^T y or gradient descent.", bold_prefix="• ")
    add_bullet_p(doc, "Polynomial Regression: Extends linear models by mapping inputs into higher-order polynomial feature spaces Φ(x) = [1, x, x^2, ..., x^d].", bold_prefix="• ")
    add_bullet_p(doc, "Ridge Regression (L2 Regularization): Adds a quadratic penalty term λ||w||_2^2 to shrink weights toward zero, preventing multicollinearity.", bold_prefix="• ")
    add_bullet_p(doc, "Lasso Regression (L1 Regularization): Adds an absolute penalty λ||w||_1, driving non-informative coefficients to exactly zero to perform automated feature selection.", bold_prefix="• ")
    add_bullet_p(doc, "ElasticNet: Combines L1 and L2 penalties via α||w||_1 + (1-α)||w||_2^2 to balance sparsity with correlated group selection.", bold_prefix="• ")
    add_bullet_p(doc, "Logistic Regression: Formulates binary classification by passing linear combinations through the sigmoid logistic function σ(z) = 1 / (1 + e^{-z}), trained using binary cross-entropy loss.", bold_prefix="• ")

    add_heading_sub2(doc, "2.3.5 Performance Evaluation Metrics")
    add_body_p(doc, "Quantitative assessment of model performance utilizes distinct statistical metrics for classification and regression tasks, as summarized in Table 2.1.")

    t21_headers = ["Metric Category", "Metric Name", "Mathematical Formulation", "Clinical / Analytical Interpretation"]
    t21_rows = [
        ["Regression", "MAE", "MAE = (1/n) ∑ |y_i - ŷ_i|", "Average magnitude of absolute error; robust to extreme outliers."],
        ["Regression", "RMSE", "RMSE = √[(1/n) ∑ (y_i - ŷ_i)^2]", "Square root of variance of residuals; heavily penalizes large errors."],
        ["Regression", "Pearson r", "r = ∑(y_i - ȳ)(ŷ_i - ȳ̂) / [√∑(y_i - ȳ)^2 √∑(ŷ_i - ȳ̂)^2]", "Measures linear tracking and correlation; tests true physiological sensitivity."],
        ["Regression", "R² Score", "R² = 1 - [∑(y_i - ŷ_i)^2 / ∑(y_i - ȳ)^2]", "Proportion of target variance explained by the model."],
        ["Classification", "Accuracy", "Acc = (TP + TN) / (TP + TN + FP + FN)", "Overall proportion of correct classifications."],
        ["Classification", "Precision", "Prec = TP / (TP + FP)", "Reliability of positive predictions (minimizes false alarms)."],
        ["Classification", "Recall (Sens.)", "Rec = TP / (TP + FN)", "Ability to identify positive cases (vital for disease screening)."],
        ["Classification", "F1-Score", "F1 = 2 · (Prec · Rec) / (Prec + Rec)", "Harmonic mean of precision and recall for imbalanced cohorts."]
    ]
    add_table_custom(doc, "2.1", "Machine Learning Performance Metrics Mathematical Summary", t21_headers, t21_rows, col_widths=[1.1, 1.1, 2.2, 2.0])

    # ---------------------------------------------------------
    # 2.4 Deep Learning Architectures & Optimization
    # ---------------------------------------------------------
    add_heading_sub1(doc, "2.4 Deep Learning Architectures & Optimization")
    add_body_p(doc, "Deep Learning replaces hand-crafted feature extraction with end-to-end hierarchical representation learning directly from raw or minimally preprocessed time series and spatial images.")

    add_heading_sub2(doc, "2.4.1 Feedforward Deep Neural Networks & Activation Functions")
    add_body_p(doc, "A Deep Neural Network (DNN) transforms an input vector x through successive affine transformations and element-wise non-linear activations:\n   z^{[l]} = W^{[l]} a^{[l-1]} + b^{[l]},   a^{[l]} = g^{[l]}(z^{[l]})")
    add_body_p(doc, "Non-linear activation functions g(·) enable neural networks to approximate arbitrary continuous functions. Table 2.2 details the core activations used across modern architectures.")

    t22_headers = ["Activation Function", "Mathematical Formulation", "Range", "Key Characteristics & Application"]
    t22_rows = [
        ["Sigmoid (σ)", "σ(z) = 1 / (1 + e^{-z})", "(0, 1)", "Smooth probability mapping; susceptible to vanishing gradient."],
        ["Hyperbolic Tangent (tanh)", "tanh(z) = (e^z - e^{-z}) / (e^z + e^{-z})", "(-1, 1)", "Zero-centered; preferred in recurrent cell state candidate gating."],
        ["Rectified Linear Unit (ReLU)", "ReLU(z) = max(0, z)", "[0, ∞)", "Fast computation, non-saturating gradients; default in CNNs."],
        ["Leaky ReLU", "LReLU(z) = max(αz, z), α≈0.01", "(-∞, ∞)", "Prevents dying ReLU neurons by maintaining small gradient for z<0."],
        ["Softmax", "σ(z)_i = e^{z_i} / ∑_j e^{z_j}", "(0, 1)", "Multi-class probability distribution normalization across output logits."]
    ]
    add_table_custom(doc, "2.2", "Deep Learning Layer Activations and Mathematical Functions", t22_headers, t22_rows, col_widths=[1.4, 1.8, 0.8, 2.4])

    add_heading_sub2(doc, "2.4.2 Backpropagation and Gradient Descent Optimization")
    add_body_p(doc, "Deep networks are trained by computing the partial derivatives of an empirical loss function L with respect to all trainable weights W and biases b using the multivariate chain rule:\n   ∂L / ∂W^{[l]} = (∂L / ∂z^{[l]}) · (a^{[l-1]})^T\n   ∂L / ∂z^{[l-1]} = (W^{[l]})^T (∂L / ∂z^{[l]}) ⊙ g'^{[l-1]}(z^{[l-1]})")
    add_body_p(doc, "Weight updates are governed by advanced optimizers, notably Adam (Adaptive Moment Estimation) and AdamW (which decouples L2 weight decay from gradient moment accumulation), maintaining exponential moving averages of first (m_t) and second (v_t) gradient moments.")

    add_heading_sub2(doc, "2.4.3 Convolutional Neural Networks (CNNs) and 1D-ResNets")
    add_body_p(doc, "Convolutional Neural Networks utilize discrete convolution kernels that slide across spatial or temporal dimensions, enforcing local connectivity and translation invariance. For 1D physiological time-series x ∈ R^{T × C_{in}}, the 1D convolution produces feature maps:\n   y_k(t) = ∑_{c=1}^{C_{in}} ∑_{τ=-K/2}^{K/2} x_c(t + τ) · w_{k,c}(τ) + b_k")
    add_body_p(doc, "To train deep architectures without gradient degradation, Deep Residual Networks (ResNets) introduce identity shortcut connections:\n   y = F(x, {W_i}) + x")
    add_body_p(doc, "These residual pathways allow gradients to flow directly through the identity mappings during backpropagation, enabling effective feature extraction across deep multi-layer backbones.")

    add_heading_sub2(doc, "2.4.4 Recurrent Neural Networks (RNN), LSTM, and BiGRU")
    add_body_p(doc, "Standard feedforward networks lack temporal memory. Recurrent Neural Networks (RNNs) maintain an internal hidden state h_t = tanh(W_{hh} h_{t-1} + W_{xh} x_t + b_h). However, standard RNNs suffer from vanishing and exploding gradients over long temporal sequences.")
    add_body_p(doc, "Long Short-Term Memory (LSTM) networks overcome this via specialized gating units:")
    add_bullet_p(doc, "Forget Gate: f_t = σ(W_f · [h_{t-1}, x_t] + b_f) — decides what information to discard from the cell state.", bold_prefix="1. ")
    add_bullet_p(doc, "Input Gate: i_t = σ(W_i · [h_{t-1}, x_t] + b_i) and Candidate: C̃_t = tanh(W_c · [h_{t-1}, x_t] + b_c) — regulates new information.", bold_prefix="2. ")
    add_bullet_p(doc, "Cell State Update: C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t — linear error carousel preserving long-term gradient flow.", bold_prefix="3. ")
    add_bullet_p(doc, "Output Gate: o_t = σ(W_o · [h_{t-1}, x_t] + b_o) and Hidden State: h_t = o_t ⊙ tanh(C_t).", bold_prefix="4. ")
    add_body_p(doc, "Bidirectional Gated Recurrent Units (BiGRU) streamline the LSTM architecture into two gates (Reset r_t and Update z_t) and execute both forward and backward temporal passes, concatenating directional hidden states h_t = [h⃗_t; h⃖_t] to capture bidirectional context.")

    add_heading_sub2(doc, "2.4.5 Self-Attention and Multi-Head Attention (MHSA)")
    add_body_p(doc, "While recurrent layers process tokens sequentially, Self-Attention mechanisms compute direct pairwise associations across all time steps. Given query (Q), key (K), and value (V) matrices projected from input embeddings, the Scaled Dot-Product Attention is computed as:\n   Attention(Q, K, V) = softmax( (Q K^T) / √d_k ) · V")
    add_body_p(doc, "Multi-Head Self-Attention (MHSA) extends this by projecting inputs into h distinct representation subspaces, allowing the model to simultaneously attend to systolic rise phases, dicrotic reflections, and global baseline variations.")

    # ---------------------------------------------------------
    # 2.5 Advanced AI Frontiers: NLP, Transformers, RAG & Agentic Systems
    # ---------------------------------------------------------
    add_heading_sub1(doc, "2.5 Advanced AI Frontiers: NLP, Transformers, RAG & Agentic Systems")
    add_body_p(doc, "The training program encompassed cutting-edge developments in Natural Language Processing (NLP), generative foundation models, vector embeddings, and autonomous agent orchestration.")

    add_heading_sub2(doc, "2.5.1 NLP Fundamentals, NLTK, and Distributed Word Representations")
    add_body_p(doc, "Text processing pipelines employ tokenization, stop-word elimination, stemming, and lemmatization (using NLTK). To transform discrete lexical tokens into continuous vector spaces, distributed representations were explored:")
    add_bullet_p(doc, "Word2Vec: Continuous Bag-of-Words (CBOW) predicts a target word from context tokens, while Continuous Skip-Gram predicts context tokens from a center word using negative sampling optimization.", bold_prefix="• ")
    add_bullet_p(doc, "GloVe (Global Vectors): Factorizes global word-word co-occurrence matrix log-probabilities to capture linear substructures in semantic vector spaces.", bold_prefix="• ")

    add_heading_sub2(doc, "2.5.2 Transformers, Encoders, and Large Language Models (LLMs)")
    add_body_p(doc, "The Transformer architecture replaces recurrent connections entirely with multi-head attention and positional encodings. Bidirectional encoder models (e.g., BERT) generate contextual embeddings for semantic understanding, while autoregressive causal decoders (e.g., GPT family, LLaMA) power generative reasoning. Fine-tuning open models via Parameter-Efficient Fine-Tuning (PEFT/LoRA) adapts large models to domain-specific biomedical tasks with low GPU compute.")

    add_heading_sub2(doc, "2.5.3 Retrieval-Augmented Generation (RAG) Architecture")
    add_body_p(doc, "Retrieval-Augmented Generation (RAG) mitigates hallucination in generative models by dynamically retrieving relevant factual documents from an external vector index. Given an input query, embedding models project the text into a latent embedding space, where Cosine Similarity:\n   cos(θ) = (u · v) / (||u||_2 · ||v||_2)\nidentifies top-k nearest semantic chunks. The retrieved knowledge is injected into the LLM context prompt, enabling grounded, traceable, and up-to-date responses.")

    add_heading_sub2(doc, "2.5.4 Agentic AI Systems, Tools, JSON Schemas, and Model Context Protocol (MCP)")
    add_body_p(doc, "Agentic AI transitions language models from passive text generators into autonomous decision-making agents capable of multi-step planning, tool invocation, environment inspection, and iterative problem solving:")
    add_bullet_p(doc, "Reasoning Loops (ReAct Paradigm): Agents interleave Thought (reasoning), Action (tool call), and Observation (environment feedback) cycles to resolve complex engineering tasks.", bold_prefix="• ")
    add_bullet_p(doc, "Structured Tool Calling via JSON Schemas: External function specifications and API contracts are declared via strict JSON schemas, allowing models to emit validated JSON arguments.", bold_prefix="• ")
    add_bullet_p(doc, "Model Context Protocol (MCP): An open architectural standard defining how AI clients, IDEs, and agents discover, connect to, and execute external tools, file repositories, and context servers.", bold_prefix="• ")
    add_bullet_p(doc, "Framework Orchestration (LangChain): Provides modular abstractions for chaining prompts, memory buffers, vector retrieval chains, and autonomous multi-agent systems.", bold_prefix="• ")
