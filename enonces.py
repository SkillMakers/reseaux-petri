"""Les reseaux de la video : le cours, le piege de l'equation d'etat, et l'exercice corrige."""
from petri import marquage, reseau

# --- Cours : un producteur et un stock de deux places ------------------------------------------------------
# Le producteur est pret, fabrique une piece (fini), puis la depose dans le stock s'il reste une place libre.
# Un consommateur retire les pieces une a une, ce qui libere une place.
PRODUCTEUR = reseau(
    ["pret", "fini", "stock", "libres"],
    {
        "fabriquer": ({"pret": 1}, {"fini": 1}),
        "deposer": ({"fini": 1, "libres": 1}, {"pret": 1, "stock": 1}),
        "retirer": ({"stock": 1}, {"libres": 1}),
    },
)
PRODUCTEUR_M0 = marquage(PRODUCTEUR, pret=1, libres=2)

# --- Cours : le meme, sans limite de stock (reseau non borne) ----------------------------------------------
SANS_LIMITE = reseau(
    ["pret", "fini", "stock"],
    {
        "fabriquer": ({"pret": 1}, {"fini": 1}),
        "deposer": ({"fini": 1}, {"pret": 1, "stock": 1}),
        "retirer": ({"stock": 1}, {}),
    },
)
SANS_LIMITE_M0 = marquage(SANS_LIMITE, pret=1)

# --- Cours : poids sur un arc --------------------------------------------------------------------------------
# Assembler un velo demande deux roues et un cadre.
VELO = reseau(
    ["roues", "cadres", "velos"],
    {"assembler": ({"roues": 2, "cadres": 1}, {"velos": 1})},
)
VELO_M0 = marquage(VELO, roues=5, cadres=3)

# --- Le piege de l'equation d'etat : une boucle que la matrice ne voit pas -----------------------------------
# Ouvrir demande la cle et la rend : cle est a la fois entree et sortie, la colonne de C vaut 0 sur cle.
PORTE = reseau(
    ["attente", "cle", "entre"],
    {"ouvrir": ({"attente": 1, "cle": 1}, {"entre": 1, "cle": 1})},
)
PORTE_M0 = marquage(PORTE, attente=1)                 # pas de cle
PORTE_CIBLE = marquage(PORTE, entre=1)

# --- Exercice : deux programmes, deux ressources ------------------------------------------------------------
# A prend R1 puis R2 (t1, t2, t3) ; B prend R2 puis R1 (t4, t5, t6). Chacun rend les deux en sortant.
# Les transitions s'appellent t1..t6 et pas a1..b3 : a l'oral, "a un" se confondrait avec la place A1.
# A0 : A au repos, A1 : A tient R1, A2 : A tient R1 et R2 (il travaille). Pareil pour B.
EXERCICE = reseau(
    ["A0", "A1", "A2", "B0", "B1", "B2", "R1", "R2"],
    {
        "t1": ({"A0": 1, "R1": 1}, {"A1": 1}),
        "t2": ({"A1": 1, "R2": 1}, {"A2": 1}),
        "t3": ({"A2": 1}, {"A0": 1, "R1": 1, "R2": 1}),
        "t4": ({"B0": 1, "R2": 1}, {"B1": 1}),
        "t5": ({"B1": 1, "R1": 1}, {"B2": 1}),
        "t6": ({"B2": 1}, {"B0": 1, "R1": 1, "R2": 1}),
    },
)
EXERCICE_M0 = marquage(EXERCICE, A0=1, B0=1, R1=1, R2=1)

# --- Exercice, question 5 : B prend les ressources dans le meme ordre que A --------------------------------
CORRIGE = reseau(
    ["A0", "A1", "A2", "B0", "B1", "B2", "R1", "R2"],
    {
        "t1": ({"A0": 1, "R1": 1}, {"A1": 1}),
        "t2": ({"A1": 1, "R2": 1}, {"A2": 1}),
        "t3": ({"A2": 1}, {"A0": 1, "R1": 1, "R2": 1}),
        "t4": ({"B0": 1, "R1": 1}, {"B1": 1}),
        "t5": ({"B1": 1, "R2": 1}, {"B2": 1}),
        "t6": ({"B2": 1}, {"B0": 1, "R1": 1, "R2": 1}),
    },
)
CORRIGE_M0 = marquage(CORRIGE, A0=1, B0=1, R1=1, R2=1)


def philosophes(n, meme_ordre=False):
    """n programmes autour d'une table, n ressources : le programme i prend la ressource i puis i+1. Avec
    meme_ordre, le dernier prend d'abord la plus petite (la correction de l'exercice, generalisee)."""
    places = [f"{x}{i}" for i in range(n) for x in ("repos", "tient", "travaille")] + [f"R{i}" for i in range(n)]
    arcs = {}
    for i in range(n):
        g, d = i, (i + 1) % n
        if meme_ordre and d < g:
            g, d = d, g
        arcs[f"prend{i}a"] = ({f"repos{i}": 1, f"R{g}": 1}, {f"tient{i}": 1})
        arcs[f"prend{i}b"] = ({f"tient{i}": 1, f"R{d}": 1}, {f"travaille{i}": 1})
        arcs[f"rend{i}"] = ({f"travaille{i}": 1}, {f"repos{i}": 1, f"R{g}": 1, f"R{d}": 1})
    R = reseau(places, arcs)
    M0 = marquage(R, **{f"repos{i}": 1 for i in range(n)}, **{f"R{i}": 1 for i in range(n)})
    return R, M0
