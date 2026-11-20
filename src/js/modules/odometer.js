/**
 * @file odometer.js
 * @description Fast mechanical odometer counter animation with quartic ease-out curve.
 * 
 * DOM Dependencies:
 * - `#why-us`: Section 03 stats container
 * - `#why-us .stat-odometer`: Numeric counter elements with `data-target` attribute
 */

/**
 * Animates a group of odometer counter elements to their target numbers.
 * Uses quartic ease-out curve to produce a crisp mechanical odometer feel.
 * 
 * @param {NodeList|Array<HTMLElement>} elements - Elements containing data-target attribute
 * @param {number} [duration=1000] - Duration in milliseconds
 */
export function animateOdometerGroup(elements, duration = 1000) {
  if (!elements || !elements.length) return;

  elements.forEach((counter) => {
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

/**
 * Initializes IntersectionObserver for Section 03 statistical counters.
 */
export function initOdometers() {
  const statsSection = document.getElementById('why-us');
  const sec3Odometers = document.querySelectorAll('#why-us .stat-odometer');

  if (statsSection && sec3Odometers.length) {
    let sec3Animated = false;
    const countObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !sec3Animated) {
            sec3Animated = true;
            animateOdometerGroup(sec3Odometers, 1100);
          }
        });
      },
      { threshold: 0.25 }
    );

    countObserver.observe(statsSection);
  }
}
