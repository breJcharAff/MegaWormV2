# Architecture de MegaWorm

Ce document décrit l'architecture technique du projet MegaWorm, un jeu de type "snake" développé en Python avec la bibliothèque Arcade.

## 1. Structure du Projet

Le projet est organisé en plusieurs modules, chacun ayant un rôle spécifique :

- **`main.py`**: Point d'entrée de l'application. Initialise la fenêtre du jeu et lance le menu principal.
- **`menu_view.py`**: Gère le menu principal du jeu, permettant à l'utilisateur de choisir entre les différents modes de jeu.
- **`game_view.py`**: La vue principale du jeu. Elle contient la boucle de jeu, gère le rendu des objets, les mises à jour de l'état du jeu et les interactions de base.
- **`config.py`**: Fichier de configuration centralisant toutes les constantes et paramètres du jeu (taille de l'écran, du monde, vitesse du serpent, etc.).
- **`world/map.py`**: Définit le monde du jeu (`World`), qui contient et gère les "pellets" (la nourriture des serpents).
- **`player/`**: Ce répertoire contient tout ce qui est lié aux serpents.
    - **`player.py`**: Définit la classe de base `PlayerWorm`, qui représente un serpent avec ses attributs et méthodes de base (mouvement, croissance, etc.).
    - **`ai_player.py`**: Définit la classe `AIWorm`, un serpent contrôlé par une IA simple basée sur des règles.
    - **`q_learning_player.py`**: Définit la classe `QLearningWorm`, un serpent contrôlé par une IA basée sur l'apprentissage par renforcement (Q-learning).

## 2. Architecture de base

### Moteur de jeu et gestion des vues

Le jeu est construit sur la bibliothèque **Arcade**, qui fournit un cadre pour les jeux 2D en Python. L'architecture est basée sur des "vues" (`arcade.View`).

- **`MenuView`**: La première vue affichée. Elle utilise `arcade.gui` pour créer une interface utilisateur simple avec des boutons. Chaque bouton lance la `GameView` avec un `player_mode` différent.
- **`GameView`**: La vue principale du jeu. Elle est responsable de :
    - La **boucle de jeu**, implémentée dans la méthode `on_update`. Cette méthode est appelée par Arcade à chaque frame et met à jour l'état de tous les objets du jeu.
    - Le **rendu**, implémenté dans la méthode `on_draw`. Elle dessine tous les éléments du jeu (fond, pellets, serpents).
    - La gestion des **entrées utilisateur** (`on_key_press`).

### Gestion multi-serpents

La `GameView` est conçue pour gérer plusieurs serpents simultanément. Elle maintient une liste `self.worms`. Le premier élément de cette liste (`self.worms[0]`) est le serpent "principal" (contrôlé par le joueur ou l'IA principale), et les autres sont des bots. La boucle `on_update` parcourt cette liste pour mettre à jour chaque serpent.

## 3. Composants du jeu

### Le monde (`world/map.py`)

La classe `World` représente l'environnement du jeu. Elle est responsable de :
- La gestion des **pellets** (création, suppression).
- La génération de nouveaux pellets lorsqu'un serpent en mange un ou lorsqu'un serpent meurt.

### Les serpents (répertoire `player/`)

L'architecture des serpents est basée sur l'héritage et le polymorphisme.

- **`PlayerWorm`**: La classe de base pour tous les serpents. Elle définit les attributs communs (cellules du corps, direction, score, etc.) et les méthodes de base comme `step` (pour avancer), `reset` (pour réinitialiser) et `die` (pour mourir). La méthode `step` inclut la logique de collision de base (murs, corps du serpent, autres serpents).

- **`AIWorm`**: Hérite de `PlayerWorm` et redéfinit la méthode `choose_direction`. Son IA est basée sur des règles : elle cherche la nourriture la plus proche tout en évitant les obstacles (murs, corps des serpents) dans son chemin.

- **`QLearningWorm`**: Hérite également de `PlayerWorm`. C'est l'implémentation de l'IA par apprentissage par renforcement.

## 4. Intelligence Artificielle (Q-learning)

L'IA Q-learning est conçue pour apprendre une stratégie de jeu optimale par essais et erreurs.

### Représentation de l'état

Pour prendre une décision, l'IA a besoin de connaître son état actuel. L'état est un tuple qui décrit l'environnement immédiat du serpent :
- **Direction de la nourriture**: Un "radar" de 10 cellules autour de la tête du serpent détecte la nourriture la plus proche. L'état inclut la direction (gauche/droite, haut/bas) de cette nourriture.
- **Dangers granulaires**: L'état inclut des informations sur les dangers dans les 4 directions cardinales adjacentes à la tête du serpent. Ces dangers sont différenciés :
    - 0 : Pas de danger
    - 1 : Mur
    - 2 : Propre corps
    - 3 : Corps d'un autre serpent

### Table Q et apprentissage

- La **Table Q** est une structure de données (un dictionnaire Python) qui stocke la "qualité" (Q-valeur) de chaque action possible pour chaque état. Elle est chargée depuis un fichier `q_table.npy` au début du jeu et sauvegardée à la fin, ce qui permet à l'IA de conserver son apprentissage entre les sessions.
- **Sélection de l'action**: L'IA utilise une stratégie **epsilon-greedy**. La plupart du temps, elle choisit l'action avec la plus haute Q-valeur pour l'état actuel (exploitation). Parfois (avec une probabilité `epsilon`), elle choisit une action au hasard pour découvrir de nouvelles stratégies (exploration).
- **Système de récompense**: Pour apprendre, l'IA reçoit des récompenses positives ou négatives pour ses actions :
    - **Récompenses positives**: Pour avoir mangé de la nourriture, pour s'être rapproché de la nourriture.
    - **Récompenses négatives**: Pour être mort, pour s'être éloigné de la nourriture, et une petite pénalité à chaque pas pour encourager l'efficacité.

## 5. Comment ajouter une nouvelle IA

Grâce à l'architecture polymorphique, il est facile d'ajouter une nouvelle IA :
1. Créez une nouvelle classe qui hérite de `PlayerWorm` dans le répertoire `player/`.
2. Redéfinissez la méthode `choose_direction(self, world, worms=None)` pour y implémenter la logique de votre IA.
3. Dans `game_view.py`, importez votre nouvelle classe.
4. Dans `menu_view.py`, ajoutez un nouveau bouton et un nouveau `player_mode` pour pouvoir sélectionner votre IA.
5. Dans `game_view.py`, mettez à jour la méthode `reset` pour instancier votre nouvelle classe d'IA lorsque le mode de jeu correspondant est sélectionné.
