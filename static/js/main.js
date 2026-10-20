/**
 * ASSA Event Manager — Main JavaScript
 * Global utilities: toast, logout, navbar scroll, mobile menu
 */

/* ── Toast Notification ─────────────────────────────────── */
function showToast(message, type = 'info', duration = 3500) {
  const toast = document.getElementById('toast');
  if (!toast) return;

  toast.textContent = message;
  toast.className   = `toast toast--${type} show`;

  if (showToast._timer) clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => {
    toast.classList.remove('show');
  }, duration);
}
/* ── User Dropdown ───────────────────────────────────────── *//* ── Event Card Expansion ────────────────────────────────── */
function toggleExpansion(btn) {
  const card = btn.closest('.event-card');
  const expansion = card.querySelector('.event-card__expansion');
  const isShowing = expansion.classList.contains('show');
  
  // Close all other expansions first (optional but cleaner)
  document.querySelectorAll('.event-card__expansion.show').forEach(el => {
    if (el !== expansion) el.classList.remove('show');
  });
  
  expansion.classList.toggle('show');
  btn.textContent = isShowing ? 'Book Now' : 'Hide Details';
  
  if (!isShowing) {
    expansion.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}
/* ── Confirm Booking ───────────────────────────────────────── */
async function confirmBooking(eventId) {
  const res = await fetch(`/api/bookings/${eventId}`, { method: 'POST' });
  const data = await res.json();
  
  if (res.ok) {
    showToast(data.message, 'success');
    setTimeout(() => window.location.href = '/dashboard', 1000);
  } else {
    showToast(data.error || 'Booking failed', 'error');
  }
}

const dropBtn = document.getElementById('userDropdownBtn');
const dropContent = document.getElementById('userDropdownContent');
if (dropBtn && dropContent) {
  dropBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    dropContent.classList.toggle('show');
  });
  document.addEventListener('click', (e) => {
    if (!dropContent.contains(e.target)) {
      dropContent.classList.remove('show');
    }
  });
}
/* ── Logout ─────────────────────────────────────────────── */
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
  logoutBtn.addEventListener('click', async () => {
    const res = await fetch('/api/auth/logout', { method: 'POST' });
    if (res.ok) {
      showToast('Logged out successfully', 'success');
      setTimeout(() => window.location.href = '/', 1000);
    }
  });
}

/* ── Navbar scroll effect ────────────────────────────────── */
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 10) {
    navbar?.classList.add('scrolled');
  } else {
    navbar?.classList.remove('scrolled');
  }
}, { passive: true });

/* ── Mobile hamburger menu ───────────────────────────────── */
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');
if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });
  // Close on outside click
  document.addEventListener('click', e => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('open');
    }
  });
}

/* ── Card input formatting (card number spaces) ─────────────── */
document.addEventListener('input', e => {
  if (e.target && e.target.id === 'cardNumber') {
    let v = e.target.value.replace(/\D/g, '').slice(0, 16);
    e.target.value = v.replace(/(\d{4})(?=\d)/g, '$1 ');
  }
  if (e.target && e.target.id === 'cardExpiry') {
    let v = e.target.value.replace(/\D/g, '').slice(0, 4);
    if (v.length >= 3) v = v.slice(0,2) + '/' + v.slice(2);
    e.target.value = v;
  }
});

/* ── Animate elements on scroll ─────────────────────────── */
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.animation = 'fadeUp 0.5s ease forwards';
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.feature-card, .event-card, .category-card').forEach(el => {
  el.style.opacity = '0';
  observer.observe(el);
});
