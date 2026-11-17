import { 
  createIcons, 
  Cctv, 
  Phone, 
  ArrowUpRight, 
  Menu, 
  X, 
  ArrowDown, 
  Calculator, 
  ShieldCheck, 
  Boxes, 
  ChevronRight, 
  ChevronDown, 
  Wrench, 
  Camera, 
  Mail, 
  MapPin, 
  Check, 
  VideoOff 
} from 'lucide';

document.addEventListener('DOMContentLoaded', () => {
  // Initialize specific Lucide icons
  createIcons({
    icons: {
      Cctv,
      Phone,
      ArrowUpRight,
      Menu,
      X,
      ArrowDown,
      Calculator,
      ShieldCheck,
      Boxes,
      ChevronRight,
      ChevronDown,
      Wrench,
      Camera,
      Mail,
      MapPin,
      Check,
      VideoOff
    }
  });

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

  // 3. FAQ Accordion Toggle
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const button = item.querySelector('.faq-button');
    const answer = item.querySelector('.faq-answer');
    const chevron = item.querySelector('.faq-chevron');

    if (button && answer) {
      button.addEventListener('click', () => {
        const isOpen = !answer.classList.contains('hidden');
        // Close all others
        faqItems.forEach(other => {
          const otherAns = other.querySelector('.faq-answer');
          const otherChev = other.querySelector('.faq-chevron');
          if (otherAns) otherAns.classList.add('hidden');
          if (otherChev) otherChev.classList.remove('rotate-180');
        });

        if (!isOpen) {
          answer.classList.remove('hidden');
          if (chevron) chevron.classList.add('rotate-180');
        }
      });
    }
  });

  // 4. Phone Input Masking
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

  // 5. Interactive Estimate Calculator
  const serviceOptions = document.querySelectorAll('.service-pill-btn');
  const serviceHiddenInput = document.getElementById('selected-service');
  const priceDisplay = document.getElementById('calc-price-display');

  const servicePrices = {
    'cctv': 'от 28 000 ₽',
    'skud': 'от 34 000 ₽',
    'alarm': 'от 22 000 ₽',
    'fire': 'от 45 000 ₽',
    'sks': 'от 30 000 ₽',
    'electro': 'от 40 000 ₽',
    'complex': 'от 95 000 ₽'
  };

  serviceOptions.forEach(btn => {
    btn.addEventListener('click', () => {
      serviceOptions.forEach(b => {
        b.classList.remove('bg-brand-red', 'text-white', 'border-brand-red');
        b.classList.add('bg-brand-surface', 'text-brand-muted', 'border-white/10');
      });
      btn.classList.add('bg-brand-red', 'text-white', 'border-brand-red');
      btn.classList.remove('bg-brand-surface', 'text-brand-muted', 'border-white/10');
      const val = btn.dataset.service;
      if (serviceHiddenInput) serviceHiddenInput.value = val;
      if (priceDisplay && servicePrices[val]) {
        priceDisplay.textContent = servicePrices[val];
      }
    });
  });

  // 6. Lead Modal (Заявка отправлена)
  const modal = document.getElementById('success-modal');
  const modalBackdrop = document.getElementById('modal-backdrop');
  const closeModalBtns = document.querySelectorAll('.close-modal-btn');
  const leadForms = document.querySelectorAll('.lead-form');

  function openSuccessModal(name) {
    if (modal) {
      modal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      const nameEl = document.getElementById('modal-client-name');
      if (nameEl && name) nameEl.textContent = name;
    }
  }

  function closeSuccessModal() {
    if (modal) {
      modal.classList.add('hidden');
      document.body.style.overflow = '';
    }
  }

  closeModalBtns.forEach(btn => btn.addEventListener('click', closeSuccessModal));
  if (modalBackdrop) modalBackdrop.addEventListener('click', closeSuccessModal);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeSuccessModal();
  });

  leadForms.forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const nameInput = form.querySelector('input[name="name"]');
      const phoneInput = form.querySelector('input[name="phone"]');

      if (!phoneInput || phoneInput.value.replace(/\D/g, '').length < 11) {
        phoneInput.focus();
        phoneInput.classList.add('border-brand-red', 'ring-2', 'ring-brand-red/30');
        setTimeout(() => {
          phoneInput.classList.remove('ring-2', 'ring-brand-red/30');
        }, 1500);
        return;
      }

      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Отправляем...
      `;

      setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        const nameVal = nameInput ? nameInput.value : '';
        form.reset();
        openSuccessModal(nameVal);
      }, 700);
    });
  });
});
