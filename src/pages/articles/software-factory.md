---
layout: ../../layouts/Article.astro
title: Monter ta software factory, des tickets Linear codés par un agent toutes les heures
description: Le guide pas à pas pour brancher Linear sur un agent de code (Claude Code), le faire tourner sur un VPS ou dans GitHub Actions, et le laisser ouvrir des PR tout seul.
date: 2026-10-17
---

Une software factory, c'est une usine à logiciels. Tu écris un ticket, et des agents IA font le reste : ils lisent le ticket, écrivent le code, lancent les tests, corrigent ce qui casse, et t'envoient une pull request. Toi, tu ne codes plus le ticket. Tu entretiens l'usine.

Des équipes le font déjà pour de vrai. Chez OpenAI, une équipe a sorti un outil interne d'à peu près un million de lignes sans en taper une seule ([leur article « Harness engineering »](https://openai.com/index/harness-engineering/)). Chez StrongDM, c'est même la règle : le code n'est ni écrit ni relu par un humain ([leur page « Software Factory »](https://factory.strongdm.ai/)).

Ce guide te montre comment monter **ta version à toi**, simple et que tu comprends de bout en bout :

- tes tickets vivent dans **Linear** ;
- toutes les heures, un petit script les récupère, soit sur un **VPS** avec un cron, soit dans **GitHub Actions** ;
- pour chaque ticket, **Claude Code** code, teste et corrige jusqu'à ce que les tests passent ;
- le script ouvre une **pull request** et met le ticket à jour dans Linear.

Compte une heure pour tout installer. Le vrai travail commence après : rendre ton repo assez clair pour qu'un agent y travaille seul.

<svg class="dg" viewBox="0 0 560 640" role="img" aria-label="La boucle de la software factory : un ticket Linear, l'orchestrateur qui tourne toutes les heures, l'agent qui code et teste, la pull request, et toi qui entretiens la machine.">
<defs><marker id="f1a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" class="ah"/></marker><marker id="f1p" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" class="ahp"/></marker></defs>
<rect x="130" y="20" width="300" height="76" rx="14" class="b"/>
<text x="280" y="52" text-anchor="middle" class="t">1. Linear</text>
<text x="280" y="76" text-anchor="middle" class="s">un ticket avec le label « factory »</text>
<line x1="280" y1="96" x2="280" y2="142" class="l" marker-end="url(#f1a)"/>
<rect x="130" y="146" width="300" height="76" rx="14" class="b"/>
<text x="280" y="178" text-anchor="middle" class="t">2. L'orchestrateur</text>
<text x="280" y="202" text-anchor="middle" class="s">VPS (cron) ou GitHub Actions, chaque heure</text>
<line x1="280" y1="222" x2="280" y2="268" class="l" marker-end="url(#f1a)"/>
<rect x="130" y="272" width="300" height="76" rx="14" class="b"/>
<text x="280" y="304" text-anchor="middle" class="t">3. L'agent (Claude Code)</text>
<text x="280" y="328" text-anchor="middle" class="s">lit le ticket, code, lance les tests</text>
<path d="M430 290 C 500 290, 500 330, 434 330" class="lp" marker-end="url(#f1p)"/>
<text x="478" y="272" text-anchor="middle" class="sp">rouge ?</text>
<text x="478" y="360" text-anchor="middle" class="sp">il corrige</text>
<line x1="280" y1="348" x2="280" y2="394" class="l" marker-end="url(#f1a)"/>
<rect x="130" y="398" width="300" height="76" rx="14" class="b"/>
<text x="280" y="430" text-anchor="middle" class="t">4. Pull request</text>
<text x="280" y="454" text-anchor="middle" class="s">+ le ticket mis à jour dans Linear</text>
<line x1="280" y1="474" x2="280" y2="520" class="l" marker-end="url(#f1a)"/>
<rect x="130" y="524" width="300" height="76" rx="14" class="bp"/>
<text x="280" y="556" text-anchor="middle" class="tp">5. Toi</text>
<text x="280" y="580" text-anchor="middle" class="tp" style="font-weight:400;font-size:14px">tu relis, tu merges, tu répares la machine</text>
<path d="M130 562 C 40 562, 40 184, 126 184" class="lp dash" marker-end="url(#f1p)"/>
<text x="62" y="360" text-anchor="middle" class="sp" transform="rotate(-90 62 360)">tu améliores l'usine</text>
</svg>

