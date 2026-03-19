# Activation Engine

## Project
Customer Activation Automation System for fintech/trading platforms.
Scores customers who completed KYC but haven't deposited, recommends actions.

## Structure
- data/generate.py — generates fake customer data → data/customers.json
- engine/scorer.py — priority scoring logic
- engine/router.py — action routing (email, sales call, escalate)
- engine/llm.py — LLM integration (Week 3)
- api/main.py — FastAPI endpoints (Week 2)

## Commands
- Generate data: python data/generate.py
- Run API: uvicorn api.main:app --reload (Week 2)
- Run tests: pytest (when added)

## Code Style
- Python 3.10, snake_case everywhere
- Type hints on function signatures
- Docstrings on all functions
- ISO 8601 for all dates/timestamps

## Rules
- Explain changes before making them
- Commit after each working feature
- Don't overwrite data/customers.json without asking
```

**Why this matters:** Your CLAUDE.md should start small, documenting based on what Claude is getting wrong.  You'll grow it over time. Start lean, add rules as you discover problems.

---

### 2. Use `/clear` aggressively

Every time you start something new, clear the chat.  Context from old conversations pollutes new ones. Finished debugging `generate.py` and now building `scorer.py`? Type `/clear` first.

The anti-pattern: you start with one task, then ask Claude something unrelated, then go back to the first task — context is full of irrelevant information. 

---

### 3. Be specific in your prompts

Don't say: *"Fix my code"*

Say: *"I'm running `python data/generate.py` and getting a TypeError on line 36. Look at the file and fix the issue."*

Reference files directly, mention the error, tell it what you expect. The more specific your input, the better the output.

---

### 4. Plan before coding on complex tasks

For anything touching more than 2-3 files, ask Claude Code to **plan first**:

> "I need to build a scoring function in engine/scorer.py. Before writing code, outline what the function should take as input, what it should return, and what scoring factors to use. Don't write code yet."

This prevents it from charging ahead and writing something you then have to undo.

---

### 5. Commit early and often

Have Claude write commits as it goes for each task step. This way either Claude or you can revert to a previous state if something goes wrong.  After every working change, commit. You can even tell Claude Code: *"Commit this with a descriptive message."*

---

### 6. Don't babysit — but DO verify

Let Claude Code work, but **read the output before accepting**. At your learning stage, this is especially important — you said you want to understand every line. So when Claude Code writes code, read it and ask "why did you do X?" if something isn't clear.

---

### 7. What NOT to worry about yet

Ignore these for now — they're for later when your project is bigger: subagents, parallel sessions, hooks, custom slash commands, headless mode. These are power-user features. Get the basics right first.

---

### Your workflow going forward
```
1. Open terminal → cd ~/activation-engine
2. Start Claude Code → claude
3. It reads CLAUDE.md automatically
4. Give it specific tasks
5. /clear between unrelated tasks
6. Commit after each working feature
7. Ask "why" when you don't understand something