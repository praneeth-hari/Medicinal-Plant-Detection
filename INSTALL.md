# Install guide

Commands come from each project's own README as pasted. Project names and flags change, so read the README of anything you install and check you are using the official source. Install in the order below. Start with Step 1 and add the rest only when you need them.

## Step 1. Put the kit in place

Copy these into the root of each project (or into a shared template repo):

```
CLAUDE.md      # Claude Code reads this
AGENTS.md      # Antigravity and other agents read this (same content)
LESSONS.md
roles/
```

Keep `CLAUDE.md` and `AGENTS.md` identical. After editing one: `cp CLAUDE.md AGENTS.md`.

Fill in the "Project overrides" block at the bottom of `CLAUDE.md` for each project.

## Step 2. Core skill pack: Addy Osmani's agent-skills (recommended)

Gives the spec, plan, build, test, review, ship lifecycle.

**Claude Code**
```
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills
```

**Antigravity**
```
agy plugin install https://github.com/addyosmani/agent-skills.git
```

**Any agent (skills.sh)**
```
npx skills add addyosmani/agent-skills
npx skills add addyosmani/agent-skills --list            # see what is inside
npx skills add addyosmani/agent-skills --skill <name>    # install one
```

## Step 3. Frontend and design (you chose the Full option)

**Emil Kowalski's skills** (apple-design, break-ui, mobile-native)
```
npx skills@latest add emilkowalski/skills
```

**frontend-design** (community installer, skim the skill before installing)
```
npx claude-code-templates@latest --skill creative-design/frontend-design
```

## Step 4. Selected skills from ECC (selective only)

ECC is large. Install the minimum, not everything.

```
npx ecc-universal@2.2.3 setup
npx ecc-universal@2.2.3 install --profile minimal --target claude --with capability:machine-learning
```

Antigravity (from a cloned copy of the official repo):
```
./install.sh --profile minimal --target antigravity
```

Pick individual skills:
```
./install.sh --target claude --skills tdd-workflow,security-review
```

Skills you wanted: `mle-workflow`, `python-patterns`, `python-testing`, `cost-aware-llm-pipeline`.

Safety notes:
- Try `--no-hooks` first. Hooks run commands automatically; turn them on only after reading them.
- Copy only `rules/common` and `rules/python` for rules.
- Don't stack several install methods for the same pack; pick one.
- Use the official source only, and pin the version as shown.

## Step 5. Google skills (only if you work on Google Cloud)

```
npx skills add google/skills
claude plugin marketplace add google/skills
agy plugin install https://github.com/google/skills/<plugin-path>
```

There are about 150 skills. Pick around 5 that match your services (for example BigQuery, Airflow, dbt, Cloud Run, Vertex AI). Do not install them all; extra skills crowd the agent's context.

## Step 6. Optional tools (add one at a time, test on a side project)

| Tool | Purpose | Install | Notes |
|---|---|---|---|
| **Headroom** | Compresses agent context to save tokens | `uv tool install --python 3.13 "headroom-ai[all]"` then `headroom wrap claude` | Set `HEADROOM_BEACON=off` to disable usage pings |
| **Reticle** | Lets the agent inspect a running web UI | `npm install -g @reticlehq/server && reticle setup mcp` then `reticle init --dry-run` | Run `reticle telemetry disable`. Young project, test first |
| **no-mistakes** | Strict gate when you `git push` | `curl -fsSL https://raw.githubusercontent.com/kunchenguid/no-mistakes/main/docs/install.sh \| sh` then `no-mistakes init`, use `git push no-mistakes` | Read the install script before piping it to a shell |
| **Shannon** | Automated pentest of a web app | `npx @keygraph/shannon@latest setup` then `start -u <staging-url> -r <repo>` | **Authorized staging only.** AGPL license. May need provider cyber verification. Never on production or systems you don't own |
| **Agent TARS** | Browser/desktop agent | `npx @agent-tars/cli@latest` (Node 22+) | Skip unless you need it |
| **Ruflo** | Multi-agent orchestration | not recommended | Heavy and invasive for daily work |

## Step 7. Check it works

Open a project with the kit and ask the agent:

1. "Which role file would you read to add RAG evaluation to this project?" It should name `roles/genai.md`.
2. "Run the pre-push gate." It should run lint, tests, and report real output.
3. "Deploy to production." It should refuse and ask for approval.

If any answer is wrong, the router in `CLAUDE.md` is not being loaded: check the file is in the project root.

## Updating

- Skill packs: re-run their install command or update via the plugin manager.
- This kit: edit the role files; keep them short. Move repeated mistakes into `LESSONS.md`, and promote rules that matter every time into `CLAUDE.md`.
