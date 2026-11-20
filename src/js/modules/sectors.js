/**
 * @file sectors.js
 * @description Section 05 mechanics: pinned horizontal card scroll and velocity-reactive
 * partner logo ticker ("при скролле вниз ускоряется, при скролле вверх замедляется, при наведении замирает").
 * 
 * DOM Dependencies:
 * - `#sectors-scroll-container`: Tall container driving scroll distance
 * - `#sectors-track`: Horizontal flex track containing sector cards
 * - `#bank-ticker-track`: Moving inner track of partner logos
 * - `#bank-ticker-wrapper`: Outer hover-sensing boundary
 */

/**
 * Initializes pinned horizontal card scroll on desktop/tablet viewports.
 */
function initHorizontalCardScroll() {
  const sectorsScrollContainer = document.getElementById('sectors-scroll-container');
  const sectorsTrack = document.getElementById('sectors-track');

  if (!sectorsScrollContainer || !sectorsTrack) return;

  const handleSectorsScroll = () => {
    const trackParent = sectorsTrack.parentElement;
    if (!trackParent) return;

    const rect = sectorsScrollContainer.getBoundingClientRect();
    const scrollDist = sectorsScrollContainer.offsetHeight - window.innerHeight;

    if (scrollDist > 0) {
      // Progress from 0 (top of container hits viewport top) to 1 (bottom of scroll)
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

/**
 * Initializes dynamic velocity-reactive bank & partner logo ticker.
 * Accelerates on scroll down, slows down on scroll up, pauses on hover,
 * with smooth momentum decay back to baseline speed.
 */
function initDynamicBankTicker() {
  const bankTickerTrack = document.getElementById('bank-ticker-track');
  const bankTickerWrapper = document.getElementById('bank-ticker-wrapper');

  if (!bankTickerTrack || !bankTickerWrapper) return;

  const baseSpeed = 1.0; // Base pixels per frame
  let scrollBoost = 0; // Momentum added from scrolling
  let tickerOffset = 0; // Current pixel translation
  let isHovered = false; // Hover state
  let lastScrollY = window.scrollY;

  // Hover freeze ("при наведении замирает")
  bankTickerWrapper.addEventListener('mouseenter', () => {
    isHovered = true;
  });
  bankTickerWrapper.addEventListener('mouseleave', () => {
    isHovered = false;
  });

  // Scroll speed reaction ("При скролле вниз ускоряется, при скролле вверх замедляется")
  window.addEventListener(
    'scroll',
    () => {
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
    },
    { passive: true }
  );

  // Animation frame loop
  const animateBankTicker = () => {
    // Smooth decay of scroll boost back to 0
    scrollBoost *= 0.93;

    // Effective speed: never drops below 0.15 (prevents freezing/reverse), capped at 9.0
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

/**
 * Initializes all Section 05 interactive components.
 */
export function initSectors() {
  initHorizontalCardScroll();
  initDynamicBankTicker();
}
