"""Reseaux de Petri : franchissement, graphe de marquage, proprietes (borne, sauf, blocage, quasi-vivant,
vivant, reinitialisable), graphe de couverture (Karp et Miller, avec omega), matrice d'incidence, equation
d'etat, invariants de places et de transitions (algorithme de Farkas).

Tout est fait comme sur une copie : les marquages sont decouverts en largeur, transitions dans l'ordre de
l'enonce, et numerotes M0, M1, M2... dans l'ordre ou on les ecrit.
"""
from collections import deque
from dataclasses import dataclass
from itertools import product
from math import gcd

OMEGA = float("inf")   # le omega du graphe de couverture : "autant de jetons qu'on veut"


@dataclass(frozen=True)
class Reseau:
    places: tuple        # dans l'ordre de l'enonce
    transitions: tuple   # dans l'ordre de l'enonce
    pre: dict            # (place, transition) -> poids de l'arc place -> transition
    post: dict           # (place, transition) -> poids de l'arc transition -> place

    def poids_pre(self, p, t):
        return self.pre.get((p, t), 0)

    def poids_post(self, p, t):
        return self.post.get((p, t), 0)


def reseau(places, arcs):
    """`arcs` : {transition: (entrees, sorties)}, chaque cote etant {place: poids}. Une place absente pese 0."""
    places = tuple(places)
    if not places or not arcs:
        raise ValueError("un reseau a au moins une place et une transition")
    if len(set(places)) != len(places):
        raise ValueError("deux places portent le meme nom")
    pre, post = {}, {}
    for t, (entrees, sorties) in arcs.items():
        if t in places:
            raise ValueError(f"{t!r} est a la fois une place et une transition")
        for cote, dico in ((entrees, pre), (sorties, post)):
            for p, w in cote.items():
                if p not in places:
                    raise ValueError(f"place inconnue {p!r} sur la transition {t!r}")
                if not (isinstance(w, int) and not isinstance(w, bool) and w >= 1):
                    raise ValueError(f"poids {w!r} invalide sur {p!r} - {t!r} : entier >= 1")
                dico[(p, t)] = w
    return Reseau(places, tuple(arcs), pre, post)


def marquage(R, **jetons):
    """Un marquage est un tuple de jetons, dans l'ordre des places."""
    for p, n in jetons.items():
        if p not in R.places:
            raise ValueError(f"place inconnue {p!r}")
        if not (isinstance(n, int) and not isinstance(n, bool) and n >= 0):
            raise ValueError(f"{p} : un nombre de jetons est un entier >= 0")
    return tuple(jetons.get(p, 0) for p in R.places)


def ecrire(R, M):
    """Un marquage lisible : seulement les places marquees ; un jeton = le nom seul, omega = w."""
    parts = []
    for p, n in zip(R.places, M):
        if n == OMEGA:
            parts.append(f"{p}=w")
        elif n == 1:
            parts.append(p)
        elif n:
            parts.append(f"{p}={n}")
    return "(" + ", ".join(parts) + ")" if parts else "(vide)"


# --- Franchissement --------------------------------------------------------------------------------------

def _verifier_transition(R, t):
    # sans ce controle, une faute de frappe serait une transition sans arc : toujours franchissable, sans effet
    if t not in R.transitions:
        raise ValueError(f"transition inconnue {t!r} (transitions : {', '.join(R.transitions)})")


def sensibilisee(R, M, t):
    """t est franchissable si chaque place d'entree a au moins autant de jetons que le poids de l'arc."""
    _verifier_transition(R, t)
    return all(M[i] >= R.poids_pre(p, t) for i, p in enumerate(R.places))


def sensibilisees(R, M):
    return [t for t in R.transitions if sensibilisee(R, M, t)]


def franchir(R, M, t):
    """On retire les jetons des entrees, puis on ajoute ceux des sorties (omega reste omega)."""
    if not sensibilisee(R, M, t):
        raise ValueError(f"{t} n'est pas franchissable depuis {ecrire(R, M)}")
    return tuple(n if n == OMEGA else n - R.poids_pre(p, t) + R.poids_post(p, t)
                 for p, n in zip(R.places, M))


def sequence(R, M0, ts):
    """Franchit une suite de transitions ; renvoie la liste des marquages traverses."""
    traces = [M0]
    for t in ts:
        traces.append(franchir(R, traces[-1], t))
    return traces


# --- Graphe de marquage ----------------------------------------------------------------------------------

