// ── HAMBURGER MENU ─────────────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks   = document.querySelector('.nav-links');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    navLinks.classList.toggle('open');
  });
  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
      hamburger.classList.remove('open');
      navLinks.classList.remove('open');
    }
  });
}

// ── NEWSLETTER MOCK ────────────────────────────
function handleNewsletter(e) {
  e.preventDefault();
  const input = e.target.querySelector('input[type="email"]');
  const btn   = e.target.querySelector('button');
  btn.textContent  = '✓ Subscribed!';
  btn.style.background = '#16a34a';
  input.value = '';
  setTimeout(() => {
    btn.textContent  = 'Subscribe';
    btn.style.background = '';
  }, 3000);
}

// ── AUTO-DISMISS FLASH ─────────────────────────
const flash = document.querySelector('.flash');
if (flash) {
  setTimeout(() => {
    flash.style.transition = 'opacity .5s';
    flash.style.opacity = '0';
    setTimeout(() => flash.parentElement && flash.parentElement.remove(), 500);
  }, 3500);
}
