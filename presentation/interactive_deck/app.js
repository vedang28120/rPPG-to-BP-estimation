/**
 * Interactive Presentation Engine & Telemetry Simulator
 * Mobile rPPG to Cuffless Blood Pressure Estimation
 * Presenters: Vedang Bhatt, Anubhav Shrivastav, Aadarsh (Students of CSE Dept.)
 * Institution: Bhilai Institute of Technology, Raipur
 * Project: vedang28120/rPPG-to-BP-estimation
 */

document.addEventListener('DOMContentLoaded', () => {
  // ==========================================================================
  // 1. Slide Navigation State Machine
  // ==========================================================================
  const slides = document.querySelectorAll('.slide');
  const totalSlides = slides.length;
  let currentSlideIndex = 0;

  const slideIndicator = document.getElementById('slide-indicator');
  const progressBar = document.getElementById('progress-bar');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const btnFullscreen = document.getElementById('btn-fullscreen');
  const btnToggleNotes = document.getElementById('btn-toggle-notes');
  const notesDrawer = document.getElementById('notes-drawer');
  const btnCloseNotes = document.getElementById('btn-close-notes');
  const notesContent = document.getElementById('notes-content');

  // Speaker notes adhering to 7 C's of Effective Communication
  const speakerNotes = {
    1: `<h4>Slide 1: Title Slide & Introduction</h4>
        <p><strong>Presenters:</strong> Vedang Bhatt, Anubhav Shrivastav, Aadarsh (B. Tech. CSE, 7th Sem, BIT Raipur).</p>
        <p><strong>Opening Script (45s):</strong> "Good morning respected committee members and faculty. Today we present our Vocational Training & Proposed Capstone Project titled 'Mobile Remote Photoplethysmography to Cuffless Blood Pressure Estimation'. This work demonstrates how standard smartphone RGB cameras can track transcutaneous micro-color changes to infer continuous blood pressure without external wearable sensors."</p>`,
    2: `<h4>Slide 2: Introduction about the Training Undergone</h4>
        <p><strong>Key Concept:</strong> Applied AI, Real-time Computer Vision & Biomedical Signal Processing.</p>
        <p><strong>Industrial Motivation:</strong> 1.28 billion adults have hypertension. Traditional cuffs are bulky and sleep-disruptive. Our focus is non-contact optical physiological sensing.</p>
        <p><strong>Tech Scope:</strong> Android Camera2 ingestion, MediaPipe landmarking, optical rPPG (POS/TS-CAN), and quantized TFLite on mobile.</p>`,
    3: `<h4>Slide 3: Training Objectives</h4>
        <p><strong>5 Core Technical Milestones:</strong></p>
        <ul>
          <li>1. Master optical rPPG physics & Beer-Lambert light attenuation.</li>
          <li>2. Implement 468-point 3D MediaPipe Face Mesh tracking for forehead ROI.</li>
          <li>3. Engineer physiological DSP (PCHIP 125 Hz, Butterworth, BayesShrink DWT).</li>
          <li>4. Architect deep sequence models (MODEL-06-SepHead) for continuous SBP/DBP.</li>
          <li>5. Optimize on-device Android latency to sub-150ms.</li>
        </ul>`,
    4: `<h4>Slide 4: Training Modules / Topics Covered</h4>
        <p><strong>5-Module Breakdown:</strong></p>
        <ul>
          <li><strong>Module 1:</strong> Beer-Lambert law, POS null space, CHROM, and TS-CAN attention.</li>
          <li><strong>Module 2:</strong> Camera2 API, 468-pt Face Mesh, Forehead ROI, EAR blink liveness.</li>
          <li><strong>Module 3:</strong> PCHIP 125 Hz resampling, Butterworth bandpass, BayesShrink DWT, SPA detrending.</li>
          <li><strong>Module 4:</strong> 1D multi-scale ResNet, BiGRU, 4-head Multi-Head Attention, Decoupled heads.</li>
          <li><strong>Module 5:</strong> Record-then-Process state machine, AE/AWB lock, TFLite quantization.</li>
        </ul>`,
    5: `<h4>Slide 5: Key Learnings</h4>
        <p><strong>Core Empirical Breakthroughs:</strong></p>
        <ol>
          <li><strong>Template Collapse Physics:</strong> Windkessel low-pass filtering attenuates dicrotic notch by 1-2 orders; 8-bit noise floor (0.39%) and 30 FPS limit inflection recovery. Requires single-point calibration.</li>
          <li><strong>Derivative Noise Pitfall:</strong> Derivatives (vPPG, aPPG) amplify sensor noise by O(f²). Single-channel raw PPG generalizes superiorly.</li>
          <li><strong>POS Null-Space:</strong> Orthogonal projection places specular white light (R=G=B) into the null space, yielding 8.9 dB SNR.</li>
          <li><strong>Record-then-Process:</strong> Offline batching eliminates JNI GC pauses and dropped frames.</li>
        </ol>`,
    6: `<h4>Slide 6: Proposed Project Title & its Introduction</h4>
        <p><strong>Capstone Scope:</strong> Non-invasive, contactless cuffless BP estimation from smartphone video.</p>
        <p><strong>Clinical Need:</strong> Frictionless daily screening for hypertension prevention without white-coat stress artifacts.</p>`,
    7: `<h4>Slide 7: Objectives of the Proposed Project</h4>
        <p><strong>Deliverable Targets:</strong></p>
        <ul>
          <li>Capture optical pulse from 30 FPS video without hardware contact.</li>
          <li>Resample to 125 Hz uniform grid and remove baseline wander via DWT.</li>
          <li>Achieve subject-level SBP/DBP MAE &lt; 11.0 / &lt; 6.5 mmHg.</li>
          <li>Meet ISO 81060-2 clinical compliance via single-point personal calibration.</li>
          <li>Deploy 100% on-device Android execution in ~120 ms.</li>
        </ul>`,
    8: `<h4>Slide 9: Methodology / Approach of Proposed Project</h4>
        <p><strong>5-Stage Flow:</strong> Camera2 AE/AWB Lock &rarr; Forehead 468 ROI &rarr; POS Null-Space Projection &rarr; Dual-Stream DSP &rarr; MODEL-06-SepHead Neural Regression.</p>`,
    9: `<h4>Slide 10: Proposed Project Work Details</h4>
        <p><strong>Architecture Details:</strong> Dual-Branch 1D-ResNet (Kernel=5 for morphology, Kernel=11 for rhythm) + 2-layer BiGRU (hidden=64) + 4-head Multi-Head Self-Attention + Decoupled SBP/DBP heads with custom loss:</p>
        <p><code>L = &lambda;<sub>sbp</sub> &middot; MSE<sub>sbp</sub> + &lambda;<sub>dbp</sub> &middot; MSE<sub>dbp</sub></code></p>`,
    10: `<h4>Slide 11: Expected Outcomes & Results of Proposed Project</h4>
        <p><strong>Validated Benchmarks:</strong></p>
        <ul>
          <li>Subject SBP/DBP MAE: <strong>10.12 / 5.91 mmHg</strong> (MCD-Iriun dataset).</li>
          <li>Progression Delta: 6.70 mmHg improvement over demographic baseline.</li>
          <li>Extractor SNR: POS = 8.9 dB | TS-CAN = 10.4 dB.</li>
          <li>Edge Latency: 120 ms on mobile CPU with zero dropped frames.</li>
        </ul>`,
    11: `<h4>Slide 12: Conclusion remarks & Future Scope of work</h4>
        <p><strong>Conclusions:</strong> Feasibility confirmed on standard smartphones; single-point calibration solves Template Collapse.</p>
        <p><strong>Future Scope:</strong> Fitzpatrick I-VI diverse trials, multi-site optical PTT, hardware NPU acceleration, and smart health kiosks.</p>`
  };

  function updateSlide(index) {
    if (index < 0) index = 0;
    if (index >= totalSlides) index = totalSlides - 1;
    currentSlideIndex = index;

    slides.forEach((slide, i) => {
      slide.classList.remove('active', 'prev');
      if (i === currentSlideIndex) {
        slide.classList.add('active');
      } else if (i < currentSlideIndex) {
        slide.classList.add('prev');
      }
    });

    slideIndicator.textContent = `Slide ${currentSlideIndex + 1} / ${totalSlides}`;
    const progressPercent = ((currentSlideIndex + 1) / totalSlides) * 100;
    progressBar.style.width = `${progressPercent}%`;

    // Update Speaker Notes content
    if (notesContent) {
      notesContent.innerHTML = speakerNotes[currentSlideIndex + 1] || '<p>No specific notes for this slide.</p>';
    }
  }

  btnPrev.addEventListener('click', () => updateSlide(currentSlideIndex - 1));
  btnNext.addEventListener('click', () => updateSlide(currentSlideIndex + 1));

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
      e.preventDefault();
      updateSlide(currentSlideIndex + 1);
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault();
      updateSlide(currentSlideIndex - 1);
    } else if (e.key === 'f' || e.key === 'F') {
      toggleFullScreen();
    } else if (e.key === 'p' || e.key === 'P') {
      toggleNotes();
    }
  });

  // Fullscreen toggle
  function toggleFullScreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }
  btnFullscreen.addEventListener('click', toggleFullScreen);

  // Speaker notes toggle
  function toggleNotes() {
    notesDrawer.classList.toggle('hidden');
    btnToggleNotes.classList.toggle('active');
  }
  btnToggleNotes.addEventListener('click', toggleNotes);
  btnCloseNotes.addEventListener('click', toggleNotes);

  // Toggle Live Signal Simulator
  const btnToggleSim = document.getElementById('btn-toggle-sim');
  const waveformPanel = document.getElementById('waveform-panel');
  if (btnToggleSim && waveformPanel) {
    btnToggleSim.addEventListener('click', () => {
      waveformPanel.classList.toggle('hidden');
      btnToggleSim.classList.toggle('active');
    });
  }

  // ==========================================================================
  // 2. Synthetic 125 Hz Hemodynamic Waveform Canvas Renderer
  // ==========================================================================
  const canvas = document.getElementById('waveform-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let time = 0;
    const history = [];
    const maxPoints = 600;

    function generatePPGSample(t) {
      // Synthesize realistic Blood Volume Pulse (BVP) with dicrotic notch
      const hrFreq = 1.2; // ~72 BPM
      const phase = (t * hrFreq * 2 * Math.PI) % (2 * Math.PI);

      // Systolic peak + dicrotic wave
      const systolic = Math.exp(-Math.pow(phase - 1.0, 2) / 0.25) * 1.0;
      const dicrotic = Math.exp(-Math.pow(phase - 2.4, 2) / 0.35) * 0.35;
      const noise = (Math.random() - 0.5) * 0.02;

      return systolic + dicrotic + noise;
    }

    function renderWaveform() {
      time += 0.016; // 60 FPS update
      const sample = generatePPGSample(time);
      history.push(sample);
      if (history.length > maxPoints) {
        history.shift();
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw grid lines
      ctx.strokeStyle = 'rgba(2, 132, 199, 0.08)';
      ctx.lineWidth = 1;
      for (let y = 15; y < canvas.height; y += 20) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }

      // Draw waveform
      ctx.strokeStyle = '#0284C7';
      ctx.lineWidth = 2.2;
      ctx.shadowColor = 'rgba(2, 132, 199, 0.5)';
      ctx.shadowBlur = 6;
      ctx.beginPath();

      const step = canvas.width / maxPoints;
      for (let i = 0; i < history.length; i++) {
        const x = i * step;
        const normalized = history[i];
        const y = canvas.height - (normalized * (canvas.height - 18) + 8);
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
      ctx.shadowBlur = 0;

      requestAnimationFrame(renderWaveform);
    }

    renderWaveform();
  }

  // Initialize first slide
  updateSlide(0);
});
