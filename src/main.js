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

  // 1f. Section 04 Scroll Reveal (Steps Staggered Entrance)
  const stepsSection = document.getElementById('steps');
  if (stepsSection) {
    const stepsObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          stepsSection.classList.add('is-visible');
          stepsObserver.unobserve(stepsSection);
        }
      });
    }, { threshold: 0.10, rootMargin: '0px 0px -40px 0px' });

    stepsObserver.observe(stepsSection);
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

  // Fast mechanical odometer animation helper (Figma annotation: "У цифр быстрый одометр")
  function animateOdometerGroup(elements, duration = 1000) {
    elements.forEach(counter => {
      const target = parseInt(counter.dataset.target, 10);
      if (isNaN(target)) return;
      if (target === 0) {
        counter.textContent = '0';
        return;
      }

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

  // 3. Fast Odometer Animation for Section 03
  const sec3Odometers = document.querySelectorAll('#why-us .stat-odometer');
  let sec3Animated = false;
  const statsSection = document.getElementById('why-us');
  if (statsSection && sec3Odometers.length) {
    const countObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !sec3Animated) {
          sec3Animated = true;
          animateOdometerGroup(sec3Odometers, 1100);
        }
      });
    }, { threshold: 0.25 });
    countObserver.observe(statsSection);
  }

  // 3.1. Section 06: Stacking Cases Cards & Fast Odometer Controller
  const caseCards = document.querySelectorAll('.case-card');
  const caseTabs = document.querySelectorAll('.case-tab-btn');
  let activeCaseIdx = 0;

  function setCaseStack(targetIdx) {
    if (targetIdx < 0 || targetIdx >= caseCards.length) return;
    activeCaseIdx = targetIdx;

    // Update tabs
    caseTabs.forEach((btn, idx) => {
      if (idx === targetIdx) {
        btn.classList.add('active');
        btn.classList.remove('bg-[#141519]', 'text-white/60', 'border-white/10');
        btn.classList.add('bg-[#1A1C22]', 'text-white', 'border-white/20');
      } else {
        btn.classList.remove('active');
        btn.classList.remove('bg-[#1A1C22]', 'text-white', 'border-white/20');
        btn.classList.add('bg-[#141519]', 'text-white/60', 'border-white/10');
      }
    });

    // Update 3 cards stacking depth (Figma: "Наслаивание карточек с перекрытием предыдущей, её затемнением и уменьшением")
    caseCards.forEach((card) => {
      const cardIdx = parseInt(card.dataset.caseIdx, 10);
      card.classList.remove('card-pos-front', 'card-pos-middle', 'card-pos-back');

      if (cardIdx === targetIdx) {
        card.classList.add('card-pos-front');
        // Trigger fast odometer for this card
        const cardOdometers = card.querySelectorAll('.stat-odometer');
        animateOdometerGroup(cardOdometers, 800);
      } else if (cardIdx === (targetIdx + 1) % 3) {
        card.classList.add('card-pos-middle');
      } else {
        card.classList.add('card-pos-back');
      }
    });
  }

  // Click on card tabs
  caseTabs.forEach((tab) => {
    tab.addEventListener('click', (e) => {
      e.stopPropagation();
      const idx = parseInt(tab.dataset.caseIndex, 10);
      setCaseStack(idx);
    });
  });

  // Click on layered cards
  caseCards.forEach((card) => {
    card.addEventListener('click', () => {
      const idx = parseInt(card.dataset.caseIdx, 10);
      if (idx !== activeCaseIdx) {
        setCaseStack(idx);
      }
    });
  });

  // Section 06 Intersection Observer to trigger initial fast odometer
  const casesSection = document.getElementById('cases');
  let casesAnimated = false;
  if (casesSection) {
    const casesObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !casesAnimated) {
          casesAnimated = true;
          const frontCard = document.querySelector('.case-card.card-pos-front');
          if (frontCard) {
            const frontOdometers = frontCard.querySelectorAll('.stat-odometer');
            animateOdometerGroup(frontOdometers, 900);
          }
        }
      });
    }, { threshold: 0.2 });
    casesObserver.observe(casesSection);
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

  // 7. Strict Phone Input Formatting and Validation (+7 (XXX) XXX-XX-XX)
  const phoneInputs = document.querySelectorAll('input[type="tel"]');
  phoneInputs.forEach(input => {
    // When focusing an empty input, prime it with +7 (
    input.addEventListener('focus', () => {
      if (!input.value.trim()) {
        input.value = '+7 (';
      }
    });

    input.addEventListener('input', (e) => {
      let value = e.target.value.replace(/\D/g, '');
      if (!value) {
        e.target.value = '';
        return;
      }
      // If user typed without 7 (e.g. 9...), prepend 7
      if (['7', '8'].includes(value[0])) {
        value = '7' + value.substring(1);
      } else {
        value = '7' + value;
      }

      let formatted = '+7 (';
      if (value.length > 1) formatted += value.substring(1, 4);
      if (value.length >= 4) formatted += ') ' + value.substring(4, 7);
      if (value.length >= 7) formatted += '-' + value.substring(7, 9);
      if (value.length >= 9) formatted += '-' + value.substring(9, 11);
      e.target.value = formatted;

      // Clear red border and error message when valid length reached
      if (value.length === 11) {
        input.classList.remove('border-brand-red');
        const err = input.parentElement.querySelector('#consult-phone-error, #modal-lead-phone-error');
        if (err) err.classList.add('hidden');
      }
    });

    input.addEventListener('blur', () => {
      const clean = input.value.replace(/\D/g, '');
      if (clean === '7' || clean === '') {
        input.value = '';
        input.classList.remove('border-brand-red');
        const err = input.parentElement.querySelector('#consult-phone-error, #modal-lead-phone-error');
        if (err) err.classList.add('hidden');
      } else if (clean.length < 11) {
        input.classList.add('border-brand-red');
        const err = input.parentElement.querySelector('#consult-phone-error, #modal-lead-phone-error');
        if (err) err.classList.remove('hidden');
      } else {
        input.classList.remove('border-brand-red');
        const err = input.parentElement.querySelector('#consult-phone-error, #modal-lead-phone-error');
        if (err) err.classList.add('hidden');
      }
    });
  });

  // 8. Lead Consult Modal & Success Modal (Exact Figma 1440px Specs)
  const leadModal = document.getElementById('lead-modal');
  const closeLeadModalBtn = document.getElementById('close-lead-modal');
  const openModalBtns = document.querySelectorAll('.open-modal-btn');
  const modalLeadForm = document.getElementById('modal-lead-form');

  const successModal = document.getElementById('success-modal');
  const closeSuccessModalBtn = document.getElementById('close-success-modal');
  const modalHomeBtn = document.getElementById('modal-home-btn');

  function openLeadModal() {
    if (!leadModal) return;
    closeMobileMenu();
    leadModal.classList.remove('opacity-0', 'pointer-events-none');
    document.body.style.overflow = 'hidden';
  }

  function closeLeadModal() {
    if (!leadModal) return;
    leadModal.classList.add('opacity-0', 'pointer-events-none');
    if (!successModal || successModal.classList.contains('opacity-0')) {
      document.body.style.overflow = '';
    }
  }

  function openSuccessModal() {
    if (!successModal) return;
    closeLeadModal();
    closeMobileMenu();
    successModal.classList.remove('opacity-0', 'pointer-events-none');
    document.body.style.overflow = 'hidden';
  }

  function closeSuccessModal() {
    if (!successModal) return;
    successModal.classList.add('opacity-0', 'pointer-events-none');
    document.body.style.overflow = '';
  }

  openModalBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openLeadModal();
    });
  });

  if (closeLeadModalBtn) closeLeadModalBtn.addEventListener('click', closeLeadModal);
  if (closeSuccessModalBtn) closeSuccessModalBtn.addEventListener('click', closeSuccessModal);

  if (modalHomeBtn) {
    modalHomeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closeSuccessModal();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  if (leadModal) {
    leadModal.addEventListener('click', (e) => {
      if (e.target === leadModal) closeLeadModal();
    });
  }

  if (successModal) {
    successModal.addEventListener('click', (e) => {
      if (e.target === successModal) closeSuccessModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeLeadModal();
      closeSuccessModal();
      closeMobileMenu();
    }
  });

  // Modal Lead Form Submit with validation
  if (modalLeadForm) {
    modalLeadForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const phoneInput = document.getElementById('modal-lead-phone');
      const phoneError = document.getElementById('modal-lead-phone-error');
      const cleanPhone = phoneInput ? phoneInput.value.replace(/\D/g, '') : '';

      if (cleanPhone.length < 11) {
        if (phoneInput) {
          phoneInput.focus();
          phoneInput.classList.add('border-brand-red');
        }
        if (phoneError) phoneError.classList.remove('hidden');
        return;
      }

      if (phoneInput) phoneInput.classList.remove('border-brand-red');
      if (phoneError) phoneError.classList.add('hidden');
      modalLeadForm.reset();
      closeLeadModal();
      openSuccessModal();
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

  // 9. Section 04: Interactive 3D Parallax Tilt & Active Step Scroll Spy
  const installation3dWrap = document.getElementById('installation-3d-wrap');
  const stepRows = document.querySelectorAll('#steps .step-row');
  const stepsList = document.getElementById('steps') || document.querySelector('.steps-container');

  // Interactive 3D mouse tilt on equipment composition
  if (stepsSection && installation3dWrap) {
    stepsSection.addEventListener('mousemove', (e) => {
      const rect = installation3dWrap.getBoundingClientRect();
      const wrapCenterX = rect.left + rect.width / 2;
      const wrapCenterY = rect.top + rect.height / 2;
      
      const deltaX = (e.clientX - wrapCenterX) / (window.innerWidth / 2);
      const deltaY = (e.clientY - wrapCenterY) / (window.innerHeight / 2);
      
      const tiltX = -deltaY * 12; // degrees
      const tiltY = deltaX * 16;  // degrees
      
      installation3dWrap.style.transform = `perspective(1000px) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg) scale3d(1.02, 1.02, 1.02)`;
    });

    stepsSection.addEventListener('mouseleave', () => {
      installation3dWrap.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  }

  // Active step scroll spy & hover mutually exclusive highlight
  if (stepRows.length > 0) {
    let scrollActiveRow = null;
    let isHoveringStep = false;

    const updateActiveStep = () => {
      if (isHoveringStep) return;
      const viewportCenter = window.innerHeight / 2;
      let closestStep = null;
      let minDistance = Infinity;

      stepRows.forEach(row => {
        const rect = row.getBoundingClientRect();
        const rowCenter = rect.top + rect.height / 2;
        const distance = Math.abs(viewportCenter - rowCenter);

        if (distance < minDistance) {
          minDistance = distance;
          closestStep = row;
        }
      });

      if (closestStep && minDistance < 320) {
        stepRows.forEach(r => r.classList.remove('is-active'));
        closestStep.classList.add('is-active');
        scrollActiveRow = closestStep;
      }
    };

    // On hover of any step row: transfer highlight to it only
    stepRows.forEach(row => {
      row.addEventListener('mouseenter', () => {
        isHoveringStep = true;
        stepRows.forEach(r => r.classList.remove('is-active'));
        row.classList.add('is-active');
      });
    });

    // When mouse leaves the steps list: restore the scroll-active step
    if (stepsList) {
      stepsList.addEventListener('mouseleave', () => {
        isHoveringStep = false;
        stepRows.forEach(r => r.classList.remove('is-active'));
        if (scrollActiveRow) {
          scrollActiveRow.classList.add('is-active');
        } else {
          updateActiveStep();
        }
      });
    }

    window.addEventListener('scroll', updateActiveStep, { passive: true });
    updateActiveStep();
  }

  // 10. Section 05: Pinned Horizontal Card Scroll ("Фиксация экрана + горизонтальная прокрутка до конца карточек")
  const sectorsScrollContainer = document.getElementById('sectors-scroll-container');
  const sectorsStickyWindow = document.getElementById('sectors-sticky-window');
  const sectorsTrack = document.getElementById('sectors-track');

  if (sectorsScrollContainer && sectorsTrack) {
    const handleSectorsScroll = () => {
      // Only apply horizontal scroll on desktop/tablet where cards overflow track
      const trackParent = sectorsTrack.parentElement;
      if (!trackParent) return;

      const rect = sectorsScrollContainer.getBoundingClientRect();
      const scrollDist = sectorsScrollContainer.offsetHeight - window.innerHeight;

      if (scrollDist > 0) {
        // How far we have scrolled past container top
        const progress = Math.max(0, Math.min(1, -rect.top / scrollDist));
        
        // Calculate max horizontal scroll needed to fully bring the last card into comfortable view
        const trackWidth = sectorsTrack.scrollWidth;
        const visibleWidth = trackParent.clientWidth;
        const maxScroll = Math.max(0, trackWidth - visibleWidth + 64);

        const currentX = progress * maxScroll;
        sectorsTrack.style.transform = `translate3d(-${currentX.toFixed(2)}px, 0, 0)`;
      } else {
        sectorsTrack.style.transform = 'translate3d(0, 0, 0)';
      }
    };

    window.addEventListener('scroll', handleSectorsScroll, { passive: true });
    window.addEventListener('resize', handleSectorsScroll, { passive: true });
    handleSectorsScroll();
  }

  // 11. Section 05: Dynamic Speed Bank & Partner Logo Ticker ("Бегущая строка. При скролле вниз ускоряется, при скролле вверх замедляется, при наведении замирает")
  const bankTickerTrack = document.getElementById('bank-ticker-track');
  const bankTickerWrapper = document.getElementById('bank-ticker-wrapper');

  if (bankTickerTrack && bankTickerWrapper) {
    let baseSpeed = 1.0;        // Base pixels per frame
    let scrollBoost = 0;        // Momentum added from scrolling
    let tickerOffset = 0;       // Current pixel translation
    let isHovered = false;      // Hover state
    let lastScrollY = window.scrollY;

    // Hover freeze ("при наведении замирает")
    bankTickerWrapper.addEventListener('mouseenter', () => { isHovered = true; });
    bankTickerWrapper.addEventListener('mouseleave', () => { isHovered = false; });

    // Scroll speed reaction ("При скролле вниз ускоряется, при скролле вверх замедляется")
    window.addEventListener('scroll', () => {
      const currentScrollY = window.scrollY;
      const deltaY = currentScrollY - lastScrollY;
      lastScrollY = currentScrollY;

      if (deltaY > 0) {
        // Scrolling down: accelerate marquee
        scrollBoost += Math.min(deltaY * 0.16, 7.0);
      } else if (deltaY < 0) {
        // Scrolling up: decelerate marquee
        scrollBoost -= Math.min(Math.abs(deltaY) * 0.16, 5.0);
      }
    }, { passive: true });

    // Animation frame loop
    const animateBankTicker = () => {
      // Smooth decay of scroll boost back to 0
      scrollBoost *= 0.93;

      // Effective speed: never drops below 0.15 (so it doesn't freeze or reverse abruptly), capped at 9.0
      const effectiveSpeed = Math.max(0.15, Math.min(baseSpeed + scrollBoost, 9.0));

      if (!isHovered) {
        tickerOffset += effectiveSpeed;
        const halfWidth = bankTickerTrack.scrollWidth / 2;
        if (halfWidth > 0 && tickerOffset >= halfWidth) {
          tickerOffset -= halfWidth;
        }
        bankTickerTrack.style.transform = `translate3d(-${tickerOffset.toFixed(2)}px, 0, 0)`;
      }

      requestAnimationFrame(animateBankTicker);
    };

    requestAnimationFrame(animateBankTicker);
  }

  // 10. Section 07: FAQ Accordion Interactivity
  const faqRows = document.querySelectorAll('.faq-row');
  faqRows.forEach(row => {
    row.addEventListener('click', () => {
      const wasOpen = row.classList.contains('is-open');
      row.classList.toggle('is-open', !wasOpen);
    });
  });

  // Section 07: Consult Form Submission
  const consultForm = document.getElementById('consult-form');
  if (consultForm) {
    consultForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const phoneInput = document.getElementById('consult-phone');
      const phoneError = document.getElementById('consult-phone-error');
      const cleanPhone = phoneInput ? phoneInput.value.replace(/\D/g, '') : '';
      if (cleanPhone.length < 11) {
        if (phoneInput) {
          phoneInput.focus();
          phoneInput.classList.add('border-brand-red');
        }
        if (phoneError) phoneError.classList.remove('hidden');
        return;
      }
      if (phoneInput) phoneInput.classList.remove('border-brand-red');
      if (phoneError) phoneError.classList.add('hidden');
      consultForm.reset();
      openSuccessModal();
    });
  }

});
