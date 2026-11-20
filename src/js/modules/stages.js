/**
 * @file stages.js
 * @description Section 04 interaction logic: 3D hardware perspective tilt and
 * mutually exclusive step row hover & scroll-spy synchronization.
 * 
 * DOM Dependencies:
 * - `#steps`: Section 04 root container
 * - `#installation-3d-wrap`: 3D equipment composition wrapper
 * - `#steps .step-row`: Individual step accordion items
 */

/**
 * Initializes 3D mouse parallax tilt on the central hardware render.
 */
function init3dParallaxTilt() {
  const stepsSection = document.getElementById('steps');
  const installation3dWrap = document.getElementById('installation-3d-wrap');

  if (!stepsSection || !installation3dWrap) return;

  stepsSection.addEventListener('mousemove', (e) => {
    const rect = installation3dWrap.getBoundingClientRect();
    const wrapCenterX = rect.left + rect.width / 2;
    const wrapCenterY = rect.top + rect.height / 2;

    const deltaX = (e.clientX - wrapCenterX) / (window.innerWidth / 2);
    const deltaY = (e.clientY - wrapCenterY) / (window.innerHeight / 2);

    const tiltX = -deltaY * 12; // degrees
    const tiltY = deltaX * 16; // degrees

    installation3dWrap.style.transform = `perspective(1000px) rotateX(${tiltX.toFixed(
      2
    )}deg) rotateY(${tiltY.toFixed(2)}deg) scale3d(1.02, 1.02, 1.02)`;
  });

  stepsSection.addEventListener('mouseleave', () => {
    installation3dWrap.style.transform =
      'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
  });
}

/**
 * Initializes scroll-spy and hover highlight logic for step rows.
 * Hover overrides active state temporarily; on mouseleave or scroll, scroll-spy resumes.
 */
function initStepScrollSpy() {
  const stepRows = document.querySelectorAll('#steps .step-row');
  if (!stepRows.length) return;

  let scrollActiveRow = null;
  let hoveredRow = null;

  const updateActiveStep = () => {
    const viewportCenter = window.innerHeight / 2;
    let closestStep = null;
    let minDistance = Infinity;

    stepRows.forEach((row) => {
      const rect = row.getBoundingClientRect();
      const rowCenter = rect.top + rect.height / 2;
      const distance = Math.abs(viewportCenter - rowCenter);

      if (distance < minDistance) {
        minDistance = distance;
        closestStep = row;
      }
    });

    if (closestStep) {
      scrollActiveRow = closestStep;
      // Only update active class if the user is not actively hovering over another row
      if (!hoveredRow) {
        stepRows.forEach((r) => r.classList.remove('is-active'));
        closestStep.classList.add('is-active');
      }
    }
  };

  stepRows.forEach((row) => {
    row.addEventListener('mouseenter', () => {
      hoveredRow = row;
      stepRows.forEach((r) => r.classList.remove('is-active'));
      row.classList.add('is-active');
    });

    row.addEventListener('mouseleave', () => {
      if (hoveredRow === row) {
        hoveredRow = null;
      }
      // When mouse leaves this step, restore the scroll-active step
      stepRows.forEach((r) => r.classList.remove('is-active'));
      if (scrollActiveRow) {
        scrollActiveRow.classList.add('is-active');
      } else {
        updateActiveStep();
      }
    });
  });

  // On scroll: clear stale hover state and update scroll-active step
  window.addEventListener(
    'scroll',
    () => {
      hoveredRow = null;
      updateActiveStep();
    },
    { passive: true }
  );

  updateActiveStep();
}

/**
 * Initializes all Section 04 interactive mechanics.
 */
export function initStages() {
  init3dParallaxTilt();
  initStepScrollSpy();
}
