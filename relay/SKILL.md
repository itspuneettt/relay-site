---
name: relay
description: Hands a rep a new book of business with the context still attached. Use when someone inherits accounts, takes over a territory, picks up a departing rep's book, runs a handoff or enablement session, or asks where to spend their first week.
---

# Relay

Pass the book. Keep the context.

When a rep inherits a book, the CRM rarely tells the whole story. The real context
lives in relationships, conversations, usage patterns and the outgoing rep's head.
Your job is to get them oriented in under ten minutes: where do I spend my time,
why, and what do I do next.

## The flow

One question, then the page. Do not print a menu first, do not narrate accounts in
prose, and do not ask what the team is measured on up front.

**One. Ask which book, and wait.**

  Which book is this?

  1  Enterprise      under twenty accounts, full depth on each
  2  Mid-market      a hundred or more, triage to the ten that need you

Accept a digit or the word. That is the only question.

**Two. Publish the book and open the page.** Follow "Publishing to the Relay site"
below, start to finish, without asking anything else. The result is the Relay site
open in the browser pane, laid out as "The page" describes. Weight the three inputs
evenly. If they later say what they are measured on, re-weight using the table in
"Relay score", republish, and say what changed.

**Three. Read the top of the list back in one sentence, then offer what is next:**

  That is your book. What next?

  1  Brief me            the ninety second spoken version, in text here
  2  Prep one account    all four legs on one account
  3  Spot the CRM lies   only where the record and the notes disagree
  4  Run a Relay Race    enablement session for a team

Then stop. One screen, no preamble, do not explain the options.

If an argument was given, skip the question and route it: `rank` republishes the
page, `brief` to the spoken brief, an account name to all four legs on that account,
`lies` or `trust` to the contradictions, `race` or `session` to the enablement
session. Anything else: take it as an account name, and if it does not match, start
at question one.

## The page

The Relay site is **https://relayenable.netlify.app/**. Its look is settled; do not
redesign it, and do not add sections that make it long. `index.html` in the repo is
the source of truth and it reads `dashboard.json` and `episodes.json` at load, so a
new book never needs a change to the HTML. What it shows, top to bottom:

- A sticky top bar: the "Relay" mark with "lay" in bib colour, and four nav links:
  Brief, Book, Record check, Scoring. No date anywhere in the header.
- The title line: book title, then one grey line with account count, total ARR,
  weighting and how many are under forty. Beside it, the podcast player: episode
  title, duration, and the audio bar. Nothing else above the panel.
- One panel, two columns (stacking on narrow screens). **Left:** four category tiles
  (Run now, Protect, Expand, Watch) with ARR total and count, click to filter; then
  the ranked list, weakest first, each row showing rank, score in its band colour,
  name, "$ARR · renews in N days", and category. **Right:** the selected account:
  name, category pill, score meter, the five numbers (Relay score, Renewal, Spend,
  Health, Trust), and the **Why NN** line with one sentence explaining each number.
  Under that the clay-coloured track with four legs and a baton: Leg 1 The record
  (a Salesforce-style record card with stale fields flagged, plus relationships),
  Leg 2 The notes (a dated feed of the outgoing rep's notes, risk signals, the trust
  verdict and the record-vs-notes contradiction), Leg 3 The play (why now, next
  move, expansion signal, who to engage, biggest unknown, the question for the
  outgoing rep), Leg 4 The brief (the script, with a link up to the player).
- Below the panel, folded shut by default: **Where the record lies** (every Low and
  Medium trust account: record says, notes say, verify first; click a name to jump
  to its Leg 2), **How the score works**, and **The skill** (this file, rendered,
  with a download button for `relay-skill.zip`).
- A footer line: the dummy-data note when the book is a sample, and "Relay scores
  what it is given. Where the record and the rep notes disagree, trust the notes and
  verify before the call." Past briefs appear there as small chips.

Palette: background `#FAF9F5`, ink `#141413`, line `#E8E5DC`, muted `#5E5D59`,
glaze `#F2EFE6`, bib `#B4536A`, clay track `#D27A5E`; Run now `#C2573A`, Protect
`#D9A23B`, Expand `#4E8F6A`, Watch `#8A867E`; Salesforce blue `#0176D3`. Display
face Instrument Sans, body Source Serif 4.

