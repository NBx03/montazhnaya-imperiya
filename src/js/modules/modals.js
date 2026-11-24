/**
 * @file modals.js
 * @description Controls modal dialogs (Lead Consultation Modal and Success Feedback Modal)
 * and form submissions with phone validation and backend API integration.
 * 
 * DOM Dependencies:
 * - `#lead-modal`: Consultation modal container
 * - `#close-lead-modal`: Lead modal close button [X]
 * - `#modal-lead-form`: Consultation form inside modal
 * - `#success-modal`: Success feedback modal container
 * - `#close-success-modal`: Success modal close button [X]
 * - `#modal-home-btn`: "На главную" button inside success modal
 * - `#consult-form`: Section 07 consultation form
 * - `.open-modal-btn`: Buttons that trigger the lead modal
 */

import { closeMobileMenu } from './header.js';
import { cleanPhoneDigits, isPhoneValid } from './phone-mask.js';

const leadModal = document.getElementById('lead-modal');
const successModal = document.getElementById('success-modal');

/**
 * Opens the consultation lead modal and locks body scrolling.
 */
export function openLeadModal() {
  if (!leadModal) return;
  closeMobileMenu();
  leadModal.classList.remove('opacity-0', 'pointer-events-none');
  document.body.style.overflow = 'hidden';
}

/**
 * Closes the consultation lead modal and restores body scrolling if success modal isn't open.
 */
export function closeLeadModal() {
  if (!leadModal) return;
  leadModal.classList.add('opacity-0', 'pointer-events-none');
  if (!successModal || successModal.classList.contains('opacity-0')) {
    document.body.style.overflow = '';
  }
}

/**
 * Opens the success feedback modal and locks body scrolling.
 */
export function openSuccessModal() {
  if (!successModal) return;
  closeLeadModal();
  closeMobileMenu();
  successModal.classList.remove('opacity-0', 'pointer-events-none');
  document.body.style.overflow = 'hidden';
}

/**
 * Closes the success feedback modal and restores body scrolling.
 */
export function closeSuccessModal() {
  if (!successModal) return;
  successModal.classList.add('opacity-0', 'pointer-events-none');
  document.body.style.overflow = '';
}

/**
 * Validates form and asynchronously sends lead to FastAPI backend.
 * Features rate-limit handling (429), honeypot anti-spam, and graceful error presentation.
 * @param {HTMLFormElement} form
 * @param {HTMLInputElement} nameInput
 * @param {HTMLInputElement} phoneInput
 * @param {HTMLElement} phoneError
 * @param {string} source
 * @param {Function} onSuccess
 */
async function handleFormSubmit(form, nameInput, phoneInput, phoneError, source, onSuccess) {
  const phoneVal = phoneInput ? phoneInput.value.trim() : '';

  if (!isPhoneValid(phoneVal)) {
    if (phoneInput) {
      phoneInput.focus();
      phoneInput.classList.add('border-brand-red');
    }
    if (phoneError) phoneError.classList.remove('hidden');
    return;
  }

  if (phoneInput) phoneInput.classList.remove('border-brand-red');
  if (phoneError) phoneError.classList.add('hidden');

  // Remove any previous status or error banners inside form
  const existingStatus = form.querySelector('.form-status-msg');
  if (existingStatus) existingStatus.remove();

  // Honeypot check (invisible to humans, filled by bots)
  const honeypotInput = form.querySelector('input[name="company_website"]');
  const honeypotVal = honeypotInput ? honeypotInput.value : '';

  const nameVal = nameInput ? nameInput.value.trim() : '';

  const submitBtn = form.querySelector('button[type="submit"]');
  const splitLabel = submitBtn ? submitBtn.querySelector('.split-label') : null;
  const originalLabel = splitLabel ? splitLabel.textContent : (submitBtn ? submitBtn.textContent : '');

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
    if (splitLabel) {
      splitLabel.textContent = 'ОТПРАВКА...';
    } else {
      submitBtn.textContent = 'ОТПРАВКА...';
    }
  }

  try {
    const response = await fetch('/api/v1/leads', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        name: nameVal || null,
        phone: phoneVal,
        source: source,
        company_website: honeypotVal || null
      })
    });

    if (response.status === 429) {
      // Rate limit triggered (e.g. rapid repeat submission)
      const errData = await response.json().catch(() => ({}));
      const friendlyMsg = errData.message || (typeof errData.detail === 'string' ? errData.detail : null) || 'Вы уже отправили заявку! Дежурный инженер свяжется с вами в течение 10–15 минут.';
      showFormStatus(form, friendlyMsg, false);
      form.reset();
      return;
    }

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      let msg = 'Проверьте корректность введенных данных';
      if (errData.message) {
        msg = errData.message;
      } else if (Array.isArray(errData.detail) && errData.detail[0]?.msg) {
        msg = errData.detail[0].msg.replace(/^Value error,\s*/i, '');
      } else if (typeof errData.detail === 'string') {
        msg = errData.detail;
      }
      const err = new Error(msg);
      err.isValidationError = response.status >= 400 && response.status < 500;
      throw err;
    }

    form.reset();
    onSuccess();
  } catch (err) {
    console.error('[Modals] Lead submission error:', err);
    if (err.isValidationError) {
      showFormStatus(form, err.message, true);
    } else {
      // Network or server 5xx error: fallback to direct phone
      const phoneLink = document.querySelector('#header a[href^="tel:"]') || document.querySelector('#footer a[href^="tel:"]');
      const directPhone = phoneLink ? phoneLink.textContent.trim() : '+7 (423) 200-00-00';
      showFormStatus(form, `Сервер временно недоступен. Пожалуйста, позвоните нам напрямую: ${directPhone}`, true);
    }
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.classList.remove('opacity-75', 'cursor-not-allowed');
      if (splitLabel) {
        splitLabel.textContent = originalLabel;
      } else {
        submitBtn.textContent = originalLabel;
      }
    }
  }
}

