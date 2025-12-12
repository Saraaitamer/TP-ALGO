
#       APP TP1 + TP2 + TP3

from flask import Flask, render_template, request
import networkx as nx
import matplotlib.pyplot as plt
import io, base64, uuid, json

from tp1_algo import (
    construire_abr, construire_avl, construire_tas, construire_amr, construire_btree,
    arbre_to_nx, hauteur_arbre,
    construire_graphe, densite_graphe
)

from treap import Treap  

plt.switch_backend('Agg')

app = Flask(__name__)


#   Position hiérarchique

def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    if not nx.is_tree(G):
        return nx.spring_layout(G)
    if root is None:
        root = next(iter(G.nodes))
    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5,
                       pos=None, parent=None, parsed=None):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        if parsed is None:
            parsed = set()
        parsed.add(root)
        neighbors = [n for n in G.neighbors(root) if n != parent]
        if len(neighbors) != 0:
            dx = width / len(neighbors)
            nextx = xcenter - width/2 - dx/2
            for neighbor in neighbors:
                nextx += dx
                pos[neighbor] = (nextx, vert_loc - vert_gap)
                pos = _hierarchy_pos(G, neighbor, width=dx, vert_gap=vert_gap,
                                     vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                     pos=pos, parent=root, parsed=parsed)
        return pos
    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


#   Dessin graphe / arbre

def graphe_to_base64(G, figsize=(8, 6), title=None):
    plt.figure(figsize=figsize)
    try:
        if nx.is_tree(G):
            root = next(iter(G.nodes))
            pos = hierarchy_pos(G, root=root, width=1.0, vert_gap=0.18, vert_loc=1.0, xcenter=0.5)
        else:
            pos = nx.spring_layout(G)
    except Exception:
        pos = nx.spring_layout(G)

    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='white', edgecolors='black', linewidths=1)
    nx.draw_networkx_labels(G, pos, font_size=10)
    nx.draw_networkx_edges(G, pos)

    if nx.is_weighted(G):
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=8)

    if title:
        plt.title(title)
    plt.axis('off')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('ascii')
    plt.close()
    return img_base64


#           ROUTES


@app.route('/')
def index():
    return render_template('index.html', title="Accueil")

# ---------- TP1 ----------
@app.route('/tp1', methods=['GET', 'POST'])
def tp1():
    resultats = {}
    if request.method == 'POST':
        choix = request.form.getlist('choix')
        valeurs_arbre_str = request.form.get('valeurs_arbre', '')
        valeurs_graphe_str = request.form.get('valeurs_graphe', '')

        valeurs_arbre = [int(v.strip()) for v in valeurs_arbre_str.split(',') if v.strip().lstrip('-').isdigit()]
        valeurs_graphe = [v.strip() for v in valeurs_graphe_str.split(',') if v.strip()]

        # --- ARBRE ---
        if 'arbre' in choix and valeurs_arbre:
            type_arbre = request.form.get('type_arbre', 'ABR')

            if type_arbre == 'Tas':
                type_tas = request.form.get('type_tas', 'min')
                heap = construire_tas(valeurs_arbre, type_tas)
                G = nx.Graph()
                n = len(heap)
                for i in range(n):
                    G.add_node(str(heap[i]))
                for i in range(n):
                    left = 2*i+1
                    right = 2*i+2
                    if left < n:
                        G.add_edge(str(heap[i]), str(heap[left]))
                    if right < n:
                        G.add_edge(str(heap[i]), str(heap[right]))
                resultats['arbre_img'] = graphe_to_base64(G)
                resultats['arbre_hauteur'] = n.bit_length() if n > 0 else 0
                degres = dict(G.degree()).values()
                resultats['arbre_degre'] = max(degres) if degres else 0
                resultats['arbre_densite'] = nx.density(G)
            else:
                if type_arbre == 'ABR':
                    root = construire_abr(valeurs_arbre)
                elif type_arbre == 'AVL':
                    root = construire_avl(valeurs_arbre)
                elif type_arbre == 'AMR':
                    nb_racines = request.form.get('nb_racines')
                    try:
                        nb_racines = int(nb_racines) if nb_racines else 2
                    except:
                        nb_racines = 2
                    root = construire_amr(valeurs_arbre, nb_racines=nb_racines)
                elif type_arbre == 'B-arbre':
                    t = request.form.get('bordre')
                    try:
                        t = int(t) if t else 2
                    except:
                        t = 2
                    root = construire_btree(valeurs_arbre, t=t)
                else:
                    root = construire_abr(valeurs_arbre)

                if isinstance(root, list):
                    G_arbre = nx.Graph()
                    super_root = f"ROOT_{uuid.uuid4().hex[:6]}"
                    for r in root:
                        G_temp = arbre_to_nx(r)
                        G_arbre = nx.compose(G_arbre, G_temp)
                        G_arbre.add_node(super_root)
                        G_arbre.add_edge(super_root, r.val)
                    resultats['arbre_img'] = graphe_to_base64(G_arbre, title="AMR")
                    resultats['arbre_hauteur'] = hauteur_arbre(root)
                    degres = dict(G_arbre.degree()).values()
                    resultats['arbre_degre'] = max(degres) if degres else 0
                    resultats['arbre_densite'] = nx.density(G_arbre)
                else:
                    G_arbre = arbre_to_nx(root)
                    resultats['arbre_img'] = graphe_to_base64(G_arbre)
                    resultats['arbre_hauteur'] = hauteur_arbre(root)
                    degres = dict(G_arbre.degree()).values()
                    resultats['arbre_degre'] = max(degres) if degres else 0
                    resultats['arbre_densite'] = nx.density(G_arbre)

        # --- GRAPHE ---
        if 'graphe' in choix and valeurs_graphe:
            oriente = request.form.get('oriente') in ['on','true']
            pondere = request.form.get('pondere') in ['on','true']
            G_graph = construire_graphe(valeurs_graphe, oriente, pondere)
            resultats['graphe_img'] = graphe_to_base64(G_graph)
            degres = dict(G_graph.degree()).values()
            resultats['graphe_degre'] = max(degres) if degres else 0
            resultats['graphe_densite'] = densite_graphe(G_graph) if G_graph.number_of_nodes() > 0 else 0

    return render_template('tp1.html', resultats=resultats)

