// === Rafraîchir la carte ===
function refreshMap() {
  const iframe = document.getElementById("mapFrame");
  if (iframe) iframe.src = iframe.src;
}

// === Créer ou mettre à jour le formulaire ===
function renderForm() {
  const container = document.getElementById("enclosFormContainer");
  container.className = "mt-6 p-3 bg-white rounded-xl shadow-lg animate-fade-in max-w-[300px] relative";
  container.innerHTML = `
    <button id="closeFormBtn" class="absolute top-2 right-2 text-gray-500 hover:text-gray-800 font-bold">&times;</button>
    <h2 class="text-md font-semibold text-gray-800 mb-2">Créer / Modifier un enclos</h2>
    <form id="enclosForm" class="flex flex-col gap-2">
      <input type="text" id="enclosName" placeholder="Nom" class="w-full p-1 text-sm border rounded-lg" required>
      <select id="enclosType" class="w-full p-1 text-sm border rounded-lg">
        <option value="activité">Activité</option>
        <option value="blanc">Blanc</option>
        <option value="interdit">Interdit</option>
      </select>
      <button type="submit" class="bg-primary text-white px-2 py-1 text-sm rounded-lg hover:bg-accent transition-colors flex items-center justify-center gap-1">
        Enregistrer
      </button>
    </form>
  `;

  // Fermer le formulaire
  document.getElementById("closeFormBtn").addEventListener("click", () => {
    container.classList.add("hidden");
    window.editingEnclosId = null;
  });
}

// === Ouvrir le formulaire d’édition ===
function openEditForm(enclos) {
  renderForm();
  const nameField = document.getElementById("enclosName");
  const typeField = document.getElementById("enclosType");

  document.getElementById("enclosFormContainer").classList.remove("hidden");
  nameField.value = enclos.name;
  typeField.value = enclos.description;
  window.editingEnclosId = enclos.id;
}

// === Création ou mise à jour d’un enclos ===
document.body.addEventListener("submit", async (e) => {
  if (e.target && e.target.id === "enclosForm") {
    e.preventDefault();
    const name = document.getElementById("enclosName").value.trim();
    const description = document.getElementById("enclosType").value;
    const [latitude, longitude] = window.currentMarkerCoords || [0, 0];

    if (!name) return; // Pas d'alert

    const enclosData = { name, description, latitude, longitude };

    try {
      const method = window.editingEnclosId ? "PUT" : "POST";
      const url = window.editingEnclosId
        ? `/enclosures/${window.editingEnclosId}`
        : "/enclosures/";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(enclosData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Erreur de sauvegarde.");
      }

      document.getElementById("enclosFormContainer").classList.add("hidden");
      window.currentMarkerCoords = null;
      window.editingEnclosId = null;

      await loadEnclos();
      refreshMap();
    } catch (err) {
      console.error("Erreur :", err.message);
    }
  }
});

// === Charger la liste des enclos ===
async function loadEnclos() {
  try {
    const res = await fetch("/enclosures/");
    if (!res.ok) throw new Error("Erreur de chargement des enclos");

    const enclos = await res.json();
    const list = document.getElementById("enclosList");
    list.className = "space-y-2 max-h-[calc(100vh-200px)] overflow-y-auto pr-2";
    list.innerHTML = "";

    enclos.forEach((e) => {
      const li = document.createElement("li");
      li.className = "flex justify-between items-center p-2 border rounded-lg bg-white hover:shadow-md transition-all text-sm";
      li.innerHTML = `
        <span class="font-medium text-gray-700 truncate" title="${e.name} (${e.description || 'N/A'})">
          ${e.name} (${e.description || "N/A"})
        </span>
        <div class="flex gap-1">
          <button onclick='openEditForm(${JSON.stringify(e)})' class="bg-yellow-500 text-white p-1 rounded-lg hover:bg-yellow-600 transition" title="Modifier">✎</button>
          <button onclick='deleteEnclos(${e.id})' class="bg-danger text-white p-1 rounded-lg hover:bg-red-700 transition" title="Supprimer">×</button>
        </div>
      `;
      list.appendChild(li);
    });
  } catch (err) {
    console.error(err);
  }
}

// === Supprimer un enclos ===
async function deleteEnclos(id) {
  try {
    await fetch(`/enclosures/${id}`, { method: "DELETE" });
    await loadEnclos();
    refreshMap();
  } catch (err) {
    console.error("Erreur :", err.message);
  }
}

// === Initialisation ===
renderForm(); // Formulaire visible au chargement
loadEnclos();