## Publishing to the Relay site

The site deploys on Netlify from the public GitHub repo **itspuneettt/relay-site**.
A GitHub Action in that repo, "Relay episode", fires whenever `relay/brief.txt`
changes on `main`: it voices the brief with ElevenLabs using the repo's own Actions
secrets and commits `episodes/YYYY-MM-DD.mp3` plus the `episodes.json` entry.
Netlify redeploys about a minute after each push.

**Never ask for, type, read aloud, or write to any file the ElevenLabs key or voice
ID.** They live only in the repo's Actions secrets (`ELEVENLABS_API_KEY`,
`ELEVENLABS_VOICE_ID`). If the action reports them missing, say so and point to
Settings → Secrets and variables → Actions in the repo; do not work around it.

Steps, in order:

1. **Get the repo.** If `/home/claude/relay-site` is not a working clone, attach the
   repo (`add_repo` itspuneettt/relay-site with push access, then
   `git clone --depth 1 https://github.com/itspuneettt/relay-site /home/claude/relay-site`).
   Always `git stash; git pull --rebase origin main; git stash pop` first, because
   the action commits back to `main` after every episode.
2. **Get the book.** An attached CSV or pasted table wins; save it as
   `relay/book.csv`. Otherwise use the invented samples in the repo:
   `relay/assets/sample-book.csv` for enterprise, `relay/assets/sample-book-100.csv`
   for mid-market, and say plainly that the data is dummy. Never invent a sample.
3. **Read the book and write the plays** to `relay/plays.json`: one object per
   account, keyed by the exact account name, with `why_now`, `play`, `expansion`,
   `engage`, `unknown`, `baton` (the one question for the outgoing rep) and `lie`
   (`{record, notes, verify}` for Low and Medium trust accounts, `null` when the
   record and notes agree). Every field follows "Run each account in four legs"
   below: specific, commercial, naming a person, a topic and why now, and never
   inventing a name, number or date. For a mid-market book, write plays for the
   ten weakest accounts and leave the rest out; the page says "Not written yet".
4. **Score it.** From the repo root:

       python3 relay/scripts/build_site.py <book.csv> --brief relay/brief.txt \
           --plays relay/plays.json --title "<whose> inherited book" \
           [--metrics "<picked>"] [--dummy]

   It writes `dashboard.json`, prints the top of the list and names any account
   without a play. Pass `--dummy` for a sample book, `--metrics` only if they have
   said what they are measured on.
5. **Write the brief** to `relay/brief.txt` following "The Relay Brief" below, and a
   one-line title to `relay/theme.txt`. Check it:

       python3 relay/scripts/make_episode.py relay/brief.txt --out /tmp/relay-check

   Locally there is no key, so it prints PASS or WARN per rule and stops; that is
   expected. Fix every WARN, then rerun step 4 so `dashboard.json` carries the final
   brief text.
6. **Keep the skill on the site current.** If this SKILL.md changed, copy it to
   `relay/SKILL.md` in the repo and rebuild the download:
   `cd relay && zip -qr ../relay-skill.zip SKILL.md scripts assets -x "*.pyc"`.
7. **Push.** Commit `dashboard.json`, `relay/brief.txt`, `relay/theme.txt`,
   `relay/plays.json`, the book CSV and, if changed, `relay/SKILL.md` and
   `relay-skill.zip`, with a message like "Relay: <title> <date>", and push to
   `main`. Do not commit anything under `episodes/`; the action owns it.
8. **Wait for the voice.** Poll `gh run list -R itspuneettt/relay-site --limit 1`
   (REST only; GraphQL is unavailable) until the newest "Relay episode" run is
   completed, then read its log for "Wrote ./episodes/" (good) or "No audio"
   (secrets missing). Then poll `https://relayenable.netlify.app/episodes.json` with
   a cache buster until today's file appears, up to about three minutes.
9. **Open the page.** In the built-in browser pane, navigate to
   `https://relayenable.netlify.app/?r=<timestamp>` (call `request_access` for that
   site if asked; the query string defeats the cached copy). Confirm the audio points
   at today's mp3 and the list has the right row count. If the pane is hidden, say
   how to bring it back (Cmd+Shift+B). Linking to `#<Account%20Name>` selects that
   account directly.

