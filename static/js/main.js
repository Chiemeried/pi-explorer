// Ðarlingtøn🦅 — shared frontend helpers

function truncateMiddle(str, front = 8, back = 8) {
  if (!str || str.length <= front + back + 3) return str;
  return `${str.slice(0, front)}...${str.slice(-back)}`;
}

function timeAgo(isoString) {
  const then = new Date(isoString).getTime();
  const now = Date.now();
  const diff = Math.max(0, Math.floor((now - then) / 1000));
  if (diff < 5) return "just now";
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function formatPi(stroopsOrAmount, isStroops = false) {
  const val = isStroops ? Number(stroopsOrAmount) / 10000000 : Number(stroopsOrAmount);
  if (isNaN(val)) return "—";
  return val.toLocaleString(undefined, { maximumFractionDigits: 7 }) + " π";
}

async function apiGet(path) {
  const res = await fetch(path);
  const data = await res.json();
  if (!res.ok || data.ok === false) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}

function el(tag, className, html) {
  const e = document.createElement(tag);
  if (className) e.className = className;
  if (html !== undefined) e.innerHTML = html;
  return e;
}

// Mark active nav tab based on current path
document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  document.querySelectorAll(".tab").forEach((tab) => {
    const href = tab.getAttribute("href");
    if (href === "/" ? path === "/" : path.startsWith(href)) {
      tab.classList.add("active");
    }
  });
});
