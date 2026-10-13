---
layout: ../../layouts/Article.astro
title: Installer Reverse Engineer Anything (REA) sur Windows ou Linux
description: Le guide pas à pas pour installer REA en local et le brancher à ton agent IA (Claude Code, Cursor, Codex…), même si tu débutes.
date: 2026-10-13
---

Reverse Engineer Anything (REA) est un outil open source qui donne à ton agent IA (Claude Code, Cursor, Codex…) des outils de reverse engineering. Tu lui montres une appli, tu lui demandes comment une fonctionnalité marche, et il va chercher la réponse dans l'appli elle-même, avec les preuves.

Ce guide part de zéro. Compte 10 minutes pour la partie de base, et 15 de plus si tu veux analyser des programmes natifs (des `.exe`, des binaires Linux).

> Avant de commencer : utilise REA uniquement sur des logiciels que tu as le droit d'analyser (les tiens, de l'open source, ou avec l'accord de l'éditeur). Beaucoup de licences interdisent la décompilation.

## Ce qu'il te faut

| | Obligatoire ? | Pourquoi |
|---|---|---|
| Node.js 22.19+, 24.11+ ou 26+ | Oui | REA est un paquet npm |
| Un agent IA (Claude Code, Cursor, Codex, Gemini CLI, VS Code…) | Oui | C'est lui qui utilise REA |
| Ghidra + Java 21 | Seulement pour les programmes natifs | Le moteur qui ouvre les binaires |

Pour les applis JavaScript ou Electron et pour les sites web, Node.js suffit. Ghidra ne sert que pour les vrais binaires.

Attention : les versions 23 et 25 de Node.js ne sont pas supportées.

## Étape 1 : installer Node.js

### Sur Windows

