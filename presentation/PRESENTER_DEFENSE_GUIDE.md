# Presenter's Master Defense & Technical Cue Sheet

## Vocational Training ("AI with Python" @ IIIT-NR) & Proposed Capstone Presentation
**Researchers & Presenters:**
1. **Vedang Bhatt** (B. Tech. Computer Science & Engineering, 4th Semester)
2. **Anubhav Shrivastav** (B. Tech. Computer Science & Engineering, 4th Semester)
3. **Aadarsh** (B. Tech. Computer Science & Engineering, 4th Semester)

**Parent Institution:** Department of Computer Science & Engineering, Bhilai Institute of Technology (BIT), Raipur  
**Training Host Institution:** International Institute of Information Technology, Naya Raipur (IIIT-NR)  
**Training Program:** Vocational Training on *"AI with Python"* (01/07/2026 to 10/08/2026)  
**Mentors & Guides:**
* **VT Mentor (IIIT-NR):** Dr. Anurag Singh
* **College Mentor (BIT Raipur):** Prof. Aparna Pandey

**Proposed Project Title:** *Mobile Remote Photoplethysmography (rPPG) to Cuffless Blood Pressure Estimation*  
**Presentation Framework:** Humble, Respectful, Academic, and Factually Grounded

---

## 1. Presentation Time Management Matrix

| Format | Duration | Focus / Key Deliverable | Slide Emphasis |
|:---|:---:|:---|:---|
| **VT Defense / Committee Review** | **12–15 Mins** | VT Learnings @ IIIT-NR &rarr; Syllabus Mastery &rarr; Capstone Motivation & Methodology &rarr; Preliminary Findings | Slides 1 through 11 |
| **Executive / High-Level Overview** | **8–10 Mins** | Training Summary &rarr; Problem Statement &rarr; End-to-End Pipeline &rarr; Expected Outcomes &rarr; Next Steps | Slides 1, 4, 6, 8, 10, 11 |
| **Comprehensive Seminar** | **20–25 Mins** | Mathematical Concepts (Regression, CNN/LSTM, Savitzky-Golay) &rarr; rPPG Pipeline &rarr; Future Roadmap | All Slides + Q&A |

---

## 2. Slide-by-Slide Speaker Notes & Technical Cue Cards

### Slide 1: Title Slide & Institutional Acknowledgement
* **Slide Title:** A Presentation on Vocational Training & Proposed Project based on Vocational Training/Internship
* **Core Takeaway:** Respectfully introduce the student team, express sincere gratitude to VT Mentor Dr. Anurag Singh (IIIT-NR) and College Mentor Prof. Aparna Pandey (BIT Raipur), and introduce the proposed capstone project.
* **Speaker Script (45s):**  
  *"Respected committee members, faculty, and mentors: Good morning. We are 4th-semester Computer Science & Engineering students from Bhilai Institute of Technology, Raipur. Today, we present our Vocational Training report on 'AI with Python', which we completed at IIIT Naya Raipur under the mentorship of Dr. Anurag Singh from 1st July to 10th August 2026, with the kind guidance of our college mentor Prof. Aparna Pandey. We also present our proposed undergraduate capstone project: 'Mobile Remote Photoplethysmography to Cuffless Blood Pressure Estimation', which directly builds upon the mathematical, signal processing, and deep learning foundations we learned during our training."*

---

### Slide 2: Introduction to the Vocational Training Program
* **Slide Title:** Introduction to the Vocational Training Undergone
* **Core Takeaway:** Academic growth from undergraduate classroom theory (4th Sem) to practical AI workflows at IIIT-NR.
* **Speaker Script:**  
  *"The 6-week Vocational Training at IIIT-NR gave us deep exposure to end-to-end Artificial Intelligence with Python. Under the guidance of our mentors, we progressed from foundational scientific computing and classical machine learning to advanced deep learning architectures, digital signal filtering, and modern agentic AI workflows. This hands-on training empowered us to tackle interdisciplinary problems bridging computational algorithms and biomedical data."*

---

### Slide 3: Training Objectives & Learning Milestones
* **Slide Title:** Training Objectives & Learning Milestones
* **Core Takeaway:** Five clear learning milestones achieved across data science, machine learning, deep learning, signal filtering, and modern AI.
* **Speaker Script:**  
  *"Our training objectives were structured into five key milestones: First, mastering scientific data manipulation in Python using NumPy, Pandas, and Matplotlib. Second, understanding classical machine learning algorithms, bias-variance tradeoffs, and rigorous cross-validation. Third, building deep neural networks (CNNs, RNNs, LSTMs, and Self-Attention) in TensorFlow. Fourth, exploring signal smoothing algorithms like the Savitzky-Golay filter. And fifth, gaining early exposure to modern AI paradigms including NLP, Embeddings, RAG, LangChain, and Agentic AI tools."*

