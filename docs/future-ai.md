# Future AI Integration

## Current state

NAVORA's intelligence today is an **explainable, rules-based
personalization engine** (see `docs/recommendation-engine.md`), not a
large language model. This was a deliberate product decision (spec section
5): the platform must stay fully functional, explainable, and free to run
even if no external AI vendor is configured or affordable.

The one integration seam that exists is `app/services/ai_adapter.py`:

```python
def generate(prompt: str, context: dict | None = None) -> str:
    if not is_configured():
        raise AIAdapterNotConfigured(...)
    raise NotImplementedError(...)  # no vendor wired up in this build
```

`app/routes/chatbot.py` calls this first and catches
`AIAdapterNotConfigured`, falling back to
`app/services/chatbot_fallback.py` — a deterministic engine that answers
from the student's actual profile, roadmap, and the resource/project/skill
tables, never inventing facts.

## What a v2 integration would add

If `AI_PROVIDER_API_KEY` (e.g. for the Claude API) were configured in a
future version:

1. `ai_adapter.generate()` would be implemented to call the provider with
   the user's message plus structured `context` (Learning DNA, current
   roadmap stage, recent activity) — giving the model real grounding
   instead of letting it hallucinate a student's situation.
2. The AI Study Mentor's replies would become more naturally phrased and
   able to handle open-ended questions the deterministic engine can't
   parse (e.g. multi-part questions, follow-ups referencing earlier turns).
3. **The underlying facts should still route through the same data the
   deterministic engine uses** — which resource exists, what its rating
   actually is, which skills are prerequisites — so the LLM layer adds
   fluency, not fabricated claims. A practical implementation would give
   the model read-only tool access to `app/services/chatbot_fallback.py`'s
   helper functions rather than letting it free-associate.
4. The recommendation engine itself would likely stay rules-based (it's
   already explainable and fast); an LLM layer would sit on top to
   generate more natural *phrasing* of the same `reasons` list, not to
   replace the scoring.

## Why this wasn't built now

No AI vendor credentials were provided for this environment, and the
project brief explicitly warns against making "the entire application
dependent on an expensive AI API" or faking AI capability. Building a
mocked/fake LLM call would violate the "never fabricate AI capabilities"
principle more directly than simply documenting the seam and leaving it
unconfigured.
