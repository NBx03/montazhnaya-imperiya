/**
 * @file main.js
 * @description Main application orchestrator for Montazhnaya Imperiya landing page.
 * Boots all UI, animation, modal, and interaction modules on DOMContentLoaded.
 * 
 * Architecture:
 * - `hero.js`: Background video autoplay, REC CCTV timer, dynamic localized date
 * - `header.js`: Smart sticky header visibility on scroll, mobile drawer navigation
 * - `scroll-reveal.js`: IntersectionObservers for staggered section entrances (01, 02, 04)
 * - `odometer.js`: Fast mechanical numerical counter animations
 * - `stages.js`: Section 04 3D composition perspective tilt and hover/scroll-spy sync
 * - `sectors.js`: Section 05 horizontal card track scroll and dynamic partner logo ticker
 * - `cases.js`: Section 06 portfolio card stacking depth layers and tab controller
 * - `faq.js`: Section 07 FAQ accordion smooth expand/collapse
 * - `phone-mask.js`: Strict +7 (XXX) XXX-XX-XX input masking and validation
 * - `modals.js`: Lead consultation modal, success dialog, and form submissions
 */

import { initHero } from './js/modules/hero.js';
import { initHeader } from './js/modules/header.js';
import { initScrollReveals } from './js/modules/scroll-reveal.js';
import { initOdometers } from './js/modules/odometer.js';
import { initStages } from './js/modules/stages.js';
import { initSectors } from './js/modules/sectors.js';
import { initCases } from './js/modules/cases.js';
import { initFaq } from './js/modules/faq.js';
import { initPhoneMasks } from './js/modules/phone-mask.js';
import { initModals } from './js/modules/modals.js';
import { initContentLoader } from './js/modules/content-loader.js';

document.addEventListener('DOMContentLoaded', () => {
  initContentLoader();
  initHero();
  initHeader();
  initScrollReveals();
  initOdometers();
  initStages();
  initSectors();
  initCases();
  initFaq();
  initPhoneMasks();
  initModals();
});
