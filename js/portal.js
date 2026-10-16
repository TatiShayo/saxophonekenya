/**
 * portal.js — Contract & invoice portal
 * --------------------------------------------------------------------------
 * Fixes carried over:
 *  - "Download Contract (PDF)" called window.print(), which printed the
 *    ENTIRE page including the navbar, hero video and footer. It now sets a
 *    body class so css/print.css renders the contract alone, then restores
 *    the page after printing. print() is also a blocking call in some
 *    browsers, so the class is reset on a timeout as well as afterprint.
 *  - generateInvoicePreview() was a stub: it showed a toast and produced no
 *    invoice. It now renders a real, editable preview.
 *  - Tabs had no ARIA tablist contract. Now role="tab"/"tabpanel" with
 *    aria-selected and arrow-key navigation.
 *  - The invoice date input had no value and no minimum, so a past date
 *    could be invoiced.
 */

import { qs, qsa, el, safeSetText, formatISODate, isFutureDate } from './utils.js';
import { showToast } from './toast.js';
import { CONFIG } from './config.js';

const PRINT_CLASS = 'printing-invoice';
const PRINT_RESET_MS = 4000;

/* --------------------------------------------------------------------------
   Tabs
   -------------------------------------------------------------------------- */

function switchPortalTab(tab) {
  const views = { contract: qs('#contract-view'), invoice: qs('#invoice-view') };
  const buttons = { contract: qs('#tab-contract-btn'), invoice: qs('#tab-invoice-btn') };

  for (const [key, view] of Object.entries(views)) {
    if (!view) continue;
    const active = key === tab;
    view.hidden = !active;
    view.setAttribute('role', 'tabpanel');
    view.setAttribute('aria-labelledby', `${key}-tab`);
  }

  for (const [key, button] of Object.entries(buttons)) {
    if (!button) continue;
    const active = key === tab;
    button.classList.toggle('active', active);
    button.setAttribute('aria-selected', String(active));
    button.setAttribute('role', 'tab');
    button.tabIndex = active ? 0 : -1;
  }
}

function initTabs() {
  const header = qs('.portal-tab-header');
  if (!header) return;

  const buttons = qsa('.portal-nav-tab', header);
  buttons.forEach((button, index) => {
    button.addEventListener('click', () => switchPortalTab(button.dataset.tab));
    button.addEventListener('keydown', (event) => {
      if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
      event.preventDefault();
      const delta = event.key === 'ArrowRight' ? 1 : -1;
      const next = buttons[(index + delta + buttons.length) % buttons.length];
      next.focus();
      switchPortalTab(next.dataset.tab);
    });
  });
}

/* --------------------------------------------------------------------------
   Print helpers — see css/print.css
   -------------------------------------------------------------------------- */

function printOnly(bodyClass, selector) {
  const target = qs(selector);
  if (!target) {
    showToast('Nothing to print yet.');
    return;
  }

  document.body.classList.add(bodyClass);
  window.print();

  const reset = () => document.body.classList.remove(bodyClass);
  window.addEventListener('afterprint', reset, { once: true });
  /* Safety net: some browsers never fire afterprint. */
  window.setTimeout(reset, PRINT_RESET_MS);
}

function downloadSampleContract() {
  showToast('Preparing your performance agreement for print...');
  printOnly('printing-contract', '#contract-view');
}

function printInvoice() {
  const preview = qs('#invoice-preview');
  if (!preview) {
    showToast('Preview the invoice first, then print.');
    return;
  }
  showToast('Preparing your invoice for print...');
  printOnly(PRINT_CLASS, '#invoice-view');
}

/* --------------------------------------------------------------------------
   Invoice generator
   -------------------------------------------------------------------------- */

const PACKAGE_PRICES = Object.freeze({
  'Full Wedding Day Package':  { kes: 'KES 75,000',  usd: '$580' },
  'Solo Sax • Cocktail Hour':  { kes: 'KES 25,000',  usd: '$190' },
  'Solo Sax • Extended Event': { kes: 'KES 45,000',  usd: '$350' },
  'Saxophone + DJ Live Duo':   { kes: 'KES 65,000',  usd: '$500' },
  'Full Live Band Experience': { kes: 'KES 120,000', usd: '$920' }
});

function invoiceLine(term, value) {
  return el('div', { class: 'invoice-line' }, [
    el('dt', { text: term }),
    el('dd', { text: value })
  ]);
}

function buildInvoicePreview() {
  const host = qs('#invoice-preview');
  if (!host) return;

  const client = qs('#inv-client-name');
  const date = qs('#inv-date');
  const pkg = qs('#inv-package');
  const status = qs('#inv-status');

  const pkgMeta = PACKAGE_PRICES[pkg?.value];
  const ref = `FSK-INV-${date?.value ? date.value.replace(/-/g, '') : 'DRAFT'}`;

  const lines = [
    invoiceLine('Invoice reference', ref),
    invoiceLine('Prepared for', client?.value.trim() || '—'),
    invoiceLine('Performance date', date?.value || '—'),
    invoiceLine('Package', pkg?.value || '—'),
    invoiceLine('Investment', pkgMeta ? pkgMeta.kes : 'On quotation'),
    invoiceLine('Payment status', status?.value || '—'),
    invoiceLine('Artist', `${CONFIG.ARTIST_LEGAL} (${CONFIG.ARTIST_STAGE})`),
    invoiceLine('Business contact', CONFIG.EMAIL),
    invoiceLine('Deposit terms', '50% to hold the date · balance on the event day')
  ];

  host.replaceChildren(
    el('h4', { class: 'invoice-preview-title', text: 'Invoice preview' }),
    el('dl', { class: 'invoice-lines' }, lines)
  );

  showToast(`Invoice ${ref} previewed for ${client?.value.trim() || 'client'}.`);
}

function initInvoiceForm() {
  const form = qs('#invoice-form');
  const client = qs('#inv-client-name');
  const date = qs('#inv-date');

  if (date) {
    /* Never allow a past invoice date. Uses the local-time helper so the
       UTC/ISOString() off-by-one-day bug cannot return yesterday. */
    date.min = formatISODate(new Date());
    if (!date.value || !isFutureDate(date.value)) {
      const state = window.AirbnbCalendarState;
      date.value = formatISODate(state?.rangeStart || new Date());
    }
  }

  if (form) {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      buildInvoicePreview();
    });
  }
}

/* --------------------------------------------------------------------------
   Init
   -------------------------------------------------------------------------- */

export function initPortal() {
  initTabs();
  initInvoiceForm();
  /* Pre-select defaults */
  switchPortalTab('contract');

  window.switchPortalTab = switchPortalTab;
  window.downloadSampleContract = downloadSampleContract;
  window.printInvoice = printInvoice;
  window.generateInvoicePreview = (event) => {
    event?.preventDefault();
    buildInvoicePreview();
  };
}

export { switchPortalTab, downloadSampleContract, printInvoice, buildInvoicePreview };
