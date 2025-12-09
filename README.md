[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adambeloucif/) ![Visitor Badge](https://visitor-badge.laobi.icu/badge?page_id=Adam-Blf.WalkingAI)



![Dernier commit](https://img.shields.io/github/last-commit/Adam-Blf/WalkingAI?style=flat&logo=git&logoColor=white&color=0080ff&label=Dernier%20commit) ![Langage principal](https://img.shields.io/github/languages/top/Adam-Blf/WalkingAI?style=flat&logo=git&logoColor=white&color=0080ff&label=Langage%20principal) ![Nombre de langages](https://img.shields.io/github/languages/count/Adam-Blf/WalkingAI?style=flat&logo=git&logoColor=white&color=0080ff&label=Nombre%20de%20langages)

### Construit avec les outils et technologies : 

🇫🇷 Français | 🇬🇧 Anglais | 🇪🇸 Espagnol | 🇮🇹 Italien | 🇵🇹 Portugais | 🇷🇺 Russe | 🇩🇪 Allemand | 🇹🇷 Turc

# IA Marcheuse (Walking AI)

Ce projet utilise l'apprentissage par renforcement (Reinforcement Learning) pour apprendre à un robot bipède à marcher.

## Prérequis

1.  Installer Python (si ce n'est pas déjà fait).
2.  Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```
    *Note : Sur Windows, l'installation de `box2d` peut parfois nécessiter des outils de compilation C++. Si vous avez une erreur, essayez d'installer `swig` via `choco install swig` ou téléchargez les binaires précompilés.*

## Comment utiliser

### 1. Entraînement (L'école)
Lancez le script d'entraînement pour que l'IA apprenne par essais et erreurs.
```bash
python train.py
```
L'IA va s'entraîner pendant 100 000 pas (environ 5-10 minutes selon votre PC). Les modèles seront sauvegardés dans le dossier `models/PPO`.

### 2. Visualisation (Le spectacle)
Une fois l'entraînement terminé, regardez le résultat :
```bash
python visualize.py
```
Une fenêtre s'ouvrira montrant le robot essayant de marcher (ou tombant avec style s'il n'a pas assez appris !).

## Le Système de Punition/Récompense
L'environnement `BipedalWalker-v3` donne des points à l'IA :
-   **Récompense (+)** : Avancer vers la fin du niveau.
-   **Punition (-)** : Tomber au sol (-100 points), utiliser trop de force moteur (coût énergétique).

L'IA cherche à maximiser son score total.