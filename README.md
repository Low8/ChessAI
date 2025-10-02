# 🏁 Jeu d’Échecs avec IA Min-Max
*Projet personnel pour implémenter un moteur d’échecs en [Python/Java/...] avec une IA basée sur Min-Max + élagage alpha-bêta.*

---

## 🎯 Objectifs
- **Comprendre Min-Max** : Algorithme de décision pour jeux à 2 joueurs.
- **Implémenter les règles des échecs** : Mouvements légaux, échecs, roques, etc.
- **Optimiser l’IA** :
  - Fonction d’évaluation (valeur des pièces + positionnement).
  - Élagage alpha-bêta pour réduire l’arbre de recherche.
  - *(Autres optimisations si tu en as)*

---

## 🧠 Concepts Clés

### 1. Algorithme Min-Max
**Principe** : L’IA explore les coups possibles en alternant entre :
- **Niveau Max** (elle cherche à maximiser son score).
- **Niveau Min** (l’adversaire cherche à minimiser son score).

**Mon implémentation** :
- Profondeur limitée à **4 coups** (pour éviter l’explosion combinatoire).
- Utilisation de **récursivité** avec une fonction `minmax(position, profondeur, est_max_joueur)`.

**Exemple de code** :
```python
def minmax(position, profondeur, est_max, alpha=-inf, beta=inf):
    if profondeur == 0 or jeu_terminé(position):
        return evaluer_position(position)

    if est_max:
        max_eval = -inf
        for coup in coups_légaux(position):
            eval = minmax(appliquer_coup(position, coup), profondeur-1, False, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:  # Élagage alpha-bêta
                break
        return max_eval
    else:
        # Logique similaire pour le joueur Min
        ...
