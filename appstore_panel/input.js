import { api } from "../../../scripts/api.js";
const api_base = api.api_base;
async function loadVueApp() {
  try {
    const e = await fetch("appstore_panel/dist/index.html");
    if (!e.ok) throw new Error("Network response was not ok");
    const t = await e.text(),
      n = document.createElement("div");
    n.innerHTML = t;

    n.querySelectorAll('link[rel="stylesheet"]').forEach((e) => {
      const t = document.createElement("link");
      (t.rel = "stylesheet"),
        (t.href = `${e.getAttribute("href")}`),
        document.head.appendChild(t);
    });
    const o = n.querySelectorAll("script");
    for (const e of o) {
      const t = document.createElement("script");
      e.getAttribute("src") &&
        (
          (t.src = `${e.getAttribute("src")}`), 
          (t.type = "module"),
          (t.defer = !0),
          document.body.appendChild(t));
    }
    const r = n.querySelector("#admin-app-appstore");
    if (
      (r &&
        (function e(t) {
          Array.from(t.childNodes).forEach((n) => {
            3 === n.nodeType ? t.removeChild(n) : 1 === n.nodeType && e(n);
          });
        })(r),
      r)
    ) {
      const e = document.getElementById("root");
      e ? (e.innerHTML = r.innerHTML) : document.body.appendChild(r)
    }
  } catch (e) {}
}
setTimeout(() => {
  loadVueApp();
}, 500);
