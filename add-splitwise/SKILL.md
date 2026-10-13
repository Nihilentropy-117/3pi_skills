---
name: add-splitwise
description: Adds expenses to the user's Splitwise account, including one-off shared expenses and saved premade transactions from JSONL such as phone and power bills. Use when the user asks to add, create, save, record, or run a Splitwise expense/bill and provides who paid, who owes, description, cost, and optionally group.
---

# Add a Splitwise Expense

Use this skill whenever the user asks to add or run a Splitwise expense/bill.

## Helper executable

Run the helper from this skill directory:

```bash
/root/.pi/agent/skills/add-splitwise/splitwise-add --help
```

The skill directory should also be on the pi agent PATH, so this shorter form may work:

```bash
splitwise-add --help
```

The helper uses Splitwise API v3. It expects credentials in environment variables. Supported names:

```bash
# Preferred simple API key access
SPLITWISE_API_KEY="..."

# Optional OAuth consumer credentials, if the environment/tooling uses them
SPLITWISE_CONSUMER_KEY="..."
SPLITWISE_CONSUMER_SECRET="..."

# Optional explicit bearer token aliases
SPLITWISE_ACCESS_TOKEN="..."
SPLITWISE_BEARER_TOKEN="..."
```

Do not expose credentials or tokens in replies.

## Known people

Use these IDs first. If the user mentions a person not listed here, query Splitwise with `splitwise-add list people` and resolve the ID from the live account data.

| ID | Name / note |
|---:|---|
| 53665987 | Nathan Gruebmeyer |
| 48415524 | Fen Jensen |
| 22444750 | Skye Nova |
| 48415650 | Tuca |
| 21510761 | Gray Lott (me) |
| 23353628 | Ethan |
| 22664155 | Hiro (Chris) |
| 51393333 | Elle Scott |

## Known groups

Use these IDs first. If the user mentions a group not listed here, query Splitwise with `splitwise-add list groups` and resolve the ID from the live account data.

| ID | Name |
|---:|---|
| 72165496 | 12112 Bills And Household Expenses |
| 31014911 | Phone Bill |

## Required workflow for one-off expenses

1. Parse the user's request:
   - `paid_by`: person who paid. Resolve to a Splitwise user ID.
   - `owed`: people who owe, possibly multiple people. Resolve each to a Splitwise user ID.
   - `description`: what the expense is.
   - `cost`: total cost or per-person shares.
   - `group`: optional Splitwise group. Resolve to a group ID if provided.
2. Resolve people/groups from the Known people/groups tables above.
3. If a person or group is not in the tables, run one of:

   ```bash
   splitwise-add list people
   splitwise-add list groups
   ```

4. Decide how to split:
   - Equal split among named owed people: use `--split equal --owe ID,ID,...` and `--cost TOTAL`.
   - Exact owed shares: use `--split exact --share ID=AMOUNT --share ID=AMOUNT ...`. The helper sets total cost to the sum of exact shares unless `--cost` is provided.
   - If the payer should also owe a share, include the payer's ID in `--owe` or `--share`.
   - If the payer should not owe anything, do not include the payer in the owed list/share list.
5. If ambiguity would create the wrong expense (unclear payer, unclear whether cost is total vs per-person, or unresolved person), ask a clarification. Otherwise add the expense.
6. Use `--dry-run` first only when you need to inspect the payload or the request is unusual. For normal clear requests, create the expense directly.
7. Confirm the description, total, payer, owed people/shares, and group.

## Add command examples

Equal split:

```bash
splitwise-add add \
  --description "Dinner" \
  --cost 120 \
  --paid-by 21510761 \
  --owe 53665987,48415524,21510761 \
  --group 72165496 \
  --split equal
```

Exact shares:

```bash
splitwise-add add \
  --description "Groceries" \
  --paid-by 21510761 \
  --group 72165496 \
  --split exact \
  --share 53665987=30 \
  --share 48415524=25 \
  --share 21510761=25
```

Common flags:

| User concept | Helper flag(s) | Notes |
|---|---|---|
| description / what it is | `--description`, `--desc` | Required for add. |
| total cost | `--cost` | Required for equal split. Optional for exact split; defaults to sum of shares. |
| payer | `--paid-by ID` | Required unless premade transaction contains `paid_by`. |
| who owes | `--owe ID,ID` or repeated `--owe ID` | Used with equal split. |
| exact owed shares | repeated `--share ID=AMOUNT` | Used with exact split. |
| group | `--group ID` | Optional. |
| date | `--date YYYY-MM-DD` | Optional; defaults to Splitwise/API current date behavior. |
| currency | `--currency USD` | Defaults to USD. |
| dry run | `--dry-run` | Prints request payload without creating. |

## Premade transactions

Premade transactions are stored as JSON Lines in:

```bash
/root/.pi/agent/skills/add-splitwise/transactions.jsonl
```

Do not read or edit this file by hand — the JSONL format is easy to corrupt with
quote escaping. Use `splitwise-add list premade` to inspect it and
`splitwise-add premade add` to append new entries.

Current saved transactions:

- `phone_bill` / aliases `phone bill`, `phone`: group `31014911`, description `Phone Bill for {current_month}`, no default payer (ask or pass `--paid-by`).
- `power_bill` / aliases `power bill`, `power`, `electric bill`: group `72165496`, description `Utilities for {current_month} — Power $650, Internet $105, Water $200`.

Run a premade transaction by name or alias:

```bash
splitwise-add run phone_bill --paid-by 21510761
splitwise-add run "power bill" --paid-by 53665987
```

The helper expands placeholders in descriptions:

- `{current_month}` -> current month name and year, e.g. `June 2026`
- `{month}` -> current month name, e.g. `June`
- `{year}` -> current year, e.g. `2026`
- `{today}` -> current date, e.g. `2026-06-29`

Save a new premade transaction with the helper (never by editing the JSONL directly):

```bash
splitwise-add premade add \
  --name example_bill \
  --alias "example" \
  --group 72165496 \
  --description "Example for {current_month}" \
  --paid-by 21510761 \
  --share 21510761=10.00 \
  --share 53665987=10.00
```

- `--share USER_ID=AMOUNT` is repeatable; at least one is required.
- Omit `--paid-by` to force asking who paid at run time.
- The helper rejects duplicate names/aliases and serializes the JSON itself.

When running a premade transaction:

1. If the user says who paid, pass `--paid-by ID` to override the JSONL `paid_by`.
2. If neither the user nor JSONL gives a payer, ask who paid.
3. Confirm the resulting expense and group.

## Listing and lookup commands

```bash
splitwise-add list people
splitwise-add list groups
splitwise-add list premade
```

The live `people` command combines friends, current user, and group members when available. Use it when a requested person is missing from the known table.

## Notes

- Splitwise exact split API fields use `users__N__user_id`, `users__N__paid_share`, and `users__N__owed_share`; the helper constructs these.
- The helper sets the payer's `paid_share` to total cost and everyone else's `paid_share` to `0.00`.
- The payer can also have an owed share if included in the owed list or exact shares.
- Do not invent IDs. Use the known tables or live lookup.
