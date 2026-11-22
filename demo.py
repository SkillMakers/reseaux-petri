"""Le cours et l'exercice corrige, executes. Chaque graphe et chaque matrice sont ceux qu'on ecrit sur la copie.

    python demo.py
"""
import time

from enonces import (CORRIGE, CORRIGE_M0, EXERCICE, EXERCICE_M0, PORTE, PORTE_CIBLE, PORTE_M0, PRODUCTEUR,
                     PRODUCTEUR_M0, SANS_LIMITE, SANS_LIMITE_M0, VELO, VELO_M0, philosophes)
from petri import (boucles, ecrire, ecrire_invariant, ecrire_t_invariant, equation_etat, graphe_couverture,
                   graphe_marquage, invariants_places, invariants_transitions, matrices, proprietes, sequence,
                   sensibilisees, solutions_equation, table_matrice, vecteur_comptage)


def titre(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def afficher_graphe(R, G):
    for i, M in enumerate(G.marquages):
        succ = ", ".join(f"{t} -> M{j}" for t, j in G.successeurs(i)) or "AUCUNE TRANSITION (blocage)"
        print(f"  M{i} = {ecrire(R, M):28} | {succ}")


def afficher_proprietes(R, G, P):
    print(f"  marquages atteignables : {P['marquages']}")
    print(f"  bornes par place : " + ", ".join(f"{p} <= {b}" for p, b in P['bornes'].items()))
    print(f"  borne : {P['borne']} | sauf (1-borne) : {P['sauf']}")
    print(f"  blocages : " + (", ".join(f"M{i} = {ecrire(R, G.marquages[i])}" for i in P['blocages']) or "aucun"))
    print(f"  quasi-vivant (chaque transition franchie au moins une fois) : {P['quasi_vivant']}")
    print(f"  vivant (chaque transition reste franchissable depuis tout marquage) : {P['vivant']}")
    for i, mortes in P["mortes_depuis"].items():
        if mortes:
            print(f"    depuis M{i}, plus jamais : {', '.join(mortes)}")
    print(f"  reinitialisable (M0 atteignable depuis tout marquage) : {P['reinitialisable']}")


def afficher_invariants(R, M0):
    for f in invariants_places(R):
        print("  P-invariant :", ecrire_invariant(R, f, M0))
    for x in invariants_transitions(R):
        print("  T-invariant :", ecrire_t_invariant(R, x))


titre("COURS 1 - franchir une transition : le producteur et son stock de 2 places")
R, M0 = PRODUCTEUR, PRODUCTEUR_M0
print("M0 =", ecrire(R, M0), "| franchissables :", sensibilisees(R, M0))
for M, t in zip(sequence(R, M0, ["fabriquer", "deposer", "fabriquer", "deposer"]),
                ["fabriquer", "deposer", "fabriquer", "deposer", None]):
    print(f"  {ecrire(R, M):28} franchissables : {sensibilisees(R, M)}" + (f"  -> on franchit {t}" if t else ""))
print("  deposer est-il franchissable a la fin ?", "deposer" in sensibilisees(R, sequence(
    R, M0, ["fabriquer", "deposer", "fabriquer", "deposer", "fabriquer"])[-1]), "(stock plein, libres = 0)")

titre("COURS 2 - poids sur un arc : assembler un velo (2 roues + 1 cadre)")
G = graphe_marquage(VELO, VELO_M0)
afficher_graphe(VELO, G)
afficher_proprietes(VELO, G, proprietes(VELO, G))

titre("COURS 3 - graphe de marquage du producteur")
G = graphe_marquage(R, M0)
afficher_graphe(R, G)
afficher_proprietes(R, G, proprietes(R, G))

titre("COURS 4 - sans limite de stock : le graphe de marquage est infini")
G = graphe_marquage(SANS_LIMITE, SANS_LIMITE_M0, limite=1000)
print(f"  graphe de marquage arrete a {len(G.marquages)} marquages, complet : {G.complet}")
print(f"  stock maximum vu : {max(M[2] for M in G.marquages)}")
noeuds, arcs = graphe_couverture(SANS_LIMITE, SANS_LIMITE_M0)
print("  graphe de couverture (Karp et Miller), w = autant qu'on veut :")
for i, M in enumerate(noeuds):
    succ = ", ".join(f"{t} -> N{j}" for d, t, j in arcs if d == i)
    print(f"    N{i} = {ecrire(SANS_LIMITE, M):20} | {succ}")

titre("COURS 5 - matrice d'incidence et equation d'etat du producteur")
Pre, Post, C = matrices(R)
print(table_matrice(R, Pre, "Pre"))
print(table_matrice(R, Post, "Post"))
print(table_matrice(R, C, "C"))
ts = ["fabriquer", "deposer", "fabriquer", "deposer", "retirer"]
s = vecteur_comptage(R, ts)
print(f"  sequence {' '.join(ts)} : vecteur de comptage {s}")
print(f"  M0 + C.s = {ecrire(R, equation_etat(R, M0, s))} | en franchissant : {ecrire(R, sequence(R, M0, ts)[-1])}")
afficher_invariants(R, M0)

titre("COURS 6 - le piege de l'equation d'etat : la porte et la cle")
Pre, Post, C = matrices(PORTE)
print(table_matrice(PORTE, Pre, "Pre"))
print(table_matrice(PORTE, Post, "Post"))
print(table_matrice(PORTE, C, "C"))
print("  boucles (invisibles dans C) :", boucles(PORTE))
print(f"  M0 = {ecrire(PORTE, PORTE_M0)}, cible = {ecrire(PORTE, PORTE_CIBLE)}")
print("  solutions de cible = M0 + C.s :", solutions_equation(PORTE, PORTE_M0, PORTE_CIBLE))
G = graphe_marquage(PORTE, PORTE_M0)
print("  marquages vraiment atteignables :", [ecrire(PORTE, M) for M in G.marquages],
      "| ouvrir franchissable :", sensibilisees(PORTE, PORTE_M0))

titre("EXERCICE - question 1 : matrice d'incidence")
R, M0 = EXERCICE, EXERCICE_M0
Pre, Post, C = matrices(R)
print(table_matrice(R, C, "C"))

titre("EXERCICE - question 2 : graphe de marquage")
G = graphe_marquage(R, M0)
afficher_graphe(R, G)

titre("EXERCICE - question 3 : proprietes")
P = proprietes(R, G)
afficher_proprietes(R, G, P)
franchies = sorted({t for _, t, _ in G.arcs}, key=R.transitions.index)
print("  transitions qui apparaissent dans le graphe :", franchies, f"({len(franchies)} sur {len(R.transitions)})")

titre("EXERCICE - question 4 : invariants de places")
afficher_invariants(R, M0)
travaillent_ensemble = [ecrire(R, M) for M in G.marquages if M[R.places.index("A2")] and M[R.places.index("B2")]]
print("  marquages ou A2 et B2 sont marques ensemble :", travaillent_ensemble or "aucun")

titre("EXERCICE - question 5 : B prend R1 avant R2, comme A")
G = graphe_marquage(CORRIGE, CORRIGE_M0)
afficher_graphe(CORRIGE, G)
afficher_proprietes(CORRIGE, G, proprietes(CORRIGE, G))
afficher_invariants(CORRIGE, CORRIGE_M0)

titre("POUR ALLER PLUS LOIN - n programmes autour d'une table (philosophes)")
print("   n | ordre            | marquages | blocages | vivant | temps")
for n in range(2, 9):
    for meme in (False, True):
        R, M0 = philosophes(n, meme)
        t0 = time.perf_counter()
        G = graphe_marquage(R, M0)
        P = proprietes(R, G)
        dt = time.perf_counter() - t0
        print(f"  {n:2} | {'meme ordre' if meme else 'chacun sa gauche':16} | {P['marquages']:9} | "
              f"{len(P['blocages']):8} | {str(P['vivant']):6} | {dt:.2f} s")
