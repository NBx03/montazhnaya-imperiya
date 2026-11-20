/**
 * @file modals.js
 * @description Controls modal dialogs (Lead Consultation Modal and Success Feedback Modal)
 * and form submissions with phone validation.
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
 * Validates a form's telephone input and triggers error state or success callback.
 * @param {HTMLFormElement} form
 * @param {HTMLInputElement} phoneInput
 * @param {HTMLElement} phoneError
 * @param {Function} onSuccess
 */
function handleFormSubmit(form, phoneInput, phoneError, onSuccess) {
  const phoneVal = phoneInput ? phoneInput.value : '';

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
  form.reset();
  onSuccess();
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
      const phoneInput = document.getElementById('modal-lead-phone');
      const phoneError = document.getElementById('modal-lead-phone-error');
      handleFormSubmit(modalLeadForm, phoneInput, phoneError, () => {
        closeLeadModal();
        openSuccessModal();
      });
    });
  }

  // Section 07 Consult Form submission
  if (consultForm) {
    consultForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const phoneInput = document.getElementById('consult-phone');
      const phoneError = document.getElementById('consult-phone-error');
      handleFormSubmit(consultForm, phoneInput, phoneError, () => {
        openSuccessModal();
      });
    });
  }
}
