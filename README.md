# Outil OSINT Passif Avancé

Ce projet est un outil pour effectuer des recherches en ligne de manière efficace.

## Table des matières

1. [Présentation](#présentation)
2. [Fonctionnalités](#fonctionnalités)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Utilisation](#utilisation)
6. [Données d'entrée](#données-d'entrée)
7. [Sorties](#sorties)
8. [Sauvegarde des résultats](#sauvegarde-des-résultats)
9. [Dépendances](#dépendances)
10. [Licence](#licence)

## Présentation

L'Outil OSINT Passif Avancé est une application Python qui permet de réaliser des recherches en ligne de manière automatisée. Il offre trois types de recherches principales :

- Recherche par adresse IP
- Recherche par nom complet (Pages Jaunes ou JSON)
- Recherche par nom d'utilisateur sur divers plateformes

Cette application utilise des technologies modernes comme Selenium, asyncio et aiohttp pour effectuer des tâches complexes de manière efficace.

## Fonctionnalités

- Recherche d'informations sur une adresse IP
- Recherche de contacts via Pages Jaunes ou un fichier JSON local
- Recherche de profils utilisateurs sur plusieurs plateformes sociales
- Interface graphique utilisateur avec Tkinter
- Sauvegarde automatique des résultats

## Installation

Pour installer ce projet, vous aurez besoin de Python et de certaines dépendances. Voici comment procéder :
pip install -r requirements.txt


Assurez-vous également d'avoir installé le pilote WebDriver pour Chrome.

## Configuration

Aucune configuration supplémentaire n'est nécessaire. L'application fonctionne directement après l'exécution.

## Utilisation

1. Lancez l'application en exécutant le script Python.
2. Une interface graphique s'affichera avec trois champs de saisie :
   - Recherche par IP
   - Recherche par nom complet
   - Recherche par nom d'utilisateur
3. Entrez vos critères de recherche dans les champs appropriés.
4. Cliquez sur le bouton correspondant pour lancer la recherche.
5. Les résultats apparaîtront dans la zone de sortie.

## Données d'entrée

### Recherche par IP
- Adresse IP valide (format XXX.XXX.XXX.XXX)

### Recherche par nom complet
- Nom complet à rechercher (ex: Jean Dupont)

### Recherche par nom d'utilisateur
- Nom d'utilisateur sans symbole "@" si applicable (ex: john_doe)

## Sorties

Les résultats sont affichés dans une zone de texte à l'écran. Ils incluent :

- Pour la recherche par IP :
  - ISP
  - Ville
  - Région
  - Pays
  - Localisation (Latitude, Longitude)

- Pour la recherche par nom complet :
  - Nom complet
  - Adresse
  - Téléphone

- Pour la recherche par nom d'utilisateur :
  - Statut de la recherche sur chaque plateforme

## Sauvegarde des résultats

L'application sauvegarde automatiquement les résultats dans deux formats :

1. Fichier texte : `result.txt` dans un dossier `found/`
2. Fichier JSON : `result.json` dans un dossier `found/`

Chaque résultat est numéroté pour éviter les conflits de nom.

## Dépendances

Ce projet nécessite les bibliothèques suivantes :

- tkinter
- requests
- aiohttp
- selenium
- json
- os

Installez-les en exécutant `pip install -r requirements.txt`.

## Licence

Ce projet est sous licence Zone01.