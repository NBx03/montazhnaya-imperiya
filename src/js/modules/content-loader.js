/**
 * @file content-loader.js
 * @description Dynamic content & media hydration module from FastAPI backend (/api/v1/content).
 *
 * Features:
 * - Instant boot hydration using cached JSON and ETag validation (304 Not Modified).
 * - Full coverage of all 11 website sections, texts, images, icons, logos, and Hero loop video.
 * - Sanitized URL & media paths (blocks javascript:, data:, vbscript:, path traversal).
 * - Graceful degradation: preserves pre-rendered static HTML if backend is unreachable or offline.
 */

const CACHE_KEY = 'montazh_content_cache';
const ETAG_KEY = 'montazh_content_etag';

function sanitizeHref(url) {
  if (!url || typeof url !== 'string') return null;
  const trimmed = url.trim();
  const low = trimmed.toLowerCase();
  if (low.startsWith('javascript:') || low.startsWith('data:') || low.startsWith('vbscript:')) {
    return null;
  }
  if (low.startsWith('https://') || low.startsWith('http://') || low.startsWith('tel:') || low.startsWith('mailto:') || trimmed.startsWith('/')) {
    return trimmed;
  }
  return null;
}

function sanitizeMediaSrc(url) {
  if (!url || typeof url !== 'string') return null;
  const trimmed = url.trim();
  const low = trimmed.toLowerCase();
  if (low.startsWith('javascript:') || low.startsWith('data:') || low.startsWith('vbscript:') || trimmed.includes('..')) {
    return null;
  }
  if (trimmed.startsWith('/') || low.startsWith('https://') || low.startsWith('http://')) {
    return trimmed;
  }
  return null;
}

/**
 * Updates an <img> src only if sanitized URL is valid and actually changed.
 */
function setImageSrc(imgEl, url) {
  if (!imgEl || !url) return;
  const safeSrc = sanitizeMediaSrc(url);
  if (!safeSrc) return;
  if (imgEl.getAttribute('src') !== safeSrc) {
    imgEl.src = safeSrc;
  }
}

/**
 * Strips trailing arrow character so .split-icon doesn't duplicate "→ →".
 */
function cleanSplitLabel(text) {
  return String(text || '').replace(/\s*[→↗]+\s*$/u, '').trim();
}

export async function initContentLoader() {
  // Step 1: Instant boot from cache if available
  try {
    const cached = sessionStorage.getItem(CACHE_KEY);
    if (cached) {
      const data = JSON.parse(cached);
      if (data && data.sections) {
        applyAllSections(data.sections);
      }
    }
  } catch (e) {
    // SessionStorage unavailable or parse error — non-fatal
  }

  // Step 2: Fetch fresh data with ETag conditional request
  try {
    const headers = { 'Accept': 'application/json' };
    const cachedEtag = sessionStorage.getItem(ETAG_KEY);
    if (cachedEtag) {
      headers['If-None-Match'] = cachedEtag;
    }

    const res = await fetch('/api/v1/content', {
      headers,
      cache: 'default'
    });

    if (res.status === 304) {
      console.info('[ContentLoader] HTTP 304 Not Modified: Cache is up to date.');
      return;
    }

    if (!res.ok) {
      console.info(`[ContentLoader] Server returned HTTP ${res.status}. Preserving static HTML.`);
      return;
    }

    const json = await res.json();
    if (!json || !json.sections) return;

    // Save to cache
    const newEtag = res.headers.get('etag');
    if (newEtag) sessionStorage.setItem(ETAG_KEY, newEtag);
    sessionStorage.setItem(CACHE_KEY, JSON.stringify(json));

    // Apply updates
    applyAllSections(json.sections);
    console.info('[ContentLoader] Dynamic content successfully hydrated from backend.');

  } catch (err) {
    // Offline or network error: graceful fallback to pre-rendered HTML
    console.info('[ContentLoader] Backend unreachable. Using static HTML fallback.');
  }
}

/**
 * Dispatches hydration to all section handlers.
 * @param {Object} sections
 */
