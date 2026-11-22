"""Tests : chaque resultat cite dans la video, puis les algorithmes compares a des juges independants
(definitions appliquees mot pour mot, recherche exhaustive) sur des reseaux tires au hasard.

    python -m unittest -v
"""
import random
import unittest
from collections import deque
from itertools import product

from enonces import (CORRIGE, CORRIGE_M0, EXERCICE, EXERCICE_M0, PORTE, PORTE_CIBLE, PORTE_M0, PRODUCTEUR,
                     PRODUCTEUR_M0, SANS_LIMITE, SANS_LIMITE_M0, VELO, VELO_M0, philosophes)
from petri import (OMEGA, boucles, equation_etat, franchir, graphe_couverture, graphe_marquage,
                   invariants_places, invariants_transitions, marquage, matrices, proprietes, reseau, sensibilisee,
                   sensibilisees, sequence, solutions_equation, table_matrice, vecteur_comptage)


def reseau_au_hasard(graine, n_places=4, n_trans=4):
    """Places p0.., transitions t0.. ; chaque arc existe avec une probabilite 0,3, poids 1 ou 2."""
    rnd = random.Random(graine)
    places = [f"p{i}" for i in range(n_places)]
    arcs = {}
    for j in range(n_trans):
        entrees = {p: rnd.choice((1, 1, 2)) for p in places if rnd.random() < 0.3}
        sorties = {p: rnd.choice((1, 1, 2)) for p in places if rnd.random() < 0.3}
        arcs[f"t{j}"] = (entrees, sorties)
    R = reseau(places, arcs)
    M0 = tuple(rnd.randint(0, 2) for _ in places)
    return R, M0


def chemins(R, G):
    """Pour chaque marquage du graphe, une suite de transitions qui y mene depuis M0 (parcours en largeur)."""
    vers = {0: []}
    file = deque([0])
    while file:
        i = file.popleft()
        for t, j in G.successeurs(i):
            if j not in vers:
                vers[j] = vers[i] + [t]
                file.append(j)
    return vers


def supports(vecteurs):
    return [frozenset(i for i, x in enumerate(v) if x) for v in vecteurs]


def semi_flots_exhaustifs(A, n, max_coef=3):
    """Juge : tous les y >= 0 non nuls (coefficients 0 a max_coef) tels que y . A = 0, A ayant n lignes."""
    m = len(A[0])
    return [y for y in product(range(max_coef + 1), repeat=n)
            if any(y) and all(sum(y[i] * A[i][j] for i in range(n)) == 0 for j in range(m))]


