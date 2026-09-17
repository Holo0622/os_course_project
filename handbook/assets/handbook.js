const GRID = 20;
const SHOP = { w: 120, h: 86 };
const MACHINE = { w: 84, h: 64 };

const SHOPS = {
  press: { name: "冲压车间", role: "进程", cap: 80, cost: 1200 },
  assemble: { name: "装配车间", role: "进程", cap: 70, cost: 1100 },
  store: { name: "仓储车间", role: "共享内存", cap: 24, cost: 500 }
};
const MACHINES = {
  station: { name: "工位机", role: "工作线程", cap: 35, cost: 400 },
  arm: { name: "机械臂", role: "工作线程", cap: 28, cost: 360 }
};
const SCHED = {
  fcfs: { factor: 0.82, note: "先到先服务，长订单容易堵住流水线" },
  sjf: { factor: 0.91, note: "短作业优先，吞吐更高，大单可能饥饿" },
  priority: { factor: 0.94, note: "急单插队，接近课设急诊室示例" },
  rr: { factor: 0.86, note: "更公平，但换模/上下文切换有损耗" }
};

let uid = 3;
const shops = [
  { id: 1, type: "press", x: 40, y: 80, machines: [{ id: 11, type: "station", x: 20, y: 60 }] },
  { id: 2, type: "assemble", x: 160, y: 80, machines: [] }
];
let view = { mode: "factory" };
let drag = null;

const stage = document.getElementById("stage");
const palette = document.getElementById("palette");
const schedSel = document.getElementById("sched");
const daemonBox = document.getElementById("daemon-on");
const priceInput = document.getElementById("price");
const backBtn = document.getElementById("back");
const crumb = document.getElementById("crumb");

function snap(v) {
  return Math.round(v / GRID) * GRID;
}
function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}
function currentShop() {
  return shops.find((s) => s.id === view.id);
}
function paletteSpec() {
  return view.mode === "factory" ? SHOPS : MACHINES;
}
function sizeOf(level) {
  return level === "shop" ? SHOP : MACHINE;
}

function magnet(x, y, w, h, others) {
  let nx = snap(x);
  let ny = snap(y);
  others.forEach((o) => {
    const ox = o.x, oy = o.y, ow = o.w, oh = o.h;
    if (Math.abs((nx + w) - ox) <= GRID) nx = ox - w;
    if (Math.abs(nx - (ox + ow)) <= GRID) nx = ox + ow;
    if (Math.abs((ny + h) - oy) <= GRID) ny = oy - h;
    if (Math.abs(ny - (oy + oh)) <= GRID) ny = oy + oh;
  });
  return { x: nx, y: ny };
}

function renderPalette() {
  palette.innerHTML = "";
  Object.entries(paletteSpec()).forEach(([type, meta]) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "brick-src " + type;
    btn.innerHTML = `<strong>${meta.name}</strong><small>${meta.role} · 拖出去</small>`;
    btn.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      startDrag({ mode: "new", type, level: view.mode === "factory" ? "shop" : "machine" }, e);
    });
    palette.appendChild(btn);
  });
}

function pieceHTML(title, role, extra) {
  return `<div class="studs"><i></i><i></i><i></i></div>
    <div class="body"><strong>${title}</strong><em>${role}</em>${extra || ""}</div>`;
}

function renderStage() {
  stage.classList.toggle("inside", view.mode === "inside");
  stage.innerHTML = "";
  if (view.mode === "factory") {
    backBtn.hidden = true;
    crumb.textContent = "厂区平面 · 把车间拖近，接口会吸住";
    drawLinks();
    shops.forEach((shop) => drawPiece(shop, "shop"));
    if (!shops.length) {
      stage.insertAdjacentHTML("beforeend", `<div class="stage-hint">从左侧拖一个车间到这张平面上</div>`);
    }
  } else {
    const shop = currentShop();
    backBtn.hidden = false;
    crumb.textContent = `${SHOPS[shop.type].name}内部 · 机器 = 线程 · 还可继续拖`;
    (shop.machines || []).forEach((m) => drawPiece(m, "machine"));
    if (!(shop.machines || []).length) {
      stage.insertAdjacentHTML("beforeend", `<div class="stage-hint">车间是空的。把工位机或机械臂拖进来</div>`);
    }
  }
}