---

### Slide 4: Detailed Curriculum & Topics Covered
* **Slide Title:** Comprehensive Curriculum Covered at IIIT-NR
* **Core Takeaway:** Clear categorization of the 45 syllabus topics into 4 structured, coherent modules.
* **Key Topics Summary:**
  * **Module 1 (Python & Scientific Foundations):** Python core, NumPy vectorization, Pandas data preprocessing & wrangling, Matplotlib visualization.
  * **Module 2 (Machine Learning & Validation):** Supervised, Unsupervised & Reinforcement paradigms; Linear, Polynomial & Logistic Regressions; Overfitting/Underfitting & Regularization; K-Fold Cross-Validation, Bias-Variance, and Metrics (Accuracy, Precision, Recall, F1).
  * **Module 3 (Deep Learning & Architectures):** TensorFlow graph execution, Activations (Sigmoid, ReLU, Tanh, SoftMax), Backpropagation, CNNs (Convolution, Pooling), Sequence models (RNN, LSTM), and Self-Attention mechanisms.
  * **Module 4 (Signal Processing, NLP & Modern AI):** Savitzky-Golay digital filter, NLTK, Word2Vec, GloVe, Contextual Embeddings, Transformer Encoders, RAG architecture, Open Model Fine-Tuning, LangChain, Agentic AI, and MCP (Model Context Protocol).

---

### Slide 5: Key Learnings & Bridging Theory to Project
* **Slide Purpose:** Explain how classroom learning inspired our applied capstone project.
* **Speaker Script:**  
  *"Our key takeaway was that raw data in real-world applications is rarely clean. Specifically, understanding the Savitzky-Golay filter for local polynomial smoothing taught us how to denoise physiological signals without distorting their characteristic peaks. Combining this with 1D Convolutions and Recurrent/Attention layers inspired us to ask: can we use a standard smartphone camera to extract optical heart pulses and estimate blood pressure? This question formed the foundation of our proposed project."*

---

### Slide 6: Proposed Project — Title & Introduction
* **Slide Title:** Proposed Capstone Project: Mobile rPPG to Cuffless Blood Pressure Estimation
* **Core Takeaway:** Clinical motivation around hypertension and the non-invasive optical alternative.
* **Speaker Script:**  
  *"Hypertension affects over 1.28 billion people worldwide and is often asymptomatic. While traditional upper-arm cuffs are accurate, they are cumbersome and cannot provide continuous monitoring. Our proposed project explores remote Photoplethysmography (rPPG)—detecting microscopic skin color fluctuations caused by cardiovascular pulsations via commodity smartphone cameras—to non-invasively estimate blood pressure without specialized hardware."*

---

### Slide 7: Objectives & Scope of Proposed Project
* **Slide Title:** Objectives & Scope of Proposed Project
* **Key Deliverables:**
  * Front-camera optical pulse acquisition with illumination stabilization.
  * Robust facial ROI extraction and color-space pulse extraction (POS / CHROM).
  * Digital filtering and signal conditioning via Butterworth bandpass and Savitzky-Golay smoothing.
  * Deep neural sequence modeling using TensorFlow (1D-CNN + BiGRU + Attention).
  * Investigating single-point calibration to account for individual vascular dynamics.
  * Exploring edge mobile feasibility for on-device privacy.

---

### Slide 8: Slide 9: Methodology / Approach of the Proposed Project
* **Slide Title:** Slide 9: Methodology / Approach of the Proposed Project
* **Stage Flow:**
  $$\text{Camera2 Sensor Lock} \longrightarrow \text{Facial ROI Tracking} \longrightarrow \text{POS Chrominance Subspace} \longrightarrow \text{Savitzky-Golay DSP} \longrightarrow \text{Deep Sequence Regression}$$
* **Speaker Script:**  
  *"Our proposed methodology follows a structured five-stage pipeline: First, locking camera sensor parameters to eliminate auto-exposure drift. Second, tracking facial regions to extract average skin pixel channels. Third, applying Plane-Orthogonal-to-Skin (POS) projection to cancel ambient specular reflections. Fourth, smoothing the pulse using Savitzky-Golay and bandpass filtering. And fifth, feeding the conditioned pulse into a deep regression network to estimate Systolic and Diastolic blood pressure."*

