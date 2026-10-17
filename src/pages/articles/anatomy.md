---
layout: ../../layouts/Article.astro
title: Installer et utiliser Anatomy, le skill qui transforme un concept en machine
description: Le guide pas à pas pour installer Anatomy dans Claude Code et créer ta première machine animée, même si tu débutes.
date: 2026-10-15
image: /anatomy/og-card.png
---

Anatomy est un skill gratuit et open source pour Claude Code. Tu lui donnes un concept technique à expliquer (un cache, une file d'attente, une table de hachage…), et il invente un vrai objet qui marche exactement pareil. Une étagère, une serrure, des tubes pneumatiques. Il le dessine en 3D isométrique, l'anime, et tu peux jouer avec à la souris.

Pour voir à quoi ça ressemble avant d'installer quoi que ce soit, fais un tour sur [la galerie officielle](https://skills.wheresryan.sh/anatomy). Passe ta souris sur le moteur de fusée : il se démonte en 11 morceaux.

Ce guide part de zéro. Compte 10 minutes pour l'installation. La création d'une figure, elle, prend beaucoup plus de temps (on en parle plus bas).

## Ce qu'il te faut

| | Obligatoire ? | Pourquoi |
|---|---|---|
| Node.js 22.20 ou plus (la 24 conseillée) | Oui | Pour la commande d'installation et pour construire les figures |
| Claude Code (avec un abonnement Claude Pro ou Max, ou une clé API) | Oui | C'est lui qui utilise le skill |
| Google Chrome | Conseillé | Anatomy s'en sert pour prendre des captures et vérifier son propre travail |

Anatomy marche aussi avec Codex, OpenCode et Antigravity. Ce guide prend l'exemple de Claude Code.

## Étape 1 : installer Node.js

### Sur Windows

1. Va sur [nodejs.org](https://nodejs.org) et télécharge la version **LTS** (la 24, en ce moment).
2. Lance l'installeur et laisse les options par défaut.
3. Ouvre **PowerShell** (touche Windows, tape « PowerShell ») et vérifie :

```powershell
node -v
```

Tu dois voir un numéro qui commence par `v24`.

### Sur Mac

Télécharge la version **LTS** sur [nodejs.org](https://nodejs.org), installe-la, puis ouvre le **Terminal** (Cmd + Espace, tape « Terminal ») et lance `node -v`.

### Sur Linux

Les paquets de ta distribution sont souvent trop vieux. Le plus simple est **nvm**, qui installe Node.js dans ton dossier perso, sans `sudo`. Copie la commande d'installation donnée sur [github.com/nvm-sh/nvm](https://github.com/nvm-sh/nvm), ferme puis rouvre ton terminal, et lance :

```bash
nvm install 24
node -v
```

## Étape 2 : installer Claude Code

Si tu l'as déjà, passe à l'étape 3.

Sur Mac et Linux :

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Sur Windows, dans PowerShell :

```powershell
irm https://claude.ai/install.ps1 | iex
```

Ensuite, place-toi dans un dossier de travail et lance Claude Code :

```bash
mkdir mes-machines
cd mes-machines
claude
```

Au premier lancement, il te demande de te connecter avec ton compte Claude. Suis les instructions, c'est un aller-retour dans le navigateur. Si quelque chose coince, la [doc officielle de Claude Code](https://code.claude.com/docs/en/overview) détaille chaque système.

## Étape 3 : installer Anatomy

Quitte Claude Code (tape `/exit`) et lance cette commande dans ton terminal. C'est la même sur Windows, Mac et Linux :

```bash
npx skills add wheresryan22/anatomy -g -a claude-code
```

Ce que ça veut dire :

- `npx skills add` télécharge le skill depuis GitHub. npm te demande s'il peut installer l'outil `skills` : réponds oui.
- `-g` l'installe pour toi, dans tous tes projets (dans le dossier `~/.claude/skills/anatomy`).
- `-a claude-code` le configure seulement pour Claude Code.

Le téléchargement fait une dizaine de Mo, parce que les exemples sont inclus. Il n'y a rien d'autre à installer : pas de clé API, pas de `npm install`.

Pour Codex, remplace `-a claude-code` par `-a codex`. Pour OpenCode, par `-a opencode`.

## Étape 4 : vérifier que c'est bien installé

Relance Claude Code avec `claude`, puis tape `/` : `anatomy` doit apparaître dans la liste.

S'il n'y est pas, tape `/reload-skills`, ou ferme et rouvre Claude Code.

## Étape 5 : ta première machine

Tape `/anatomy` suivi de ce que tu veux expliquer, en langage normal. En français, ça marche très bien :

```text
/anatomy explique comment marche un rate limiter "token bucket", interactif, page HTML, thème sombre
```

Ce qui va se passer :

1. Claude annonce la **taille** de la figure et le temps que ça va prendre.
2. Il cherche les vrais chiffres du concept, puis invente l'objet et fait la liste de ses pièces (au moins 40).
3. Il construit la figure dans une page HTML que tu ouvres dans ton navigateur. Une première version arrive en général dans l'heure.
4. Il vérifie son travail : il prend des captures dans Chrome, zoome sur chaque jointure et corrige ce qui dépasse.

À la fin, tu as dans ton dossier un script `build.mjs` et la page `.html` qu'il génère. Double-clique sur la page pour l'ouvrir.

### Les trois réflexes pour un bon résultat

1. **Dis ce que tu veux expliquer, pas ce qu'il faut dessiner.** Donne les vrais chiffres si tu les as (tailles, nombres, délais). Trouver l'objet, c'est son travail, et il le fait mieux que toi.
2. **Ou nomme l'objet directement**, si tu as déjà une idée : « une machine à espresso », « une serrure à goupilles ». Et dis ce qui doit bouger.
3. **Dis où la figure va vivre** : une page HTML toute seule, un fichier SVG, ou un composant React / Next.js. Et le thème : clair ou sombre.

### Des idées de prompts

```text
/anatomy explique le problème N+1 : une requête pour la liste, puis une requête par élément. Interactif, page HTML, thème sombre
```

```text
/anatomy un pool de 10 connexions à une base de données : chaque requête emprunte une connexion et la rend, et quand les 10 sont prises, les nouvelles attendent dans une file. Page HTML, thème clair
```

```text
/anatomy un bec Bunsen sur une paillasse : quand on ouvre la bague d'air, la flamme jaune devient un cône bleu. WebGL pour la flamme, un seul fichier HTML, thème sombre
```

## Ce qu'il faut savoir avant de te lancer

- **C'est lent, et c'est voulu.** Une petite figure prend souvent moins d'une heure. Une grosse, 2 à 4 heures. Les plus impressionnantes de la galerie, c'est plus de 10 heures. Pour un gros projet, Claude te proposera d'abord une version plus simple.
- **Ça consomme beaucoup de messages.** Avec un abonnement Pro, une grosse figure peut te faire atteindre ta limite. Commence par un concept simple.
- **Il dessine des machines, pas des personnes.** Pas de personnages, pas de cartes, pas de graphiques avec des axes. Un concept qui n'a aucun mécanisme donnera un résultat plus faible.
- **La 3D est en bêta.** Les figures en SVG classique sont les plus fiables.

## Partager ta figure

Si ta machine te plaît, demande simplement à Claude : « publie cette figure dans la galerie communautaire d'Anatomy ». Il te demande un titre et ton pseudo GitHub, te montre ce qu'il va envoyer, et propose la figure sur [anatomy-community](https://github.com/wheresryan22/anatomy-community) après ton accord.

## Mettre à jour ou désinstaller

Pour mettre à jour, relance la même commande que pour l'installation :

```bash
npx skills add wheresryan22/anatomy -g -a claude-code
```

Pour le retirer, supprime simplement le dossier `anatomy` dans `~/.claude/skills/` (sur Windows : `C:\Users\<ton-nom>\.claude\skills\`).

## Ça ne marche pas ?

- **`npx` n'est pas reconnu** : Node.js n'est pas installé, ou ton terminal était déjà ouvert pendant l'installation. Ferme-le, rouvre-le, et vérifie `node -v`.
- **Erreur sur la version de Node.js** : il te faut la 22.20 au minimum. Installe la 24 LTS.
- **`/anatomy` n'apparaît pas** : tape `/reload-skills`, ou redémarre Claude Code.
- **Les vérifications dans Chrome échouent** : la figure est quand même construite, seules les captures manquent. Installe Google Chrome, ou indique son chemin à Claude.

Le code complet (en anglais) est sur [le repo GitHub d'Anatomy](https://github.com/wheresryan22/anatomy), et la galerie sur [skills.wheresryan.sh/anatomy](https://skills.wheresryan.sh/anatomy).