# ---------- TP2 ----------
class TreapManager:
    def __init__(self):
        self.trees = {}

    def create_tree(self, heap_type='MAX'):
        tree_id = str(uuid.uuid4())
        self.trees[tree_id] = Treap(heap_type)
        return tree_id

    def insert(self, tree_id, key, priority):
        tree = self.trees.get(tree_id)
        if not tree:
            return {"success": False, "error": "Arbre non trouvé"}
        try:
            tree.insert(int(key), float(priority))
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": True}

    def search(self, tree_id, key):
        tree = self.trees.get(tree_id)
        if not tree:
            return {"success": False, "error": "Arbre non trouvé"}
        found = tree.search(int(key))
        return {"success": True, "found": found is not None}

    def delete(self, tree_id, key):
        tree = self.trees.get(tree_id)
        if not tree:
            return {"success": False, "error": "Arbre non trouvé"}
        deleted = tree.delete(int(key))
        return {"success": True, "deleted": deleted}

    def get_tree_data(self, tree_id):
        tree = self.trees.get(tree_id)
        if not tree:
            return {"size": 0, "height": 0, "operations": []}
        stats = tree.get_stats()
        return {"size": stats['nombre_noeuds'], "height": stats['hauteur'], "operations": tree.operations_log}

    def get_visualization(self, tree_id):
        tree = self.trees.get(tree_id)
        if not tree or not tree.root:
            return None
        G = nx.DiGraph()
        def add_edges(node):
            if not node:
                return
            G.add_node(str(node.key))
            if node.left:
                G.add_node(str(node.left.key))
                G.add_edge(str(node.key), str(node.left.key))
                add_edges(node.left)
            if node.right:
                G.add_node(str(node.right.key))
                G.add_edge(str(node.key), str(node.right.key))
                add_edges(node.right)
        add_edges(tree.root)
        return graphe_to_base64(G)

manager = TreapManager()

@app.route('/tp2')
def tp2_index():
    return render_template('tp2.html')

@app.route('/tp2/create_tree', methods=['POST'])
def tp2_create_tree():
    data = request.json or {}
    heap_type = data.get('heap_type', 'MAX').upper()
    tree_id = manager.create_tree(heap_type)
    return json.dumps({'success': True, 'tree_id': tree_id})

@app.route('/tp2/insert', methods=['POST'])
def tp2_insert():
    data = request.json or {}
    tree_id = data.get('tree_id')
    key = data.get('key')
    priority = data.get('priority')
    return json.dumps(manager.insert(tree_id, key, priority))

@app.route('/tp2/search', methods=['POST'])
def tp2_search():
    data = request.json or {}
    tree_id = data.get('tree_id')
    key = data.get('key')
    return json.dumps(manager.search(tree_id, key))

@app.route('/tp2/delete', methods=['POST'])
def tp2_delete():
    data = request.json or {}
    tree_id = data.get('tree_id')
    key = data.get('key')
    return json.dumps(manager.delete(tree_id, key))

@app.route('/tp2/tree_data/<tree_id>')
def tp2_tree_data(tree_id):
    data = manager.get_tree_data(tree_id)
    return json.dumps({'success': True, 'data': data})

@app.route('/tp2/visualization/<tree_id>')
def tp2_visualization(tree_id):
    image = manager.get_visualization(tree_id)
    if not image:
        return json.dumps({'success': False, 'error': 'Impossible de générer la visualisation'})
    return json.dumps({'success': True, 'image': image})

# ---------- TP3 : Insertion, Suppression, Tri ----------

from flask import Flask, render_template, request
from treap import Treap
from tp3 import run_tp3

@app.route("/tp3", methods=["GET", "POST"])
def tp3_index():
    resultats = None
    if request.method == "POST":
        values_str = request.form.get("values", "")
        method = request.form.get("method")              
        priority_mode = request.form.get("priority_mode", "auto")  
        heap_type = request.form.get("heap_type", "max").lower()   
        priorities_str = request.form.get("priorities", "")

        resultats = run_tp3(values_str, method, priority_mode, heap_type, priorities_str)

    return render_template("tp3.html", resultats=resultats)


if __name__ == "__main__":
    app.run(debug=True)

