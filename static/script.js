let currentTreeId = null;
let currentHeapType = null;

// ==========================
//       CREATE TREE
// ==========================
async function createTree(heapType) {
  try {
    const response = await fetch("/tp2/create_tree", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ heap_type: heapType }),
    });

    if (!response.ok) {
      const text = await response.text();
      console.error("Erreur HTTP:", response.status, text);
      showMessage("Erreur lors de la création de l'arbre", "error");
      return;
    }

    const data = await response.json();

    if (data.success) {
      currentTreeId = data.tree_id;
      currentHeapType = heapType;

      document.getElementById("welcome-screen").style.display = "none";
      document.getElementById("main-screen").style.display = "block";

      const badge = document.getElementById("heap-type-badge");
      badge.textContent = heapType + " Heap";
      badge.className = `badge ${heapType.toLowerCase()}`;

      showMessage(`Arbre ${heapType} Heap créé avec succès!`, "success");
      refreshVisualization();
    }
  } catch (error) {
    showMessage("Erreur lors de la création de l'arbre", "error");
    console.error(error);
  }
}

// ==========================
//       INSERT NODE
// ==========================
async function insertNode() {
  const key = document.getElementById("insert-key").value;
  const priority = document.getElementById("insert-priority").value;

  if (!key || !priority) {
    showMessage("Veuillez remplir tous les champs", "error");
    return;
  }

  try {
    const response = await fetch("/tp2/insert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tree_id: currentTreeId, key, priority }),
    });

    if (!response.ok) {
      const text = await response.text();
      console.error("Erreur HTTP:", response.status, text);
      showMessage("Erreur lors de l'insertion", "error");
      return;
    }

    const data = await response.json();

    if (data.success) {
      showMessage(data.message || "Nœud inséré avec succès", "success");
      document.getElementById("insert-key").value = "";
      document.getElementById("insert-priority").value = "";
      refreshVisualization();
    } else {
      showMessage(data.error || "Erreur lors de l'insertion", "error");
    }
  } catch (error) {
    showMessage("Erreur lors de l'insertion", "error");
    console.error(error);
  }
}

// ==========================
//       SEARCH NODE
// ==========================
async function searchNode() {
  const key = document.getElementById("search-key").value;

  if (!key) {
    showMessage("Veuillez entrer une clé", "error");
    return;
  }

  try {
    const response = await fetch("/tp2/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tree_id: currentTreeId, key }),
    });

    if (!response.ok) {
      const text = await response.text();
      console.error("Erreur HTTP:", response.status, text);
      showMessage("Erreur lors de la recherche", "error");
      return;
    }

    const data = await response.json();

    if (data.success) {
      if (data.found) {
        showMessage(`Clé ${key} trouvée avec priorité ${data.priority || "N/A"}`, "info");
      } else {
        showMessage(`Clé ${key} non trouvée`, "error");
      }
      document.getElementById("search-key").value = "";
    } else {
      showMessage(data.error || "Erreur lors de la recherche", "error");
    }
  } catch (error) {
    showMessage("Erreur lors de la recherche", "error");
    console.error(error);
  }
}

// ==========================
//       DELETE NODE
// ==========================
async function deleteNode() {
  const key = document.getElementById("delete-key").value;

  if (!key) {
    showMessage("Veuillez entrer une clé", "error");
    return;
  }

  try {
    const response = await fetch("/tp2/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tree_id: currentTreeId, key }),
    });

    if (!response.ok) {
      const text = await response.text();
      console.error("Erreur HTTP:", response.status, text);
      showMessage("Erreur lors de la suppression", "error");
      return;
    }

    const data = await response.json();

    if (data.success) {
      showMessage(data.message || "Nœud supprimé avec succès", "success");
      document.getElementById("delete-key").value = "";
      refreshVisualization();
    } else {
      showMessage(data.error || "Erreur lors de la suppression", "error");
    }
  } catch (error) {
    showMessage("Erreur lors de la suppression", "error");
    console.error(error);
  }
}

// ==========================
//       REFRESH VISUALIZATION
// ==========================
async function refreshVisualization() {
  if (!currentTreeId) return;

  try {
    const response = await fetch(`/tp2/tree_data/${currentTreeId}`);
    if (!response.ok) {
      const text = await response.text();
      console.error("Erreur HTTP:", response.status, text);
      return;
    }

    const data = await response.json();
    const treeData = data.data || { size: 0, height: 0, operations: [] };

    document.getElementById("stat-nodes").textContent = treeData.size || 0;
    document.getElementById("stat-height").textContent = treeData.height || 0;

    updateOperationsList(treeData.operations || []);

    if (treeData.size > 0) {
      loadVisualization();
    } else {
      document.getElementById("tree-image").style.display = "none";
      document.getElementById("empty-state").style.display = "block";
    }
  } catch (error) {
    console.error("Erreur lors du rafraîchissement", error);
  }
}

// ==========================
//       LOAD VISUALIZATION
// ==========================
async function loadVisualization() {
  if (!currentTreeId) return;

  try {
    const response = await fetch(`/tp2/visualization/${currentTreeId}`);
    if (!response.ok) {
      const text = await response.text();
      console.error("Erreur HTTP:", response.status, text);
      return;
    }

    const data = await response.json();

    if (data.success) {
      const img = document.getElementById("tree-image");
      img.src = "data:image/png;base64," + data.image;  // Correction ici
      img.style.display = "block";
      document.getElementById("empty-state").style.display = "none";
    }
  } catch (error) {
    console.error("Erreur lors du chargement de la visualisation", error);
  }
}

// ==========================
//       UPDATE OPERATIONS LIST
// ==========================
function updateOperationsList(operations) {
  const list = document.getElementById("operations-list");
  list.innerHTML = "";

  operations.reverse().forEach((op) => {
    const item = document.createElement("div");
    item.className = `operation-item ${op.type}`;

    let text = "";
    if (op.type === "insert") {
      text = `➕ Inséré: clé=${op.key}, priorité=${op.priority}`;
    } else if (op.type === "delete") {
      text = `➖ Supprimé: clé=${op.key}`;
    } else if (op.type === "search") {
      text = `🔍 Recherche: clé=${op.key} ${op.found ? "✓" : "✗"}`;
    }

    item.textContent = text;
    list.appendChild(item);
  });
}

// ==========================
//       SHOW MESSAGE
// ==========================
function showMessage(message, type) {
  const messageBox = document.getElementById("message-box");
  messageBox.textContent = message;
  messageBox.className = `message-box ${type}`;

  setTimeout(() => {
    messageBox.className = "message-box";
  }, 3000);
}

// ==========================
//       RESET TREE
// ==========================
function resetTree() {
  if (confirm("Êtes-vous sûr de vouloir réinitialiser l'arbre?")) {
    document.getElementById("welcome-screen").style.display = "flex";
    document.getElementById("main-screen").style.display = "none";
    currentTreeId = null;
    currentHeapType = null;
  }
}