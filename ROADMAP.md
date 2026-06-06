# ROADMAP — agent-ready tasks

The autocoding agent picks up any task marked *(agent-ready)*, implements it on a
branch, runs the test suite, and opens a pull request. Keep each task scoped to a
single PR with clear acceptance criteria.

**Format (required, one line each):**
`- [ ] **Title** — short description *(agent-ready)*`

All four parts are required: the leading `- [ ]` checkbox, the `**bold title**`,
a ` — ` before the description, and `*(agent-ready)*`. Markdown headings (`##`)
and plain bullets are NOT picked up — the controller rewrites the `- [ ]` marker as
it tracks each task (`- [ ]` → `- [~]` → `~~done~~`).

## Tasks
- [ ] **Add a GET endpoint for a single record by id** — returns the record, 404 if missing, with input validation *(agent-ready)*
- [ ] **Write tests for the authentication layer** — cover valid, missing, and expired credentials *(agent-ready)*
- [ ] **Fix empty values in the data table** — render "—" when a field is null instead of blank *(agent-ready)*

<!-- The agent does best on focused, testable units: one feature / endpoint / bugfix /
     test touching a few files. Avoid vague or large tasks ("rewrite the dashboard",
     "make it faster") and anything needing design decisions or external credentials. -->
