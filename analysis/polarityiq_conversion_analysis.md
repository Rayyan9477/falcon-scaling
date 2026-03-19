# PolarityIQ: Free Trial → Paid Conversion Analysis

## Executive Summary

After a thorough review of all three Falcon Scaling / PolarityIQ web properties (app.polarityiq.com, polarityiq.com, falconscaling.com), I identified **3 critical trust-breaking inconsistencies**, **5 high-impact conversion friction points**, and **12 specific recommendations** organized by timeline. The platform's core value proposition is strong — 10,000+ FO profiles with verified contact data at $295-$1,995/mo vs. $15K-$25K/yr from legacy providers. However, messaging contradictions between properties, a suboptimal signup flow, and missing in-product conversion triggers are likely leaving significant conversion upside on the table.

---

## 1. Platform Audit — What I Observed

### 1.1 app.polarityiq.com (SaaS Platform + Landing Page)

**What works well:**
- **Hero section** is strong: "Comprehensive Family Office Intelligence" with social proof ("Trusted by 600+ Investment Professionals") and triple CTA (Start Free Trial / View Guide / Book Demo)
- **Comparison table** (PolarityIQ vs Legacy Providers) is the single strongest conversion element on the entire site. The price anchoring ($295/mo vs $15K-$25K/yr legacy) is highly effective against competitors
- **10 specific user personas** listed in "Who It's For" section — unusually specific, helps visitors self-identify immediately
- **3-step "How It Works"** with visual mockups showing the search → reveal → export flow is clean and effective
- **Platform Guide page** (/guide-ex) acts as an interactive demo substitute — well-designed educational content

**Pricing structure observed:**
| Plan | Price | Tokens | Per Token |
|------|-------|--------|-----------|
| Starter | $295/mo | 100 | $2.95 |
| Basic (Most Popular) | $395/mo | 250 | $1.58 |
| Pro | $795/mo | 600 | $1.33 |
| Premium | $1,995/mo | 2,000 | $1.00 |

Trial: 7 days, 10 tokens (contact reveals), credit card required.

### 1.2 polarityiq.com (Marketing / Data Sales Site)

- Completely different design (white theme on Webflow vs. dark theme on app)
- Sells **one-time database packages** (not SaaS subscriptions): Institutional Investor MAX, REI MAX, CIO MAX, RIA MAX, etc.
- Service request form with 10+ fields including budget dropdown ($2,500-$50,000)
- Product pages show real data previews (BlackRock, Vanguard, etc.) — very effective
- 8 distinct data products beyond the Family Office SaaS
- Stats: "2,000+ Clients Served" | "$100 Million Raised in 36 Months"

### 1.3 falconscaling.com (Parent Company)

- WordPress blog, last updated May 2022 — completely dormant
- Same address (344 West 38th St) and phone as PolarityIQ
- No CTAs, no lead capture, no cross-links to PolarityIQ
- Broken footer link (email href points to WordPress theme provider site)
- Content about CRM optimization (PipeDrive, Salesforce) — unrelated to current FO intelligence business

---

## 2. Critical Trust-Breaking Issues (Fix Immediately)

### Issue #1: Data Count Contradiction
**Location**: app.polarityiq.com hero section
**Problem**: The H1 subtext says **"10,000+ Family Offices"** but the stats bar directly below says **"800+ Family Offices"**. A prospect reading both in sequence immediately questions which number is real.
**Fix**: Reconcile to one number. If the database has 10,000+ FO profiles but 800+ with verified contacts, say: "10,000+ Family Office profiles | 800+ with verified decision-maker contacts."
**Impact**: Eliminates the single most damaging trust signal on the page.

### Issue #2: Credit Card Requirement Contradiction
**Location**: Platform Guide page (/guide-ex) vs. Signup page (/signup) and Pricing section
**Problem**: The guide page CTA says **"No credit card required"** while the signup page and every pricing card explicitly state **"Credit card required"** with a warning icon. A prospect who reads the guide, clicks "Start Free Trial," and then sees "credit card required" will feel deceived.
**Fix**: Update the guide page CTA to match reality, or remove the CC requirement from the trial.
**Impact**: Prevents the most common reason for trial abandonment complaints.

