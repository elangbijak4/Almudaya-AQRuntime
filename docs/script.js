/* ==========================================================================
   AQRuntime Landing Page Interactive Script
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Sticky Navbar Glass Glow on Scroll
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.5)';
      navbar.style.borderColor = 'rgba(0, 242, 254, 0.2)';
    } else {
      navbar.style.boxShadow = 'none';
      navbar.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }
  });
});

// Copy CLI Commands Function
function copyCliCommands() {
  const commands = `aq help
aq ui
aq doctor
aq discover audio
aq pull bartowski/gemma-2-2b-it-GGUF
aq run bartowski/gemma-2-2b-it-GGUF --max-tokens 2048`;

  navigator.clipboard.writeText(commands).then(() => {
    const btn = document.querySelector('.btn-copy');
    if (btn) {
      const originalText = btn.innerText;
      btn.innerText = '✓ Copied!';
      btn.style.background = '#10b981';
      btn.style.color = '#ffffff';
      setTimeout(() => {
        btn.innerText = originalText;
        btn.style.background = 'rgba(255, 255, 255, 0.08)';
        btn.style.color = 'var(--text-muted)';
      }, 2000);
    }
  }).catch(err => {
    alert('Failed to copy to clipboard.');
  });
}