function applyAllSections(sections) {
  if (!sections) return;

  if (sections.header) hydrateHeader(sections.header);
  if (sections.hero) hydrateHero(sections.hero);
  if (sections.expertise) hydrateExpertise(sections.expertise);
  if (sections.services) hydrateServices(sections.services);
  if (sections.why_us) hydrateWhyUs(sections.why_us);
  if (sections.steps) hydrateSteps(sections.steps);
  if (sections.sectors) hydrateSectors(sections.sectors);
  if (sections.engineer_cta) hydrateEngineerCta(sections.engineer_cta);
  if (sections.cases) hydrateCases(sections.cases);
  if (sections.faq) hydrateFaq(sections.faq);
  if (sections.contacts) hydrateContacts(sections.contacts);
}

// ------------------------------------------
// SECTION HYDRATORS
// ------------------------------------------

function hydrateHeader(data) {
  if (!data) return;

  if (data.logo_image) {
    document.querySelectorAll('img[data-brand-logo]').forEach(img => setImageSrc(img, data.logo_image));
  }
  if (data.phone) {
    const cleanHref = data.phone_clean ? sanitizeHref(`tel:${data.phone_clean}`) : null;
    document.querySelectorAll('#header a[href^="tel:"], #mobile-drawer a[href^="tel:"], a[data-site-phone]').forEach(a => {
      a.textContent = data.phone;
      if (cleanHref) a.setAttribute('href', cleanHref);
    });
  }
  if (data.working_hours) {
    document.querySelectorAll('[data-header-hours]').forEach(el => {
      el.textContent = data.working_hours;
    });
  }
  if (data.tg_link) {
    const safeTg = sanitizeHref(data.tg_link);
    if (safeTg) {
      document.querySelectorAll('a[data-tg-link]').forEach(a => a.setAttribute('href', safeTg));
    }
  }
  if (data.wa_link) {
    const safeWa = sanitizeHref(data.wa_link);
    if (safeWa) {
      document.querySelectorAll('a[data-wa-link]').forEach(a => a.setAttribute('href', safeWa));
    }
  }
  if (data.cta_button) {
    const drawerCta = document.querySelector('#mobile-drawer .open-modal-btn .split-label');
    if (drawerCta) drawerCta.textContent = cleanSplitLabel(data.cta_button);
  }
}

function hydrateHero(data) {
  if (!data) return;
  const heroSection = document.getElementById('hero');
  if (!heroSection) return;

  if (data.bg_poster) {
    const videoEl = document.getElementById('hero-bg-video');
    const safePoster = sanitizeMediaSrc(data.bg_poster);
    if (videoEl && safePoster && videoEl.getAttribute('poster') !== safePoster) {
      videoEl.setAttribute('poster', safePoster);
    }
  }

  if (data.bg_video) {
    const videoEl = document.getElementById('hero-bg-video');
    const safeVideo = sanitizeMediaSrc(data.bg_video);
    if (videoEl && safeVideo) {
      const currentAssigned = videoEl.dataset.hydratedVideo || '/videos/hero-bg.mp4';
      if (currentAssigned !== safeVideo) {
        videoEl.dataset.hydratedVideo = safeVideo;
        videoEl.querySelectorAll('source').forEach(srcEl => srcEl.remove());
        const sourceEl = document.createElement('source');
        sourceEl.src = safeVideo;
        sourceEl.type = safeVideo.toLowerCase().endsWith('.webm') ? 'video/webm' : 'video/mp4';
        videoEl.appendChild(sourceEl);
        videoEl.src = safeVideo;
        videoEl.load();
        videoEl.play().catch(() => {});
      }
    }
  }

  if (data.title) {
    const titleEl = heroSection.querySelector('h1');
    if (titleEl) titleEl.textContent = data.title;
  }
  if (data.description) {
    const descEl = heroSection.querySelector('p');
    if (descEl) descEl.textContent = data.description;
  }
  if (data.subtext) {
    const subEl = heroSection.querySelectorAll('p')[1];
    if (subEl) subEl.textContent = data.subtext;
  }
  if (data.cta_button) {
    const ctaLabel = heroSection.querySelector('.split-label');
    if (ctaLabel) ctaLabel.textContent = cleanSplitLabel(data.cta_button);
  }

  const featureTags = Array.isArray(data.features) ? data.features : (Array.isArray(data.tags) ? data.tags : null);
  if (featureTags) {
    const tagEls = heroSection.querySelectorAll('.tag-chamfered');
    featureTags.forEach((tag, idx) => {
      if (tagEls[idx]) tagEls[idx].textContent = tag;
    });
  }
}

