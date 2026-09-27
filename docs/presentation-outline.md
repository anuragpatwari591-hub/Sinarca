# Presentation Outline (12 slides)

Suggested structure for a B.Tech project presentation / demo. Pair with a
live walkthrough of the Demo Student account (`/demo`) between slides 5–9.

1. **Title** — NAVORA: "Stop searching. Start knowing what to learn next."
   Team, guide, institution.

2. **Problem** — Students face information overload across free/paid
   resources with no personalized sequencing. Searching ≠ learning path.

3. **Existing systems & gap** — Course marketplaces sell courses; search
   engines rank by query relevance; career sites map skills to jobs. None
   combine profile-aware sequencing + explainability + a free-first bias.

4. **Proposed system** — One coherent loop: Discover → Understand → Plan →
   Learn → Practice → Build → Measure → Improve, built around a "Learning
   DNA" profile and an explainable recommendation engine.

5. **Live demo: onboarding** — Show the 7-step wizard building a Learning
   DNA (stream → interests → skills → career goal → learning style → time
   & language → budget).

6. **Live demo: dashboard & "Your Next Move"** — The signature feature:
   one clear next action with a plain-language reason, time estimate, and
   a suggested follow-up project.

7. **Live demo: resource discovery & explainability** — Search, filters,
   Free-First mode, and a resource detail page's "Why this resource?" box.

8. **Live demo: roadmap, skill gap, career explorer** — Structured stages
   with milestone projects; skill-gap analysis against a target career
   with a prerequisite-ordered learning path.

9. **Live demo: AI Study Mentor & admin panel** — Deterministic mentor
   modes (Explain / Quiz Me / Plan My Day / …); admin CRUD, reports queue,
   and analytics.

10. **Architecture & database** — Flask app-factory pattern, blueprint
    module map, ER-model summary (streams/skills/careers/resources/
    roadmaps/progress/recommendations). One slide diagram from
    `docs/architecture.md`.

11. **Recommendation engine internals** — The weighted-factor table from
    `docs/recommendation-engine.md`; emphasize *explainable*, not a black
    box, and the personalization feedback loop.

12. **Testing, security, business model & future scope** — 31 passing
    tests; CSRF/auth/authorization measures; potential-vs-actual revenue
    distinction; named limitations and next steps (Flask-Migrate, real
    affiliate integration, LLM layer per `docs/future-ai.md`).

## Suggested diagram assets

- Architecture layer diagram (browser → Flask blueprints → services/
  recommendation engine → models → DB) — see `docs/architecture.md`'s
  ASCII diagram as a source.
- ER diagram — table list in `docs/database.md`, grouped by "Identity",
  "Taxonomy", "Content", "Learning activity", "Personalization loop",
  "Monetization", "Admin & misc".
- Recommendation-engine factor table — directly from
  `docs/recommendation-engine.md`.