function drawLinks() {
  shops.forEach((a, i) => {
    shops.slice(i + 1).forEach((b) => {
      const ax2 = a.x + SHOP.w, ay2 = a.y + SHOP.h;
      const bx2 = b.x + SHOP.w, by2 = b.y + SHOP.h;
      const overlapY = Math.min(ay2, by2) - Math.max(a.y, b.y);
      const overlapX = Math.min(ax2, bx2) - Math.max(a.x, b.x);
      const el = document.createElement("div");
      el.className = "link";
      if (overlapY > 24 && (Math.abs(ax2 - b.x) <= 2 || Math.abs(bx2 - a.x) <= 2)) {
        const left = Math.min(ax2, bx2);
        el.classList.add("h");
        el.style.left = left - 4 + "px";
        el.style.top = Math.max(a.y, b.y) + overlapY / 2 - 4 + "px";
        el.style.width = "8px";
        el.style.height = "10px";
        el.style.width = "12px";
        el.style.height = "10px";
        stage.appendChild(el);
      } else if (overlapX > 24 && (Math.abs(ay2 - b.y) <= 2 || Math.abs(by2 - a.y) <= 2)) {
        el.classList.add("v");
        el.style.left = Math.max(a.x, b.x) + overlapX / 2 - 4 + "px";
        el.style.top = Math.min(ay2, by2) - 4 + "px";
        el.style.width = "10px";
        el.style.height = "12px";
        stage.appendChild(el);
      }
    });
  });
}

function countLinks() {
  let n = 0;
  shops.forEach((a, i) => {
    shops.slice(i + 1).forEach((b) => {
      const ax2 = a.x + SHOP.w, ay2 = a.y + SHOP.h;
      const bx2 = b.x + SHOP.w, by2 = b.y + SHOP.h;
      const overlapY = Math.min(ay2, by2) - Math.max(a.y, b.y);
      const overlapX = Math.min(ax2, bx2) - Math.max(a.x, b.x);
      if (overlapY > 24 && (Math.abs(ax2 - b.x) <= 2 || Math.abs(bx2 - a.x) <= 2)) n += 1;
      if (overlapX > 24 && (Math.abs(ay2 - b.y) <= 2 || Math.abs(by2 - a.y) <= 2)) n += 1;
    });
  });
  return n;
}

function drawPiece(item, level) {
  const spec = level === "shop" ? SHOPS[item.type] : MACHINES[item.type];
  const size = sizeOf(level);
  const el = document.createElement("div");
  el.className = "piece " + level + " " + item.type;
  el.style.left = item.x + "px";
  el.style.top = item.y + "px";
  el.style.zIndex = "2";
  const extra = level === "shop"
    ? `<button class="enter" type="button" data-enter="${item.id}">进入</button>`
    : "";
  el.innerHTML = pieceHTML(spec.name, spec.role, extra);
  el.addEventListener("pointerdown", (e) => {
    if (e.button !== 0) return;
    if (e.target.closest(".enter")) return;
    startDrag({ mode: "move", id: item.id, level }, e);
  });
  const enter = el.querySelector(".enter");
  if (enter) {
    enter.addEventListener("click", (e) => {
      e.stopPropagation();
      view = { mode: "inside", id: item.id };
      renderPalette();
      renderStage();
      compute();
    });
  }
  stage.appendChild(el);
}

function startDrag(info, e) {
  const size = sizeOf(info.level);
  drag = {
    ...info,
    dx: e.clientX,
    dy: e.clientY,
    originX: 0,
    originY: 0,
    ghost: null
  };
  if (info.mode === "move") {
    const list = info.level === "shop" ? shops : currentShop().machines;
    const item = list.find((x) => x.id === info.id);
    drag.originX = item.x;
    drag.originY = item.y;
  }
  const ghost = document.createElement("div");
  ghost.className = "piece ghost " + info.level + " " + (info.type || findType(info));
  const spec = (info.level === "shop" ? SHOPS : MACHINES)[info.type || findType(info)];
  ghost.innerHTML = pieceHTML(spec.name, spec.role);
  ghost.style.width = size.w + "px";
  ghost.style.left = e.clientX - size.w / 2 + "px";
  ghost.style.top = e.clientY - 16 + "px";
  document.body.appendChild(ghost);
  drag.ghost = ghost;
  e.preventDefault();
}

function findType(info) {
  const list = info.level === "shop" ? shops : currentShop().machines;
  return list.find((x) => x.id === info.id).type;
}

function onMove(e) {
  if (!drag) return;
  const size = sizeOf(drag.level);
  drag.ghost.style.left = e.clientX - size.w / 2 + "px";
  drag.ghost.style.top = e.clientY - 16 + "px";
}