function hydrateExpertise(data) {
  if (!data) return;
  const sec = document.getElementById('expertise');
  if (!sec) return;

  if (data.title) {
    const titleEl = sec.querySelector('h2');
    if (titleEl) titleEl.textContent = data.title;
  }
  if (data.lead) {
    const leadEl = sec.querySelector('p');
    if (leadEl) leadEl.textContent = data.lead;
  }

  // Hydrate 3 expertise cards
  if (data.items && Array.isArray(data.items)) {
    const cardHeadings = sec.querySelectorAll('h3');
    const cardImgs = sec.querySelectorAll('img[data-expertise-img]');
    data.items.forEach((item, idx) => {
      if (cardHeadings[idx]) {
        const h3 = cardHeadings[idx];
        if (item.title) h3.textContent = item.title;
        const card = h3.parentElement;
        if (card) {
          const descEl = card.querySelector('p');
          if (descEl && item.desc) descEl.textContent = item.desc;
        }
      }
      if (cardImgs[idx] && item.image) {
        setImageSrc(cardImgs[idx], item.image);
      }
    });
  }
}

function hydrateServices(data) {
  if (!data) return;
  const servicesSec = document.getElementById('services');
  if (!servicesSec) return;

  if (data.title) {
    const titleEl = servicesSec.querySelector('h2');
    if (titleEl) titleEl.textContent = data.title;
  }
  if (data.subtitle) {
    const subEl = servicesSec.querySelector('[data-services-subtitle]');
    if (subEl) subEl.textContent = data.subtitle;
  }
  if (data.banner_image) {
    document.querySelectorAll('img[data-banner-img]').forEach(img => setImageSrc(img, data.banner_image));
  }

  if (Array.isArray(data.items)) {
    const cards = servicesSec.querySelectorAll('.service-card-stagger');
    data.items.forEach((item, idx) => {
      if (cards[idx]) {
        const card = cards[idx];
        const title = card.querySelector('h3');
        const desc = card.querySelector('p');
        const img = card.querySelector('img');
        if (title && item.name) title.textContent = item.name;
        if (desc && item.desc) desc.textContent = item.desc;
        if (img && item.image) setImageSrc(img, item.image);
      }
    });
  }
}

function hydrateWhyUs(data) {
  if (!data) return;
  const whyUsSec = document.getElementById('why-us');
  if (!whyUsSec) return;

  if (Array.isArray(data.items)) {
    const metricCols = whyUsSec.querySelectorAll('.stat-odometer');
    data.items.forEach((item, idx) => {
      if (metricCols[idx]) {
        const odoEl = metricCols[idx];
        const col = odoEl.closest('.space-y-3');
        if (col) {
          if (item.val && odoEl.dataset.target !== String(item.val)) {
            odoEl.dataset.target = String(item.val);
            if (odoEl.dataset.animated === 'true') {
              odoEl.textContent = String(item.val);
            }
          }
          const unitEl = col.querySelector('.font-condensed');
          if (unitEl && item.unit) unitEl.textContent = item.unit;

          const titleEl = col.querySelector('.font-mono.font-bold');
          if (titleEl && item.title) titleEl.textContent = item.title;

          const descEl = col.querySelector('.font-sans');
          if (descEl && item.desc) descEl.textContent = item.desc;
        }
      }
    });
  }

  if (data.ticker_photos && typeof data.ticker_photos === 'object') {
    Object.entries(data.ticker_photos).forEach(([slotKey, photoUrl]) => {
      if (!photoUrl) return;
      whyUsSec.querySelectorAll(`img[data-ticker-photo="${slotKey}"]`).forEach(img => {
        setImageSrc(img, photoUrl);
      });
    });
  }
}