class ChiffresDeLaVideo(unittest.TestCase):
    def test_producteur(self):
        # GIVEN
        R, M0 = PRODUCTEUR, PRODUCTEUR_M0
        # WHEN
        P = proprietes(R, graphe_marquage(R, M0))
        # THEN
        self.assertEqual(P["marquages"], 6)
        self.assertEqual(P["borne"], 2)
        self.assertFalse(P["sauf"])
        self.assertTrue(P["vivant"] and P["reinitialisable"] and not P["blocages"])
        self.assertEqual(invariants_places(R), [(1, 1, 0, 0), (0, 0, 1, 1)])
        self.assertEqual(invariants_transitions(R), [(1, 1, 1)])

    def test_stock_plein_bloque_deposer(self):
        # GIVEN
        M = marquage(PRODUCTEUR, fini=1, stock=2)
        # WHEN / THEN
        self.assertEqual(sensibilisees(PRODUCTEUR, M), ["retirer"])

    def test_equation_etat_du_producteur(self):
        # GIVEN
        ts = ["fabriquer", "deposer", "fabriquer", "deposer", "retirer"]
        # WHEN
        s = vecteur_comptage(PRODUCTEUR, ts)
        # THEN
        self.assertEqual(s, (2, 2, 1))
        attendu = marquage(PRODUCTEUR, pret=1, stock=1, libres=1)
        self.assertEqual(equation_etat(PRODUCTEUR, PRODUCTEUR_M0, s), attendu)
        self.assertEqual(sequence(PRODUCTEUR, PRODUCTEUR_M0, ts)[-1], attendu)

    def test_velo(self):
        # GIVEN
        R, M0 = VELO, VELO_M0
        # WHEN
        G = graphe_marquage(R, M0)
        # THEN
        self.assertEqual(G.marquages[-1], marquage(R, roues=1, cadres=1, velos=2))
        self.assertEqual(proprietes(R, G)["blocages"], [2])

    def test_sans_limite_omega(self):
        # GIVEN
        R, M0 = SANS_LIMITE, SANS_LIMITE_M0
        # WHEN
        G = graphe_marquage(R, M0, limite=500)
        noeuds, _ = graphe_couverture(R, M0)
        # THEN
        self.assertFalse(G.complet)
        self.assertEqual(len(noeuds), 4)
        self.assertIn((1, 0, OMEGA), noeuds)

    def test_piege_de_la_porte(self):
        # GIVEN
        R, M0, cible = PORTE, PORTE_M0, PORTE_CIBLE
        # WHEN
        solutions = solutions_equation(R, M0, cible)
        atteignables = graphe_marquage(R, M0).marquages
        # THEN : l'equation a une solution, et pourtant la cible n'est pas atteignable
        self.assertEqual(boucles(R), [("cle", "ouvrir")])
        self.assertEqual(solutions, [(1,)])
        self.assertEqual(atteignables, [M0])

    def test_exercice(self):
        # GIVEN
        R, M0 = EXERCICE, EXERCICE_M0
        # WHEN
        G = graphe_marquage(R, M0)
        P = proprietes(R, G)
        # THEN
        self.assertEqual(P["marquages"], 6)
        self.assertTrue(P["sauf"])
        self.assertEqual(P["blocages"], [4])
        self.assertEqual(G.marquages[4], marquage(R, A1=1, B1=1))
        self.assertTrue(P["quasi_vivant"])          # le piege : chaque transition apparait...
        self.assertFalse(P["vivant"])               # ... et pourtant le reseau n'est pas vivant
        self.assertFalse(P["reinitialisable"])
        self.assertEqual(len(invariants_places(R)), 4)

    def test_exclusion_mutuelle(self):
        # GIVEN
        R, M0 = EXERCICE, EXERCICE_M0
        a2, b2 = R.places.index("A2"), R.places.index("B2")
        # WHEN
        G = graphe_marquage(R, M0)
        # THEN
        self.assertFalse(any(M[a2] and M[b2] for M in G.marquages))
        self.assertIn((0, 1, 1, 0, 0, 1, 1, 0), invariants_places(R))     # A1 + A2 + B2 + R1 = 1

    def test_correction(self):
        # GIVEN
        R, M0 = CORRIGE, CORRIGE_M0
        # WHEN
        P = proprietes(R, graphe_marquage(R, M0))
        # THEN
        self.assertEqual(P["marquages"], 5)
        self.assertTrue(P["vivant"] and P["reinitialisable"] and not P["blocages"])

    def test_philosophes(self):
        for n in range(2, 7):
            for meme in (False, True):
                with self.subTest(n=n, meme_ordre=meme):
                    # GIVEN
                    R, M0 = philosophes(n, meme)
                    # WHEN
                    P = proprietes(R, graphe_marquage(R, M0))
                    # THEN
                    self.assertEqual(len(P["blocages"]), 0 if meme else 1)
                    self.assertEqual(P["vivant"], meme)
        # GIVEN
        R, M0 = philosophes(5)
        # WHEN / THEN
        self.assertEqual(proprietes(R, graphe_marquage(R, M0))["marquages"], 82)


class Erreurs(unittest.TestCase):
    def test_franchir_refuse_une_transition_non_franchissable(self):
        # GIVEN
        M = marquage(EXERCICE, A1=1, B1=1)
        # WHEN / THEN
        with self.assertRaises(ValueError):
            franchir(EXERCICE, M, "t2")

    def test_transition_inconnue(self):
        # GIVEN : une faute de frappe dans le nom
        ts = ["fabriquer", "deposser"]
        # WHEN / THEN
        with self.assertRaises(ValueError):
            sequence(PRODUCTEUR, PRODUCTEUR_M0, ts)
        with self.assertRaises(ValueError):
            vecteur_comptage(PRODUCTEUR, ts)
        with self.assertRaises(ValueError):
            sensibilisee(PRODUCTEUR, PRODUCTEUR_M0, "xyz")

    def test_sigma_de_mauvaise_longueur(self):
        # WHEN / THEN
        with self.assertRaises(ValueError):
            equation_etat(PRODUCTEUR, PRODUCTEUR_M0, (1, 1))

    def test_reseau_et_marquage_invalides(self):
        # WHEN / THEN
        for mauvais in [lambda: reseau(["p"], {"t": ({"q": 1}, {})}),
                        lambda: reseau(["p"], {"t": ({"p": 0}, {})}),
                        lambda: reseau(["p"], {"p": ({}, {})}),
                        lambda: reseau(["p"], {}),
                        lambda: reseau([], {"t": ({}, {})}),
                        lambda: marquage(EXERCICE, A0=-1),
                        lambda: marquage(EXERCICE, A0=True)]:
            with self.assertRaises(ValueError):
                mauvais()

    def test_table_alignee(self):
        # GIVEN : un nom de matrice plus long que les noms de places
        _, Post, _ = matrices(EXERCICE)
        # WHEN
        lignes = table_matrice(EXERCICE, Post, "Post").splitlines()
        # THEN : toutes les lignes ont la meme largeur
        self.assertEqual(len({len(l) for l in lignes}), 1)


