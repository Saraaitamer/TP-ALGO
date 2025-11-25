import random, math, time, io, base64
from treap import Treap
import networkx as nx
import matplotlib.pyplot as plt

plt.switch_backend('Agg')

# ---------- Fonctions utilitaires ----------
def parse_keys(values_str):
    return [int(v.strip()) for v in values_str.split(",") if v.strip()]

def parse_priorities(priorities_str):
    return [float(p.strip()) for p in priorities_str.split(",") if p.strip()]

def compute_theory(n):
    log_n = round(math.log2(n), 2) if n > 1 else 1
    return {
        "insertion": "O(log n)", "insertion_val": log_n,
        "suppression": "O(log n)", "suppression_val": log_n,
        "tri": "O(n log n)", "tri_val": round(n * log_n, 2),
        "recherche": "O(log n)", "recherche_val": log_n
    }

# ---------- Visualisation ----------
def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    if not nx.is_tree(G):
        return nx.spring_layout(G)
    if root is None:
        root = next(iter(G.nodes))
    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5,
                       pos=None, parent=None):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        neighbors = [n for n in G.neighbors(root) if n != parent]
        if neighbors:
            dx = width / len(neighbors)
            nextx = xcenter - width/2 - dx/2
            for neighbor in neighbors:
                nextx += dx
                pos[neighbor] = (nextx, vert_loc - vert_gap)
                pos = _hierarchy_pos(G, neighbor, width=dx, vert_gap=vert_gap,
                                     vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                     pos=pos, parent=root)
        return pos
    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

def treap_to_base64(treap, title=None):
    plt.figure(figsize=(8,6))
    if not treap.root:
        plt.text(0.5, 0.5, "Arbre vide", fontsize=20, ha='center')
        plt.axis('off')
    else:
        G = nx.DiGraph()
        def add_edges(node):
            if not node:
                return
            G.add_node(f"{node.key}\n(p={round(node.priority,3)})")
            if node.left:
                G.add_edge(f"{node.key}\n(p={round(node.priority,3)})",
                           f"{node.left.key}\n(p={round(node.left.priority,3)})")
                add_edges(node.left)
            if node.right:
                G.add_edge(f"{node.key}\n(p={round(node.priority,3)})",
                           f"{node.right.key}\n(p={round(node.right.priority,3)})")
                add_edges(node.right)
        add_edges(treap.root)
        root_label = next(iter(G.nodes))
        pos = hierarchy_pos(G, root=root_label)
        nx.draw(G, pos, with_labels=True, node_size=900, node_color="white", edgecolors="black")
    if title:
        plt.title(title)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("ascii")
    plt.close()
    return img_base64

# ---------- Construction du Treap ----------
def build_treap(keys, priority_mode, priorities_in, heap_type):
    treap = Treap(heap_type.upper())
    if priority_mode == "manual":
        for i, k in enumerate(keys):
            p = priorities_in[i] if i < len(priorities_in) else random.random()
            treap.insert(k, p)
    else:
        for k in keys:
            treap.insert(k, random.random())
    return treap

def treap_sort_with_steps(treap):
    steps = []
    steps.append({"label": "Avant suppression", "img": treap_to_base64(treap)})
    sorted_keys = []
    while treap.root is not None:
        key = treap.root.key
        sorted_keys.append(key)
        treap.delete(key)
        steps.append({"label": f"Suppression clé {key}", "img": treap_to_base64(treap)})
    return sorted_keys, steps

# ---------- Fonction principale ----------
def run_tp3(values_str, method, priority_mode="auto", heap_type="max", priorities_str=""):
    keys = parse_keys(values_str)
    n = len(keys)
    priorities_in = parse_priorities(priorities_str) if priority_mode=="manual" else []

    treap = build_treap(keys, priority_mode, priorities_in, heap_type)
    start_time = time.time()

    treap.comparisons = 0  # reset compteur avant tri

    if method == "abr":
        sorted_keys = [k for (k, _) in treap.inorder()]
        steps = [{"label": "Arbre complet", "img": treap_to_base64(treap)}]
    elif method == "tas":
        sorted_keys, steps = treap_sort_with_steps(treap)
    else:
        sorted_keys, steps = [], []

    elapsed = round(time.time() - start_time, 5)
    theorique = compute_theory(n)

    return {
        "original": keys,
        "sorted": sorted_keys,
        "method": method,
        "heap_type": heap_type,
        "priority_mode": priority_mode,
        "theorique": theorique,
        "steps": steps,
        "counters": {
            "comparisons": treap.comparisons,  # Comparaisons réelles
            "deletions": len(sorted_keys) if method=="tas" else 0
        },
        "time_sec": elapsed,
        "n": n
    }