function hydrateSteps(data) {
  if (!data) return;
  const stepsSec = document.getElementById('steps');
  if (!stepsSec) return;

  if (data.title) {
    const secTitle = stepsSec.querySelector('h2');
    if (secTitle) secTitle.textContent = data.title;
  }

  if (data.illustration_image) {
    const illImg = document.getElementById('installation-3d-img');
    setImageSrc(illImg, data.illustration_image);
  }

  if (Array.isArray(data.items)) {
    const stepTitles = stepsSec.querySelectorAll('h3.step-title');
    data.items.forEach((item, idx) => {
      if (stepTitles[idx]) {
        const titleEl = stepTitles[idx];
        if (item.name) titleEl.textContent = item.name;

        const stepRow = titleEl.closest('.step-row') || titleEl.parentElement.parentElement;
        if (stepRow) {
          const stepNumEl = stepRow.querySelector('.step-num');
          if (stepNumEl && item.step) stepNumEl.textContent = `[ ${item.step} ]`;

          const descEl = stepRow.querySelector('p');
          if (descEl && item.desc) descEl.textContent = item.desc;
        }
      }
    });
  }
}

function hydrateSectors(data) {
  if (!data) return;
  const sectorsSec = document.getElementById('sectors');
  if (!sectorsSec) return;

  if (data.title) {
    const titleEl = sectorsSec.querySelector('h2');
    if (titleEl) titleEl.textContent = data.title;
  }

  // Hydrate 4 horizontal sector cards (both photo and corner icon)
  if (Array.isArray(data.items)) {
    const cards = sectorsSec.querySelectorAll('#sectors-track > div');
    data.items.forEach((item, idx) => {
      if (cards[idx]) {
        const card = cards[idx];
        const h3 = card.querySelector('h3');
        const p = card.querySelector('p');
        const photoImg = card.querySelector('.photo-chamfered img');
        const iconImg = card.querySelector('img[data-sector-icon]');
        if (h3 && item.title) h3.textContent = item.title;
        if (p && item.desc) p.textContent = item.desc;
        if (photoImg && item.image) setImageSrc(photoImg, item.image);
        if (iconImg && item.icon) setImageSrc(iconImg, item.icon);
      }
    });
  }

  // Hydrate scrolling partner logos (updates all marquee clones identically)
  if (Array.isArray(data.partner_logos)) {
    data.partner_logos.forEach((logoUrl, idx) => {
      if (!logoUrl) return;
      sectorsSec.querySelectorAll(`img[data-partner-logo="${idx}"]`).forEach(img => {
        setImageSrc(img, logoUrl);
      });
    });
  }
}

function hydrateEngineerCta(data) {
  if (!data) return;

  const formIds = ['consult-form', 'modal-lead-form'];

  formIds.forEach((formId) => {
    const form = document.getElementById(formId);
    if (!form) return;

    const formCol = form.parentElement;
    if (formCol) {
      if (data.title) {
        const titleEl = formCol.querySelector('h3');
        if (titleEl) titleEl.textContent = data.title;
      }
      if (data.subtitle) {
        const subEl = formCol.querySelector('p');
        if (subEl) subEl.textContent = data.subtitle;
      }
      if (data.button_text) {
        const splitLabel = form.querySelector('.split-label');
        if (splitLabel) splitLabel.textContent = cleanSplitLabel(data.button_text);
      }
    }

    const grid = formCol ? formCol.parentElement : null;
    if (grid && data.engineer_photo) {
      const imgEl = grid.querySelector('img');
      setImageSrc(imgEl, data.engineer_photo);
    }
  });

  if (data.success_bg_image) {
    const successBgImg = document.querySelector('img[data-success-bg]');
    setImageSrc(successBgImg, data.success_bg_image);
  }
}

