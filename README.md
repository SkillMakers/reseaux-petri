# Réseaux de Petri : cours et exercices corrigés

Code de la vidéo [**Réseaux de Petri : cours et exercices corrigés (graphe de marquage)**](https://youtu.be/rhRuo28aUmY) de la chaîne
[IT Skills Maker](https://www.youtube.com/@ItSkillsMaker).

Le programme refait le corrigé **comme sur une copie** : franchissement, graphe de marquage (marquages numérotés dans
l'ordre où on les trouve), propriétés (borné, sauf, blocage, quasi-vivant, vivant, réinitialisable), graphe de
couverture de Karp et Miller (avec ω), matrices Pré, Post et d'incidence, équation d'état, invariants de places et de
transitions (algorithme de Farkas). Les tests comparent ces calculs à la définition appliquée mot pour mot et à une
recherche exhaustive, sur 300 réseaux tirés au hasard.

## Lancer

Python 3.11 ou plus, aucune dépendance.

```
python demo.py           # le cours, l'exercice corrigé et les philosophes
python -m unittest -v    # les 20 tests
```

Les sorties obtenues pour la vidéo sont dans [`preuves/`](preuves/) : `demo.txt` (Python 3.15.1) et `tests.txt`
(20 tests verts sous 3.15.1 et 3.11).

Pour ton propre réseau :

```python
from petri import reseau, marquage, graphe_marquage, proprietes, invariants_places, ecrire_invariant

R = reseau(["p1", "p2"], {"t1": ({"p1": 1}, {"p2": 1}), "t2": ({"p2": 1}, {"p1": 1})})
M0 = marquage(R, p1=1)
G = graphe_marquage(R, M0)
print(proprietes(R, G))
for f in invariants_places(R):
    print(ecrire_invariant(R, f, M0))
```

## L'énoncé

Deux programmes A et B partagent deux ressources R1 et R2.

- A : au repos (A0), prend R1 (transition t1, place A1), prend R2 (t2, place A2 : il travaille), rend R1 et R2 et
  retourne au repos (t3).
- B : au repos (B0), prend **R2** (t4, place B1), prend **R1** (t5, place B2 : il travaille), rend R1 et R2 (t6).
- Marquage initial M0 : A0, B0, R1 et R2 ont un jeton chacun.

1. Écris la matrice d'incidence.
2. Construis le graphe de marquage depuis M0.
3. Le réseau est-il borné ? sauf ? quasi-vivant ? vivant ? réinitialisable ? A-t-il un blocage ?
4. Donne les invariants de places ; déduis-en que A et B ne travaillent jamais en même temps.
5. Modifie le réseau pour supprimer le blocage, s'il y en a un, et vérifie.

## Le corrigé

**1.** C = Post − Pré :

| C | t1 | t2 | t3 | t4 | t5 | t6 |
|---|---|---|---|---|---|---|
| A0 | −1 | 0 | +1 | 0 | 0 | 0 |
| A1 | +1 | −1 | 0 | 0 | 0 | 0 |
| A2 | 0 | +1 | −1 | 0 | 0 | 0 |
| B0 | 0 | 0 | 0 | −1 | 0 | +1 |
| B1 | 0 | 0 | 0 | +1 | −1 | 0 |
| B2 | 0 | 0 | 0 | 0 | +1 | −1 |
| R1 | −1 | 0 | +1 | 0 | −1 | +1 |
| R2 | 0 | −1 | +1 | −1 | 0 | +1 |

**2.** Six marquages :

| Marquage | Contenu | Successeurs |
|---|---|---|
| M0 | A0, B0, R1, R2 | t1 → M1, t4 → M2 |
| M1 | A1, B0, R2 | t2 → M3, t4 → M4 |
| M2 | A0, B1, R1 | t1 → M4, t5 → M5 |
| M3 | A2, B0 | t3 → M0 |
| M4 | A1, B1 | aucun : **blocage** |
| M5 | A0, B2 | t6 → M0 |

**3.** Borné par 1, donc sauf. Blocage en M4. Quasi-vivant (les 6 transitions apparaissent dans le graphe) mais **pas
vivant** : c'est le piège. Pas réinitialisable.

**4.** A0 + A1 + A2 = 1 · B0 + B1 + B2 = 1 · A1 + A2 + B2 + R1 = 1 · A2 + B1 + B2 + R2 = 1. Le troisième donne
A2 + B2 ≤ 1 : A et B ne travaillent jamais ensemble.

**5.** B prend R1 puis R2, comme A : 5 marquages, aucun blocage, vivant, réinitialisable, toujours sauf.

## Le piège de l'équation d'état

Le réseau `PORTE` de `enonces.py` : ouvrir prend la clé et la rend. Dans la matrice d'incidence, la colonne vaut 0 sur
la clé : la boucle est invisible. Sans clé au départ, l'équation M = M0 + C·s a la solution s = (1), et pourtant le
marquage « entré » n'est pas atteignable. L'équation d'état est une condition nécessaire, pas suffisante.