## Ce qu'il te faut

| | Obligatoire ? | Pourquoi |
|---|---|---|
| Un repo GitHub **avec des tests qui tournent** (`npm test` ou autre) | Oui | C'est le seul moyen pour l'agent (et pour toi) de savoir que le code marche |
| Un compte **Linear** | Oui | C'est là que tu écris les tickets |
| **Claude Code** + une clé API Anthropic | Oui | C'est l'agent qui code. La clé API te permet de suivre et de plafonner ce que coûte chaque ticket |
| Le **CLI GitHub** (`gh`) | Oui | Pour ouvrir les pull requests depuis le script |
| Un **VPS** (Linux) **ou** GitHub Actions | L'un des deux | C'est l'orchestrateur, la machine qui tourne toutes les heures |
| Node.js 22 ou plus | Oui | Le script de l'usine est écrit en JavaScript, sans aucune dépendance |

Le script de ce guide utilise Claude Code, mais le principe marche avec n'importe quel agent qui tourne en ligne de commande (Codex, par exemple).

## Étape 1 : préparer le repo pour un agent

C'est l'étape la plus importante, et celle que tout le monde saute. Un agent qui arrive dans ton repo ne connaît rien : ni ta stack, ni tes conventions, ni la commande qui lance les tests. Tout ce qu'il sait, c'est ce que tu as écrit.

Crée un fichier `CLAUDE.md` à la racine du repo. Claude Code le lit automatiquement au début de chaque session. Garde-le court et concret :

```md
# Règles pour les agents

- Stack : Next.js, TypeScript strict, Prisma, Postgres.
- Avant de terminer : `npm run lint` puis `npm test` doivent passer.
- Un ticket = un petit changement. Ne touche pas aux fichiers sans rapport avec le ticket.
- Toute nouvelle fonction a au moins un test.
- Pas de nouvelle dépendance sans le signaler dans ton résumé final.
- Si le ticket est ambigu, choisis le comportement le plus simple et explique ton choix dans le résumé.
- Les dates s'affichent au format JJ/MM/AAAA (utilise `formatDate` dans `src/lib/date.ts`).
```

Deux choses comptent plus que tout le reste :

1. **Des tests rapides et fiables.** Un test qui échoue une fois sur dix va rendre l'agent fou : il va « corriger » du code qui marchait. Commence par rendre ta suite de tests verte et stable.
2. **Une seule commande pour tout vérifier.** Si l'agent doit deviner comment lancer les tests, il se trompera. `npm test` doit suffire.

C'est ce qu'OpenAI appelle le *harness engineering* : ton travail n'est plus d'écrire le code, c'est de construire l'environnement dans lequel un agent peut écrire du code correct.

## Étape 2 : préparer Linear

### Un label et des statuts

Dans Linear, crée un label **`factory`**. C'est l'interrupteur : seuls les tickets avec ce label partent à l'usine. Les autres restent pour les humains.

Le script utilise les statuts par défaut de Linear :

<svg class="dg wide" viewBox="0 0 680 230" role="img" aria-label="Le parcours d'un ticket : Todo avec le label factory, puis In Progress quand l'agent le prend, puis In Review avec une pull request, puis Done quand tu merges. S'il bloque, il reste en In Progress avec une PR brouillon et un commentaire.">
<defs><marker id="f2a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" class="ah"/></marker><marker id="f2p" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" class="ahp"/></marker></defs>
<rect x="10" y="20" width="140" height="64" rx="12" class="b"/>
<text x="80" y="50" text-anchor="middle" class="t">Todo</text>
<text x="80" y="72" text-anchor="middle" class="sp">+ « factory »</text>
<line x1="150" y1="52" x2="182" y2="52" class="l" marker-end="url(#f2a)"/>
<rect x="186" y="20" width="140" height="64" rx="12" class="b"/>
<text x="256" y="50" text-anchor="middle" class="t">In Progress</text>
<text x="256" y="72" text-anchor="middle" class="s">l'agent code</text>
<line x1="326" y1="52" x2="358" y2="52" class="l" marker-end="url(#f2a)"/>
<rect x="362" y="20" width="140" height="64" rx="12" class="b"/>
<text x="432" y="50" text-anchor="middle" class="t">In Review</text>
<text x="432" y="72" text-anchor="middle" class="s">PR à relire</text>
<line x1="502" y1="52" x2="534" y2="52" class="l" marker-end="url(#f2a)"/>
<rect x="538" y="20" width="132" height="64" rx="12" class="bp"/>
<text x="604" y="50" text-anchor="middle" class="tp">Done</text>
<text x="604" y="72" text-anchor="middle" class="tp" style="font-weight:400;font-size:14px">tu as mergé</text>
<line x1="256" y1="84" x2="256" y2="136" class="lp dash" marker-end="url(#f2p)"/>
<rect x="120" y="140" width="272" height="72" rx="12" class="b"/>
<text x="256" y="170" text-anchor="middle" class="t">Bloqué après 3 essais</text>
<text x="256" y="194" text-anchor="middle" class="s">PR brouillon + commentaire</text>
</svg>

