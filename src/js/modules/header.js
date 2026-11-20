/**
 * @file header.js
 * @description Manages smart sticky header visibility on scroll and mobile drawer menu state.
 * 
 * DOM Dependencies:
 * - `#header`: Sticky main navigation header
 * - `#mobile-menu-btn`: Burger menu button in header
 * - `#close-menu-btn`: Close [X] button in mobile drawer
 * - `#mobile-drawer`: Slide-out navigation drawer
 * - `#drawer-backdrop`: Semi-transparent dark overlay behind drawer
 * - `.mobile-nav-link`: Navigation links inside drawer
 */

const mobileDrawer = document.getElementById('mobile-drawer');
const drawerBackdrop = document.getElementById('drawer-backdrop');

/**
 * Opens the mobile drawer navigation and locks document body scroll.
 */
export function openMobileMenu() {
  if (!mobileDrawer || !drawerBackdrop) return;
  mobileDrawer.classList.remove('translate-x-full');
  drawerBackdrop.classList.remove('opacity-0', 'pointer-events-none');
  document.body.style.overflow = 'hidden';
}

/**
 * Closes the mobile drawer navigation and restores document body scroll.
 */
export function closeMobileMenu() {
  if (!mobileDrawer || !drawerBackdrop) return;
  mobileDrawer.classList.add('translate-x-full');
  drawerBackdrop.classList.add('opacity-0', 'pointer-events-none');
  document.body.style.overflow = '';
}

/**
 * Initializes smart header auto-hide on downward scroll and reveal on upward scroll.
 */
function initSmartHeader() {
  const header = document.getElementById('header');
  if (!header) return;

  let lastScrollY = window.scrollY;
  let ticking = false;

  window.addEventListener(
    'scroll',
    () => {
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
    },
    { passive: true }
  );
}

/**
 * Initializes mobile drawer menu event triggers.
 */
function initMobileDrawer() {
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const closeMenuBtn = document.getElementById('close-menu-btn');
  const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');

  if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', openMobileMenu);
  if (closeMenuBtn) closeMenuBtn.addEventListener('click', closeMobileMenu);
  if (drawerBackdrop) drawerBackdrop.addEventListener('click', closeMobileMenu);
  mobileNavLinks.forEach((link) => link.addEventListener('click', closeMobileMenu));
}

/**
 * Initializes header and mobile navigation system.
 */
export function initHeader() {
  initSmartHeader();
  initMobileDrawer();
}
