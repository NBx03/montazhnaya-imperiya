/**
 * @file phone-mask.js
 * @description Strict Russian phone input masking (+7 (XXX) XXX-XX-XX) and validation.
 * Automatically attaches to all `input[type="tel"]` fields across the site.
 * 
 * DOM Dependencies:
 * - `input[type="tel"]`: Phone number input fields
 * - `#consult-phone-error`, `#modal-lead-phone-error`: Error feedback spans
 */

/**
 * Extracts raw digits from a string.
 * @param {string} value - Formatted or unformatted phone string
 * @returns {string} Digits only
 */
export function cleanPhoneDigits(value) {
  return (value || '').replace(/\D/g, '');
}

/**
 * Validates if the phone input has complete 11 digits starting with Russian country code (7).
 * @param {string} value - Phone string
 * @returns {boolean} True if strictly valid
 */
export function isPhoneValid(value) {
  const digits = cleanPhoneDigits(value);
  return digits.length === 11 && (digits.startsWith('7') || digits.startsWith('8'));
}

/**
 * Attaches real-time mask and blur validation to all telephone input fields.
 */
export function initPhoneMasks() {
  const phoneInputs = document.querySelectorAll('input[type="tel"]');

  phoneInputs.forEach((input) => {
    // When focusing an empty input, prime it with "+7 ("
    input.addEventListener('focus', () => {
      if (!input.value.trim()) {
        input.value = '+7 (';
      }
    });

    input.addEventListener('input', (e) => {
      let value = cleanPhoneDigits(e.target.value);
      if (!value) {
        e.target.value = '';
        return;
      }

      // If user typed without 7 (e.g. 9...), normalize to start with 7
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
        const err = input.parentElement.querySelector(
          '#consult-phone-error, #modal-lead-phone-error'
        );
        if (err) err.classList.add('hidden');
      }
    });

    input.addEventListener('blur', () => {
      const clean = cleanPhoneDigits(input.value);
      const err = input.parentElement.querySelector(
        '#consult-phone-error, #modal-lead-phone-error'
      );

      if (clean === '7' || clean === '') {
        input.value = '';
        input.classList.remove('border-brand-red');
        if (err) err.classList.add('hidden');
      } else if (clean.length < 11) {
        input.classList.add('border-brand-red');
        if (err) err.classList.remove('hidden');
      } else {
        input.classList.remove('border-brand-red');
        if (err) err.classList.add('hidden');
      }
    });
  });
}
