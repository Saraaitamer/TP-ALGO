import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Optional, Tuple, List
import networkx as nx

class TreapNode:
    """Nœud d'un arbre Treap"""
    def __init__(self, key: int, priority: float):
        self.key = key
        self.priority = priority
        self.left: Optional[TreapNode] = None
        self.right: Optional[TreapNode] = None

class Treap:
    """Arbre Treap (Treap = Tree + Heap)
    - Propriété BST : clé(gauche) < clé(nœud) < clé(droite)
    - Propriété Heap : priorité(parent) >= priorité(enfants) pour MAX heap
                       priorité(parent) <= priorité(enfants) pour MIN heap
    """
    def __init__(self, heap_type="MAX"):
        self.root = None
        self.heap_type = heap_type.upper()
        self.comparisons = 0 
    
    def __init__(self, heap_type: str = "MAX"):
        """
        Initialise un Treap
        heap_type: "MAX" ou "MIN"
        """
        self.root: Optional[TreapNode] = None
        self.heap_type = heap_type.upper()
        if self.heap_type not in ["MAX", "MIN"]:
            raise ValueError("heap_type doit être 'MAX' ou 'MIN'")
        self.operations_log: List[str] = []
    
    def _compare_priority(self, p1: float, p2: float) -> bool:
        """Compare deux priorités selon le type de heap"""
        if self.heap_type == "MAX":
            return p1 > p2
        else:
            return p1 < p2
    
    def _rotate_right(self, node: TreapNode) -> TreapNode:
        """Rotation droite"""
        left_child = node.left
        node.left = left_child.right
        left_child.right = node
        return left_child
    
    def _rotate_left(self, node: TreapNode) -> TreapNode:
        """Rotation gauche"""
        right_child = node.right
        node.right = right_child.left
        right_child.left = node
        return right_child
    
    def insert(self, key: int, priority: float) -> bool:
        """Insère une clé avec une priorité"""
        if not (0 < priority < 1):
            raise ValueError("La priorité doit être entre 0 et 1 (exclusif)")
        
        self.root, inserted = self._insert_recursive(self.root, key, priority)
        if inserted:
            self.operations_log.append(f"✓ Insertion: clé={key}, priorité={priority:.2f}")
        else:
            self.operations_log.append(f"✗ Insertion échouée: clé={key} existe déjà")
        return inserted
    
    def _insert_recursive(self, node: Optional[TreapNode], key: int, priority: float) -> Tuple[TreapNode, bool]:
        """Insertion récursive avec rotations"""
        if node is None:
            return TreapNode(key, priority), True
        
        if key == node.key:
            return node, False  # Clé existe déjà
        
        if key < node.key:
            node.left, inserted = self._insert_recursive(node.left, key, priority)
            if inserted and node.left and self._compare_priority(node.left.priority, node.priority):
                node = self._rotate_right(node)
        else:
            node.right, inserted = self._insert_recursive(node.right, key, priority)
            if inserted and node.right and self._compare_priority(node.right.priority, node.priority):
                node = self._rotate_left(node)
        
        return node, inserted
    
    def search(self, key: int) -> Optional[float]:
        """Recherche une clé et retourne sa priorité"""
        node = self._search_recursive(self.root, key)
        if node:
            self.operations_log.append(f"✓ Recherche: clé={key} trouvée (priorité={node.priority:.2f})")
            return node.priority
        else:
            self.operations_log.append(f"✗ Recherche: clé={key} non trouvée")
            return None
    
    def _search_recursive(self, node: Optional[TreapNode], key: int) -> Optional[TreapNode]:
        """Recherche récursive"""
        if node is None:
            return None
        
        if key == node.key:
            return node
        elif key < node.key:
            return self._search_recursive(node.left, key)
        else:
            return self._search_recursive(node.right, key)
    
    def delete(self, key: int) -> bool:
        """Supprime une clé"""
        self.root, deleted = self._delete_recursive(self.root, key)
        if deleted:
            self.operations_log.append(f"✓ Suppression: clé={key}")
        else:
            self.operations_log.append(f"✗ Suppression échouée: clé={key} non trouvée")
        return deleted
    
    def _delete_recursive(self, node: Optional[TreapNode], key: int) -> Tuple[Optional[TreapNode], bool]:
        """Suppression récursive avec rotations"""
        if node is None:
            return None, False
        
        if key < node.key:
            node.left, deleted = self._delete_recursive(node.left, key)
            return node, deleted
        elif key > node.key:
            node.right, deleted = self._delete_recursive(node.right, key)
            return node, deleted
        else:
            # Nœud trouvé
            if node.left is None:
                return node.right, True
            elif node.right is None:
                return node.left, True
            else:
                # Deux enfants: rotation vers le fils avec priorité plus élevée
                if self._compare_priority(node.left.priority, node.right.priority):
                    node = self._rotate_right(node)
                    node.right, deleted = self._delete_recursive(node.right, key)
                else:
                    node = self._rotate_left(node)
                    node.left, deleted = self._delete_recursive(node.left, key)
                return node, deleted
    
    def inorder(self) -> List[Tuple[int, float]]:
        """Parcours en ordre (BST)"""
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node: Optional[TreapNode], result: List):
        """Parcours en ordre récursif"""
        if node:
            self._inorder_recursive(node.left, result)
            result.append((node.key, node.priority))
            self._inorder_recursive(node.right, result)
    
    def visualize(self):
        """Visualise l'arbre avec matplotlib et networkx"""
        if self.root is None:
            print("L'arbre est vide!")
            return
        
        # Créer un graphe networkx
        G = nx.DiGraph()
        pos = {}
        
        # Ajouter les nœuds et arêtes
        self._add_nodes_to_graph(self.root, G, pos, x=0, y=0, layer=1)
        
        # Créer la figure
        plt.figure(figsize=(14, 10))
        
        # Dessiner le graphe
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, 
                              arrowsize=20, arrowstyle='->', width=2)
        
        # Dessiner les nœuds
        node_colors = []
        for node in G.nodes():
            node_colors.append('#3498db')  # Bleu
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=1500, node_shape='o')
        
        # Dessiner les labels (clé et priorité)
        labels = {}
        for node in G.nodes():
            key, priority = node
            labels[node] = f"{key}\n({priority:.2f})"
        
        nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold')
        
        plt.title(f"Arbre Treap ({self.heap_type} Heap)", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def _add_nodes_to_graph(self, node: Optional[TreapNode], G: nx.DiGraph, 
                           pos: dict, x: float, y: float, layer: int):
        """Ajoute les nœuds au graphe networkx"""
        if node is None:
            return
        
        node_id = (node.key, node.priority)
        G.add_node(node_id)
        pos[node_id] = (x, -y)
        
        offset = 2 ** (5 - layer)
        
        if node.left:
            left_id = (node.left.key, node.left.priority)
            G.add_edge(node_id, left_id)
            self._add_nodes_to_graph(node.left, G, pos, x - offset, y + 1, layer + 1)
        
        if node.right:
            right_id = (node.right.key, node.right.priority)
            G.add_edge(node_id, right_id)
            self._add_nodes_to_graph(node.right, G, pos, x + offset, y + 1, layer + 1)
    
    def print_tree(self):
        """Affiche l'arbre en format texte"""
        if self.root is None:
            print("L'arbre est vide!")
            return
        
        print("\n" + "="*50)
        print(f"Arbre Treap ({self.heap_type} Heap)")
        print("="*50)
        self._print_tree_recursive(self.root, "", True)
        print("="*50 + "\n")
    
    def _print_tree_recursive(self, node: Optional[TreapNode], prefix: str, is_tail: bool):
        """Affiche l'arbre récursivement"""
        if node is None:
            return
        
        print(prefix + ("└── " if is_tail else "├── ") + 
              f"[clé={node.key}, priorité={node.priority:.2f}]")
        
        children = []
        if node.left:
            children.append((node.left, False))
        if node.right:
            children.append((node.right, True))
        
        for i, (child, is_last) in enumerate(children):
            extension = "    " if is_tail else "│   "
            self._print_tree_recursive(child, prefix + extension, is_last)
    
    def print_operations_log(self):
        """Affiche l'historique des opérations"""
        print("\n" + "="*50)
        print("Historique des opérations")
        print("="*50)
        for i, op in enumerate(self.operations_log, 1):
            print(f"{i}. {op}")
        print("="*50 + "\n")
    
    def get_stats(self) -> dict:
        """Retourne les statistiques de l'arbre"""
        return {
            "type_heap": self.heap_type,
            "nombre_noeuds": self._count_nodes(self.root),
            "hauteur": self._get_height(self.root),
            "elements": self.inorder()
        }
    
    def _count_nodes(self, node: Optional[TreapNode]) -> int:
        """Compte le nombre de nœuds"""
        if node is None:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)
    
    def _get_height(self, node: Optional[TreapNode]) -> int:
        """Calcule la hauteur de l'arbre"""
        if node is None:
            return 0
        return 1 + max(self._get_height(node.left), self._get_height(node.right))


