document.addEventListener('DOMContentLoaded', () => {

  // 0. Smart Header (Hide on scroll down, show on scroll up)
  const header = document.getElementById('header');
  if (header) {
    let lastScrollY = window.scrollY;
    let ticking = false;

    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const currentScrollY = window.scrollY;
          // Hide when scrolling down past 80px, reveal when scrolling up
          if (currentScrollY > 80 && currentScrollY > lastScrollY) {
            header.classList.add('-translate-y-full');
          } else {
            header.classList.remove('-translate-y-full');
          }
          lastScrollY = currentScrollY <= 0 ? 0 : currentScrollY;
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  // 1. Live REC Timer (CCTV timecode)
  const recTimerEl = document.getElementById('rec-timer');
  if (recTimerEl) {
    let seconds = 0;
    setInterval(() => {
      seconds++;
      const hrs = String(Math.floor(seconds / 3600)).padStart(2, '0');
      const mins = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
      const secs = String(seconds % 60).padStart(2, '0');
      recTimerEl.textContent = `${hrs}:${mins}:${secs}`;
    }, 1000);
  }

  // 1b. Dynamic Current Date (Figma: "Дата отображается актуальная DATE / DD.MM.YYYY")
  const heroDateEl = document.getElementById('hero-date');
  if (heroDateEl) {
    const now = new Date();
    const d = String(now.getDate()).padStart(2, '0');
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const y = now.getFullYear();
    heroDateEl.textContent = `DATE / ${d}.${m}.${y}`;
  }

  // 1c. Section 01 Scroll Reveal (Title lines masked reveal + Cards staggered entrance)
  const expertiseSection = document.getElementById('expertise');
  if (expertiseSection) {
    const expertiseObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          expertiseSection.classList.add('is-visible');
          expertiseObserver.unobserve(expertiseSection);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    expertiseObserver.observe(expertiseSection);
  }

  // 1d. Section 02 Scroll Reveal (Service Cards Staggered Entrance)
  const servicesSection = document.getElementById('services');
  if (servicesSection) {
    const servicesObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          servicesSection.classList.add('is-visible');
          servicesObserver.unobserve(servicesSection);
        }
      });
    }, { threshold: 0.10, rootMargin: '0px 0px -40px 0px' });

    servicesObserver.observe(servicesSection);
  }

  // 1e. CTA Banner Gradient Reveal ("Плавно появляется градиент")
  const bannerContainer = document.querySelector('.banner-container');
  if (bannerContainer) {
    const bannerObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          bannerContainer.classList.add('is-visible');
          bannerObserver.unobserve(bannerContainer);
        }
      });
    }, { threshold: 0.20, rootMargin: '0px 0px -50px 0px' });

    bannerObserver.observe(bannerContainer);
  }

  // 2. Mobile Menu Drawer Toggle
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const closeMenuBtn = document.getElementById('close-menu-btn');
  const mobileDrawer = document.getElementById('mobile-drawer');
  const drawerBackdrop = document.getElementById('drawer-backdrop');
  const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');

  function openMobileMenu() {
    if (!mobileDrawer || !drawerBackdrop) return;
    mobileDrawer.classList.remove('translate-x-full');
    drawerBackdrop.classList.remove('opacity-0', 'pointer-events-none');
    document.body.style.overflow = 'hidden';
  }

  function closeMobileMenu() {
    if (!mobileDrawer || !drawerBackdrop) return;
    mobileDrawer.classList.add('translate-x-full');
    drawerBackdrop.classList.add('opacity-0', 'pointer-events-none');
    document.body.style.overflow = '';
  }

  if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', openMobileMenu);
  if (closeMenuBtn) closeMenuBtn.addEventListener('click', closeMobileMenu);
  if (drawerBackdrop) drawerBackdrop.addEventListener('click', closeMobileMenu);
  mobileNavLinks.forEach(link => link.addEventListener('click', closeMobileMenu));

  // 3. Fast Odometer Animation for Section 03 (Figma annotation: "У цифр быстрый одометр")
  const odometerEls = document.querySelectorAll('.stat-odometer, .counter-val');
  let countersAnimated = false;

  function runFastOdometer() {
    odometerEls.forEach(counter => {
      const target = parseInt(counter.dataset.target, 10);
      if (isNaN(target)) return;
      if (target === 0) {
        counter.textContent = '0';
        return;
      }

      const duration = 1100; // ms: fast and responsive
      const startTime = performance.now();

      function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Exponential deceleration curve for crisp mechanical odometer feel
        const ease = 1 - Math.pow(1 - progress, 4);
        const currentVal = Math.floor(ease * target);

        counter.textContent = currentVal;

        if (progress < 1) {
          requestAnimationFrame(update);
        } else {
          counter.textContent = target; // Ensure exact final target number
        }
      }

      requestAnimationFrame(update);
    });
  }

  const countObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !countersAnimated) {
        countersAnimated = true;
        runFastOdometer();
      }
    });
  }, { threshold: 0.25 });

  const statsSection = document.getElementById('why-us') || document.querySelector('.stat-odometer, .counter-val')?.closest('section');
  if (statsSection) {
    countObserver.observe(statsSection);
  }

  // 4. Section 04: Interactive Step Accordion Rows
  const stageRows = document.querySelectorAll('.stage-row');
  stageRows.forEach(row => {
    row.addEventListener('click', () => {
      stageRows.forEach(r => r.classList.remove('is-active'));
      row.classList.add('is-active');
    });
  });

  // 5. FAQ Accordion Toggle
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    item.addEventListener('click', () => {
      const answer = item.querySelector('.faq-answer');
      const icon = item.querySelector('.faq-icon');
      if (!answer) return;

      const isClosed = answer.classList.contains('hidden');

      // Close all
      faqItems.forEach(other => {
        const otherAns = other.querySelector('.faq-answer');
        const otherIcon = other.querySelector('.faq-icon');
        if (otherAns) otherAns.classList.add('hidden');
        if (otherIcon) otherIcon.textContent = '+';
      });

      if (isClosed) {
        answer.classList.remove('hidden');
        if (icon) icon.textContent = '−';
      }
    });
  });

  // 6. Interactive Calculator
  const calcButtons = document.querySelectorAll('#calc-service-group .calc-btn');
  const areaSlider = document.getElementById('area-slider');
  const areaVal = document.getElementById('area-val');
  const calcTotalPrice = document.getElementById('calc-total-price');
  let currentRate = 450; // default rate per sq meter base

  function updateCalcTotal() {
    const area = parseInt(areaSlider ? areaSlider.value : '150', 10);
    if (areaVal) areaVal.textContent = area;
    const baseEquipment = 25000;
    const total = Math.round(baseEquipment + (area * currentRate));
    if (calcTotalPrice) {
      calcTotalPrice.textContent = total.toLocaleString('ru-RU');
    }
  }

  calcButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      calcButtons.forEach(b => {
        b.classList.remove('border-brand-red', 'text-white');
        b.classList.add('border-white/10', 'text-white/70');
      });
      btn.classList.add('border-brand-red', 'text-white');
      btn.classList.remove('border-white/10', 'text-white/70');
      currentRate = parseInt(btn.dataset.rate, 10) || 450;
      updateCalcTotal();
    });
  });

  if (areaSlider) {
    areaSlider.addEventListener('input', updateCalcTotal);
  }

  // 7. Strict Phone Input Formatting and Validation
  const phoneInputs = document.querySelectorAll('input[type="tel"]');
  phoneInputs.forEach(input => {
    input.addEventListener('input', (e) => {
      let value = e.target.value.replace(/\D/g, '');
      if (!value) {
        e.target.value = '';
        return;
      }
      if (['7', '8', '9'].includes(value[0])) {
        if (value[0] === '9') value = '7' + value;
        let formatted = '+7 (';
        if (value.length > 1) formatted += value.substring(1, 4);
        if (value.length >= 4) formatted += ') ' + value.substring(4, 7);
        if (value.length >= 7) formatted += '-' + value.substring(7, 9);
        if (value.length >= 9) formatted += '-' + value.substring(9, 11);
        e.target.value = formatted;
      } else {
        e.target.value = '+' + value.substring(0, 15);
      }
    });
  });

  // 8. Modal Lead Form Handling
  const leadModal = document.getElementById('lead-modal');
  const closeModalBtn = document.getElementById('close-modal-btn');
  const openModalBtns = document.querySelectorAll('.open-modal-btn');
  const leadForm = document.getElementById('lead-form');
  const modalSuccess = document.getElementById('modal-success');
  const modalSuccessClose = document.getElementById('modal-success-close');

  function openModal() {
    if (!leadModal) return;
    leadModal.classList.remove('opacity-0', 'pointer-events-none');
    document.body.style.overflow = 'hidden';
    if (leadForm) leadForm.classList.remove('hidden');
    if (modalSuccess) modalSuccess.classList.add('hidden');
  }

  function closeModal() {
    if (!leadModal) return;
    leadModal.classList.add('opacity-0', 'pointer-events-none');
    document.body.style.overflow = '';
  }

  openModalBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openModal();
    });
  });

  if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
  if (modalSuccessClose) modalSuccessClose.addEventListener('click', closeModal);
  if (leadModal) {
    leadModal.addEventListener('click', (e) => {
      if (e.target === leadModal) closeModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeModal();
      closeMobileMenu();
    }
  });

  // Modal Form Submit with strict validation
  if (leadForm) {
    leadForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const phoneInput = document.getElementById('modal-phone');
      const phoneError = document.getElementById('modal-phone-error');
      const cleanPhone = phoneInput ? phoneInput.value.replace(/\D/g, '') : '';

      if (cleanPhone.length < 11) {
        if (phoneError) phoneError.classList.remove('hidden');
        if (phoneInput) {
          phoneInput.focus();
          phoneInput.classList.add('border-brand-red');
        }
        return;
      }

      if (phoneError) phoneError.classList.add('hidden');
      if (leadForm) leadForm.classList.add('hidden');
      if (modalSuccess) modalSuccess.classList.remove('hidden');
      leadForm.reset();
    });
  }

  // Calculator Form Submit with validation
  const calcForm = document.getElementById('calc-form');
  if (calcForm) {
    calcForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const phoneInput = document.getElementById('calc-phone');
      const phoneError = document.getElementById('calc-phone-error');
      const cleanPhone = phoneInput ? phoneInput.value.replace(/\D/g, '') : '';

      if (cleanPhone.length < 11) {
        if (phoneError) phoneError.classList.remove('hidden');
        if (phoneInput) {
          phoneInput.focus();
          phoneInput.classList.add('border-brand-red');
        }
        return;
      }

      if (phoneError) phoneError.classList.add('hidden');
      openModal();
      if (leadForm) leadForm.classList.add('hidden');
      if (modalSuccess) modalSuccess.classList.remove('hidden');
      calcForm.reset();
    });
  }

});
