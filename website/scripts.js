/* ============================================================
   PLUGINS MX · Interacciones JS
   ============================================================ */

(function () {
  'use strict';

  // ----------------------------------------
  // 1. SCROLL REVEAL con IntersectionObserver
  // ----------------------------------------
  const revealTargets = document.querySelectorAll(
    '.section-head, .productos-grid, .big-stats, .mcp-cat, .vert-grid, .casos-grid, .como-grid, .code-frame, .demo-card'
  );

  revealTargets.forEach((el) => {
    if (el.classList.contains('vert-grid') ||
        el.classList.contains('mcp-list') ||
        el.classList.contains('productos-grid') ||
        el.classList.contains('big-stats') ||
        el.classList.contains('casos-grid')) {
      el.classList.add('reveal-stagger');
    } else {
      el.classList.add('reveal');
    }
  });

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -60px 0px' }
  );

  revealTargets.forEach((el) => io.observe(el));

  // ----------------------------------------
  // 2. COUNT-UP ANIMATION para stats
  // ----------------------------------------
  const counters = document.querySelectorAll('[data-target]');

  const animateCount = (el) => {
    const target = parseFloat(el.dataset.target);
    const suffix = el.dataset.suffix || '';
    const duration = 1800;
    const start = performance.now();
    const isInt = Number.isInteger(target);

    const tick = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out-expo
      const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      const current = target * eased;
      el.textContent = (isInt ? Math.floor(current) : current.toFixed(1)) + suffix;
      if (progress < 1) requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
  };

  const counterObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.5 }
  );

  counters.forEach((el) => counterObserver.observe(el));

  // ----------------------------------------
  // 3. TILT 3D en cards de producto (hover)
  // ----------------------------------------
  const tiltCards = document.querySelectorAll('.prod, .caso');

  tiltCards.forEach((card) => {
    let rafId = null;

    card.addEventListener('mousemove', (e) => {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const xRot = ((y - rect.height / 2) / rect.height) * -3;
        const yRot = ((x - rect.width / 2) / rect.width) * 3;
        card.style.transform = `perspective(900px) rotateX(${xRot}deg) rotateY(${yRot}deg) translateY(-6px)`;
      });
    });

    card.addEventListener('mouseleave', () => {
      if (rafId) cancelAnimationFrame(rafId);
      card.style.transform = '';
    });
  });

  // ----------------------------------------
  // 4. SMOOTH ANCHOR con offset por nav sticky
  // ----------------------------------------
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id.length <= 1) return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      const navH = document.querySelector('.nav')?.offsetHeight || 60;
      const top = target.getBoundingClientRect().top + window.scrollY - navH - 20;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  // ----------------------------------------
  // 5. NAV: cambia opacidad / sombra al scroll
  // ----------------------------------------
  const nav = document.querySelector('.nav');
  let lastScroll = 0;

  window.addEventListener(
    'scroll',
    () => {
      const y = window.scrollY;
      if (nav) {
        if (y > 40) {
          nav.style.boxShadow = '0 4px 24px -8px rgba(22, 19, 19, 0.08)';
        } else {
          nav.style.boxShadow = 'none';
        }
      }
      lastScroll = y;
    },
    { passive: true }
  );

  // ----------------------------------------
  // 6. CURSOR personalizado en sección hero
  //    (sutil, solo highlight)
  // ----------------------------------------
  // Se omite por respeto a accesibilidad / dispositivos touch.

  // ----------------------------------------
  // 7. MAGNETIC BUTTON sobre el CTA primario
  // ----------------------------------------
  const magnetic = document.querySelectorAll('.btn-primary');

  magnetic.forEach((btn) => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate(${x * 0.15}px, ${y * 0.2}px) translateY(-2px)`;
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.transform = '';
    });
  });
})();

// ----------------------------------------
// 8. Form handler (demo de captura)
// ----------------------------------------
function handleDemo(event) {
  event.preventDefault();
  const form = event.target;
  const data = Object.fromEntries(new FormData(form));

  // Construir mensaje WhatsApp
  const msg = encodeURIComponent(
    `Hola Elías,\n\nSoy ${data.nombre} de ${data.empresa}.\nMe interesa: ${data.interes}\n\nEmail: ${data.email}` +
      (data.tel ? `\nTel: ${data.tel}` : '') +
      `\n\nQuiero agendar la demo de 20 min.`
  );

  // Email principal + fallback WhatsApp
  const wa = `https://wa.me/525500000000?text=${msg}`; // reemplazar número
  const mailto = `mailto:elias@cipreholding.com?subject=${encodeURIComponent(
    'Demo Plugins MX · ' + data.empresa
  )}&body=${msg}`;

  // Mensaje de éxito visual (textContent para evitar XSS — contenido controlado)
  const btn = form.querySelector('button[type="submit"]');
  const btnSpan = btn.querySelector('span');
  if (btnSpan) btnSpan.textContent = '✓ Abriendo tu cliente de correo…';
  btn.style.background = 'var(--c-jade)';

  // Abrir mailto
  setTimeout(() => {
    window.location.href = mailto;
    setTimeout(() => {
      if (btnSpan) btnSpan.textContent = 'Agendar mi demo →';
      btn.style.background = '';
      form.reset();
    }, 2000);
  }, 600);
}
