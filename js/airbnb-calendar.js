/**
 * Airbnb-Style Continuous Calendar & Reservation Engine
 * Frederic Sax Ke Luxury Booking Showcase
 * Matches Airbnb Mobile/Web Specifications (Screenshots 1 & 2)
 */

(function () {
  'use strict';

  // Base state
  const STATE = {
    viewYear: 2026,
    viewMonth: 9, // 9 = October (0-indexed)
    monthsCount: 2, // October & November continuous stream
    rangeStart: new Date(2026, 9, 8), // Default selection: Oct 8
    rangeEnd: new Date(2026, 9, 10),   // Default range end: Oct 10 (matching Screenshot 1)
    bookingMode: 'dates', // 'dates' | 'flexible'
    flexTolerance: 'exact', // 'exact', '1', '2', '3', '7'
    selectedSlot: {
      name: 'Evening Set (18:00 – 22:00)',
      label: 'Evening Reception & Cocktail',
      package: 'Full Wedding Day Package'
    },
    today: new Date(2026, 9, 7), // Oct 7, 2026
    bookedDates: [
      '2026-10-05',
      '2026-10-06',
      '2026-10-12',
      '2026-10-13',
      '2026-10-14',
      '2026-10-15',
      '2026-10-16',
      '2026-11-05',
      '2026-11-06'
    ]
  };

  const MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  // Helper: Format date as YYYY-MM-DD
  function toISODate(d) {
    if (!d) return '';
    const yr = d.getFullYear();
    const mo = String(d.getMonth() + 1).padStart(2, '0');
    const dy = String(d.getDate()).padStart(2, '0');
    return `${yr}-${mo}-${dy}`;
  }

  // Helper: Format date for readable display (e.g. "Oct 8 – 10, 2026")
  function formatRangeDisplay(start, end) {
    if (!start) return 'Select performance dates';
    const sMonth = MONTH_NAMES[start.getMonth()].slice(0, 3);
    const sDay = start.getDate();
    const sYr = start.getFullYear();

    if (!end || start.getTime() === end.getTime()) {
      return `${sMonth} ${sDay}, ${sYr}`;
    }

    const eMonth = MONTH_NAMES[end.getMonth()].slice(0, 3);
    const eDay = end.getDate();
    const eYr = end.getFullYear();

    if (start.getMonth() === end.getMonth() && sYr === eYr) {
      return `${sMonth} ${sDay} – ${eDay}, ${sYr}`;
    }
    return `${sMonth} ${sDay} – ${eMonth} ${eDay}, ${eYr}`;
  }

  // Days in month calculation (Leap year safe)
  function getDaysInMonth(year, month) {
    return new Date(year, month + 1, 0).getDate();
  }

  // Day of week index for Monday-first grid: Mon=0, Tue=1, ..., Sun=6
  function getMondayFirstDayIndex(year, month, day = 1) {
    const rawDay = new Date(year, month, day).getDay(); // Sun=0, Mon=1...
    return (rawDay + 6) % 7;
  }

  // Check if date is in past or booked
  function isDateUnavailable(d) {
    const iso = toISODate(d);
    if (d < STATE.today) return true;
    if (STATE.bookedDates.includes(iso)) return true;
    return false;
  }

  // Check if date is within selected range
  function isDateInRange(d) {
    if (!STATE.rangeStart || !STATE.rangeEnd) return false;
    const t = d.getTime();
    return t > STATE.rangeStart.getTime() && t < STATE.rangeEnd.getTime();
  }

  function isSameDay(d1, d2) {
    if (!d1 || !d2) return false;
    return d1.getFullYear() === d2.getFullYear() &&
           d1.getMonth() === d2.getMonth() &&
           d1.getDate() === d2.getDate();
  }

  // Render the continuous calendar stream
  function renderCalendarStream() {
    const streamContainer = document.getElementById('bnb-calendar-stream');
    if (!streamContainer) return;

    streamContainer.innerHTML = '';

    for (let i = 0; i < STATE.monthsCount; i++) {
      let curMonth = STATE.viewMonth + i;
      let curYear = STATE.viewYear;
      if (curMonth > 11) {
        curMonth -= 12;
        curYear += 1;
      }

      const monthSection = document.createElement('div');
      monthSection.className = 'bnb-month-section';

      const monthTitle = document.createElement('div');
      monthTitle.className = 'bnb-month-title';
      monthTitle.textContent = `${MONTH_NAMES[curMonth]} ${curYear}`;
      monthSection.appendChild(monthTitle);

      const daysGrid = document.createElement('div');
      daysGrid.className = 'bnb-days-grid';

      const firstDayOffset = getMondayFirstDayIndex(curYear, curMonth, 1);
      const totalDays = getDaysInMonth(curYear, curMonth);

      // Empty lead-in cells
      for (let empty = 0; empty < firstDayOffset; empty++) {
        const emptyCell = document.createElement('div');
        emptyCell.className = 'bnb-day-cell empty';
        daysGrid.appendChild(emptyCell);
      }

      // Day cells
      for (let day = 1; day <= totalDays; day++) {
        const cellDate = new Date(curYear, curMonth, day);
        const cell = document.createElement('div');
        cell.className = 'bnb-day-cell';

        const numSpan = document.createElement('span');
        numSpan.className = 'bnb-day-num';
        numSpan.textContent = String(day);
        cell.appendChild(numSpan);

        // Check states
        const isUnavailable = isDateUnavailable(cellDate);
        if (isUnavailable) {
          cell.classList.add('struck');
          cell.title = 'Date unavailable / held';
        } else {
          // Range states
          const isStart = isSameDay(cellDate, STATE.rangeStart);
          const isEnd = isSameDay(cellDate, STATE.rangeEnd);
          const inRange = isDateInRange(cellDate);

          if (isStart && isEnd) {
            cell.classList.add('single-selected');
          } else if (isStart) {
            cell.classList.add('range-start');
          } else if (isEnd) {
            cell.classList.add('range-end');
          } else if (inRange) {
            cell.classList.add('in-range');
          }

          if (isSameDay(cellDate, STATE.today)) {
            cell.classList.add('today');
          }

          // Click handler
          cell.onclick = () => handleDateClick(cellDate);
        }

        daysGrid.appendChild(cell);
      }

      monthSection.appendChild(daysGrid);
      streamContainer.appendChild(monthSection);
    }

    // Synchronize UI texts
    syncUIWithSelection();
  }

  // Handle date selection (Airbnb range logic)
  function handleDateClick(clickedDate) {
    if (!STATE.rangeStart || (STATE.rangeStart && STATE.rangeEnd)) {
      // Starting new selection
      STATE.rangeStart = clickedDate;
      STATE.rangeEnd = null;
    } else if (STATE.rangeStart && !STATE.rangeEnd) {
      if (clickedDate.getTime() < STATE.rangeStart.getTime()) {
        // Clicked before start: restart with this as new start
        STATE.rangeStart = clickedDate;
        STATE.rangeEnd = null;
      } else {
        // Complete range
        STATE.rangeEnd = clickedDate;
      }
    }

    renderCalendarStream();
  }

  // Synchronize state with floating cards and forms
  function syncUIWithSelection() {
    const rangeText = formatRangeDisplay(STATE.rangeStart, STATE.rangeEnd);

    // Update segmented card on right
    const selectedDateTextEl = document.getElementById('cal-selected-date-text');
    if (selectedDateTextEl) {
      selectedDateTextEl.textContent = rangeText;
    }

    // Update contact form performance date
    const formDateInput = document.getElementById('form-date');
    if (formDateInput && STATE.rangeStart) {
      formDateInput.value = toISODate(STATE.rangeStart);
    }

    // Update bottom drawer date summary if present
    const summaryEl = document.getElementById('bnb-selection-summary');
    if (summaryEl) {
      const flexLabel = STATE.flexTolerance !== 'exact' ? ` (± ${STATE.flexTolerance} days)` : '';
      summaryEl.textContent = `${rangeText}${flexLabel} • ${STATE.selectedSlot.name}`;
    }
  }

  // Segmented control: [ Dates | Flexible ]
  window.setAirbnbBookingMode = function (mode) {
    STATE.bookingMode = mode;
    const btnDates = document.getElementById('bnb-mode-dates');
    const btnFlex = document.getElementById('bnb-mode-flexible');
    const flexSection = document.getElementById('bnb-flex-section');

    if (btnDates) btnDates.classList.toggle('active', mode === 'dates');
    if (btnFlex) btnFlex.classList.toggle('active', mode === 'flexible');

    if (flexSection) {
      flexSection.style.display = mode === 'flexible' ? 'block' : 'none';
    }

    syncUIWithSelection();
  };

  // Flexibility tolerance chips: exact, 1, 2, 3, 7
  window.setAirbnbTolerance = function (btn, tol) {
    STATE.flexTolerance = tol;
    document.querySelectorAll('.bnb-flex-chip').forEach(el => el.classList.remove('active'));
    if (btn) btn.classList.add('active');
    syncUIWithSelection();
  };

  // Clear / Reset selection
  window.clearAirbnbDates = function () {
    STATE.rangeStart = null;
    STATE.rangeEnd = null;
    renderCalendarStream();
    if (typeof showToast === 'function') {
      showToast('Dates reset. Select your preferred performance date.');
    }
  };

  // Performance slot change modal
  window.openSlotChangeModal = function () {
    const modal = document.getElementById('bnb-slot-modal');
    if (modal) modal.classList.add('active');
  };

  window.closeSlotChangeModal = function () {
    const modal = document.getElementById('bnb-slot-modal');
    if (modal) modal.classList.remove('active');
  };

  window.selectPerformanceSlot = function (slotName, slotLabel, slotPkg) {
    STATE.selectedSlot = { name: slotName, label: slotLabel, package: slotPkg };
    const valEl = document.getElementById('bnb-slot-bar-val');
    if (valEl) valEl.textContent = slotName;

    const pkgDisplay = document.getElementById('airbnb-selected-pkg-display');
    if (pkgDisplay) pkgDisplay.textContent = slotPkg;

    const itemTotal = document.getElementById('airbnb-item-name');
    if (itemTotal) itemTotal.textContent = slotPkg;

    closeSlotChangeModal();
    syncUIWithSelection();
    if (typeof showToast === 'function') {
      showToast(`Performance slot updated: ${slotLabel}`);
    }
  };

  /**
   * Dispatch to WhatsApp
   * @param {boolean} isSimulation - Whether this is an automated test simulation
   */
  window.dispatchAirbnbReservationWhatsApp = function (isSimulation = false) {
    const start = STATE.rangeStart || STATE.today;
    const end = STATE.rangeEnd || start;
    const dateRangeStr = formatRangeDisplay(start, end);
    const flexText = STATE.flexTolerance !== 'exact' ? `± ${STATE.flexTolerance} days` : 'Exact dates';
    const pkgName = STATE.selectedSlot.package || 'Full Wedding Day Package';
    const slotName = STATE.selectedSlot.name;
    const refNum = `FSK-BNB-${start.getFullYear()}${String(start.getMonth() + 1).padStart(2, '0')}${String(start.getDate()).padStart(2, '0')}`;

    let message = '';

    if (isSimulation) {
      // Explicitly marked as a test simulation
      message =
        `⚠️ [TEST BOOKING SIMULATION]\n` +
        `----------------------------------------\n` +
        `*AUTOMATED SYSTEM VERIFICATION TEST*\n` +
        `Note: This is a simulated booking test to verify WhatsApp routing.\n` +
        `----------------------------------------\n` +
        `Client / Tester: Automated System Verification\n` +
        `Performance Dates: ${dateRangeStr}\n` +
        `Tolerance: ${flexText}\n` +
        `Performance Slot: ${slotName}\n` +
        `Package Requested: ${pkgName}\n` +
        `Venue / Location: Nairobi & Surrounds (Simulated)\n` +
        `----------------------------------------\n` +
        `STATUS: TEST SIMULATION VERIFIED\n` +
        `Ref: ${refNum} | fredericsax.com`;
    } else {
      // Standard executive booking inquiry
      message =
        `*FREDERIC SAX KE - PERFORMANCE RESERVATION*\n` +
        `----------------------------------------\n` +
        `Performance Dates: ${dateRangeStr}\n` +
        `Date Flexibility: ${flexText}\n` +
        `Performance Slot: ${slotName}\n` +
        `Package: ${pkgName}\n` +
        `Location: Nairobi & East Africa\n` +
        `----------------------------------------\n` +
        `Please confirm date availability and performance hold.\n` +
        `Ref: ${refNum} | fredericsax.com`;
    }

    const waUrl = `https://wa.me/254745163122?text=${encodeURIComponent(message)}`;

    if (typeof showToast === 'function') {
      const toastText = isSimulation
        ? 'Dispatching [TEST BOOKING SIMULATION] to WhatsApp...'
        : 'Connecting directly to Frederic on WhatsApp...';
      showToast(toastText);
    }

    setTimeout(() => {
      window.open(waUrl, '_blank');
    }, 500);
  };

  // Expose state and init
  window.AirbnbCalendarState = STATE;
  window.initAirbnbCalendar = renderCalendarStream;

  // Auto-init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderCalendarStream);
  } else {
    renderCalendarStream();
  }
})();
