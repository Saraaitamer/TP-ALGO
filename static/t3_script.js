let selectedSort = null;

function chooseSort(type) {
  selectedSort = type;
  document.getElementById("welcome-screen").style.display = "none";
  document.getElementById("main-screen").style.display = "block";

  const nameMap = {
    insertion: "Tri par insertion",
    selection: "Tri par sélection",
    quick: "Tri rapide (Quick Sort)",
    merge: "Tri fusion (Merge Sort)",
  };

  document.getElementById("sort-name").innerText = "Algorithme : " + nameMap[type];
}

function startSorting() {
  if (!selectedSort) {
    alert("Veuillez d'abord choisir un algorithme de tri !");
    return;
  }

  const input = document.getElementById("numbers-input").value;
  const numbers = input.split(",").map(n => parseInt(n.trim())).filter(n => !isNaN(n));

  if (numbers.length === 0) {
    alert("Veuillez entrer des nombres valides !");
    return;
  }

  let sorted = [];

  switch (selectedSort) {
    case "insertion":
      sorted = insertionSort(numbers);
      break;
    case "selection":
      sorted = selectionSort(numbers);
      break;
    case "quick":
      sorted = quickSort(numbers);
      break;
    case "merge":
      sorted = mergeSort(numbers);
      break;
  }

  document.getElementById("result-text").innerText =
    "Résultat du tri (" + selectedSort + ") : " + sorted.join(", ");
}

function resetSorting() {
  document.getElementById("welcome-screen").style.display = "block";
  document.getElementById("main-screen").style.display = "none";
  document.getElementById("numbers-input").value = "";
  document.getElementById("result-text").innerText = "Aucun tri effectué.";
  selectedSort = null;
}

// Algorithmes simples
function insertionSort(arr) {
  let a = [...arr];
  for (let i = 1; i < a.length; i++) {
    let key = a[i];
    let j = i - 1;
    while (j >= 0 && a[j] > key) {
      a[j + 1] = a[j];
      j--;
    }
    a[j + 1] = key;
  }
  return a;
}

function selectionSort(arr) {
  let a = [...arr];
  for (let i = 0; i < a.length; i++) {
    let min = i;
    for (let j = i + 1; j < a.length; j++) {
      if (a[j] < a[min]) min = j;
    }
    [a[i], a[min]] = [a[min], a[i]];
  }
  return a;
}

function quickSort(arr) {
  if (arr.length <= 1) return arr;
  const pivot = arr[arr.length - 1];
  const left = arr.filter(x => x < pivot);
  const right = arr.filter(x => x > pivot);
  const equal = arr.filter(x => x === pivot);
  return [...quickSort(left), ...equal, ...quickSort(right)];
}

function mergeSort(arr) {
  if (arr.length <= 1) return arr;
  const mid = Math.floor(arr.length / 2);
  const left = mergeSort(arr.slice(0, mid));
  const right = mergeSort(arr.slice(mid));
  return merge(left, right);
}

function merge(left, right) {
  let result = [];
  while (left.length && right.length) {
    result.push(left[0] < right[0] ? left.shift() : right.shift());
  }
  return result.concat(left, right);
}
