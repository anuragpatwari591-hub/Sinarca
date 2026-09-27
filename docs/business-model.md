# Business Model

Per the project brief's explicit instruction: this document clearly
separates **Potential Revenue** (what the architecture supports) from
**Actual Revenue** (what is live in this build — which is none; NAVORA is
not a live commercial product).

## Potential revenue streams

### 1. Affiliate commissions
**Architecture status: partially built.** Every outbound resource click is
logged (`affiliate_clicks` table), and `Resource.affiliate_url` exists as a
field an admin could populate. **No real affiliate network (Amazon
Associates, Coursera affiliate program, etc.) is connected.** When one is
connected, `Resource.click_url` already prefers `affiliate_url` over `url`
transparently, and the affiliate disclosure page
(`/disclosures`) already exists.

### 2. Sponsored educational content
**Architecture status: schema only.** The `sponsored_content` table and an
admin listing page exist; `Resource.is_sponsored` renders a visible
"Sponsored" badge wherever that resource appears. **No sponsors are
connected.** The product principle — sponsored content is always labeled
and never silently mixed into organic rankings — is enforced in the
templates (search results, resource detail) regardless of whether any
sponsor is live.

### 3. Premium student features
**Architecture status: not built.** Advanced roadmap customization,
portfolio review, and mentor matching are named in the product brief as
*future* premium features. No paywall or subscription billing exists in
this build — building one without a real payment processor would be
demonstrating a capability the platform doesn't have, which the project
brief explicitly forbids.

### 4. Institutional partnerships (colleges, coaching institutes)
**Architecture status: not built.** Would require a B2B admin role and
cohort-level reporting, both out of scope for this build.

### 5. Recruiter integrations / B2B dashboards
**Architecture status: not built.** Would require a recruiter-facing
portal and consent flows for sharing student readiness data — a
significant privacy surface intentionally deferred.

## What NAVORA actually monetizes today

**Nothing.** This is a capstone project, not a live business. The revenue
architecture above exists so a hypothetical v2 could plug in real
integrations without redesigning the schema, but claiming any current
revenue, user counts, or partnerships would violate the project's core
"never fabricate" principle.

## Why this separation matters for the viva

A common weak point in student ed-tech projects is presenting an
aspirational business model as if it were operational. NAVORA's admin
dashboard (`/admin/`) is explicit about this: the "Sponsored Content" page
reads "No sponsors are connected in this build," and the analytics page
shows real, current counts (clicks, resource starts, completions) rather
than invented revenue figures.
