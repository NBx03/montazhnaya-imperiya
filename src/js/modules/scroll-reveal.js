/**
 * @file scroll-reveal.js
 * @description Staggered section entrance animations triggered via IntersectionObserver.
 * 
 * DOM Dependencies:
 * - `#expertise`: Section 01 container (title masked reveal & cards)
 * - `#services`: Section 02 container (service cards staggered slide-up)
 * - `#steps`: Section 04 container (steps rows entrance)
 */

/**
 * Initializes staggered scroll entrance animations for sections 01, 02, and 04.
 */
export function initScrollReveals() {
  const observeSection = (id, threshold = 0.1, rootMargin = '0px 0px -40px 0px') => {
    const el = document.getElementById(id);
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            el.classList.add('is-visible');
            observer.unobserve(el);
          }
        });
      },
      { threshold, rootMargin }
    );

    observer.observe(el);
  };

  // Section 01: Headline masked line reveal + cards staggered slide-up
  observeSection('expertise', 0.12);

  // Section 02: Service cards staggered entrance
  observeSection('services', 0.1);

  // Section 04: Process steps staggered entrance
  observeSection('steps', 0.1);
}