@dataclass
class Graphe:
    marquages: list      # M0, M1... dans l'ordre de decouverte
    arcs: list           # (indice depart, transition, indice arrivee)
    complet: bool        # False si on a atteint la limite (reseau probablement non borne)

    def __post_init__(self):
        self._succ = {}
        for d, t, j in self.arcs:
            self._succ.setdefault(d, []).append((t, j))

    def successeurs(self, i):
        return self._succ.get(i, [])


def graphe_marquage(R, M0, limite=100_000):
    """Parcours en largeur depuis M0, transitions dans l'ordre de l'enonce. S'arrete a `limite` marquages
    (graphe marque incomplet) : un reseau non borne a un graphe de marquage infini."""
    index = {M0: 0}
    marquages, arcs = [M0], []
    file = deque([M0])
    while file:
        M = file.popleft()
        for t in sensibilisees(R, M):
            N = franchir(R, M, t)
            if N not in index:
                if len(marquages) >= limite:
                    return Graphe(marquages, arcs, False)
                index[N] = len(marquages)
                marquages.append(N)
                file.append(N)
            arcs.append((index[M], t, index[N]))
    return Graphe(marquages, arcs, True)


def _atteignables(G, depart):
    vus, pile = {depart}, [depart]
    while pile:
        i = pile.pop()
        for _, j in G.successeurs(i):
            if j not in vus:
                vus.add(j)
                pile.append(j)
    return vus


def proprietes(R, G):
    """Les proprietes qu'on lit sur un graphe de marquage FINI.

    Cout quadratique en nombre de marquages (un ensemble d'atteignables par marquage) : quelques milliers de
    marquages au plus (philosophes jusqu'a n = 8, environ 1 000 marquages, ~2 s)."""
    if not G.complet:
        raise ValueError("graphe incomplet : utiliser le graphe de couverture")
    n = len(G.marquages)
    bornes = {p: max(M[i] for M in G.marquages) for i, p in enumerate(R.places)}
    blocages = [i for i in range(n) if not G.successeurs(i)]
    franchies = {t for _, t, _ in G.arcs}
    quasi_vivant = all(t in franchies for t in R.transitions)
    # vivant : depuis TOUT marquage atteignable, chaque transition peut encore etre franchie un jour
    acces = [_atteignables(G, i) for i in range(n)]
    sortantes = [{t for t, _ in G.successeurs(i)} for i in range(n)]
    mortes_depuis = {i: [t for t in R.transitions if not any(t in sortantes[j] for j in acces[i])]
                     for i in range(n)}
    vivant = all(not m for m in mortes_depuis.values())
    reinitialisable = all(0 in acces[i] for i in range(n))
    return {
        "marquages": n,
        "bornes": bornes,
        "borne": max(bornes.values()),
        "sauf": max(bornes.values()) <= 1,
        "blocages": blocages,
        "quasi_vivant": quasi_vivant,
        "vivant": vivant,
        "mortes_depuis": mortes_depuis,
        "reinitialisable": reinitialisable,
    }


# --- Graphe de couverture (Karp et Miller) ---------------------------------------------------------------

def _couvre_strictement(N, A):
    return all(n >= a for n, a in zip(N, A)) and N != A


def graphe_couverture(R, M0):
    """Arbre de Karp et Miller replie en graphe, en largeur. Quand un nouveau marquage couvre strictement un
    ancetre, les places qui ont grossi passent a omega. Termine toujours, meme si le reseau n'est pas borne."""
    noeuds = [(M0, None)]                  # (marquage, parent)
    vus = {M0: 0}
    arcs, file = [], deque([0])
    while file:
        i = file.popleft()
        M = noeuds[i][0]
        for t in sensibilisees(R, M):
            N = list(franchir(R, M, t))
            a = i
            while a is not None:            # remonter les ancetres
                A = noeuds[a][0]
                if _couvre_strictement(tuple(N), A):
                    N = [OMEGA if n > x else n for n, x in zip(N, A)]
                a = noeuds[a][1]
            N = tuple(N)
            if N not in vus:
                vus[N] = len(noeuds)
                noeuds.append((N, i))
                file.append(vus[N])
            arcs.append((i, t, vus[N]))
    return [n[0] for n in noeuds], arcs


# --- Matrice d'incidence et equation d'etat ---------------------------------------------------------------

def matrices(R):
    """Pre, Post et C = Post - Pre : une ligne par place, une colonne par transition."""
    Pre = [[R.poids_pre(p, t) for t in R.transitions] for p in R.places]
    Post = [[R.poids_post(p, t) for t in R.transitions] for p in R.places]
    C = [[Post[i][j] - Pre[i][j] for j in range(len(R.transitions))] for i in range(len(R.places))]
    return Pre, Post, C