---

### Slide 9: Slide 10: Proposed Project Work Details & Live Demonstration
* **Slide Title:** Slide 10: Proposed Project Work Details & Demonstration
* **Core Takeaway:** Detailing the hybrid 1D-CNN + BiGRU + Self-Attention model architecture in TensorFlow and smoothly transitioning to the live mobile app demonstration.
* **Speaker Script & Live Demo Transition:**  
  *"Our neural architecture—MODEL-06-SepHead—combines dual-branch 1D Convolutions for systolic peak extraction with Bidirectional GRU and 4-head Self-Attention for cardiac rhythm modeling, terminating in decoupled heads for SBP and DBP.  
  
  **[Live Demo Transition]:** At this stage, we would like to switch to our smartphone for a brief live demonstration, showcasing real-time Camera2 video acquisition, facial ROI tracking, and on-device pulse waveform visualization in action."*

---

### Slide 10: Slide 11: Expected Outcomes & Results of the Proposed Project Work
* **Slide Title:** Slide 11: Expected Outcomes & Results of the Proposed Project Work
* **Core Takeaway:** Validated empirical results across clinical datasets and model generations.
* **Speaker Script:**  
  *"In our exploratory evaluations, our model achieved an MAE of 10.12 mmHg for SBP and 5.91 mmHg for DBP, representing a 6.70 mmHg reduction in error compared to baseline linear models. Furthermore, POS chrominance projection achieved 8.9 dB SNR, and offline batch inference executes in approximately 120 ms on commodity mobile CPUs with zero dropped frames."*

---

### Slide 11: Slide 12: Conclusion remarks & Future Scope of work
* **Slide Title:** Slide 12: Conclusion remarks & Future Scope of work
* **Core Takeaway:** Sincere gratitude to mentors at IIIT-NR and BIT Raipur, followed by an outline of upcoming capstone milestones.
* **Speaker Script:**  
  *"In conclusion, our 6-week training at IIIT-NR in 'AI with Python' under the guidance of Dr. Anurag Singh and Prof. Aparna Pandey gave us the theoretical and practical foundation to formulate this capstone project. Moving forward, our roadmap includes clinical testing across diverse Fitzpatrick skin phototypes, mobile NPU hardware acceleration for sub-50ms inference, and multimodal optical sensing. We sincerely thank our mentors and faculty members for their support, and we welcome your questions."*

---

## 3. Humble & Prepared Answers for Committee Questions

### Q1: *"How does what you learned at IIIT-NR relate to your proposed project?"*
> **Answer:**  
> *"At IIIT-NR, we were taught the full spectrum of AI with Python—from data preprocessing with NumPy/Pandas to deep learning architectures in TensorFlow (CNNs, LSTMs, Attention) and digital filtering like Savitzky-Golay. Our proposed project applies these exact principles: we use Python scientific tools for signal wrangling, the Savitzky-Golay filter to smooth optical pulse waves, and CNN/LSTM/Attention networks to regress blood pressure from those waves."*

### Q2: *"Why is digital signal filtering (like Savitzky-Golay) necessary if you are using deep learning?"*
> **Answer:**  
> *"While deep neural networks are strong feature extractors, raw camera signals contain high-frequency sensor noise and low-frequency baseline drifts. As we learned during training, quality preprocessing and local polynomial filtering (like Savitzky-Golay) preserve essential peak morphology (such as systolic peaks) while removing out-of-band noise, which substantially eases the neural network's learning burden."*

### Q3: *"Can smartphone cameras accurately estimate blood pressure without any cuff?"*
> **Answer:**  
> *"Camera rPPG directly measures relative optical blood volume pulses, not absolute pressure in mmHg. Because arterial stiffness and vascular geometry vary across individuals, a completely uncalibrated model tends to regress towards the dataset average. Therefore, our proposal incorporates single-point calibration—using an initial reference reading to anchor personal baseline values—making continuous tracking much more reliable."*

### Q4: *"What are the limitations of your current student prototype?"*
> **Answer:**  
> *"Currently, our work is in the prototype and research formulation stage. Key limitations include sensitivity to sudden head movement, variations under low ambient illumination, and the need for testing across broader datasets with diverse skin tones. Addressing these challenges forms our primary roadmap for the upcoming capstone semesters."*