### Issue #3: "Not a SaaS Platform" Claim
**Location**: polarityiq.com/polarity-difference
**Problem**: This page states **"Polarity IQ is not a SaaS platform. We build and deliver private markets insights directly to our clients, not through a pay-wall interface."** Meanwhile, app.polarityiq.com IS a SaaS platform with $295-$1,995/mo subscriptions and a paywall. If a prospect sees both, credibility is significantly weakened.
**Fix**: Rewrite the Polarity Difference page to distinguish the custom data business from the SaaS platform: "PolarityIQ offers two ways to access intelligence: our self-serve SaaS platform for Family Office data, and custom-built datasets for institutional, real estate, and other investor verticals."
**Impact**: Resolves the fundamental brand confusion between the two properties.

---

## 3. High-Impact Conversion Friction Points

### Friction #1: Signup Flow — All Fields on One Page, No SSO
**Observed**: The signup page shows all fields simultaneously (First Name, Last Name, Email, Password, Confirm Password + strict password requirements). No Google or LinkedIn SSO option.
**Problem**: For a B2B product targeting investment professionals, LinkedIn SSO is table stakes. Every additional field reduces completion by ~10%. Showing password requirements upfront creates cognitive load.
**Recommendation**:
1. Add LinkedIn SSO and Google SSO (one-click signup)
2. Progressive wizard: Step 1 = Email only → Step 2 = Name + Password → Step 3 = Plan selection
3. Show real-time password strength feedback instead of listing all 5 requirements upfront

**Expected impact**: Meaningful lift in signup completion. The multi-step wizard is the highest-ROI change here (low engineering cost, fast to implement). LinkedIn SSO requires OAuth integration, LinkedIn developer application approval, and account linking logic — typically 3-4 weeks of engineering — so treat it as a medium-term investment.

### Friction #2: Deferred Plan Selection Creates Uncertainty
**Observed**: The signup page shows only the free trial details. A note says "After signup, you'll choose your plan and enter payment details." But the actual plan tiers ($295-$1,995/mo) are not visible during signup.
**Problem**: Users don't know what they're committing to. The pricing page shows plans, but the signup flow hides them. This creates a "what will it cost me after the trial?" anxiety. Specifically for PolarityIQ's token model, users need to understand the per-token economics before committing — a fund manager evaluating 50 FOs needs to know whether Starter (100 tokens at $2.95/reveal) or Basic (250 at $1.58) fits their workflow.
**Recommendation**: Show all 4 plan cards on the signup page with the trial framing: "Start with 7 days free. Choose a plan to continue after your trial." Highlight the per-token cost difference to help users self-select.

**Expected impact**: Users who enter the trial with a specific plan in mind convert at higher rates because the pricing decision is already partially made.

### Friction #3: Token Allocation May Not Reach "Aha Moment"
**Observed**: Free trial includes 10 token reveals over 7 days.
**Problem**: 10 reveals may not be enough to demonstrate the platform's value for a user who needs to evaluate data quality across multiple FOs. If they reveal 10 contacts and 2-3 have bounced emails or outdated titles, the trial feels like a failure.
**Important caveat**: There's a real risk in going too high — if users can satisfy their immediate need within free tokens (e.g., find the 15-20 FOs they actually want to contact), they may never convert. The right number should be enough to demonstrate value but not enough to complete the user's task.
**Recommendation**: Rather than a fixed increase, A/B test token allocation (10 vs. 15 vs. 25) and track the correlation between tokens used and conversion. The "bonus tokens for actions" approach is likely superior — offer +5 tokens for running a first search, +5 for saving a search, +5 for exporting CSV. This gamifies onboarding while preventing users from getting full value without engagement.

**Key metric to track**: "Tokens used during trial" as a conversion predictor. If users who use 8+ tokens convert at 3x the rate of those who use <3, then the token allocation isn't the problem — activation is.

