/* ============================================================
   BHARGAV VAGADIYA — PORTFOLIO JAVASCRIPT
   ============================================================ */

// ---- Navbar scroll effect ----
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 50);
});

// ---- Hamburger menu ----
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('nav-links');
hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('active');
  navLinks.classList.toggle('open');
});
navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    hamburger.classList.remove('active');
    navLinks.classList.remove('open');
  });
});

// ---- Scroll Reveal ----
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('visible'), i * 80);
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
);
document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// ---- Animated counters ----
const counterObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.5 }
);
document.querySelectorAll('.stat-num').forEach(el => counterObserver.observe(el));

function animateCounter(el) {
  const target = parseInt(el.dataset.target, 10);
  const duration = 1200;
  const start = performance.now();
  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
    el.textContent = Math.floor(eased * target);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target;
  }
  requestAnimationFrame(step);
}

// ---- Particle canvas ----
(function initParticles() {
  const canvas = document.createElement('canvas');
  canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;';
  const container = document.getElementById('particles');
  container.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let W, H, particles = [];

  const resize = () => {
    W = canvas.width = container.offsetWidth || window.innerWidth;
    H = canvas.height = container.offsetHeight || window.innerHeight;
  };
  window.addEventListener('resize', () => { resize(); spawnParticles(); });
  resize();

  function randomParticle() {
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.5 + 0.4,
      dx: (Math.random() - 0.5) * 0.3,
      dy: (Math.random() - 0.5) * 0.3,
      alpha: Math.random() * 0.6 + 0.1,
    };
  }

  function spawnParticles() {
    const count = Math.floor((W * H) / 14000);
    particles = Array.from({ length: count }, randomParticle);
  }
  spawnParticles();

  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(99,102,241,${p.alpha})`;
      ctx.fill();

      p.x += p.dx;
      p.y += p.dy;
      if (p.x < 0) p.x = W;
      if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H;
      if (p.y > H) p.y = 0;
    });

    // Draw connecting lines
    particles.forEach((a, i) => {
      for (let j = i + 1; j < particles.length; j++) {
        const b = particles[j];
        const dist = Math.hypot(a.x - b.x, a.y - b.y);
        if (dist < 110) {
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(99,102,241,${0.07 * (1 - dist / 110)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    });

    requestAnimationFrame(draw);
  }
  draw();
})();

// ---- Active nav link highlight ----
const sections = document.querySelectorAll('section[id]');
const navItems = document.querySelectorAll('.nav-links a');

const sectionObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navItems.forEach(a => {
          a.style.color = '';
          if (a.getAttribute('href') === '#' + entry.target.id) {
            a.style.color = '#fff';
          }
        });
      }
    });
  },
  { threshold: 0.4 }
);
sections.forEach(s => sectionObserver.observe(s));

// ---- Contact form — EmailJS ----
// ⚙️  SETUP REQUIRED (one-time, ~2 minutes):
//   1. Go to https://www.emailjs.com/ and sign up (free)
//   2. Add an Email Service  → copy the  Service ID
//   3. Create an Email Template with these variables:
//        {{from_name}}  {{from_email}}  {{subject}}  {{message}}
//      Set "To Email" to bhargav.h.vagadiya@gmail.com → copy the Template ID
//   4. Go to Account → API Keys → copy the Public Key
//   5. Replace the three placeholder strings below + in index.html

const EMAILJS_SERVICE_ID = 'YOUR_SERVICE_ID';   // injected by GitHub Actions
const EMAILJS_TEMPLATE_ID = 'YOUR_TEMPLATE_ID';  // injected by GitHub Actions
// Public Key is injected into index.html via GitHub Actions (YOUR_PUBLIC_KEY)

function handleSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const btn = document.getElementById('submit-btn');
  const success = document.getElementById('form-success');
  const error = document.getElementById('form-error');

  // Reset previous feedback
  success.style.display = 'none';
  error.style.display = 'none';

  btn.disabled = true;
  btn.querySelector('span').textContent = 'Sending…';

  const templateParams = {
    from_name: form.name.value.trim(),
    from_email: form.email.value.trim(),
    subject: form.subject.value.trim(),
    message: form.message.value.trim(),
    to_email: 'bhargav.h.vagadiya@gmail.com',
  };

  emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, templateParams)
    .then(() => {
      success.style.display = 'block';
      form.reset();
      setTimeout(() => { success.style.display = 'none'; }, 6000);
    })
    .catch((err) => {
      console.error('EmailJS error:', err);
      error.style.display = 'block';
      setTimeout(() => { error.style.display = 'none'; }, 6000);
    })
    .finally(() => {
      btn.disabled = false;
      btn.querySelector('span').textContent = 'Send Message';
    });
}

// ---- Smooth typing effect on phone screen ----
(function typingEffect() {
  const lines = document.querySelectorAll('.screen-code .code-line');
  lines.forEach((line, i) => {
    line.style.opacity = '0';
    line.style.transition = `opacity 0.4s ease ${i * 0.15 + 0.5}s`;
    setTimeout(() => { line.style.opacity = '1'; }, i * 150 + 500);
  });
})();

// ============================================================
//  AI CHATBOT
// ============================================================

const AI_BASE_URL = 'https://portfolio-five-tawny-21.vercel.app/api'; // change this to your deployed URL when ready

// ---- Configure marked.js for chat ----
if (typeof marked !== 'undefined') {
  // Custom renderer: wrap tables in a scrollable div
  const renderer = new marked.Renderer();
  renderer.table = function (header, body) {
    return `<div class="table-wrap"><table><thead>${header}</thead><tbody>${body}</tbody></table></div>`;
  };

  marked.setOptions({
    breaks: true,       // newlines → <br>
    gfm: true,          // GitHub-flavoured markdown
    mangle: false,
    headerIds: false,
    renderer,
  });
}

function renderMarkdown(text) {
  if (typeof marked === 'undefined') return text;
  return marked.parse(text);
}


let chatOpen = false;
let chatBusy = false;

// ---- Toggle panel ----
function toggleChat() {
  const panel = document.getElementById('chat-panel');
  const fab = document.getElementById('chat-fab');
  const iconOpen = document.getElementById('icon-open');
  const iconClose = document.getElementById('icon-close');

  chatOpen = !chatOpen;
  panel.classList.toggle('open', chatOpen);
  fab.classList.toggle('open', chatOpen);

  iconOpen.style.display = chatOpen ? 'none' : 'block';
  iconClose.style.display = chatOpen ? 'block' : 'none';

  if (chatOpen) {
    setTimeout(() => document.getElementById('chat-input').focus(), 350);
  }
}

// ---- Keyboard: Enter sends, Shift+Enter newline ----
function handleChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendChatMessage();
  }
}

// ---- Auto-resize textarea ----
function autoResizeInput(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 90) + 'px';
}

// ---- Suggested question chips ----
function sendSuggestion(btn) {
  // Strip emoji span text and get the full text
  const text = btn.innerText.trim();
  document.getElementById('chat-input').value = text;
  sendChatMessage();
}

// ---- Append a message bubble ----
function appendMessage(role, text) {
  const welcome = document.getElementById('chat-welcome');
  if (welcome) welcome.remove();

  const msgs = document.getElementById('chat-messages');

  const row = document.createElement('div');
  row.className = `chat-msg ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = role === 'ai' ? 'BV' : 'You';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  if (role === 'ai' && text) {
    bubble.innerHTML = renderMarkdown(text);
  } else {
    // User messages: plain text (escape HTML for safety)
    bubble.textContent = text;
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  msgs.appendChild(row);
  scrollToBottom();
  return bubble;
}

// ---- Typing indicator ----
function showTyping() {
  const msgs = document.getElementById('chat-messages');
  const row = document.createElement('div');
  row.className = 'chat-typing';
  row.id = 'typing-indicator';

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.style.cssText = 'background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.6rem;font-weight:700;flex-shrink:0';
  avatar.textContent = 'BV';

  const bubble = document.createElement('div');
  bubble.className = 'typing-bubble';
  [1, 2, 3].forEach(() => {
    const dot = document.createElement('div');
    dot.className = 'typing-dot';
    bubble.appendChild(dot);
  });

  row.appendChild(avatar);
  row.appendChild(bubble);
  msgs.appendChild(row);
  scrollToBottom();
}

function removeTyping() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

function scrollToBottom() {
  const msgs = document.getElementById('chat-messages');
  msgs.scrollTop = msgs.scrollHeight;
}

// ---- Main send function (non-streaming /chat endpoint) ----
async function sendChatMessage() {
  if (chatBusy) return;

  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send-btn');
  const message = input.value.trim();
  if (!message) return;

  // Clear input
  input.value = '';
  input.style.height = 'auto';

  // Show user bubble
  appendMessage('user', message);

  // Lock UI
  chatBusy = true;
  sendBtn.disabled = true;

  // Show typing indicator while waiting for response
  showTyping();

  let aiBubble = null;

  try {
    const res = await fetch(`${AI_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    const fullText = (data.response || '').trim();

    removeTyping();
    aiBubble = appendMessage('ai', '');

    if (!fullText) {
      aiBubble.classList.add('error');
      aiBubble.textContent = '⚠️ No response received. Is the AI server running?';
    } else {
      // Typewriter: reveal words one-by-one, re-render markdown each step
      await typewriterReveal(aiBubble, fullText);
    }

  } catch (err) {
    removeTyping();
    if (!aiBubble) aiBubble = appendMessage('ai', '');
    aiBubble.classList.add('error');
    aiBubble.textContent = '⚠️ Could not reach the AI server. Start it with: uvicorn main:app --reload';
    console.error('[Chatbot]', err);
  } finally {
    chatBusy = false;
    sendBtn.disabled = false;
    scrollToBottom();
  }
}

// ---- Typewriter word-reveal effect ----
function typewriterReveal(bubble, fullText) {
  return new Promise(resolve => {
    const words = fullText.split(' ');
    let revealed = '';
    let i = 0;

    function step() {
      if (i >= words.length) {
        // Final render with full text to ensure correct markdown
        bubble.innerHTML = renderMarkdown(fullText);
        scrollToBottom();
        resolve();
        return;
      }
      revealed += (i === 0 ? '' : ' ') + words[i];
      bubble.innerHTML = renderMarkdown(revealed);
      scrollToBottom();
      i++;
      // Slight speed variation for a natural feel
      const delay = words[i - 1].length > 6 ? 40 : 28;
      setTimeout(step, delay);
    }

    step();
  });
}



