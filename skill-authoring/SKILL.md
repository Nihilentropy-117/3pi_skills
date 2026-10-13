---
name: skill-authoring
description: How to create or update a skill in this assistant (layout, SKILL.md frontmatter, scripts, dependencies, what never to include). Use whenever you turn a solution into a reusable skill.
---

# Writing a skill here

Skills live in `/data/agent/skills/<name>/` (`~/.pi/agent/skills` links there). That directory is a git
repository; after your turn ends, changes are committed and pushed automatically. Do not run
git there yourself.

## Layout
```
<name>/
├── SKILL.md          # required: frontmatter + instructions
├── <script>.py       # optional scripts beside it; run with `python`
└── references/       # optional supporting files
```

## SKILL.md
```markdown
---
name: <name>              # lowercase, digits, hyphens; same as the directory
description: <what it does AND when to use it, one or two sentences>
---
# <name>
Exact commands to run, inputs, outputs, failure modes.
```
The description is what routes future requests to the skill; make it specific.

## Rules
- Dependencies: `pip install <pkg>` into the venv (persists). Mention them in SKILL.md.
- Scripts take arguments and print results; no interactive prompts; bounded timeouts.
- Read config from environment variables. Never write secrets, tokens, keys, or personal data
  into a skill. The push is scanned and refused if a secret value appears.
- Test the script once before finishing the turn. Run `/reload` only if a skill is not picked up.
- Prefer updating an existing skill over creating a near-duplicate.