/**
 * Injects a styled status message banner directly into the form.
 * @param {HTMLFormElement} form
 * @param {string} message
 * @param {boolean} isError
 */
function showFormStatus(form, message, isError = false) {
  const existing = form.querySelector('.form-status-msg');
  if (existing) existing.remove();

  const msgDiv = document.createElement('div');
  msgDiv.className = `form-status-msg font-mono text-[13px] px-4 py-3 rounded border transition-all mt-3 ${
    isError
      ? 'bg-brand-red/15 text-[#ff7b82] border-brand-red/40'
      : 'bg-[#10B981]/15 text-[#34D399] border-[#10B981]/40'
  }`;
  msgDiv.textContent = message;

  // Append right above or below the submit button
  const submitBtn = form.querySelector('button[type="submit"]');
  if (submitBtn && submitBtn.parentElement) {
    submitBtn.parentElement.appendChild(msgDiv);
  } else {
    form.appendChild(msgDiv);
  }

  // Auto-remove error when user starts editing inputs
  const inputs = form.querySelectorAll('input');
  const clearHandler = () => {
    msgDiv.remove();
    inputs.forEach(input => input.removeEventListener('input', clearHandler));
  };
  inputs.forEach(input => input.addEventListener('input', clearHandler));
}

/**
 * Initializes modal dialog triggers, backdrop clicks, Escape key listener, and form submissions.
 */
export function initModals() {
  const closeLeadModalBtn = document.getElementById('close-lead-modal');
  const closeSuccessModalBtn = document.getElementById('close-success-modal');
  const modalHomeBtn = document.getElementById('modal-home-btn');
  const openModalBtns = document.querySelectorAll('.open-modal-btn');
  const modalLeadForm = document.getElementById('modal-lead-form');
  const consultForm = document.getElementById('consult-form');

  // Trigger buttons (e.g. Header CTA, Hero CTA, Banner CTA)
  openModalBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openLeadModal();
    });
  });

  // Close buttons
  if (closeLeadModalBtn) closeLeadModalBtn.addEventListener('click', closeLeadModal);
  if (closeSuccessModalBtn) closeSuccessModalBtn.addEventListener('click', closeSuccessModal);

  // Return to home button inside success modal
  if (modalHomeBtn) {
    modalHomeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closeSuccessModal();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Backdrop click dismiss
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

  // Escape key dismiss for all overlays
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeLeadModal();
      closeSuccessModal();
      closeMobileMenu();
    }
  });

  // Modal Lead Form submission
  if (modalLeadForm) {
    modalLeadForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const nameInput = document.getElementById('modal-lead-name');
      const phoneInput = document.getElementById('modal-lead-phone');
      const phoneError = document.getElementById('modal-lead-phone-error');
      handleFormSubmit(modalLeadForm, nameInput, phoneInput, phoneError, 'modal_popup', () => {
        closeLeadModal();
        openSuccessModal();
      });
    });
  }

  // Section 07 Consult Form submission
  if (consultForm) {
    consultForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const nameInput = document.getElementById('consult-name');
      const phoneInput = document.getElementById('consult-phone');
      const phoneError = document.getElementById('consult-phone-error');
      handleFormSubmit(consultForm, nameInput, phoneInput, phoneError, 'section07_engineer', () => {
        openSuccessModal();
      });
    });
  }
}