Si ton équipe n'a pas de statut **In Review**, crée-le dans les réglages de l'équipe (Workflow), ou le script laissera simplement le ticket en In Progress.

### Un modèle de ticket

Un agent ne pose pas de questions. Tout ce qu'il ne trouve pas dans le ticket, il l'invente. Crée un modèle de ticket dans Linear et utilise-le pour chaque ticket « factory » :

```md
## Contexte
Les comptables doivent exporter les factures du mois pour leur logiciel.

## Ce qui est attendu
Un bouton « Exporter en CSV » sur la page /factures télécharge les factures
du mois affiché, une ligne par facture.

## Critères d'acceptation (testables)
- [ ] Colonnes : numero, date (JJ/MM/AAAA), client, montant_ttc
- [ ] Les montants utilisent la virgule : 19,99
- [ ] Un mois sans facture télécharge un CSV avec seulement l'en-tête

## Où regarder
src/app/factures/page.tsx, src/lib/invoices.ts

## Hors sujet
Ne change pas le design de la page.
```

Les **critères d'acceptation** sont la partie la plus utile : ce sont des tests déjà écrits en français. L'agent n'a plus qu'à les traduire en code.

Commence par des tickets petits et précis : un bug avec les étapes pour le reproduire, une petite feature, une migration répétitive. Garde les gros chantiers flous pour les humains.

### La clé API

Dans Linear, va dans **Settings → Security & access → Personal API keys** et crée une clé. Garde-la de côté : ce sera `LINEAR_API_KEY`.

## Étape 3 : le script de l'usine

Voici le cœur de la factory. Un seul fichier, `factory/run.mjs`, sans aucune dépendance (Node.js 22 a `fetch` intégré). À chaque passage, il :