### Friction #4: No Onboarding Email Sequence
**Observed**: No evidence of a post-signup drip campaign in the public-facing properties. (Caveat: an internal email sequence may exist but was not visible from external audit — confirm with the product team.)
**Problem**: Users who sign up for a 7-day trial typically explore once, leave, and forget to return before expiry. Without email nudges, these users are lost.
**Recommendation**: Implement a 5-email activation sequence tailored to PolarityIQ's specific value prop:

| Day | Email | Purpose |
|-----|-------|---------|
| Day 0 | "Your first FO intel: [Marquee FO like Cascade Investment]" | Pre-built search result showing real data to prove value immediately |
| Day 1 | "You have 10 tokens — here's how top fund managers use them" | Teach the token economy with a specific workflow: search → filter → reveal → export |
| Day 3 | "3 family offices matching [user's stated sector/region]" | Personalized based on signup data — PolarityIQ-specific content, not a generic drip |
| Day 5 | "You've used X of Y tokens — unlock 5 more" | Urgency + gamified token bonus for completing an action (e.g., save a search) |
| Day 6 | "Trial ends tomorrow: Starter ($295/mo) vs. Basic ($395/mo)" | Final push with specific plan comparison and per-token cost difference |

**Expected impact**: Well-executed onboarding sequences typically lift trial engagement by 25-40% for B2B SaaS (Source: Intercom benchmarks). Actual lift depends on current email open rates and activation baseline.

### Friction #5: Two Disconnected Web Properties
**Observed**: app.polarityiq.com and polarityiq.com have different designs, different business models (SaaS vs. custom data), and no cross-navigation.
**Problem**: A prospect who finds the marketing site sees a custom data business. A prospect who finds the app sees a SaaS platform. There's no unified navigation explaining the relationship. Prospects looking for custom datasets can't find them from the app, and vice versa.
**Recommendation**:
1. Add a persistent top bar to both sites: "SaaS Platform | Custom Data | Contact Us"
2. Unify the brand narrative on both sites
3. Add a "Need a custom dataset?" CTA on the app's pricing page for users who need more than the SaaS
4. Add a "Try our self-serve platform" CTA on the marketing site for users who want instant access

**Expected impact**: Captures prospects who would otherwise bounce between properties and leave.

---

## 4. What's Working — Don't Change These

1. **Comparison table** (PolarityIQ vs Legacy Providers) — most powerful conversion element on the site. The price anchoring is excellent.
2. **10 user personas** — specific ICP targeting helps visitors self-identify
3. **Triple CTA** (Free Trial / Guide / Demo) — caters to different buyer intent levels
4. **Token reveal system** — the "blur → reveal" UX for contacts is elegant and demonstrates value before purchase
5. **Platform Guide** (/guide-ex) — acts as an interactive demo without requiring signup
6. **"A+/A/B" email quality badges** — unique differentiator that signals data quality
7. **Logo bar** (Saison Capital, Cresset, Hamilton Lane, Marathon, Roth) — institutional credibility
8. **$0 due today** messaging on signup — strong reassurance for trial conversion

---

## 5. In-Product Conversion Opportunities (Not Visible from External Audit)

The following recommendations address what happens *inside* the product during the trial — the highest-leverage conversion surface area. These require internal product team validation.

### 5.1 Token Exhaustion Experience
**The moment a trial user runs out of tokens is the single most important conversion moment.** What does the user see? Options:
- **Worst**: Generic "upgrade to continue" modal → feels like a paywall, not a value exchange
- **Better**: "You've revealed 10 contacts. Here's a summary of what you found: [list of revealed FOs]. Upgrade to continue building your target list." → reinforces value already received
- **Best**: "You've revealed 10 contacts. 37 more family offices match your search criteria. Upgrade to Starter ($295/mo, 100 reveals) to unlock them." → shows the specific opportunity cost of not upgrading

### 5.2 Upgrade Path from Starter → Basic → Pro
For a tiered token model, in-product upgrade nudges matter enormously:
- When a Starter user ($295/mo, 100 tokens) approaches 80% usage mid-month, surface: "You're running low. Basic ($395/mo) gives you 150 more reveals at a lower per-token cost ($1.58 vs $2.95)."
- Track which tier's users churn fastest — if Starter has 2x churn vs. Basic, the Starter allocation may be too low to deliver sufficient value.

