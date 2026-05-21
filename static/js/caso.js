// static/js/caso.js
// -------------------------------------------------------
// Página Caso de Estudio
// 1. Scroll Spy inteligente
// 2. Smooth Scroll responsive
// 3. Animación de barras
// 4. Navbar horizontal en móviles
// 5. Optimización rendimiento
// -------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {

  // ─────────────────────────────────────────────
  // ELEMENTOS
  // ─────────────────────────────────────────────

  const navLinks = document.querySelectorAll('.snav-link');
  const sections = document.querySelectorAll('.case-section');
  const header = document.querySelector('.site-header');
  const resultSection = document.getElementById('resultados');
  const bars = document.querySelectorAll('.ub-fill');

  // Si no existen elementos, evitar errores
  if (!sections.length || !navLinks.length) return;

  // ─────────────────────────────────────────────
  // 1. SCROLL SPY MEJORADO
  // ─────────────────────────────────────────────

  let currentActive = null;

  const activateLink = (id) => {

    // Evitar renders innecesarios
    if (currentActive === id) return;

    currentActive = id;

    navLinks.forEach(link => {
      link.classList.remove('active');

      if (link.getAttribute('href') === `#${id}`) {
        link.classList.add('active');

        // Scroll horizontal automático en móvil
        if (window.innerWidth <= 1024) {
          link.scrollIntoView({
            behavior: 'smooth',
            inline: 'center',
            block: 'nearest'
          });
        }
      }
    });
  };

  // Observer optimizado
  const sectionObserver = new IntersectionObserver((entries) => {

    entries.forEach(entry => {

      if (entry.isIntersecting) {
        activateLink(entry.target.id);
      }

    });

  }, {
    threshold: 0.35,
    rootMargin: '-20% 0px -55% 0px'
  });

  sections.forEach(section => {
    sectionObserver.observe(section);
  });

  // ─────────────────────────────────────────────
  // 2. SMOOTH SCROLL RESPONSIVE
  // ─────────────────────────────────────────────

  navLinks.forEach(link => {

    link.addEventListener('click', (e) => {

      e.preventDefault();

      const targetId = link.getAttribute('href').replace('#', '');
      const target = document.getElementById(targetId);

      if (!target) return;

      const headerHeight = header ? header.offsetHeight : 0;

      // Offset dinámico responsive
      const extraOffset = window.innerWidth <= 768 ? 12 : 20;

      const y =
        target.getBoundingClientRect().top +
        window.scrollY -
        headerHeight -
        extraOffset;

      window.scrollTo({
        top: y,
        behavior: 'smooth'
      });

    });

  });

  // ─────────────────────────────────────────────
  // 3. ANIMACIÓN DE BARRAS
  // ─────────────────────────────────────────────

  if (bars.length && resultSection) {

    // Guardar anchos originales
    const targetWidths = [];

    bars.forEach(bar => {

      const width = bar.style.width || '0%';

      targetWidths.push(width);

      // Estado inicial
      bar.style.width = '0%';
      bar.style.opacity = '0';

    });

    const barsObserver = new IntersectionObserver((entries) => {

      entries.forEach(entry => {

        if (entry.isIntersecting) {

          bars.forEach((bar, index) => {

            setTimeout(() => {

              bar.style.transition =
                'width .9s cubic-bezier(.4,0,.2,1), opacity .4s ease';

              bar.style.width = targetWidths[index];
              bar.style.opacity = '1';

            }, index * 140);

          });

          // Solo una vez
          barsObserver.disconnect();

        }

      });

    }, {
      threshold: 0.25
    });

    barsObserver.observe(resultSection);
  }

  // ─────────────────────────────────────────────
  // 4. EFECTO SHADOW HEADER AL SCROLL
  // ─────────────────────────────────────────────

  const handleHeaderShadow = () => {

    if (!header) return;

    if (window.scrollY > 10) {
      header.classList.add('header-scrolled');
    } else {
      header.classList.remove('header-scrolled');
    }

  };

  window.addEventListener('scroll', handleHeaderShadow, {
    passive: true
  });

  // ─────────────────────────────────────────────
  // 5. REVEAL ANIMATIONS
  // ─────────────────────────────────────────────

  const revealElements = document.querySelectorAll(
    '.info-card, .resource-card, .result-card, .concl-item'
  );

  const revealObserver = new IntersectionObserver((entries) => {

    entries.forEach(entry => {

      if (entry.isIntersecting) {

        entry.target.classList.add('revealed');

        revealObserver.unobserve(entry.target);

      }

    });

  }, {
    threshold: 0.12
  });

  revealElements.forEach(el => {

    el.classList.add('reveal-init');

    revealObserver.observe(el);

  });

});