def main():
    """Fonction principale avec interface interactive"""
    print("\n" + "="*60)
    print("VISUALISEUR D'ARBRE TREAP (Treap = Tree + Heap)")
    print("="*60)
    
    # Choix du type de heap
    while True:
        heap_choice = input("\nChoisissez le type de heap:\n1. MAX Heap (priorité élevée = racine)\n2. MIN Heap (priorité basse = racine)\nVotre choix (1 ou 2): ").strip()
        if heap_choice in ["1", "2"]:
            heap_type = "MAX" if heap_choice == "1" else "MIN"
            break
        print("Choix invalide! Entrez 1 ou 2.")
    
    treap = Treap(heap_type)
    print(f"\nArbre Treap créé avec {heap_type} Heap")
    
    while True:
        print("\n" + "-"*60)
        print("MENU PRINCIPAL")
        print("-"*60)
        print("1. Insérer un nœud (clé, priorité)")
        print("2. Rechercher une clé")
        print("3. Supprimer une clé")
        print("4. Afficher l'arbre (texte)")
        print("5. Visualiser l'arbre (graphique)")
        print("6. Afficher les statistiques")
        print("7. Afficher l'historique des opérations")
        print("8. Parcours en ordre (BST)")
        print("9. Quitter")
        print("-"*60)
        
        choice = input("Votre choix: ").strip()
        
        if choice == "1":
            try:
                key = int(input("Entrez la clé (entier): "))
                priority = float(input("Entrez la priorité (entre 0 et 1): "))
                treap.insert(key, priority)
                print("✓ Nœud inséré avec succès!")
            except ValueError as e:
                print(f"✗ Erreur: {e}")
        
        elif choice == "2":
            try:
                key = int(input("Entrez la clé à rechercher: "))
                result = treap.search(key)
                if result is not None:
                    print(f"✓ Clé trouvée avec priorité: {result:.2f}")
                else:
                    print("✗ Clé non trouvée")
            except ValueError:
                print("✗ Erreur: Entrez un entier valide")
        
        elif choice == "3":
            try:
                key = int(input("Entrez la clé à supprimer: "))
                treap.delete(key)
            except ValueError:
                print("✗ Erreur: Entrez un entier valide")
        
        elif choice == "4":
            treap.print_tree()
        
        elif choice == "5":
            try:
                treap.visualize()
            except Exception as e:
                print(f"✗ Erreur lors de la visualisation: {e}")
        
        elif choice == "6":
            stats = treap.get_stats()
            print("\n" + "="*50)
            print("STATISTIQUES DE L'ARBRE")
            print("="*50)
            print(f"Type de heap: {stats['type_heap']}")
            print(f"Nombre de nœuds: {stats['nombre_noeuds']}")
            print(f"Hauteur: {stats['hauteur']}")
            print(f"Éléments (en ordre): {stats['elements']}")
            print("="*50 + "\n")
        
        elif choice == "7":
            treap.print_operations_log()
        
        elif choice == "8":
            elements = treap.inorder()
            if elements:
                print("\nParcours en ordre (BST):")
                print([f"({k}, {p:.2f})" for k, p in elements])
            else:
                print("L'arbre est vide!")
        
        elif choice == "9":
            print("\nAu revoir!")
            break
        
        else:
            print("✗ Choix invalide! Entrez un numéro entre 1 et 9.")


if __name__ == "__main__":
    main() 