### 5.3 Trial Win-Back Flow
When a 7-day trial expires without conversion:
- **Day 8**: "Your trial ended, but your saved searches are still here. Reactivate with Starter ($295/mo) to pick up where you left off."
- **Day 14**: "Still interested? Here's a 20% discount on your first month: code COMEBACK20."
- **Day 30**: Final attempt with a different angle: "3 new family offices were added this month that match your search criteria. Reactivate to see them."
This win-back sequence typically recovers 5-10% of expired trials at near-zero acquisition cost.

### 5.4 In-Product Trial Experience

**These in-product moments are often the highest-leverage conversion points for token-based SaaS.** The following checklist should be validated with the product team:

- **Token exhaustion upgrade modal**: When trial tokens are exhausted, does the user see a clear, value-reinforcing upgrade modal (not a generic paywall)? The modal should recap what they found and quantify what they'll miss — e.g., "You revealed 10 contacts. 37 more family offices match your criteria. Upgrade to Starter ($295/mo) to unlock them."
- **Usage dashboard**: Is there a persistent, visible indicator showing tokens remaining? Trial users should always know where they stand. A "5 of 10 tokens used" counter in the nav bar creates healthy urgency without being pushy.
- **Pre-exhaustion upgrade nudges**: Are there in-app nudges *before* tokens run out? When a user reaches 7-8 of 10 tokens, surface a contextual prompt: "Running low on reveals? Upgrade now to keep building your list." Nudging before exhaustion converts better than nudging after — the user is still engaged and in-flow.
- **Trial extension / win-back flow**: What happens when a 7-day trial expires without conversion? Is there a mechanism to offer a short extension (e.g., 3 bonus days + 5 bonus tokens) in exchange for a specific action (booking a demo, completing a profile)? Expired-trial win-back is a near-zero-cost recovery channel.

### 5.5 In-App Chat / Support for High-Value Prospects
At $295-$1,995/mo ($3,540-$23,940/yr), PolarityIQ's ACV justifies real-time support:
- Add live chat or Intercom during trial for users who have revealed 5+ tokens (high-intent signal)
- For users browsing the Premium tier ($1,995/mo), trigger a sales-assist nudge: "Want a walkthrough of the Premium plan? Book a 10-minute call."
- The Premium tier specifically may convert better through a hybrid PLG + sales-assist motion than pure self-serve

---

## 6. Competitive Context

| Feature | PolarityIQ | Fintrx | Dakota | PitchBook |
|---------|-----------|--------|--------|-----------|
| FO-specific database | 10,000+ profiles | 3,800+ firms | Partial | Partial |
| Verified emails | Yes (A+/A/B grading) | Yes | Limited | Yes |
| Direct phone numbers | Yes | Yes | No | Yes |
| Price | $295-$1,995/mo | ~$10K-15K/yr | ~$5K-10K/yr | ~$20K-40K/yr |
| Free trial | 7 days, 10 tokens | No (demo only) | No (demo only) | No (demo only) |
| Token/usage model | Yes (pay-per-reveal) | Unlimited access | Unlimited | Unlimited |
| Self-serve signup | Yes | No (sales-led) | No (sales-led) | No (sales-led) |
| NL query / AI features | Emerging | No | No | Limited |
| Custom data packages | Yes (via polarityiq.com) | No | No | Custom pricing |

**PolarityIQ's strongest competitive advantage**: Self-serve + low price + free trial. Every competitor requires a sales call. PolarityIQ is the only platform where a fund manager can sign up, search, and reveal a family office decision-maker's email in 5 minutes, without talking to anyone. This is a massive differentiator that should be emphasized more prominently.

---

## 7. Recommendations by Timeline

### Quick Wins (1-2 Weeks) — Copy/config changes only
1. **Fix the three data contradictions** (10K vs 800, CC required vs not, "not a SaaS" claim) — pure copy fixes, < 1 hour each
2. **Add competitive pricing anchor** to the pricing section: "PitchBook: $24K/yr. Fintrx: $12K/yr. PolarityIQ: from $295/mo." — copy change only
3. **A/B test trial token allocation** (10 vs 15 vs 20) — configuration change, track conversion by cohort
4. **Optimize token exhaustion modal** — show specific opportunity cost ("37 more FOs match your criteria") instead of generic upgrade prompt
5. **Add "Remember me" checkbox** and improve signup form with real-time password strength indicator