1. demande à Linear un ticket avec le label `factory` et le statut Todo ;
2. le passe en In Progress et crée une branche `factory/eng-123` ;
3. lance Claude Code en mode non interactif avec le contenu du ticket ;
4. lance lui-même `npm test`, et si c'est rouge, renvoie les erreurs à l'agent (3 essais maximum) ;
5. pousse la branche, ouvre une PR (en brouillon si c'est toujours rouge), commente le ticket dans Linear avec le lien.

```js
// factory/run.mjs : un passage de la software factory.
// Prend un ticket Linear « factory », le fait coder par Claude Code, vérifie les tests, ouvre une PR.
import { execFileSync, spawnSync } from "node:child_process";

const MAX_TRIES = 3;                    // corrections autorisées quand les tests échouent
const TEST = ["npm", ["test"]];         // la commande qui dit si le code marche

const sh = (cmd, args) => execFileSync(cmd, args, { encoding: "utf8" }).trim();

async function linear(query, variables = {}) {
  const res = await fetch("https://api.linear.app/graphql", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: process.env.LINEAR_API_KEY },
    body: JSON.stringify({ query, variables }),
  });
  const { data, errors } = await res.json();
  if (errors) throw new Error(JSON.stringify(errors));
  return data;
}

const comment = (issueId, body) =>
  linear(`mutation($input: CommentCreateInput!) { commentCreate(input: $input) { success } }`,
    { input: { issueId, body } });

async function moveTo(issue, name) {
  const state = issue.team.states.nodes.find((s) => s.name === name);
  if (!state) return;   // ce statut n'existe pas dans l'équipe : on laisse le ticket où il est
  await linear(`mutation($id: String!, $stateId: String!) { issueUpdate(id: $id, input: { stateId: $stateId }) { success } }`,
    { id: issue.id, stateId: state.id });
}

function agent(prompt, sessionId) {
  const args = ["-p", prompt, "--output-format", "json",
    "--permission-mode", "acceptEdits",                                   // il peut modifier les fichiers du repo
    "--allowedTools", "Bash(npm test *),Bash(npm run *),Bash(git diff *),Bash(git status *)",
    "--max-turns", "80", "--max-budget-usd", "5"];                        // garde-fous : temps et argent
  if (sessionId) args.push("--resume", sessionId);                        // on reprend la même conversation
  const out = spawnSync("claude", args, { encoding: "utf8", maxBuffer: 50e6 });
  try { return JSON.parse(out.stdout); } catch { return { result: out.stdout || out.stderr }; }
}

function tests() {
  const r = spawnSync(TEST[0], TEST[1], { encoding: "utf8", maxBuffer: 50e6 });
  return { ok: r.status === 0, log: (r.stdout + r.stderr).slice(-6000) };
}

// 1. un ticket avec le label « factory », pas encore commencé
const { issues } = await linear(`{
  issues(first: 1, orderBy: createdAt, filter: {
    labels: { name: { eq: "factory" } }
    state: { type: { eq: "unstarted" } }
  }) {
    nodes { id identifier title description url team { states { nodes { id name } } } }
  }
}`);
const issue = issues.nodes[0];
if (!issue) { console.log("Rien à faire."); process.exit(0); }

// 2. on le prend
const branch = `factory/${issue.identifier.toLowerCase()}`;
await moveTo(issue, "In Progress");
await comment(issue.id, "🤖 La factory prend ce ticket.");
sh("git", ["checkout", "main"]);
sh("git", ["pull", "--ff-only"]);
sh("git", ["checkout", "-B", branch]);

// 3 et 4. l'agent code, on vérifie nous-mêmes, et on lui renvoie les erreurs
let run = agent(`Ticket ${issue.identifier} : ${issue.title}\n\n${issue.description ?? ""}\n\n` +
  "Implémente ce ticket dans ce repo en respectant CLAUDE.md. Ajoute ou mets à jour les tests. " +
  "Lance npm test et corrige jusqu'à ce que tout passe. Ne fais ni commit ni push. " +
  "Termine par un résumé de ce que tu as changé et des choix que tu as faits.");
let check = tests();
for (let i = 1; !check.ok && i < MAX_TRIES; i++) {
  run = agent(`Les tests échouent encore :\n\n${check.log}\n\nCorrige le code. Ne modifie un test que s'il est faux.`, run.session_id);
  check = tests();
}

// 5. on livre : PR normale si c'est vert, brouillon si c'est encore rouge
sh("git", ["add", "-A"]);
sh("git", ["commit", "--allow-empty", "-m", `${issue.identifier}: ${issue.title}`]);
sh("git", ["push", "-u", "origin", branch, "--force-with-lease"]);
const pr = sh("gh", ["pr", "create", ...(check.ok ? [] : ["--draft"]), "--base", "main", "--head", branch,
  "--title", `${issue.identifier}: ${issue.title}`,
  "--body", `Fixes ${issue.identifier}\n\n${run.result ?? ""}\n\n_Ouverte par la software factory._`]);

