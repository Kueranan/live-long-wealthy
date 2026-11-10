# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Young Thai workers: first jobbers and people in their 20s–30s with little finance knowledge, often carrying credit-card, BNPL or personal-loan debt. They open the planner to find out, in plain Thai, whether their money will last their whole life and what one small change would help most. Secondary audiences are mid-career workers and near-retirees (covered by the sample personas) and the Trinity Hackathon 2026 judges who evaluate the demo.

## Product Purpose

Live Long Wealthy is a lifetime financial-planning simulator (Trinity Hackathon 2026 · Track 2 Wealth for Everyone). It simulates 2,000 possible financial futures with Monte Carlo and reduces them to one number: the chance the user's money lasts their whole life. Success means a young worker understands that number, sees their future self at 60/80/90, and leaves knowing which concrete action (save a little more, pay off high-interest debt, retire later, spend less) moves the number most.

## Positioning

Not a savings calculator with one fixed return: it models uncertain markets, uncertain parameters (Bayesian priors), inflation, and an uncertain lifespan (Gompertz), then compares every what-if on the same 2,000 futures so the deltas are fair. The output is a probability plus a story, not a single projected balance.

## Operating Context

- Main demo is the static page `web/index.html` (opens directly in a browser, no server). A Streamlit version (`app.py`) exists but is secondary.
- Submission is a GitHub link; the page may be viewed by judges on laptops and phones.
- Sample personas: First jobber (23), Working age (35), Near retirement (55).

## Capabilities and Constraints

- Inputs: age, monthly income, monthly saving, current savings, debt (balance, rate, payment), retirement age, retirement spending (today's baht), risk level, Save More Tomorrow, pay-high-interest-debt-first.
- Outputs: success probability, typical age money runs out, safe monthly spending (≥85% success), wealth at ages 60/80/90, survival odds, lifetime wealth fan chart (P10–P90), what-if deltas.
- All money is real (today's purchasing power).
- The simulation logic (in `model.py` and the `<script>` model section of `web/index.html`) belongs to a teammate and must not be changed by design work; design work changes only presentation and input handling.
- CSS is Tailwind v4, built from `web/tailwind.css` to `web/styles.css` (`npm run build:css`); the built CSS is committed so the page works without Node.
- Language: Thai UI.

## Brand Commitments

- Name: Live Long Wealthy.
- Must state it is a prototype and not investment advice.

## Evidence on Hand

- Academic grounding listed on the page: Modigliani & Brumberg (1954), Markowitz (1952), Ibbotson et al. (2007), Yaari (1965), Bengen (1994), Hershfield et al. (2011), Thaler & Benartzi (2004).
- No real users, testimonials, partner logos or performance claims exist; none may be invented.

## Product Principles

1. One number first, then the story behind it.
2. Plain Thai for people new to money; theory is available but never in the way.
3. Every suggestion is a concrete, small action with its measured effect.
4. Honest about uncertainty: show ranges, not promises.

## Accessibility & Inclusion

Must work on phones and in light and dark mode; respect reduced-motion; inputs reachable by keyboard and typeable (not slider-only).
