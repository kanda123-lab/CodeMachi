# CodeMachi — Telegram Bot Build Plan (with Claude Code)
### Step-by-step execution guide

You have Claude Code Pro — that changes the plan. Instead of hand-writing everything, you'll mostly **direct Claude Code** with clear prompts and review/run what it produces. This doc gives you the exact sequence: what to set up manually (accounts, keys — Claude Code can't do this part for you), then what to ask Claude Code to build at each stage, in order.

---

## 0. Before You Open Claude Code — Manual Setup (30–45 min)

These steps need a human (you) because they involve external accounts:

1. **Create the Telegram bot**
   - Open Telegram, message `@BotFather`
   - Send `/newbot`, choose a name and username (must end in `bot`, e.g. `CodeMachiBot`)
   - BotFather gives you a **bot token** — save it somewhere safe, you'll need it shortly

2. **Get your Anthropic API key**
   - Go to console.anthropic.com → API Keys → create one
   - Save it — Claude Code will need this in an environment variable

3. **Create a project folder locally**
   ```bash
   mkdir codemachi-bot && cd codemachi-bot
   git init
   ```

4. **Create a `.env` file** (never commit this — add to `.gitignore` immediately)
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   ANTHROPIC_API_KEY=your_key_here
   ```

5. **Open Claude Code in this folder:**
   ```bash
   claude
   ```

Everything from here on, you're working inside Claude Code.

---

## 1. Day 1 — Scaffold the Project

**Prompt to give Claude Code:**

> Set up a Python Telegram bot project called CodeMachi. Use python-telegram-bot v20+ (async). Create this structure:
> - `bot.py` — main entry point
> - `handlers/` — folder for command and message handlers
> - `db.py` — SQLite database helper
> - `prompts.py` — system prompts for each language mode (tanglish, tamil, english)
> - `requirements.txt`
> - `.gitignore` (exclude .env, __pycache__, *.db)
>
> Load TELEGRAM_BOT_TOKEN and ANTHROPIC_API_KEY from a .env file using python-dotenv. Don't implement logic yet — just scaffold the structure with placeholder functions and clear TODO comments so I can review the architecture before we build it out.

**What to check before moving on:**
- Does the structure match what you'd expect to maintain long-term?
- Is `.env` actually in `.gitignore`?

---

## 2. Day 1–2 — Core Bot Logic

**Prompt to give Claude Code:**

> Implement the bot's core logic in `bot.py` and `handlers/`:
>
> 1. `/start` command — sends a welcome message and an inline keyboard with 3 buttons: 🔀 Tanglish, 🟢 Tamil, 🔵 English. Pressing one sets the user's mode and confirms it.
> 2. A general message handler — when a user sends any text (not a command), call the Anthropic API using the system prompt that matches their current mode (default to Tanglish if they haven't picked one), and reply with Claude's response.
> 3. `/mode` command — lets the user change their language mode anytime, same inline keyboard as /start.
> 4. Store each user's telegram ID and chosen mode in SQLite (table: users, columns: telegram_id, mode, created_at).
>
> Put the 3 system prompts in `prompts.py` — write them properly for Tanglish (natural Tamil-English code-switching, like real Chennai/Coimbatore developers talk, NOT formal Tamil), Tamil (full Tamil script explanations but technical terms stay English), and English (clear, friendly, practical).
>
> Use the Anthropic Python SDK, model `claude-sonnet-4-6`, max_tokens 1000.

**What to check before moving on:**
- Test `/start` in Telegram (you'll need to run the bot locally first — ask Claude Code how to run it if unsure)
- Send a test message in each mode, confirm the tone actually sounds like Tanglish vs formal Tamil vs English
- If Tanglish doesn't sound natural enough, tell Claude Code specifically what's wrong and ask it to revise the system prompt — this is the part worth iterating on most

---

## 3. Day 3 — Usage Limits (Free Tier Gating)

**Prompt to give Claude Code:**

> Add daily usage limits to the bot:
>
> 1. Extend the SQLite `users` table with: `daily_count` (int, default 0), `last_reset_date` (date), `is_pro` (boolean, default false)
> 2. Before responding to any message, check: if the user is not Pro and `daily_count >= 5` and `last_reset_date` is today, reply with a friendly limit-reached message in their current mode (write one for each mode — Tanglish should say something like "Bro, indha naaikku free questions mudinjiruchu" with a note about upgrading) instead of calling the API.
> 3. Reset `daily_count` to 0 automatically if `last_reset_date` is not today (reset on first message of a new day, midnight IST boundary).
> 4. Add a `/usage` command that tells the user how many free questions they have left today, in their current mode.
> 5. Increment `daily_count` by 1 each time a question is actually answered (not on limit-reached replies).

**What to check before moving on:**
- Send 6 messages in a row, confirm the 6th gets the limit message instead of an answer
- Confirm `/usage` reports correctly

---

## 4. Day 4 — Learn Mode and Quick Actions

**Prompt to give Claude Code:**

> Add a `/learn` command:
>
> 1. Shows an inline keyboard with topic buttons: Python, JavaScript, React, DSA, SQL, Git, Node.js, System Design
> 2. When a topic is tapped, send a message to Claude asking it to teach that topic from basics, using the user's current language mode, and reply with the explanation.
>
> Also add a few quick-action inline buttons under the bot's welcome message and after each answer: "🔁 Switch Mode" (calls /mode), "📚 Learn a Topic" (calls /learn), "📊 My Usage" (calls /usage) — so users don't have to remember command names.

**What to check before moving on:**
- Tap through `/learn` → pick a topic → confirm a reasonable lesson comes back in the right language mode
- Confirm quick-action buttons actually trigger the right commands

---

## 5. Day 5 — Deploy to Production

You have two reasonable free/cheap hosting options. Ask Claude Code to help with whichever you pick:

**Prompt to give Claude Code:**

> Prepare this bot for deployment on Railway.app. Create:
> 1. A `Procfile` or `railway.json` as needed for Railway to know how to start the bot
> 2. Make sure the bot uses polling (not webhooks) for simplicity at this stage
> 3. Add a note in README.md on which environment variables need to be set in Railway's dashboard (TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY)
> 4. Make sure the SQLite file path works correctly in a deployed environment (Railway's filesystem is ephemeral on redeploys — flag this as a known limitation for me, since user data will reset; we may need to migrate to a hosted Postgres later as the bot grows. For now SQLite is fine for the first 1–2 weeks of testing.)

**Manual steps you do yourself:**
1. Push code to a GitHub repo (private is fine to start)
2. Create a Railway.app account, connect the GitHub repo
3. Set the environment variables in Railway's dashboard
4. Deploy and confirm the bot responds to `/start` from your phone, not just locally

---

## 6. Day 6 — Telegram Channel and Group

This part is manual (Telegram doesn't have an API for creating channels via Claude Code):

1. Create a Telegram **Channel** named "CodeMachi" (or your chosen name) — this is your one-way content/marketing feed
2. Create a Telegram **Group** "CodeMachi Community" — two-way space for users to talk and ask the bot questions
3. Add your bot to the group (so people can tag it for help there too — ask Claude Code to add group support to the message handler if you want this)
4. Write your first 3 channel posts using the Tanglish content style (filter coffee analogy for async/await, etc. — reuse the format we discussed earlier)

**Optional prompt for Claude Code:**

> Update the message handler so the bot also responds when added to a group, but only when it's directly mentioned (@botusername) or replied to — not on every group message, to avoid spam.

---

## 7. Day 7 — Soft Launch

1. Share the bot link in 3–5 existing Tamil dev Telegram/WhatsApp groups (be a real participant first, don't just drop a link)
2. Watch the Railway logs (or ask Claude Code to add basic logging if it hasn't already) for errors as real users hit it
3. Collect feedback directly — DM a few early users and ask what felt off

**Prompt to give Claude Code if you want logging:**

> Add simple logging throughout the bot — log every incoming message (telegram_id, mode, truncated message text) and every error, to a local log file and to stdout, so I can monitor behavior after deployment.

---

## 8. Week 2 — Payments (Pro Tier)

Once you've validated people are using it and hitting the free limit:

**Prompt to give Claude Code:**

> Integrate Razorpay for the Pro subscription (₹199/month):
> 1. Create a Razorpay payment link generation flow — when a user hits their daily limit or sends `/upgrade`, generate a Razorpay payment link with their telegram_id embedded as a reference/notes field
> 2. Set up a webhook endpoint (small Flask or FastAPI app, can run alongside the bot) that Razorpay calls on successful payment — when received, set `is_pro = true` for that telegram_id in the database
> 3. Make sure Pro users skip the daily_count check entirely
> 4. Add a `/upgrade` command that explains Pro benefits in the user's current language mode and sends the payment link

**Manual steps you do yourself:**
1. Create a Razorpay account, get API keys, set up the webhook URL in Razorpay's dashboard pointing to your deployed webhook endpoint
2. Test the full flow with a real small payment to yourself before announcing Pro publicly

---

## Quick Reference — Full Build Timeline

| Day | What gets built | Who does it |
|---|---|---|
| 0 | Bot token, API key, project setup | You (manual) |
| 1 | Project scaffold | Claude Code |
| 1–2 | Core chat logic, 3 language modes | Claude Code (you test + iterate on tone) |
| 3 | Daily usage limits | Claude Code |
| 4 | /learn mode, quick-action buttons | Claude Code |
| 5 | Deploy to Railway | Claude Code (config) + You (accounts/deploy) |
| 6 | Channel + group setup, first content | You (manual) |
| 7 | Soft launch in existing groups | You (manual) |
| Week 2 | Razorpay Pro tier integration | Claude Code + You (Razorpay account) |

---

## A Few Things Worth Knowing Going In

- **Claude Code can't create Telegram bots, Railway accounts, or Razorpay accounts for you** — anything requiring a new external account/login is on you. It can write all the code that talks to those services once you have the keys.
- **Iterate hardest on the Tanglish system prompt.** This is your actual product differentiator — spend real time testing it against real questions and refining wording with Claude Code rather than treating it as a one-shot task.
- **SQLite is fine for weeks 1–2, not for scale.** Once you're past ~500 users or move to Pro billing seriously, ask Claude Code to help migrate to a hosted Postgres (Railway offers this with one click) — don't do this prematurely, but don't forget it either.
- **Test in your own personal chat with the bot constantly during building** — Telegram makes this trivial, there's no reason to wait until "done" to start sending it real messages.
