let token = localStorage.getItem("token") || null;
let userName = localStorage.getItem("userName") || "";
let editingId = null;
let calificacionPendiente = {};

function api(path, options = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = "Bearer " + token;
  return fetch(path, { headers, ...options });
}

function showView(name) {
  document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
  document.getElementById("view-" + name).classList.add("active");
}

function showAlert(id, msg, type = "error") {
  const el = document.getElementById(id);
  if (el) el.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
}

function clearAlert(id) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = "";
}

function setLoggedIn(name) {
  token = localStorage.getItem("token");
  userName = name;
  document.getElementById("btn-show-login").style.display = "none";
  document.getElementById("btn-show-register").style.display = "none";
  document.getElementById("btn-logout").style.display = "";
  const un = document.getElementById("user-name");
  un.style.display = "";
  un.textContent = "Hola, " + name;
  showView("app");
  loadIngredientes();
  loadRecetas();
}

function logout() {
  token = null;
  localStorage.removeItem("token");
  localStorage.removeItem("userName");
  document.getElementById("btn-show-login").style.display = "";
  document.getElementById("btn-show-register").style.display = "";
  document.getElementById("btn-logout").style.display = "none";
  document.getElementById("user-name").style.display = "none";
  showView("home");
}

async function login() {
  clearAlert("login-alert");
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  if (!email || !password)
    return showAlert("login-alert", "Completa todos los campos.");
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch("/auth/login", {
    method: "POST",
    body,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  const data = await res.json();
  if (!res.ok)
    return showAlert("login-alert", data.detail || "Error al iniciar sesion.");
  localStorage.setItem("token", data.access_token);
  const name = email.split("@")[0];
  localStorage.setItem("userName", name);
  setLoggedIn(name);
}

async function register() {
  clearAlert("register-alert");
  const nombre = document.getElementById("reg-nombre").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;
  if (!nombre || !email || !password)
    return showAlert("register-alert", "Completa todos los campos.");
  if (password.length < 6)
    return showAlert("register-alert", "La contrasena debe tener al menos 6 caracteres.");
  const res = await api("/auth/registro", {
    method: "POST",
    body: JSON.stringify({ nombre, email, password }),
  });
  const data = await res.json();
  if (!res.ok)
    return showAlert("register-alert", data.detail || "Error al registrarse.");
  showAlert("register-alert", "Cuenta creada. Iniciando sesion...", "success");
  document.getElementById("login-email").value = email;
  document.getElementById("login-password").value = password;
  await new Promise((r) => setTimeout(r, 800));
  await login();
}

function toggleAddForm() {
  const f = document.getElementById("add-form");
  const isHidden = f.style.display === "none" || f.style.display === "";
  if (isHidden) {
    f.style.display = "block";
  } else {
    // Reset al cerrar
    f.style.display = "none";
    editingId = null;
    document.getElementById("ingr-nombre").value = "";
    document.getElementById("ingr-cantidad").value = "";
    document.getElementById("ingr-unidad").value = "unidades";
    document.querySelector("#add-form h2").textContent = "Nuevo ingrediente";
    document.querySelector("#add-form .btn-primary").textContent = "Guardar";
    clearAlert("ingr-alert");
  }
}

async function loadIngredientes() {
  const res = await api("/ingredientes");
  if (!res.ok) return;
  const data = await res.json();
  const list = document.getElementById("ingredientes-list");
  if (!data.length) {
    list.innerHTML = '<div class="empty-state"><p>No tienes ingredientes registrados.<br>Agrega ingredientes para poder generar recetas.</p></div>';
    return;
  }
  list.innerHTML = data.map((i) => `
    <div class="ingrediente-item" id="ingr-${i.id}">
      <div class="ingrediente-info">
        <div class="ingrediente-nombre">${i.nombre}</div>
        <div class="ingrediente-cantidad">${i.cantidad} ${i.unidad}</div>
      </div>
      <div class="ingrediente-acciones" style="display:flex;gap:0.5rem;flex-shrink:0">
        <button class="btn btn-warning btn-sm" onclick="updateIngrediente(${i.id})">Actualizar</button>
        <button class="btn btn-danger btn-sm" onclick="deleteIngrediente(${i.id})">Eliminar</button>
      </div>
    </div>
  `).join("");
}

async function addIngrediente() {
  clearAlert("ingr-alert");
  const nombre = document.getElementById("ingr-nombre").value.trim();
  const cantidad = document.getElementById("ingr-cantidad").value.trim();
  const unidad = document.getElementById("ingr-unidad").value;
  if (!nombre || !cantidad)
    return showAlert("ingr-alert", "Nombre y cantidad son obligatorios.");

  const url = editingId ? "/ingredientes/" + editingId : "/ingredientes";
  const method = editingId ? "PUT" : "POST";

  const res = await api(url, {
    method,
    body: JSON.stringify({ nombre, cantidad, unidad }),
  });
  const data = await res.json();
  if (!res.ok)
    return showAlert("ingr-alert", data.detail || "Error al guardar.");

  editingId = null;
  document.getElementById("ingr-nombre").value = "";
  document.getElementById("ingr-cantidad").value = "";
  document.getElementById("ingr-unidad").value = "unidades";
  document.querySelector("#add-form h2").textContent = "Nuevo ingrediente";
  document.querySelector("#add-form .btn-primary").textContent = "Guardar";
  toggleAddForm();
  loadIngredientes();
}

async function deleteIngrediente(id) {
  if (!confirm("Eliminar este ingrediente?")) return;
  const res = await api("/ingredientes/" + id, { method: "DELETE" });
  if (res.ok) loadIngredientes();
}

async function updateIngrediente(id) {
  const item = document.getElementById("ingr-" + id);
  const nombre = item.querySelector(".ingrediente-nombre").textContent;
  const cantidadUnidad = item.querySelector(".ingrediente-cantidad").textContent.split(" ");
  const cantidad = cantidadUnidad[0];
  const unidad = cantidadUnidad[1] || "unidades";

  document.getElementById("ingr-nombre").value = nombre;
  document.getElementById("ingr-cantidad").value = cantidad;
  document.getElementById("ingr-unidad").value = unidad;

  editingId = id;
  document.querySelector("#add-form h2").textContent = "Editar ingrediente";
  document.querySelector("#add-form .btn-primary").textContent = "Actualizar";
  document.getElementById("add-form").style.display = "block";
}

async function generarReceta() {
  const overlay = document.getElementById("loading-overlay");
  overlay.classList.add("visible");
  const btn = document.getElementById("btn-generar");
  btn.disabled = true;
  try {
    const res = await api("/recetas/generar", { method: "POST" });
    const data = await res.json();
    if (!res.ok) {
      alert(data.detail || "Error al generar receta.");
      return;
    }
    switchTab("recetas");
    loadRecetas();
  } finally {
    overlay.classList.remove("visible");
    btn.disabled = false;
  }
}

async function loadRecetas() {
  const res = await api("/recetas");
  if (!res.ok) return;
  const data = await res.json();
  const count = document.getElementById("recetas-count");
  count.textContent = data.length + (data.length === 1 ? " receta" : " recetas");
  const list = document.getElementById("recetas-list");
  if (!data.length) {
    list.innerHTML = '<div class="empty-state"><p>Aun no has generado ninguna receta.<br>Ve a tu inventario y presiona "Generar receta".</p></div>';
    return;
  }
  list.innerHTML = data.map((r) => {
    const ingredientes = JSON.parse(r.ingredientes_json);
    const pasos = JSON.parse(r.pasos_json);
    const calificacion = r.calificacion || 0;
    const bloqueado = calificacion > 0;
    return `
      <div class="receta-card" id="receta-${r.id}">
        <div class="receta-header">
          <div>
            <div class="receta-nombre">${r.nombre_plato}</div>
            <div class="receta-meta">
              <span class="badge badge-time">${r.tiempo_estimado}</span>
              <span class="badge badge-level">${r.nivel_dificultad}</span>
            </div>
          </div>
          <button class="btn btn-danger btn-sm" onclick="deleteReceta(${r.id})">Eliminar</button>
        </div>
        <div class="stars" id="stars-${r.id}">
          ${[1, 2, 3, 4, 5].map((n) => `
            <span class="star ${n <= calificacion ? "active" : ""}"
              ${!bloqueado ? `onclick="calificar(${r.id},${n})"` : ""}
              style="${bloqueado ? "cursor:default" : "cursor:pointer"}"
              title="${n} estrellas">&#9733;</span>
          `).join("")}
        </div>
        ${!bloqueado ? `<button class="btn btn-sm btn-primary" style="margin-top:0.5rem" onclick="guardarCalificacion(${r.id})">Guardar calificación</button>` : ""}
        <div class="receta-actions">
          <button class="btn btn-sm btn-secondary" onclick="toggleDetail(${r.id})">Ver detalle</button>
        </div>
        <div class="receta-detail" id="detail-${r.id}">
          <h4>Ingredientes</h4>
          <ul>${ingredientes.map((i) => `<li>${i.nombre} - ${i.cantidad} ${i.unidad || ""}</li>`).join("")}</ul>
          <h4>Preparacion</h4>
          <ol>${pasos.map((p) => `<li>${p}</li>`).join("")}</ol>
        </div>
      </div>`;
  }).join("");
}

function toggleDetail(id) {
  const el = document.getElementById("detail-" + id);
  el.classList.toggle("open");
  const btn = el.previousElementSibling.querySelector("button");
  btn.textContent = el.classList.contains("open") ? "Ocultar detalle" : "Ver detalle";
}

function calificar(recetaId, estrellas) {
  calificacionPendiente[recetaId] = estrellas;
  document.querySelectorAll(`#stars-${recetaId} .star`).forEach((s, i) => {
    s.classList.toggle("active", i < estrellas);
  });
}

async function guardarCalificacion(recetaId) {
  const estrellas = calificacionPendiente[recetaId];
  if (!estrellas) return;
  const res = await api("/recetas/" + recetaId + "/calificar", {
    method: "POST",
    body: JSON.stringify({ estrellas }),
  });
  if (res.ok) loadRecetas();
}

async function deleteReceta(id) {
  if (!confirm("Eliminar esta receta del historial?")) return;
  const res = await api("/recetas/" + id, { method: "DELETE" });
  if (res.ok) loadRecetas();
}

function switchTab(name) {
  document.querySelectorAll(".tab").forEach((t, i) => {
    t.classList.toggle("active", ["inventario", "recetas"][i] === name);
  });
  document.querySelectorAll(".tab-content").forEach((c, i) => {
    c.classList.toggle("active", ["inventario", "recetas"][i] === name);
  });
}

if (token) setLoggedIn(localStorage.getItem("userName") || "Usuario");