if (check.ok) {
  await comment(issue.id, `✅ PR prête à relire : ${pr}`);
  await moveTo(issue, "In Review");
} else {
  await comment(issue.id, `🛑 Bloqué après ${MAX_TRIES} essais. PR brouillon : ${pr}\n\n` +
    "```\n" + check.log.slice(-1500) + "\n```\n" +
    "Il manque sûrement quelque chose à la machine : un ticket trop flou, un test, une règle dans CLAUDE.md.");
}
console.log(pr);
```

Quelques détails qui comptent :

- **Le script ne fait pas confiance à l'agent.** Même si Claude dit « les tests passent », c'est le script qui relance `npm test` et qui décide. C'est la différence entre un agent et une usine.
- **`--allowedTools`** liste les seules commandes que l'agent peut lancer sans demander : les tests, les scripts npm, et lire l'état de git. Il ne peut pas pousser, ni installer n'importe quoi.
- **`--max-turns` et `--max-budget-usd`** plafonnent un ticket qui part en vrille. 5 dollars par ticket, c'est large pour un petit changement.
- **`--resume`** reprend la même conversation pour les corrections : l'agent se souvient de ce qu'il a déjà essayé.
- **`Fixes ENG-123`** dans la PR : si tu as installé l'intégration GitHub de Linear, le ticket passe tout seul en Done quand tu merges.
- **Un ticket par passage.** Si tu as 5 tickets, il en traite un par heure. C'est volontaire au début : tu relis au rythme de l'usine.

Pour tester sur ta machine avant d'automatiser, mets un ticket « factory » en Todo et lance :

```bash
export LINEAR_API_KEY=lin_api_...
export ANTHROPIC_API_KEY=sk-ant-...
node factory/run.mjs
```

## Étape 4, option A : sur un VPS avec un cron

N'importe quel petit VPS Linux suffit (2 Go de RAM), du moment que ton projet s'y installe et que ses tests tournent.

1. Crée un utilisateur dédié, sans droits sudo, pour que l'agent ne touche à rien d'autre sur la machine :

```bash
sudo adduser --disabled-password factory
sudo -iu factory
```

2. Installe Node.js 22 ou plus, le CLI GitHub (`gh`) et Claude Code :

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

3. Clone ton repo, installe ses dépendances, et vérifie que `npm test` passe.

4. Connecte `gh` avec un token GitHub limité à ce repo (un *fine-grained token* avec les droits **Contents** et **Pull requests** en écriture) :

```bash
gh auth login --with-token < token.txt
gh auth setup-git
```

5. Crée un fichier `.env` à la racine du repo (et ajoute-le à `.gitignore`) :

```bash
LINEAR_API_KEY=lin_api_...
ANTHROPIC_API_KEY=sk-ant-...
```

6. Ajoute un petit lanceur `factory/cron.sh` :

```bash
#!/usr/bin/env bash
cd "$(dirname "$0")/.."
set -a; source .env; set +a
exec node factory/run.mjs
```

7. Et le cron, avec `crontab -e` :

```bash
0 * * * * flock -n /tmp/factory.lock /home/factory/mon-repo/factory/cron.sh >> /home/factory/factory.log 2>&1
```

`flock -n` empêche deux passages de tourner en même temps : si un ticket prend plus d'une heure, le passage suivant est simplement sauté. Pour voir ce qui se passe : `tail -f ~/factory.log`.

## Étape 4, option B : dans GitHub Actions

Pas de serveur à gérer : GitHub lance le script toutes les heures sur une machine neuve. Ajoute ce fichier dans ton repo, `.github/workflows/factory.yml` :

```yaml
name: software-factory

on:
  schedule:
    - cron: "17 * * * *"    # toutes les heures (à la 17e minute, hors du pic de début d'heure)
  workflow_dispatch:         # bouton pour lancer un passage à la main

concurrency:
  group: software-factory    # jamais deux passages en même temps
  cancel-in-progress: false

jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.FACTORY_GITHUB_TOKEN }}

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - run: npm ci

      - name: Installer Claude Code
        run: |
          curl -fsSL https://claude.ai/install.sh | bash
          echo "$HOME/.local/bin" >> "$GITHUB_PATH"

      - run: |
          git config user.name "software-factory"
          git config user.email "software-factory@users.noreply.github.com"

      - run: node factory/run.mjs
        env:
          LINEAR_API_KEY: ${{ secrets.LINEAR_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GH_TOKEN: ${{ secrets.FACTORY_GITHUB_TOKEN }}
```

Ajoute les trois secrets dans **Settings → Secrets and variables → Actions** du repo.

Pourquoi un token à toi (`FACTORY_GITHUB_TOKEN`) plutôt que le token automatique de GitHub Actions ? Parce que les pull requests ouvertes avec le token automatique ne déclenchent pas les autres workflows : ta CI ne tournerait pas sur les PR de l'usine. Un *fine-grained token* limité au repo, avec **Contents** et **Pull requests** en écriture, règle le problème.

Trois limites à connaître, tirées de la doc de GitHub :

- le cron tourne au mieux **toutes les 5 minutes**, et il peut être **retardé** quand GitHub est chargé, en particulier en début d'heure. C'est pour ça que le workflow tourne à `17 * * * *` plutôt qu'à `0 * * * *` ;
- il ne tourne que sur la **branche par défaut** du repo ;
- sur un repo public, les crons sont **désactivés après 60 jours sans activité**.

### VPS ou GitHub Actions ?

| | VPS + cron | GitHub Actions |
|---|---|---|
| Mise en place | Une heure de config serveur | Un fichier YAML |
| Coût | Quelques euros par mois | Gratuit sur les repos publics, minutes comptées sur les privés |
| Machine | Toujours la même : dépendances déjà installées, base de données de test qui reste en place | Neuve à chaque passage : tout se réinstalle |
| Ponctualité | À la minute | Peut avoir du retard |
| Ce qui tourne à côté | Ce que tu veux (Postgres, Redis, un navigateur…) | Ce que tu déclares dans le workflow |

Mon conseil : commence avec **GitHub Actions** pour essayer en dix minutes. Passe sur un **VPS** quand tes tests ont besoin de services (une vraie base de données, des fichiers lourds) ou quand tu veux plusieurs passages par heure.

## Étape 5 : faire tourner la boucle

Une fois en place, l'usine tourne avec deux boucles. La petite, c'est l'agent qui corrige ses propres erreurs. La grande, c'est toi qui corriges l'usine.

<svg class="dg" viewBox="0 0 560 500" role="img" aria-label="Les deux boucles : l'agent code, le script lance les tests, si c'est rouge les erreurs repartent à l'agent jusqu'à trois fois, si c'est vert une PR est ouverte. Si ça bloque, toi tu cherches ce qui manquait à la machine et tu améliores CLAUDE.md, les tests ou le ticket.">
<defs><marker id="f3a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" class="ah"/></marker><marker id="f3p" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" class="ahp"/></marker></defs>
<rect x="40" y="30" width="200" height="70" rx="14" class="b"/>
<text x="140" y="61" text-anchor="middle" class="t">L'agent code</text>
<text x="140" y="84" text-anchor="middle" class="s">à partir du ticket</text>
<line x1="240" y1="65" x2="316" y2="65" class="l" marker-end="url(#f3a)"/>
<rect x="320" y="30" width="200" height="70" rx="14" class="b"/>
<text x="420" y="61" text-anchor="middle" class="t">Le script teste</text>
<text x="420" y="84" text-anchor="middle" class="s">npm test</text>
<path d="M420 100 C 420 160, 140 160, 140 104" class="lp" marker-end="url(#f3p)"/>
<text x="280" y="188" text-anchor="middle" class="sp">rouge : les erreurs repartent à l'agent (3 fois max)</text>
<line x1="520" y1="65" x2="540" y2="65" class="l"/>
<line x1="540" y1="65" x2="540" y2="244" class="l" marker-end="url(#f3a)"/>
<rect x="360" y="248" width="190" height="64" rx="14" class="b"/>
<text x="455" y="276" text-anchor="middle" class="t">Vert : une PR</text>
<text x="455" y="298" text-anchor="middle" class="s">tu relis, tu merges</text>
<line x1="155" y1="204" x2="155" y2="244" class="lp dash" marker-end="url(#f3p)"/>
<rect x="30" y="248" width="250" height="64" rx="14" class="b"/>
<text x="155" y="276" text-anchor="middle" class="t">Toujours rouge : bloqué</text>
<text x="155" y="298" text-anchor="middle" class="s">PR brouillon + commentaire</text>
<line x1="155" y1="312" x2="155" y2="348" class="l" marker-end="url(#f3a)"/>
<rect x="30" y="352" width="500" height="120" rx="14" class="bp"/>
<text x="280" y="386" text-anchor="middle" class="tp">Toi : qu'est-ce qui manquait à la machine ?</text>
<text x="280" y="416" text-anchor="middle" class="tp" style="font-weight:400;font-size:15px">une règle dans CLAUDE.md, un test qui aurait guidé l'agent,</text>
<text x="280" y="440" text-anchor="middle" class="tp" style="font-weight:400;font-size:15px">un ticket plus précis… puis tu remets le ticket en Todo</text>
</svg>

Quand un ticket bloque, le réflexe naturel, c'est de prendre la main et de coder la correction toi-même. Ne le fais pas (ou pas seulement). Pose-toi la question que se pose l'équipe d'OpenAI : **qu'est-ce qui manquait à la machine pour réussir seule ?** Quelques exemples :

- L'agent a affiché les dates à l'américaine → ajoute la règle des dates dans `CLAUDE.md`, et un test sur le format.
- L'agent a « corrigé » un test au lieu du code → ajoute dans `CLAUDE.md` : « ne modifie jamais un test existant sans le justifier dans le résumé ».
- L'agent n'a pas trouvé où était la logique de paiement → ajoute une section « Où sont les choses » dans `CLAUDE.md`.
- L'agent a fait autre chose que ce que tu voulais → c'est le ticket qui était flou. Améliore le modèle de ticket.

Chaque correction de la machine profite à **tous les tickets suivants**. C'est pour ça qu'au bout de quelques semaines, l'usine bloque de moins en moins. Et c'est ça, le nouveau métier : tu n'écris plus le code, tu entretiens l'usine qui l'écrit.

## Les garde-fous

- **Relis toutes les PR au début.** StrongDM va jusqu'à ne plus relire le code, mais ils ont construit des tests énormes pour ça. Toi, commence avec la relecture humaine, et ne la lâche que sur les types de tickets où l'usine ne s'est jamais trompée.
- **Aucun secret de production sur la machine de l'usine.** L'agent lance des commandes : s'il peut lire une clé, il peut la mettre dans un log. Donne-lui seulement ce qu'il faut pour coder et tester.
- **Protège la branche main** dans GitHub (Settings → Branches) : l'usine ne doit pouvoir passer que par des PR.
- **N'utilise pas `--dangerously-skip-permissions`** sur un VPS : ça laisse l'agent lancer n'importe quelle commande. La liste `--allowedTools` est plus sûre.
- **Surveille la facture.** `--max-budget-usd` plafonne chaque ticket, et la sortie JSON de Claude Code donne une estimation du coût (`total_cost_usd`) que tu peux ajouter au commentaire Linear.

## Combien ça coûte ?

Pour un petit changement bien décrit, compte quelques dizaines de centimes à quelques dollars de tokens par ticket. Un ticket flou, qui part en corrections, coûte beaucoup plus : c'est une raison de plus pour soigner tes tickets.

À l'autre bout du spectre, StrongDM dit qu'une software factory qui ne dépense pas au moins **1 000 dollars de tokens par jour et par ingénieur** a encore de la marge pour s'améliorer. C'est leur règle à eux, pour une usine qui tourne à plein régime, pas un passage obligé. Ton usine peut commencer à quelques euros par semaine.

## Pour aller plus loin

- **Un webhook au lieu du cron.** Linear peut appeler une URL dès qu'un ticket change. Ton usine démarre alors en quelques secondes au lieu d'attendre l'heure suivante.
- **Un agent relecteur.** Ajoute une étape où un second agent relit la PR (avec `gh pr diff` et `claude -p`) avant que tu la voies.
- **Plusieurs tickets en parallèle.** Un dossier de travail par ticket (avec `git worktree`), et un passage qui en traite plusieurs à la fois.
- **Symphony**, l'orchestrateur open source d'OpenAI, fait exactement ce montage en version complète : il surveille un tableau Linear et lance un agent par ticket, chacun dans son espace isolé. Le code est sur [github.com/openai/symphony](https://github.com/openai/symphony). OpenAI le présente comme un aperçu à tester dans un environnement de confiance, et il marche mieux sur un repo déjà préparé pour les agents (l'étape 1 de ce guide).

Les lectures qui ont inspiré ce guide : [Harness engineering](https://openai.com/index/harness-engineering/) (OpenAI), [Software Factories and the Agentic Moment](https://factory.strongdm.ai/) (StrongDM), et [la doc de Claude Code en mode non interactif](https://code.claude.com/docs/en/headless).