function onUp(e) {
  if (!drag) return;
  const box = stage.getBoundingClientRect();
  const inside = e.clientX >= box.left && e.clientX <= box.right && e.clientY >= box.top && e.clientY <= box.bottom;
  const size = sizeOf(drag.level);
  if (inside) {
    let x = e.clientX - box.left - size.w / 2;
    let y = e.clientY - box.top - 16;
    const others = (drag.level === "shop" ? shops : currentShop().machines)
      .filter((p) => p.id !== drag.id)
      .map((p) => ({ x: p.x, y: p.y, w: size.w, h: size.h }));
    const m = magnet(x, y, size.w, size.h, others);
    x = clamp(m.x, 0, box.width - size.w);
    y = clamp(m.y, 8, box.height - size.h);
    if (drag.mode === "new") {
      if (drag.level === "shop") {
        shops.push({ id: ++uid, type: drag.type, x, y, machines: [] });
      } else {
        currentShop().machines.push({ id: ++uid, type: drag.type, x, y });
      }
    } else {
      const list = drag.level === "shop" ? shops : currentShop().machines;
      const item = list.find((p) => p.id === drag.id);
      item.x = x;
      item.y = y;
    }
  }
  drag.ghost.remove();
  drag = null;
  renderStage();
  compute();
}

document.addEventListener("pointermove", onMove);
document.addEventListener("pointerup", onUp);

function compute() {
  const shopN = shops.length;
  const machineN = shops.reduce((n, s) => n + (s.machines || []).length, 0);
  const links = countLinks();
  const types = new Set(shops.map((s) => s.type));
  const rawCap = shops.reduce((n, s) => n + SHOPS[s.type].cap, 0) + machineN * 30;
  const topology = 1
    - (shopN === 0 ? 0.55 : 0)
    - (machineN === 0 ? 0.22 : 0)
    - (types.has("store") ? 0 : 0.08)
    - (links === 0 && shopN > 1 ? 0.1 : 0);
  const pipeBonus = 1 + Math.min(links, 3) * 0.04;
  const sched = SCHED[schedSel.value];
  const crash = daemonBox.checked ? 0.03 : 0.18;
  const yieldDay = Math.max(0, Math.round(rawCap * Math.max(topology, 0.12) * pipeBonus * sched.factor * (1 - crash)));
  const cost = shops.reduce((n, s) => n + SHOPS[s.type].cost + s.machines.reduce((m, k) => m + MACHINES[k.type].cost, 0), 0)
    + (daemonBox.checked ? 80 : 0);
  const revenue = yieldDay * (Number(priceInput.value) || 18) - cost;

  document.getElementById("m-yield").textContent = yieldDay + " 件/班";
  document.getElementById("m-rev").textContent = revenue.toLocaleString("zh-CN") + " 元";
  document.getElementById("m-note").textContent = sched.note
    + (daemonBox.checked ? "；守护进程把故障恢复损耗压到约 3%。" : "；无守护进程时宕机损失约 18%。")
    + (shopN && machineN ? "" : " 厂区要有车间，车间里还要有机器。");
  document.getElementById("m-struct").textContent =
    `车间 ${shopN} · 机器 ${machineN} · 拼接接口 ${links}`;
}

backBtn.onclick = () => {
  view = { mode: "factory" };
  renderPalette();
  renderStage();
  compute();
};
document.getElementById("clear").onclick = () => {
  if (view.mode === "factory") shops.splice(0, shops.length);
  else currentShop().machines.splice(0, currentShop().machines.length);
  renderStage();
  compute();
};
schedSel.onchange = compute;
daemonBox.onchange = compute;
priceInput.oninput = compute;

document.querySelectorAll(".nav a").forEach((a) => {
  a.addEventListener("click", () => {
    document.getElementById("sidebar").classList.remove("open");
  });
});
document.getElementById("menu").onclick = () => {
  document.getElementById("sidebar").classList.toggle("open");
};

const sections = [...document.querySelectorAll("main section[id]")];
const navLinks = [...document.querySelectorAll(".nav a")];
const spy = () => {
  const y = window.scrollY + 90;
  let current = sections[0]?.id;
  sections.forEach((sec) => {
    if (sec.offsetTop <= y) current = sec.id;
  });
  navLinks.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === "#" + current));
};
window.addEventListener("scroll", spy, { passive: true });

const CHECKS_KEY = "brickforge-handbook-v1";
function bindChecks() {
  const box = document.getElementById("checklist");
  const saved = JSON.parse(localStorage.getItem(CHECKS_KEY) || "{}");
  box.querySelectorAll("input[type=checkbox]").forEach((input) => {
    input.checked = Boolean(saved[input.id]);
    input.onchange = () => {
      saved[input.id] = input.checked;
      localStorage.setItem(CHECKS_KEY, JSON.stringify(saved));
    };
  });
}

renderPalette();
renderStage();
compute();
bindChecks();
spy();
