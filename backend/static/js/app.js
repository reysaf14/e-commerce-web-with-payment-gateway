/* ═══════════════════════════════════════════════════════════
   APP.JS — Main app logic (cart, search, navigation)
   ═══════════════════════════════════════════════════════════ */

// ── Cart Badge ───────────────────────────────────────────

async function updateCartBadge() {
  try {
    const res = await fetch("/api/v1/cart/");
    if (res.ok) {
      const cart = await res.json();
      const badge = document.getElementById("cart-count");
      if (badge) badge.textContent = cart.item_count || 0;
    }
  } catch (e) { /* silent */ }
}

// ── Search ───────────────────────────────────────────────

function doSearch() {
  const q = document.getElementById("search-input").value.trim();
  if (q) {
    window.location.href = `/catalog/?q=${encodeURIComponent(q)}`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search-input");
  if (searchInput) {
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") doSearch();
    });
  }
  updateCartBadge();
});

// ── Open Cart ────────────────────────────────────────────

function openCart() {
  window.location.href = "/cart/";
}