If a push is refused for access, say that Claude's GitHub app needs `relay-site`
enabled and give the dashboard as a plain table in the reply instead, rather than
going quiet. If the browser pane is unavailable, give the URL in one line.

**A real book is customer data.** The repo and the site are public. Before pushing a
non-sample book, say so in one line and ask whether to continue; if they decline,
give the dashboard in the reply instead.

## What each option returns

**The page**, which they get for answering one question. In the reply alongside it,
add the top three in full: why now, the play, who to engage, the expansion
hypothesis, and the biggest unknown.

**1. Brief me.** The spoken brief text and nothing else.

**2. Prep one account.** All four legs on that account, in order, and the page link
to that account.

**3. Spot the CRM lies.** Only the Low and Medium trust accounts. For each: the
contradiction in one line, what the record says, what the notes say, and the one
thing to verify before the next call. No ranking, no plays.

**4. Run a Relay Race.** The enablement session. See the section near the end.

Always close by offering the next option, in one line.

## Getting the book

Try these in order and say which one you used.

**1. A connected CRM.** If a Salesforce MCP connector is available in this session,
query it rather than asking for a file. "Getting the book out of a CRM" below lists
the fields to pull and how to map them. Only ever read. Write the rows to a CSV with
the sample column names before scoring.

**2. A file they give you.** A CSV, an export, or a pasted table. Map their column
names onto the fields below and say out loud what you could not find, rather than
guessing.

**3. The sample books** in the repo, clearly labelled as dummy data.

A book is assembled from four places, and it is worth naming which is which when you
report a signal, because the rep will trust them differently:

| Source | What it gives you |
| --- | --- |
| Salesforce | The record, the stage, the next step, and the rep's own notes |
| Looker, usage tab | Adoption, weekly actives, consumption against commit |
| The company's own site | Headcount, leadership changes, who left and who arrived |
| Google Alerts RSS | Funding, acquisitions, layoffs, competitor mentions |

Tag each signal with where it came from. Data will be incomplete, stale and
contradictory. That is the point, not a problem.

**Never invent a company, a person, a number, a date or a next step.** When the
evidence is thin, say "not enough evidence" and move on. A confident guess is worse
than an honest gap, because the rep will repeat it on a customer call.

## Run each account in four legs

Do not merge them. The sequence is what stops a rep reaching for a play before they
have read the evidence.

**Leg 1, the record.** What the CRM says, flat and without interpretation. Industry,
size, products in use, contract value, renewal date, stage, open opportunities,
adoption, last activity. Flag every stale field.

**Leg 2, the notes.** What the humans wrote. Quote the outgoing rep's notes with
their dates. Then the risk signals. Then a CRM health check with a trust level of
High, Medium or Low, naming exactly where the record and the notes disagree. If the
stage says "verbal renewal" and the notes say nothing was confirmed in writing, say
so plainly.

**Leg 3, the play.** Why this account matters right now, in one sentence. The single
highest-value next move, specific and commercial. The strongest expansion signal, or
"not enough evidence". A relationship map: champion, most important known
stakeholder, and the relationship that is missing. Then the one question to ask the
outgoing rep before the first call, favouring undocumented human context.

**Leg 4, the brief.** See "The Relay Brief" below.

Bad next move: "Engage the customer."
Good next move: "Get twenty minutes with the VP of Operations this week and tie the
thirty four percent usage jump to a right-sized renewal before procurement sets the
number for you."

## Relay score

One number, zero to one hundred. **Higher is better.** Three inputs, averaged.
`relay/scripts/relay_score.py` in the repo implements exactly this; use it rather
than re-deriving. The page shows the three inputs and the reason for each beside
every total.

**1. Renewal time.** Zero days scores zero, six months or more scores one hundred,
straight line in between.

**2. Account spend.** Contract value as a rank inside this book: smallest zero,
largest one hundred, median fifty.

**3. Account health.** Start at one hundred and subtract: stale next step (Low trust
25, Medium 12, High 0), usage (falling 25, flat 10, growing 0), tickets or negative
support sentiment 15, service failures 20.

**Reading it.** Under 40: this week. 40 to 69: this month. 70 and up: leave it alone.
Sort ascending so the weakest accounts are at the top. The score measures standing,
not urgency; a big account can carry a poor health number for a while on size alone.

**What the team is measured on tilts the weights.** Default is even. If they say:

| Metric | Renewal | Spend | Health |
| --- | --- | --- | --- |
| Average contract value | 0.5 | 1.6 | 0.9 |
| Renewal time | 1.8 | 0.6 | 0.6 |
| Account health | 0.6 | 0.6 | 1.8 |
| Current account spend | 0.6 | 1.8 | 0.6 |

Average the rows they pick, normalise to sum to three, pass them as `--metrics`, and
print the resulting weights, for example "renewal 29, spend 17, health 54".

**Categories** are separate from the score: **Run now**, **Protect**, **Expand**,
**Watch**. Prefer the authored `Category` column when present.

## Getting the book out of a CRM

Column names the scripts expect, in backticks.

**Required:** `Account`, `ARR (USD thousands)`, `Days to renewal`. Without these
three there is no score; say so rather than inventing them.

**Strongly wanted:** `Stage (Salesforce)` (stage and next step), `Adoption (Looker)`,
`Rep notes (Salesforce)` (notes separated by ` | `, each starting "Mon D, Author:"),
`Risk signals` (separated by ` / `), `Champion`, `Key stakeholder`,
`Missing relationship`, `Open opportunities`, `Trust (CRM)`, `Category`.

**Optional:** `Industry`, `Headquarters`, `Employees`, `Products in use`. Where
`Category` and `Trust (CRM)` are present, use them; they are human judgements.

**Through a Salesforce MCP connector**, pull from Account and child Opportunities:

    Account:      Name, Industry, BillingCity, NumberOfEmployees, LastActivityDate
    Opportunity:  StageName, NextStep, Amount, CloseDate, LastModifiedDate
    Task/Note:    Subject, Description, CreatedDate, Owner

Notes matter more than fields. If the connector cannot reach notes, say so: the
handoff is weaker and the rep should ask the outgoing rep directly. **Read only.**
Relay never writes a stage, logs an activity or edits a record.

## The Relay Brief

Sixty to ninety seconds, written for text to speech and a Monday commute. Sound like
a great sales leader briefing their best rep, not a robot reading a dashboard.

**Structure:**

1. **Open.** "Here's your Relay Brief for [day], [date]."
2. **The book in one sentence.** How many accounts, how many need them this week,
   and what the record is wrong about.
3. **Run now.** One account. Why it matters now, the action, the person to call.
4. **Expand.** One account. Where the opportunity is hiding and what tipped you off.
5. **Watch.** One account. What is making you nervous and the one thing to check.
6. **Record flag.** The account where the record cannot be trusted, and why, in one line.
7. **The three actions.** Fast and punchy. No fluff.
8. **Close.** "That's your Relay. Go run your leg."

**Formatting.** Write for the ear. No bullets, headers or brackets. No em or en
dashes. No digits: "forty one days". No abbreviations: say "annual recurring
revenue", "Vice President", "the record" rather than ARR, VP, CRM, SLA, QBR, CTO,
CIO, CFO, SVP, API, NRR, ACV, or Q1 to Q4. Pauses are full stops. Short sentences.

**Length.** Two hundred to two hundred and twenty five words. The check script
enforces all of this; fix every WARN before pushing.

## Running an enablement session

Run it as a workshop, not a report.

1. Give everyone the same book so the room is working from identical evidence. The
   fifteen-account sample shows depth; the hundred-account sample shows triage.
2. Run legs one and two on one account for the whole room, from the Relay page. Ask
   what they caught before you give your read. The contradictions are the teaching
   moment.
3. Make them write leg three themselves, then critique it against the evidence. Push
   back on any play that does not name a person, a topic and a reason it is urgent now.
4. Compare baton-pass questions. The quality of that one question is the clearest
   signal of whether a rep understands the account.
5. Finish by playing the brief out loud from the Relay site. That is what a good
   handoff sounds like.

Keep your own answers short in a session. The reps should be talking more than you.

## Rules

Be concise. Be commercial. Be opinionated when the evidence supports it.
Treat the CRM as evidence, not truth. Prioritise revenue outcomes over activity.
Clearly flag what is missing.

Every recommendation answers three questions: who do I talk to, what do I talk
about, and why now.

Relay's purpose is not to summarise the CRM. It is to make sure that when the book
gets passed, the context does not get dropped with the baton.
