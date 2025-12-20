(function(){
  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');
  const flipBtn = document.getElementById('flipBtn');
  const deviceSelect = document.getElementById('deviceSelect');
  const preview = document.getElementById('preview');
  const statusText = document.getElementById('statusText');

  let stream = null;
  let currentDeviceId = null;
  let scanningActive = false;
  let canvas = null;
  let canvasContext = null;
  let lastScannedCode = null;
  let lastScanTime = 0;

  function showResultPopup(isValid, ticket = null, errorMessage = null) {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(4px);
      z-index: 40000;
      display: flex;
      align-items: center;
      justify-content: center;
      animation: fadeIn 0.2s ease-out;
    `;

    const modal = document.createElement('div');
    modal.style.cssText = `
      background: var(--bg-card);
      border: 1px solid var(--border-light);
      border-radius: 20px;
      padding: 32px;
      max-width: 500px;
      width: 90%;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
      animation: slideUp 0.3s ease-out;
    `;

    const icon = document.createElement('div');
    icon.style.cssText = `
      font-size: 64px;
      text-align: center;
      margin-bottom: 16px;
    `;
    icon.innerHTML = isValid 
      ? '<i class="fa-solid fa-circle-check" style="color: #22c55e;"></i>' 
      : '<i class="fa-solid fa-circle-xmark" style="color: #ef4444;"></i>';

    const title = document.createElement('div');
    title.style.cssText = `
      font-size: 1.5rem;
      font-weight: 700;
      text-align: center;
      color: #fff;
      margin-bottom: 20px;
    `;
    title.textContent = isValid ? 'Valid Ticket' : 'Invalid Ticket';

    const details = document.createElement('div');
    details.style.cssText = `
      background: var(--bg-card-hover);
      border: 1px solid var(--border-light);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 20px;
    `;

    if (isValid && ticket) {
      details.innerHTML = `
        <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 12px;">Ticket Details</div>
        <div style="display: grid; gap: 8px;">
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-muted);">Ticket ID:</span>
            <span style="color: #fff; font-weight: 600;">#${ticket.id}</span>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-muted);">Seat:</span>
            <span style="color: #fff; font-weight: 600;">${ticket.seat_label}</span>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-muted);">Type:</span>
            <span style="color: #fff; font-weight: 600;">${ticket.seat_type}</span>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-muted);">Status:</span>
            <span style="color: #22c55e; font-weight: 600;">${ticket.status}</span>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-muted);">Price Paid:</span>
            <span style="color: #fff; font-weight: 600;">$${ticket.price_paid.toFixed(2)}</span>
          </div>
        </div>
      `;
    } else {
      details.innerHTML = `
        <div style="color: var(--text-muted); text-align: center;">
          ${errorMessage || 'This ticket could not be verified. It may be invalid, cancelled, or expired.'}
        </div>
      `;
    }

    const closeBtn = document.createElement('button');
    closeBtn.style.cssText = `
      width: 100%;
      padding: 12px;
      background: linear-gradient(135deg, var(--brand-dark), var(--brand-primary));
      color: white;
      border: none;
      border-radius: 10px;
      font-weight: 700;
      font-size: 1rem;
      cursor: pointer;
      transition: transform 0.2s;
    `;
    closeBtn.textContent = 'Close';
    closeBtn.onmouseover = () => closeBtn.style.transform = 'scale(1.02)';
    closeBtn.onmouseout = () => closeBtn.style.transform = 'scale(1)';
    closeBtn.onclick = () => {
      overlay.style.animation = 'fadeOut 0.2s ease-in';
      setTimeout(() => overlay.remove(), 200);
    };

    modal.appendChild(icon);
    modal.appendChild(title);
    modal.appendChild(details);
    modal.appendChild(closeBtn);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    overlay.onclick = (e) => {
      if (e.target === overlay) {
        overlay.style.animation = 'fadeOut 0.2s ease-in';
        setTimeout(() => overlay.remove(), 200);
      }
    };
  }

  function initCanvas() {
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvasContext = canvas.getContext('2d');
    }
  }

  async function verifyTicket(token) {
    try {
      status('Verifying ticket...');
      const response = await TicketsAPI.verifyQR(token);
      
      if (response.valid && response.ticket) {
        const ticket = response.ticket;
        showResultPopup(true, ticket);
        status(`Valid: Ticket #${ticket.id} - Seat ${ticket.seat_label}`);
        
        if (navigator.vibrate) {
          navigator.vibrate([100, 50, 100]);
        }
      } else {
        showResultPopup(false);
        status('Invalid: Ticket verification failed');
        
        if (navigator.vibrate) {
          navigator.vibrate(200);
        }
      }
    } catch (error) {
      console.error('Verification error:', error);
      showResultPopup(false, null, error.message);
      status(`Error: ${error.message}`);
    }
  }

  function scanQRCode() {
    if (!scanningActive || !stream) return;

    if (preview.readyState === preview.HAVE_ENOUGH_DATA) {
      canvas.width = preview.videoWidth;
      canvas.height = preview.videoHeight;
      canvasContext.drawImage(preview, 0, 0, canvas.width, canvas.height);
      
      const imageData = canvasContext.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height, {
        inversionAttempts: "dontInvert",
      });

      if (code && code.data) {
        const now = Date.now();
        if (code.data !== lastScannedCode || now - lastScanTime > 3000) {
          lastScannedCode = code.data;
          lastScanTime = now;
          verifyTicket(code.data);
        }
      }
    }

    requestAnimationFrame(scanQRCode);
  }

  async function listDevices(){
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoInputs = devices.filter(d => d.kind === 'videoinput');
      deviceSelect.innerHTML = '';
      videoInputs.forEach((d, idx) => {
        const opt = document.createElement('option');
        opt.value = d.deviceId;
        opt.textContent = d.label || `Camera ${idx+1}`;
        deviceSelect.appendChild(opt);
      });
      if (videoInputs.length > 0) {
        currentDeviceId = videoInputs[0].deviceId;
        deviceSelect.value = currentDeviceId;
        flipBtn.disabled = videoInputs.length < 2;
      } else {
        status('No camera devices found');
      }
    } catch (e) {
      console.error(e);
      status('Unable to list devices');
    }
  }

  async function startCamera(deviceId){
    try {
      if (stream) await stopCamera();
      const constraints = {
        video: deviceId ? { deviceId: { exact: deviceId } } : { facingMode: 'environment' },
        audio: false
      };
      stream = await navigator.mediaDevices.getUserMedia(constraints);
      preview.srcObject = stream;
      await preview.play();
      status('Camera started - Ready to scan QR codes');
      startBtn.disabled = true;
      stopBtn.disabled = false;
      flipBtn.disabled = (deviceSelect.options.length < 2);
      
      initCanvas();
      scanningActive = true;
      requestAnimationFrame(scanQRCode);
    } catch (e) {
      console.error(e);
      status('Failed to start camera. Check permissions.');
    }
  }

  async function stopCamera(){
    scanningActive = false;
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      preview.srcObject = null;
      stream = null;
      status('Camera stopped');
    }
    startBtn.disabled = false;
    stopBtn.disabled = true;
    lastScannedCode = null;
  }

  function status(msg){ statusText.textContent = msg; }

  startBtn.addEventListener('click', () => startCamera(deviceSelect.value || null));
  stopBtn.addEventListener('click', stopCamera);
  flipBtn.addEventListener('click', () => {
    const idx = deviceSelect.selectedIndex;
    const next = (idx + 1) % deviceSelect.options.length;
    deviceSelect.selectedIndex = next;
    currentDeviceId = deviceSelect.value;
    startCamera(currentDeviceId);
  });
  deviceSelect.addEventListener('change', () => {
    currentDeviceId = deviceSelect.value;
    status('Selected camera changed');
  });

  // Initialize
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia){
    status('Camera API not supported in this browser');
    startBtn.disabled = true;
  } else {
    listDevices();
  }
})();