function hydrateCases(data) {
  if (!data) return;
  const casesSec = document.getElementById('cases');
  if (!casesSec) return;

  if (data.title) {
    const titleEl = casesSec.querySelector('h2');
    if (titleEl) titleEl.textContent = data.title;
  }

  // Cards in DOM are ordered 2, 1, 0 for 3D stacking depth, so match by data-case-idx!
  if (Array.isArray(data.items)) {
    data.items.forEach((item, idx) => {
      const card = casesSec.querySelector(`.case-card[data-case-idx="${idx}"]`);
      if (card) {
        const h3 = card.querySelector('h3');
        if (h3 && item.title) h3.textContent = item.title;
        const descEl = card.querySelector('p');
        if (descEl && item.scope) descEl.textContent = item.scope;
        const imgEl = card.querySelector('img');
        if (imgEl && item.image) setImageSrc(imgEl, item.image);
      }

      const tab = casesSec.querySelector(`.case-tab-btn[data-case-index="${idx}"]`);
      if (tab && item.title) {
        tab.textContent = `0${idx + 1} / ${item.title}`;
      }
    });
  }
}

function hydrateFaq(data) {
  if (!data) return;
  const faqSec = document.getElementById('faq');
  if (!faqSec) return;

  if (data.title) {
    const titleEl = faqSec.querySelector('h2');
    if (titleEl) titleEl.textContent = data.title;
  }

  if (Array.isArray(data.items)) {
    const faqItems = faqSec.querySelectorAll('.faq-row');
    data.items.forEach((item, idx) => {
      if (faqItems[idx]) {
        const el = faqItems[idx];
        const qEl = el.querySelector('.faq-trigger h3');
        const aEl = el.querySelector('.faq-answer-text');
        if (qEl && item.q) qEl.textContent = item.q;
        if (aEl && item.a) aEl.textContent = item.a;
      }
    });
  }
}

function hydrateContacts(data) {
  if (!data) return;
  const footer = document.getElementById('footer');
  if (!footer) return;

  if (data.footer_logo) {
    setImageSrc(footer.querySelector('img[data-footer-logo]'), data.footer_logo);
  }
  if (data.title) {
    const titleEl = footer.querySelector('[data-footer-title]');
    if (titleEl) titleEl.textContent = data.title;
  }
  if (data.phone) {
    const cleanHref = data.phone_clean ? sanitizeHref(`tel:${data.phone_clean}`) : null;
    footer.querySelectorAll('a[href^="tel:"]').forEach(a => {
      a.textContent = data.phone;
      if (cleanHref) a.setAttribute('href', cleanHref);
    });
  }
  if (data.email) {
    const mailHref = sanitizeHref(`mailto:${data.email}`);
    footer.querySelectorAll('a[href^="mailto:"]').forEach(a => {
      a.textContent = data.email;
      if (mailHref) a.setAttribute('href', mailHref);
    });
  }
  if (data.address) {
    const addrEl = footer.querySelector('[data-footer-address]');
    if (addrEl) addrEl.textContent = data.address;
  }
  if (data.hours) {
    const hoursEl = footer.querySelector('[data-footer-hours]');
    if (hoursEl) hoursEl.textContent = data.hours;
  }
  if (data.inn) {
    const innEl = footer.querySelector('[data-footer-inn]');
    if (innEl) innEl.textContent = data.inn;
  }
  if (data.tg_link) {
    const safeTg = sanitizeHref(data.tg_link);
    if (safeTg) {
      footer.querySelectorAll('a[data-footer-tg]').forEach(a => a.setAttribute('href', safeTg));
    }
  }
  if (data.wa_link) {
    const safeWa = sanitizeHref(data.wa_link);
    if (safeWa) {
      footer.querySelectorAll('a[data-footer-wa]').forEach(a => a.setAttribute('href', safeWa));
    }
  }
}