class Algorithmes(unittest.TestCase):
    GRAINES = range(300)

    def test_equation_etat_sur_chaque_chemin(self):
        """Tout marquage atteint par une suite s verifie M = M0 + C.s (la reciproque est fausse : la porte)."""
        for g in self.GRAINES:
            # GIVEN
            R, M0 = reseau_au_hasard(g)
            # WHEN
            G = graphe_marquage(R, M0, limite=300)
            # THEN
            for i, ts in chemins(R, G).items():
                self.assertEqual(equation_etat(R, M0, vecteur_comptage(R, ts)), G.marquages[i])

    def test_p_invariants(self):
        """f.C = 0, f >= 0, f.M constant sur tout le graphe ; supports minimaux (aucun n'en contient un autre) ;
        et toute solution d'une recherche exhaustive (coefficients 0 a 3) contient le support d'un invariant."""
        for g in self.GRAINES:
            # GIVEN
            R, M0 = reseau_au_hasard(g)
            _, _, C = matrices(R)
            # WHEN
            trouves = invariants_places(R)
            G = graphe_marquage(R, M0, limite=300)
            # THEN
            for f in trouves:
                self.assertTrue(all(x >= 0 for x in f) and any(f))
                self.assertTrue(all(sum(f[i] * C[i][j] for i in range(len(f))) == 0 for j in range(len(C[0]))))
                self.assertEqual(len({sum(a * b for a, b in zip(f, M)) for M in G.marquages}), 1)
            s = supports(trouves)
            self.assertFalse(any(a < b for a in s for b in s), g)
            for y in semi_flots_exhaustifs(C, len(R.places)):
                self.assertTrue(any(m <= supports([y])[0] for m in s), (g, y))

    def test_t_invariants(self):
        """C.x = 0, x >= 0 ; supports minimaux ; et complets contre une recherche exhaustive."""
        for g in self.GRAINES:
            # GIVEN
            R, _ = reseau_au_hasard(g)
            _, _, C = matrices(R)
            Ct = [[C[i][j] for i in range(len(R.places))] for j in range(len(R.transitions))]
            # WHEN
            trouves = invariants_transitions(R)
            # THEN
            for x in trouves:
                self.assertTrue(all(v >= 0 for v in x) and any(x))
                self.assertTrue(all(sum(C[i][j] * x[j] for j in range(len(x))) == 0 for i in range(len(C))))
            s = supports(trouves)
            self.assertFalse(any(a < b for a in s for b in s), g)
            for y in semi_flots_exhaustifs(Ct, len(R.transitions)):
                self.assertTrue(any(m <= supports([y])[0] for m in s), (g, y))

    def test_vivant_contre_la_definition(self):
        """Juge : pour chaque marquage atteignable M et chaque transition t, on cherche par un nouveau parcours
        un marquage atteignable depuis M ou t est franchissable."""
        for g in self.GRAINES:
            # GIVEN
            R, M0 = reseau_au_hasard(g, 3, 3)
            G = graphe_marquage(R, M0, limite=200)
            if not G.complet:
                continue

            def accessibles(M):
                vus, pile = {M}, [M]
                while pile:
                    X = pile.pop()
                    for t in sensibilisees(R, X):
                        Y = franchir(R, X, t)
                        if Y not in vus:
                            vus.add(Y)
                            pile.append(Y)
                return vus

            # WHEN
            P = proprietes(R, G)
            vivant = all(any(t in sensibilisees(R, Y) for Y in accessibles(M))
                         for M in G.marquages for t in R.transitions)
            # THEN
            self.assertEqual(P["vivant"], vivant, g)
            self.assertEqual(P["blocages"] == [], all(sensibilisees(R, M) for M in G.marquages))
            self.assertEqual(P["reinitialisable"], all(M0 in accessibles(M) for M in G.marquages))

    def test_couverture_contre_marquage(self):
        """Reseau borne : le graphe de couverture n'a aucun omega et donne les memes marquages. Un omega
        apparait seulement si le graphe de marquage est infini (il depasse toute limite)."""
        vus_omega = 0
        for g in self.GRAINES:
            # GIVEN
            R, M0 = reseau_au_hasard(g, 3, 3)
            # WHEN
            noeuds, _ = graphe_couverture(R, M0)
            G = graphe_marquage(R, M0, limite=2000)
            # THEN
            if any(OMEGA in M for M in noeuds):
                vus_omega += 1
                self.assertFalse(G.complet, g)
            else:
                self.assertTrue(G.complet, g)
                self.assertEqual(set(noeuds), set(G.marquages), g)
        self.assertGreater(vus_omega, 10)


if __name__ == "__main__":
    unittest.main()