### Medium-Term (2-6 Weeks) — Engineering work
6. **Redesign signup as multi-step wizard** (Email → Name/Password → Plan Selection with pricing visible)
7. **Build 5-email activation sequence** with PolarityIQ-specific content (real FO data in emails, token usage tracking triggers)
8. **Add LinkedIn SSO** (Medium-Term, 3-4 weeks — requires OAuth integration, LinkedIn developer application approval, and account linking logic)
9. **Implement trial win-back sequence** (Day 8, 14, 30 emails for expired trials)
10. **Add in-app live chat** for trial users who reveal 5+ tokens (high-intent signal)

### Strategic (1-3 Months) — Product architecture changes
11. **Unify navigation** between app.polarityiq.com and polarityiq.com with persistent cross-site bar
12. **Add annual pricing option** with discount — but first validate whether PolarityIQ's token model creates natural monthly stickiness that makes annual discounting counterproductive
13. **Retire or redirect falconscaling.com** — serves no current conversion purpose
14. **Build graduated paywall** — let free users search and see FO names/AUM/sectors, gate contact reveals behind tokens. Requires significant product architecture work; spec out separately.
15. **Sales-assist for Premium tier** ($1,995/mo) — this ACV level ($24K/yr) likely converts better with a hybrid PLG + sales motion than pure self-serve

---

## 8. Measurement Framework

### Key Metrics to Track

| Metric | Definition | B2B SaaS Benchmark | PolarityIQ Target |
|--------|-----------|-------------------|-------------------|
| Signup completion rate | % of pricing page visitors who complete signup | 20-40% (CC-required trials) | Measure baseline, then improve by 20%+ |
| Trial activation rate | % of signups who reveal ≥1 contact | 40-60% for B2B trials | >70% |
| Trial → Paid conversion | % of trial users who subscribe | 5-8% (CC-required, B2B) | >10% |
| Time to first reveal | Seconds from signup to first token use | N/A (PolarityIQ-specific) | <180s |
| Tokens used per trial | Avg tokens consumed during trial | N/A | Track as conversion predictor |
| Monthly churn (paid) | % of paid users who cancel per month | 5-7% for SMB SaaS | <6% |
| Upgrade rate | % of Starter users who upgrade to Basic+ | 10-15% for tiered SaaS | >15% |

> **Note: These estimates are based on industry benchmarks for comparable B2B SaaS products with credit-card-required free trials ($200-2000/mo ACV). They are directional benchmarks, not measured PolarityIQ data. Actual metrics should be validated with internal analytics.**

*"B2B SaaS Benchmark" values sourced from industry reports (Lenny's Newsletter, OpenView Partners, Bessemer Cloud Index). PolarityIQ's actual current metrics should be instrumented and measured before setting specific targets.*

### Leading Indicator of Conversion
Based on the token-based model, the likely activation event is: **"User reveals 5+ contacts AND exports at least 1 CSV within the first 4 days."** Users who hit this threshold should convert at 3-5x the rate of those who don't. Track this cohort and optimize onboarding to drive users toward it.

### A/B Test Priority
1. **Credit card vs. no credit card** for trial signup (highest-impact test)
2. **10 tokens vs. 25 tokens** for trial allocation — **Risk: If 25 tokens satisfy the user's immediate need (finding ~20 target FOs), they may never convert. Monitor tokens-used as a conversion predictor before changing. Consider progressive token grants (10 on signup, +15 after first search) to maintain engagement.**
3. **Single-page signup vs. multi-step wizard**
4. **With vs. without a 60-second walkthrough video** showing the search → filter → reveal → export flow on real FO data — PolarityIQ's buyer persona (fund managers, capital raisers) is time-constrained and wants to see data quality proof before committing to a trial; a short video demonstrating a real contact reveal may reduce the perceived risk of entering credit card details
