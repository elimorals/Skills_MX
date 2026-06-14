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

  // ----------------------------------------
  // 8. RADIAL MOUSE GLOW en cards (CSS vars)
  //    .prod y .caso usan --mouse-x / --mouse-y
  // ----------------------------------------
  const glowCards = document.querySelectorAll('.prod, .caso');
  glowCards.forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      card.style.setProperty('--mouse-x', `${x}%`);
      card.style.setProperty('--mouse-y', `${y}%`);
    });
  });

  // ----------------------------------------
  // 9. HERO H1 + lede · reveal escalonado al cargar
  //    Activa .is-revealed en .hero y .hero-h1 con timing controlado
  // ----------------------------------------
  const hero = document.querySelector('.hero');
  const heroH1 = document.querySelector('.hero-h1');
  const heroLede = document.querySelector('.hero-lede');

  // Envuelve cada palabra del lede en un <span class="word"> para animarlas.
  // Recorre solo TEXT_NODE — preserva markup interno (<strong>, etc.) sin usar innerHTML.
  if (heroLede && !heroLede.querySelector('.word')) {
    let wordIdx = 0;
    const walkAndWrap = (node) => {
      // Snapshot de hijos porque vamos a mutarlos
      const children = Array.from(node.childNodes);
      children.forEach((child) => {
        if (child.nodeType === Node.TEXT_NODE) {
          const text = child.nodeValue;
          if (!text || !text.trim()) return; // espacios puros: dejar
          const frag = document.createDocumentFragment();
          // Split conservando los whitespace como nodos de texto entre spans
          const parts = text.split(/(\s+)/);
          parts.forEach((part) => {
            if (!part) return;
            if (/^\s+$/.test(part)) {
              frag.appendChild(document.createTextNode(part));
            } else {
              const span = document.createElement('span');
              span.className = 'word';
              span.textContent = part;
              span.style.setProperty('--lede-delay', String(wordIdx++));
              frag.appendChild(span);
            }
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === Node.ELEMENT_NODE) {
          walkAndWrap(child);
        }
      });
    };
    walkAndWrap(heroLede);
  }

  // Trigger reveal una vez el DOM está listo
  requestAnimationFrame(() => {
    if (heroH1) heroH1.classList.add('is-revealed');
    if (hero)   hero.classList.add('is-revealed');
  });

  // ----------------------------------------
  // 10. PARALLAX sutil en el hero · solo sobre 768px
  //     Mueve el strip-top y el marquee a velocidades distintas
  // ----------------------------------------
  if (window.innerWidth > 768 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const strip = document.querySelector('.strip-top');
    const marquee = document.querySelector('.marquee');
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const y = window.scrollY;
        if (y < 600) {
          if (strip)   strip.style.transform   = `translate3d(0, ${y * 0.15}px, 0)`;
          if (marquee) marquee.style.transform = `translate3d(0, ${y * -0.08}px, 0)`;
        }
        ticking = false;
      });
    }, { passive: true });
  }
})();

// ----------------------------------------
// 8. Form handler — POST a /api/lead-demo (Vercel Function + Resend)
//    Fallback a WhatsApp si la red falla o el servicio no está configurado.
// ----------------------------------------
const WHATSAPP_NUMBER = '522711428381'; // +52 271 142 8381 — Elías

async function handleDemo(event) {
  event.preventDefault();
  const form = event.target;
  const data = Object.fromEntries(new FormData(form));
  const btn = form.querySelector('button[type="submit"]');
  const btnSpan = btn.querySelector('span');
  const fineprint = form.querySelector('.demo-fineprint');
  const originalLabel = btnSpan ? btnSpan.textContent : '';

  // UI: enviando
  if (btnSpan) btnSpan.textContent = 'Enviando…';
  btn.disabled = true;
  btn.style.background = '';

  try {
    const r = await fetch('/api/lead-demo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${r.status}`);
    }

    // Éxito
    if (btnSpan) btnSpan.textContent = '✓ Solicitud enviada · te escribo hoy';
    btn.style.background = 'var(--c-jade, #2D6A4F)';

    if (fineprint) {
      // Reemplazo seguro con textContent + <a> creado en DOM (sin innerHTML)
      while (fineprint.firstChild) fineprint.removeChild(fineprint.firstChild);
      fineprint.appendChild(document.createTextNode('¿Prefieres WhatsApp directo? '));
      const wa = document.createElement('a');
      wa.href = buildWhatsAppLink(data);
      wa.target = '_blank';
      wa.rel = 'noopener';
      wa.textContent = 'Escríbeme aquí →';
      fineprint.appendChild(wa);
    }

    form.reset();

    setTimeout(() => {
      btn.disabled = false;
      if (btnSpan) btnSpan.textContent = originalLabel || 'Agendar mi demo →';
      btn.style.background = '';
    }, 6000);
  } catch (err) {
    console.error('[handleDemo]', err);
    if (btnSpan) btnSpan.textContent = '✗ Error · prueba por WhatsApp';
    btn.style.background = 'var(--c-terracotta, #C2410C)';
    btn.disabled = false;

    // Fallback: abrir WhatsApp directo con el mensaje pre-rellenado
    setTimeout(() => {
      window.open(buildWhatsAppLink(data), '_blank', 'noopener');
    }, 400);

    setTimeout(() => {
      if (btnSpan) btnSpan.textContent = originalLabel || 'Agendar mi demo →';
      btn.style.background = '';
    }, 5000);
  }
}

function buildWhatsAppLink(data) {
  const lines = [
    'Hola Elías,',
    '',
    `Soy ${data.nombre || ''}${data.empresa ? ' de ' + data.empresa : ''}.`,
    data.interes ? `Me interesa: ${data.interes}` : '',
    '',
    data.email ? `Email: ${data.email}` : '',
    data.tel ? `Tel: ${data.tel}` : '',
    '',
    'Quiero agendar la demo de 20 min.',
  ].filter(Boolean);
  const msg = encodeURIComponent(lines.join('\n'));
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${msg}`;
}
