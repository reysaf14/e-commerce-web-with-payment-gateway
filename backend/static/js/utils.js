/* ═══════════════════════════════════════════════════════════
   UTILS — Helper functions
   ═══════════════════════════════════════════════════════════ */

function formatRupiah(amount) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency", currency: "IDR", minimumFractionDigits: 0
  }).format(amount);
}

function getCookie(name) {
  const cookies = document.cookie.split(";").map(c => c.trim());
  for (const c of cookies) {
    if (c.startsWith(name + "=")) return decodeURIComponent(c.substring(name.length + 1));
  }
  return null;
}

async function apiGet(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function apiPost(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return { ok: res.ok, data: await res.json() };
}
