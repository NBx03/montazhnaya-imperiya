/**
 * @file cases.js
 * @description Section 06 mechanics: stacking cases card layers, tab switching,
 * and card-specific mechanical odometer triggers.
 * 
 * DOM Dependencies:
 * - `#cases`: Section 06 root container
 * - `.case-card`: Individual portfolio case card elements
 * - `.case-tab-btn`: Selector tab buttons corresponding to each case
 */

import { animateOdometerGroup } from './odometer.js';

/**
 * Initializes stacking depth layers and tab controller for portfolio cases.
 */
export function initCases() {
  const caseCards = document.querySelectorAll('.case-card');
  const caseTabs = document.querySelectorAll('.case-tab-btn');
  const casesSection = document.getElementById('cases');

  if (!caseCards.length || !caseTabs.length) return;

  let activeCaseIdx = 0;

  /**
   * Sets active case index and reorders stacking depth classes.
   * @param {number} targetIdx - Index of case card to bring to front (0, 1, 2)
   */
  function setCaseStack(targetIdx) {
    if (targetIdx < 0 || targetIdx >= caseCards.length) return;
    activeCaseIdx = targetIdx;

    // Update tab button active styles
    caseTabs.forEach((btn, idx) => {
      if (idx === targetIdx) {
        btn.classList.add('active');
        btn.classList.remove('bg-[#141519]', 'text-white/60', 'border-white/10');
        btn.classList.add('bg-[#1A1C22]', 'text-white', 'border-white/20');
      } else {
        btn.classList.remove('active');
        btn.classList.remove('bg-[#1A1C22]', 'text-white', 'border-white/20');
        btn.classList.add('bg-[#141519]', 'text-white/60', 'border-white/10');
      }
    });

    // Update 3 cards stacking depth (Figma: overlapping, dimming, scale-down)
    caseCards.forEach((card) => {
      const cardIdx = parseInt(card.dataset.caseIdx, 10);
      card.classList.remove('card-pos-front', 'card-pos-middle', 'card-pos-back');

      if (cardIdx === targetIdx) {
        card.classList.add('card-pos-front');
        // Trigger fast mechanical odometer for front card stats
        const cardOdometers = card.querySelectorAll('.stat-odometer');
        animateOdometerGroup(cardOdometers, 800);
      } else if (cardIdx === (targetIdx + 1) % 3) {
        card.classList.add('card-pos-middle');
      } else {
        card.classList.add('card-pos-back');
      }
    });
  }

  // Click handler on tab buttons
  caseTabs.forEach((tab) => {
    tab.addEventListener('click', (e) => {
      e.stopPropagation();
      const idx = parseInt(tab.dataset.caseIndex, 10);
      setCaseStack(idx);
    });
  });

  // Click handler directly on layered background cards to bring forward
  caseCards.forEach((card) => {
    card.addEventListener('click', () => {
      const idx = parseInt(card.dataset.caseIdx, 10);
      if (idx !== activeCaseIdx) {
        setCaseStack(idx);
      }
    });
  });

  // Section 06 initial entrance observer to animate front card numbers once in view
  if (casesSection) {
    let casesAnimated = false;
    const casesObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !casesAnimated) {
            casesAnimated = true;
            const frontCard = document.querySelector('.case-card.card-pos-front');
            if (frontCard) {
              const frontOdometers = frontCard.querySelectorAll('.stat-odometer');
              animateOdometerGroup(frontOdometers, 900);
            }
          }
        });
      },
      { threshold: 0.2 }
    );

    casesObserver.observe(casesSection);
  }
}