1. Va sur [nodejs.org](https://nodejs.org) et télécharge la version **LTS** (la 24, en ce moment).
2. Lance l'installeur et laisse les options par défaut.
3. Ouvre **PowerShell** (touche Windows, tape « PowerShell ») et vérifie :

```powershell
node -v
npm -v
```

Tu dois voir un numéro qui commence par `v24` (ou `v22.19` minimum).

### Sur Linux

Les paquets de ta distribution sont souvent trop vieux. Le plus simple est de passer par **nvm**, qui installe Node.js dans ton dossier perso, sans `sudo`. Copie la commande d'installation donnée sur [github.com/nvm-sh/nvm](https://github.com/nvm-sh/nvm), ferme puis rouvre ton terminal, et lance :

```bash
nvm install 24
node -v
```

## Étape 2 : lancer l'installation de REA

C'est une seule commande, la même sur Windows (PowerShell) et sur Linux :

```bash
npx rea-agents@latest setup
```

Ce qui va se passer :

1. npm te demande s'il peut télécharger le paquet `rea-agents`. Réponds oui.
2. REA te montre la liste des agents qu'il sait configurer. Coche le tien avec la barre espace, puis valide avec Entrée.
3. Il t'affiche **le plan exact** de ce qu'il va modifier : les fichiers de configuration de ton agent, l'endroit où il range ses instructions. Rien n'est écrit tant que tu n'as pas dit oui. Il fait aussi une sauvegarde de tes fichiers avant d'y toucher.
4. Tu approuves, et c'est installé.

Si tu utilises Claude Desktop, quitte-le complètement avant d'approuver, sinon il peut écraser la configuration.

Pour finir, **redémarre ton agent** (ferme et rouvre Claude Code, Cursor…). Sans ça, il ne voit pas encore les nouveaux outils.

## Étape 3 : vérifier que tout marche

```bash
npx rea-agents@latest doctor
```

Cette commande ne modifie rien, elle fait juste un bilan. Ne panique pas si elle affiche `healthy: false` : elle vérifie aussi Ghidra, Hopper et IDA, et tu n'en as peut-être pas encore. Ce qui compte, c'est que ton agent apparaisse comme correctement enregistré.

Pour vérifier seulement ton agent (ici Claude Code) :

```bash
npx rea-agents@latest doctor --client claude_code --json
```

Les autres noms possibles : `cursor`, `codex`, `gemini_cli`, `vscode`, `windsurf`, `opencode`, `claude_desktop`…

Si tu préfères avoir une commande `rea` toujours disponible dans ton terminal, installe-le globalement :

```bash
npm install --global rea-agents
rea --help
```

## Étape 4 : ton premier test

Ouvre ton agent et demande-lui, en langage normal :

```text
Utilise REA pour comprendre comment marche la recherche dans [ton appli],
montre-moi les preuves, puis propose-moi une version pour mon projet.
```

Remplace l'appli et la fonctionnalité par ce que tu veux étudier. Pour une appli Electron ou un site, ça marche tout de suite. Pour un programme natif, il te faut l'étape suivante.

Tu peux aussi tester REA sans agent, directement sur le dossier d'une appli JavaScript ou Electron :

```bash
npx -y rea-agents@latest analyze-javascript-application /chemin/absolu/vers/l-appli --json
```

## Étape 5 (optionnelle) : Ghidra pour les programmes natifs

Ghidra est le logiciel de reverse engineering gratuit de la NSA. REA s'en sert pour ouvrir les binaires. Il te faut **Ghidra 12.1.x** et **un JDK 21 complet** (64 bits).

### 1. Installer Java 21

Télécharge le JDK 21 de [Adoptium (Temurin)](https://adoptium.net/temurin/releases/?version=21) pour ton système et installe-le. Prends bien le **JDK**, pas le JRE.

### 2. Télécharger Ghidra

Récupère le zip `ghidra_12.1.4_PUBLIC_….zip` sur la [page des releases de Ghidra](https://github.com/NationalSecurityAgency/ghidra/releases) et décompresse-le dans un dossier simple, par exemple `C:\tools\` sur Windows ou `~/tools/` sur Linux.

### 3. Dire à REA où ils sont

Sur **Windows**, dans PowerShell (adapte les chemins à ton installation) :

```powershell
setx GHIDRA_INSTALL_DIR "C:\tools\ghidra_12.1.4_PUBLIC"
setx JAVA_HOME "C:\Program Files\Eclipse Adoptium\jdk-21"
```

`setx` enregistre les variables pour de bon, mais seulement pour les **nouveaux** terminaux : ferme PowerShell et rouvre-le.

Sur **Linux**, ajoute ces lignes à la fin de ton `~/.bashrc` (ou `~/.zshrc`), puis rouvre ton terminal :

```bash
export GHIDRA_INSTALL_DIR="$HOME/tools/ghidra_12.1.4_PUBLIC"
export JAVA_HOME="/chemin/vers/jdk-21"
```

### 4. Vérifier, puis relancer le setup

```bash
npx rea-agents@latest doctor --provider ghidra --json
npx rea-agents@latest setup
```

Le second `setup` est important : il enregistre les chemins de Ghidra et de Java dans la configuration de ton agent. Sinon, l'agent ne les trouve pas quand il démarre. Redémarre ton agent après.

### Les cas particuliers

- **Windows** : le support de Ghidra est encore **expérimental**. Il marche pour les `.exe` et `.dll` natifs (x86 et x64), en lecture seule, sur un disque local NTFS.
- **Linux sur processeur ARM** (Raspberry Pi, certains serveurs) : l'archive de Ghidra ne contient pas le décompilateur pour ARM. Il faut le compiler une fois : va dans `support/gradle` du dossier Ghidra et lance `./gradlew buildNatives`.
- **Mac Apple Silicon** : même chose, `./gradlew buildNatives`. Je l'ai fait sur mon Mac, ça prend une trentaine de secondes.
- **Gros programmes** : la première analyse peut être longue (plusieurs minutes). Si ça coupe, augmente le délai avec la variable `REA_GHIDRA_STARTUP_TIMEOUT_MS` (en millisecondes).

Hopper (payant, version démo gratuite) et IDA marchent aussi, mais Ghidra suffit largement pour commencer.

## Mettre à jour ou désinstaller

REA évolue vite. Pour le mettre à jour, relance simplement :

```bash
npx rea-agents@latest setup
```

Si tu l'as installé globalement, `rea update` fait la mise à jour. Pour tout retirer proprement, utilise `rea uninstall`. Ça enlève seulement ce que REA a ajouté, sans toucher à Node.js, Ghidra ni à tes autres outils.

## Ça ne marche pas ?

- **Ton agent ne voit pas les outils REA** : redémarre-le complètement, puis lance `doctor --client <ton-agent>`.
- **Erreur sur la version de Node.js** : vérifie `node -v`. Il te faut la 22.19 minimum, la 24.11 minimum ou la 26, mais pas la 23 ni la 25.
- **Ghidra introuvable** : vérifie que `GHIDRA_INSTALL_DIR` pointe bien vers le dossier qui contient `support/` et `Ghidra/`, puis relance `setup`.

La doc complète (en anglais) est sur [le repo GitHub de REA](https://github.com/morluto/rea) et sur [rea.tools](https://rea.tools).
