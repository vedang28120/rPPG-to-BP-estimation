/**
 * Mobile rPPG to Cuffless Blood Pressure Estimation
 * Interactive Defense Deck & 125 Hz DSP Waveform Engine
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
  const btnNotesClose = document.getElementById('btn-notes-close');
  const notesContent = document.getElementById('notes-content');
  const notesSlideNum = document.getElementById('notes-slide-num');

  // Speaker notes dictionary adhering to 7 C's
  const speakerNotes = {
    1: `<h4>Slide 1: Executive Vision</h4>
        <p><strong>Presenter Introduction:</strong> "We are Vedang Bhatt and Anubhav Shrivastav, students of CSE Dept. Project: vedang28120/rPPG-to-BP-estimation. Today we present our research on mobile rPPG to cuffless blood pressure estimation."</p>
        <p><strong>Opening Script (30s):</strong> "Hypertension affects 1.28 billion people globally. Conventional cuffs are disruptive and intermittent. Our framework captures transcutaneous micro-color absorption from standard 30 FPS smartphone video to continuously estimate Systolic and Diastolic Blood Pressure with 10.12 / 5.91 mmHg accuracy."</p>
        <p><strong>Key Focus:</strong> Touchless, zero extra hardware, edge-ready.</p>`,
    2: `<h4>Slide 2: Optical Acquisition & State Machine</h4>
        <p><strong>Key Concept:</strong> Camera2 AE/AWB Convergence-Hold-Lock protocol.</p>
        <p><strong>Physics Defense:</strong> AC pulsatile amplitude is only 0.1–1.5% of total reflectance. Sensor gain shifts destroy this signal. Freezing ISO and exposure after convergence is mandatory.</p>
        <p><strong>ROI:</strong> MediaPipe 468 landmarks isolate the central forehead (minimal motion artifacts).</p>`,
    3: `<h4>Slide 3: Chrominance Projection (POS vs TS-CAN)</h4>
        <p><strong>Math Formula:</strong> <code>X<sub>s</sub> = G &minus; B</code>, <code>Y<sub>s</sub> = G + B &minus; 2R</code>, <code>S = X<sub>s</sub> + &alpha;&middot;Y<sub>s</sub></code>.</p>
        <p><strong>Crucial Insight:</strong> Specular reflection is equal across RGB, so it falls directly in the mathematical null space of the projection matrix, achieving 8.9 dB SNR.</p>
        <p><strong>Deep Alternative:</strong> TS-CAN provides 10.4 dB SNR by shifting temporal channels without 3D-CNN parameter bloat.</p>`,
    4: `<h4>Slide 4: Physiological DSP & Wavelet Denoising</h4>
        <p><strong>Dual-Stream Logic:</strong></p>
        <ul>
          <li><strong>Stream A:</strong> 4th-order Butterworth (0.75–3.0 Hz) &rarr; HR and RMSSD.</li>
          <li><strong>Stream B:</strong> Wavelet BayesShrink DWT (<em>sym8</em>) &rarr; preserves systolic slope and inflection dynamics for BP estimation.</li>
        </ul>
        <p><strong>PCHIP Resampling:</strong> Standardizes 28–38 ms variable frame rates onto a strict 125 Hz grid while preserving monotonicity.</p>`,
    5: `<h4>Slide 5: MODEL-06-SepHead Architecture</h4>
        <p><strong>Architectural Rationale:</strong> Dual-Branch 1D-ResNet (kernel=5 for sharp local features, kernel=11 for multi-beat modulation) + BiGRU + 4-Head Self-Attention.</p>
        <p><strong>Decoupled Heads:</strong> SBP reflects cardiac ejection volume; DBP reflects peripheral vascular resistance. Separate heads prevent gradient interference.</p>
        <p><strong>Derivative Discovery:</strong> Single-channel PPG proved superior to vPPG/aPPG derivatives because differentiation amplifies 30 FPS camera quantization noise.</p>`,
    6: `<h4>Slide 6: Empirical Benchmarks</h4>
        <p><strong>Core Numbers:</strong> Subject SBP MAE 10.12 mmHg, DBP MAE 5.91 mmHg (MCD-Iriun synchronized clinical dataset).</p>
        <p><strong>Progression Delta:</strong> SBP error reduced from 16.82 mmHg (Demo MLP) down to 10.12 mmHg.</p>
        <p><strong>Subject Split:</strong> Strict <code>GroupShuffleSplit</code> enforced zero subject identity overlap between training and testing sets.</p>`,
    7: `<h4>Slide 7: The Physics of Template Collapse</h4>
        <p><strong>Theoretical Credit:</strong> First formalized by Achraf Ben Ahmed et al. (<em>arXiv:2606.03802</em>, 2026).</p>
        <p><strong>The 3 Root Causes:</strong></p>
        <ol>
          <li><strong>Windkessel Damping:</strong> Arterial compliance dampens the facial dicrotic notch by 1–2 orders of magnitude compared to finger PPG.</li>
          <li><strong>8-Bit Quantization:</strong> 256 levels creates a 0.39% noise floor vs 0.1–1.5% pulsatile AC signal.</li>
          <li><strong>30 FPS Ceiling:</strong> 15 Hz Nyquist frequency limits high-frequency inflection recovery.</li>
        </ol>`,
    8: `<h4>Slide 8: Clinical Standards & Calibration</h4>
        <p><strong>ISO 81060-2 Target:</strong> Mean Error &le; 5.0 mmHg, SD &le; 8.0 mmHg.</p>
        <p><strong>Single-Point Calibration:</strong> A single baseline cuff reading anchors individual arterial compliance, unlocking continuous Grade A/B tracking.</p>`,
    9: `<h4>Slide 9: Android Edge Architecture</h4>
        <p><strong>Record-then-Process:</strong> Buffering 7–10s at 30 FPS in native memory and executing single-shot TFLite inference in 120 ms eliminates mobile JNI frame drops and GC stalls.</p>`,
    10: `<h4>Slide 10: Media Demonstrations & Deliverables</h4>
        <p><strong>Artifacts Available:</strong> 5-Page Academic Paper by Vedang Bhatt & Anubhav Shrivastav (<code>academic_paper_rppg.pdf</code>, Students of CSE Dept. &bull; Project: vedang28120/rPPG-to-BP-estimation), 1-Page Executive Factsheet, and Master Defense Guide.</p>`
  };

  function updateSlide(index) {
    if (index < 0) index = 0;
    if (index >= totalSlides) index = totalSlides - 1;
    currentSlideIndex = index;

    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === currentSlideIndex);
    });

    slideIndicator.textContent = `Slide ${currentSlideIndex + 1} / ${totalSlides}`;
    const progressPercent = ((currentSlideIndex + 1) / totalSlides) * 100;
    progressBar.style.width = `${progressPercent}%`;

    // Update notes content
    notesSlideNum.textContent = currentSlideIndex + 1;
    notesContent.innerHTML = speakerNotes[currentSlideIndex + 1] || '<p>No specific notes for this slide.</p>';
  }

  btnPrev.addEventListener('click', () => updateSlide(currentSlideIndex - 1));
  btnNext.addEventListener('click', () => updateSlide(currentSlideIndex + 1));

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ') {
      updateSlide(currentSlideIndex + 1);
    } else if (e.key === 'ArrowLeft') {
      updateSlide(currentSlideIndex - 1);
    } else if (e.key === 'f' || e.key === 'F') {
      toggleFullScreen();
    } else if (e.key === 'p' || e.key === 'P') {
      notesDrawer.classList.toggle('open');
    }
  });

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

  btnToggleNotes.addEventListener('click', () => {
    notesDrawer.classList.toggle('open');
  });

  btnNotesClose.addEventListener('click', () => {
    notesDrawer.classList.remove('open');
  });

  // Initial slide load
  updateSlide(0);

  // ==========================================================================
  // 2. Video Hub Switcher
  // ==========================================================================
  const vidBtns = document.querySelectorAll('.vid-btn');
  const videoPlayer = document.getElementById('main-video-player');

  vidBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      vidBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      const src = btn.getAttribute('data-src');
      if (videoPlayer && src) {
        videoPlayer.src = src;
        videoPlayer.play().catch(() => {});
      }
    });
  });

  // ==========================================================================
  // 3. Live 125 Hz Hemodynamic Waveform Simulator Engine
  // ==========================================================================
  const btnToggleSim = document.getElementById('btn-toggle-sim');
  const simDrawer = document.getElementById('simulator-drawer');
  const btnSimClose = document.getElementById('btn-sim-close');
  const btnSimReset = document.getElementById('btn-sim-reset');

  btnToggleSim.addEventListener('click', () => {
    simDrawer.classList.toggle('open');
    btnToggleSim.classList.toggle('active', simDrawer.classList.contains('open'));
  });

  btnSimClose.addEventListener('click', () => {
    simDrawer.classList.remove('open');
    btnToggleSim.classList.remove('active', false);
  });

  const canvas = document.getElementById('waveform-canvas');
  const ctx = canvas.getContext('2d');

  const sliderHR = document.getElementById('slider-hr');
  const sliderSBP = document.getElementById('slider-sbp');
  const sliderDBP = document.getElementById('slider-dbp');
  const sliderNoise = document.getElementById('slider-noise');
  const toggleNotch = document.getElementById('toggle-notch');
  const toggleWavelet = document.getElementById('toggle-wavelet');

  const valHR = document.getElementById('val-hr');
  const valSBP = document.getElementById('val-sbp');
  const valDBP = document.getElementById('val-dbp');
  const valNoise = document.getElementById('val-noise');

  const teleHR = document.getElementById('tele-hr');
  const teleBP = document.getElementById('tele-bp');
  const teleSNR = document.getElementById('tele-snr');
  const teleSQI = document.getElementById('tele-sqi');
  const teleDSP = document.getElementById('tele-dsp');

  // Slider events
  sliderHR.addEventListener('input', (e) => {
    valHR.textContent = e.target.value;
    teleHR.textContent = `${e.target.value} BPM`;
  });
  sliderSBP.addEventListener('input', (e) => {
    valSBP.textContent = e.target.value;
    teleBP.textContent = `${e.target.value} / ${sliderDBP.value} mmHg`;
  });
  sliderDBP.addEventListener('input', (e) => {
    valDBP.textContent = e.target.value;
    teleBP.textContent = `${sliderSBP.value} / ${e.target.value} mmHg`;
  });
  sliderNoise.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    valNoise.textContent = val < 20 ? 'Low' : val < 60 ? 'Medium' : 'High';
    const snr = Math.max(2.0, (14.0 - val * 0.12)).toFixed(1);
    teleSNR.textContent = `${snr} dB`;
    if (val > 70) {
      teleSQI.textContent = 'POOR (WARN)';
      teleSQI.className = 'tele-val';
      teleSQI.style.color = '#F43F5E';
    } else {
      teleSQI.textContent = 'VALID (PASS)';
      teleSQI.className = 'tele-val good';
      teleSQI.style.color = '#10B981';
    }
  });

  toggleWavelet.addEventListener('change', (e) => {
    teleDSP.textContent = e.target.checked ? 'Stream B (Wavelet)' : 'Stream A (Butterworth)';
  });

  btnSimReset.addEventListener('click', () => {
    sliderHR.value = 72;
    sliderSBP.value = 118;
    sliderDBP.value = 74;
    sliderNoise.value = 15;
    toggleNotch.checked = true;
    toggleWavelet.checked = true;
    valHR.textContent = '72';
    valSBP.textContent = '118';
    valDBP.textContent = '74';
    valNoise.textContent = 'Low';
    teleHR.textContent = '72 BPM';
    teleBP.textContent = '118 / 74 mmHg';
    teleSNR.textContent = '9.4 dB';
    teleSQI.textContent = 'VALID (PASS)';
    teleSQI.style.color = '#10B981';
    teleDSP.textContent = 'Stream B (Wavelet)';
  });

  // Animated Waveform Engine
  let timeStep = 0;
  const bufferSize = 800;
  const pulseBuffer = new Array(bufferSize).fill(0);

  function drawWaveform() {
    // Dynamic canvas resize
    if (canvas.width !== canvas.parentElement.clientWidth) {
      canvas.width = canvas.parentElement.clientWidth;
    }

    const hr = parseFloat(sliderHR.value);
    const noiseAmp = parseFloat(sliderNoise.value) / 100.0;
    const hasNotch = toggleNotch.checked;
    const useWavelet = toggleWavelet.checked;

    const cardiacFreq = hr / 60.0; // Hz
    const fs = 125.0; // 125 Hz standard rate
    const t = timeStep / fs;

    // Cardiac Pulse Model: Systolic Upstroke + Diastolic Wave + Notch
    const phase = (t * cardiacFreq) % 1.0;
    let pulseVal = 0;

    // Systolic ejection peak (sharp Gaussian)
    pulseVal += Math.exp(-Math.pow((phase - 0.20) / 0.08, 2)) * 1.0;

    // Dicrotic notch & diastolic runoff reflection
    if (hasNotch) {
      pulseVal += Math.exp(-Math.pow((phase - 0.45) / 0.10, 2)) * 0.40;
    } else {
      // Windkessel damped
      pulseVal += Math.exp(-Math.pow((phase - 0.48) / 0.22, 2)) * 0.15;
    }

    // High frequency sensor noise & respiratory wander
    let noise = (Math.random() - 0.5) * noiseAmp * 0.6;
    if (useWavelet) {
      // Wavelet soft thresholding suppresses Gaussian noise
      noise = noise * 0.3;
    }
    const respiration = Math.sin(2 * Math.PI * 0.25 * t) * 0.08;

    const finalSignal = pulseVal + noise + respiration;

    // Push into rolling buffer
    pulseBuffer.push(finalSignal);
    pulseBuffer.shift();

    // Render Canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Gridlines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 25) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Draw Pulse Trace
    ctx.beginPath();
    ctx.strokeStyle = useWavelet ? '#38BDF8' : '#10B981';
    ctx.lineWidth = 2.2;
    ctx.shadowBlur = 10;
    ctx.shadowColor = useWavelet ? 'rgba(56, 189, 248, 0.5)' : 'rgba(16, 185, 129, 0.5)';

    const midY = canvas.height * 0.55;
    const scaleY = canvas.height * 0.45;
    const stepX = canvas.width / (bufferSize - 1);

    for (let i = 0; i < bufferSize; i++) {
      const x = i * stepX;
      const y = midY - (pulseBuffer[i] - 0.4) * scaleY;
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Draw Lead-Edge Pulse Dot
    const currentX = canvas.width - 2;
    const currentY = midY - (pulseBuffer[bufferSize - 1] - 0.4) * scaleY;
    ctx.beginPath();
    ctx.arc(currentX, currentY, 4, 0, Math.PI * 2);
    ctx.fillStyle = '#F43F5E';
    ctx.fill();

    timeStep++;
    requestAnimationFrame(drawWaveform);
  }

  requestAnimationFrame(drawWaveform);
});
