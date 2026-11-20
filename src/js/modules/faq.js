/**
 * @file faq.js
 * @description Section 07 FAQ accordion functionality. Toggles `.is-open` class,
 * triggering smooth CSS grid height transition and masked text reveal.
 * 
 * DOM Dependencies:
 * - `.faq-row`: FAQ question accordion row elements
 */

/**
 * Initializes FAQ accordion row click interactions.
 */
export function initFaq() {
  const faqRows = document.querySelectorAll('.faq-row');
  if (!faqRows.length) return;

  faqRows.forEach((row) => {
    row.addEventListener('click', () => {
      const wasOpen = row.classList.contains('is-open');
      row.classList.toggle('is-open', !wasOpen);
    });
  });
}