def boucles(R):
    """Les boucles (une place a la fois entree et sortie d'une meme transition) : C ne les voit pas."""
    return [(p, t) for p in R.places for t in R.transitions if R.poids_pre(p, t) and R.poids_post(p, t)]


def equation_etat(R, M0, sigma):
    """M = M0 + C . sigma, ou sigma compte combien de fois chaque transition est franchie."""
    if len(sigma) != len(R.transitions):
        raise ValueError(f"sigma a {len(sigma)} composantes, il en faut {len(R.transitions)} (une par transition)")
    _, _, C = matrices(R)
    return tuple(M0[i] + sum(C[i][j] * sigma[j] for j in range(len(R.transitions)))
                 for i in range(len(R.places)))


def solutions_equation(R, M0, M, max_par_transition=4):
    """Les vecteurs sigma >= 0 (chaque composante <= max_par_transition) qui verifient M = M0 + C . sigma.
    Recherche exhaustive : petits reseaux seulement. Une solution ne prouve PAS que M est atteignable."""
    k = len(R.transitions)
    return [s for s in product(range(max_par_transition + 1), repeat=k) if equation_etat(R, M0, s) == M]


def vecteur_comptage(R, ts):
    ts = list(ts)
    for t in ts:
        _verifier_transition(R, t)
    return tuple(ts.count(t) for t in R.transitions)


# --- Invariants (algorithme de Farkas) --------------------------------------------------------------------

def _normaliser(v):
    g = 0
    for x in v:
        g = gcd(g, abs(x))
    return tuple(x // g for x in v) if g else tuple(v)


def _farkas(A):
    """Semi-flots positifs minimaux y >= 0, y non nul, avec y . A = 0 (A : n lignes, m colonnes). Algorithme
    de Farkas (Martinez et Silva) : on annule les colonnes une a une en combinant les lignes de signes
    opposes, et on ne garde que les supports minimaux."""
    n = len(A)
    m = len(A[0]) if A else 0
    lignes = [tuple(A[i]) + tuple(1 if k == i else 0 for k in range(n)) for i in range(n)]
    for j in range(m):
        nulles = [l for l in lignes if l[j] == 0]
        pos = [l for l in lignes if l[j] > 0]
        neg = [l for l in lignes if l[j] < 0]
        nouvelles = [_normaliser(tuple(-b[j] * x + a[j] * y for x, y in zip(a, b))) for a in pos for b in neg]
        lignes = list(dict.fromkeys(nulles + nouvelles))
        supp = [frozenset(k for k in range(n) if l[m + k]) for l in lignes]
        lignes = [l for l, s in zip(lignes, supp) if not any(o < s for o in supp)]
    resultat = {_normaliser(l[m:]) for l in lignes}
    return sorted((r for r in resultat if any(r)), reverse=True)


def invariants_places(R):
    """Les P-invariants positifs minimaux f : f . C = 0. La somme ponderee des jetons ne change jamais."""
    _, _, C = matrices(R)
    return _farkas(C)


def invariants_transitions(R):
    """Les T-invariants positifs minimaux x : C . x = 0. Franchir x (dans un ordre possible) ramene au meme
    marquage."""
    _, _, C = matrices(R)
    Ct = [[C[i][j] for i in range(len(R.places))] for j in range(len(R.transitions))]
    return _farkas(Ct)


def ecrire_invariant(R, f, M0):
    termes = [(f"{w} {p}" if w != 1 else p) for w, p in zip(f, R.places) if w]
    valeur = sum(w * n for w, n in zip(f, M0))
    return " + ".join(termes) + f" = {valeur}"


def ecrire_t_invariant(R, x):
    return " + ".join((f"{w} {t}" if w != 1 else t) for w, t in zip(x, R.transitions) if w)


def table_matrice(R, A, nom="C", signes=None):
    """Une matrice place x transition en texte. `signes` : afficher +1 / -1 (par defaut : seulement pour C)."""
    if signes is None:
        signes = nom == "C"
    largeur = max(len(t) for t in R.transitions) + 1
    gauche = max(len(nom), max(len(p) for p in R.places)) + 1
    lignes = [nom.ljust(gauche) + "".join(t.rjust(largeur + 1) for t in R.transitions)]
    for p, ligne in zip(R.places, A):
        lignes.append(p.ljust(gauche) + "".join((f"{x:+d}" if signes and x else str(x)).rjust(largeur + 1)
                                                for x in ligne))
    return "\n".join(lignes)
