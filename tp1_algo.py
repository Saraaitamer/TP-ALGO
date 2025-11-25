import networkx as nx
import heapq

# ============================
#        ARBRES
# ============================

class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

# --- 1️⃣ ABR ---
def construire_abr(valeurs):
    if not valeurs:
        return None
    root = Node(valeurs[0])
    for v in valeurs[1:]:
        insert_abr(root, v)
    return root

def insert_abr(root, val):
    if val < root.val:
        if root.left is None:
            root.left = Node(val)
        else:
            insert_abr(root.left, val)
    else:
        if root.right is None:
            root.right = Node(val)
        else:
            insert_abr(root.right, val)


# --- 2️⃣ AVL ---
class AVLNode(Node):
    def __init__(self, val):
        super().__init__(val)
        self.height = 1

def get_height(node):
    return node.height if node else 0

def update_height(node):
    node.height = 1 + max(get_height(node.left), get_height(node.right))

def get_balance(node):
    return get_height(node.left) - get_height(node.right) if node else 0

def rotate_right(y):
    x = y.left
    T2 = x.right
    x.right = y
    y.left = T2
    update_height(y)
    update_height(x)
    return x

def rotate_left(x):
    y = x.right
    T2 = y.left
    y.left = x
    x.right = T2
    update_height(x)
    update_height(y)
    return y

def insert_avl(root, val):
    if not root:
        return AVLNode(val)
    if val < root.val:
        root.left = insert_avl(root.left, val)
    else:
        root.right = insert_avl(root.right, val)
    update_height(root)
    balance = get_balance(root)
    if balance > 1 and val < root.left.val:
        return rotate_right(root)
    if balance < -1 and val > root.right.val:
        return rotate_left(root)
    if balance > 1 and val > root.left.val:
        root.left = rotate_left(root.left)
        return rotate_right(root)
    if balance < -1 and val < root.right.val:
        root.right = rotate_right(root.right)
        return rotate_left(root)
    return root

def construire_avl(valeurs):
    root = None
    for v in valeurs:
        root = insert_avl(root, v)
    return root


# --- 3️⃣ TAS ---
def construire_tas(valeurs, type_tas="min"):
    if type_tas == "min":
        h = valeurs[:]
        heapq.heapify(h)
        return h
    elif type_tas == "max":
        h = [-v for v in valeurs]
        heapq.heapify(h)
        return [-v for v in h]
    else:
        raise ValueError("Type de tas invalide : choisissez 'min' ou 'max'.")


# --- 4️⃣ AMR ---
class AMRNode:
    def __init__(self, val):
        self.val = val
        self.children = []

def construire_amr(valeurs, nb_racines=2):
    if not valeurs:
        return []
    racines = [AMRNode(valeurs[i]) for i in range(min(nb_racines, len(valeurs)))]
    index = nb_racines
    for root in racines:
        for _ in range(2):
            if index < len(valeurs):
                enfant = AMRNode(valeurs[index])
                root.children.append(enfant)
                index += 1
    return racines


# --- 5️⃣ B-ARBRE ---
class BTreeNode:
    def __init__(self, t):
        self.keys = []
        self.children = []
        self.leaf = True
        self.t = t

def insert_btree(node, key):
    node.keys.append(key)
    node.keys.sort()

def construire_btree(valeurs, t=2):
    if t < 2:
        raise ValueError("L'ordre d'un B-arbre doit être >= 2.")
    root = BTreeNode(t)
    for v in valeurs:
        insert_btree(root, v)
    return root


# --- HAUTEUR ---
def hauteur_arbre(root):
    if not root:
        return 0
    if isinstance(root, list):
        return 1 + max((hauteur_arbre(r) for r in root), default=0)
    if hasattr(root, 'children'):
        return 1 + max((hauteur_arbre(c) for c in root.children), default=0)
    return 1 + max(hauteur_arbre(root.left), hauteur_arbre(root.right))


# --- CONVERSION EN GRAPH ---
def arbre_to_nx(root):
    G = nx.Graph()
    def add_edges(node):
        if not node:
            return
        if hasattr(node, 'children'):
            for c in node.children:
                G.add_edge(node.val, c.val)
                add_edges(c)
        else:
            if hasattr(node, 'left') and node.left:
                G.add_edge(node.val, node.left.val)
                add_edges(node.left)
            if hasattr(node, 'right') and node.right:
                G.add_edge(node.val, node.right.val)
                add_edges(node.right)
    if isinstance(root, list):
        for r in root:
            add_edges(r)
    else:
        add_edges(root)
    return G


# --- GRAPHE ---
def construire_graphe(valeurs, oriente=False, pondere=False):
    G = nx.DiGraph() if oriente else nx.Graph()
    for v in valeurs:
        G.add_node(v)
    for i in range(len(valeurs) - 1):
        if pondere:
            G.add_edge(valeurs[i], valeurs[i + 1], weight=(i + 1) * 10)
        else:
            G.add_edge(valeurs[i], valeurs[i + 1])
    return G


# --- DENSITÉ ---
def densite_graphe(G):
    return nx.density(G)
