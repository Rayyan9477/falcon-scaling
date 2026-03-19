# Task 4 — Build Process Documentation

## Product: Co-Investment Intelligence Accelerator ($197)

---

## Step-by-Step Build Process

### Step 1: Problem Identification & ICP Definition
**Tool**: Human analysis + AI research
**Time**: 1 hour

- Analyzed the Falcon Scaling ecosystem: existing products (Family Office Catalyst, Private Markets Catalyst, Valuation Toolkit) to identify gaps
- Identified co-investment as the highest-value niche: 69% of FOs co-invest (UBS 2024 data), yet no affordable product maps co-investment networks
- Defined ICP: emerging fund managers ($50M-$500M AUM), PE/VC associates, placement agents
- Set price at $197: high enough to signal value, low enough for impulse purchase. Clear ascension to PolarityIQ subscription

### Step 2: Scoring Model Design
**Tool**: Python (pandas, numpy)
**Time**: 30 minutes

Designed a quantitative scoring framework for each of the 200 family offices:

**Co-Investment Score (1-10):**
- Co-Invest Frequency: High=3, Medium=2, Low=1
- Direct Investment: Yes=2, No=0
- LP Status: Active LP=3, Selective LP=2, Minimal=1
- Normalized to 1-10 scale

**Accessibility Score (1-10):**
- Data Confidence: High=3, Medium=2, Low=1
- Website exists: +1
- Email pattern available: +1
- LinkedIn exists: +1
- Contact complexity bonus: +1-3
- Normalized to 1-10 scale

**Outreach Readiness:**
- Green: Combined score >= 14 (ready for outreach)
- Yellow: Combined score 8-13 (needs more research)
- Red: Combined score < 8 (low priority)

### Step 3: Excel Dashboard Build
**Tool**: Python (openpyxl), Excel
**Time**: 1 hour

Created `scoring_model.py` to automate dashboard generation:
1. Read family office dataset (200 records, 45 fields)
2. Calculate Co-Investment Score, Accessibility Score, Outreach Readiness for each FO
3. Generate main dashboard sheet with conditional formatting (green/yellow/red)
4. Generate regional breakdown pivot sheet
5. Generate sector analysis sheet
6. Include scoring methodology documentation sheet

Output: `co_investment_accelerator.xlsx`

### Step 4: Approach Guide Writing
**Tool**: Claude AI + domain expertise
**Time**: 2 hours

Wrote "The Family Office Approach Playbook" — a 6-chapter guide covering:
1. FO co-investment decision architecture (3-Gate Model)
2. 5 types of FO co-investors with approach strategies
3. Conference strategy with specific events and playbook
4. Email/LinkedIn outreach templates
5. Red flags that destroy FO relationships
6. 12-month relationship building framework

Output: `approach_guide.md`

### Step 5: Custom GPT System Prompt
**Tool**: Manual crafting + AI assistance
**Time**: 30 minutes

Created system instructions for a ChatGPT Custom GPT:
- Personality: Senior capital introduction advisor
- Knowledge base: 200 FO co-investment dataset + approach methodology
- Capabilities: Personalized FO targeting based on fund specifics
- Example conversations for training

Output: `custom_gpt_prompt.md`

### Step 6: Product Packaging & Documentation
**Tool**: Manual
**Time**: 30 minutes

Created product overview (problem, ICP, price, ascension path) and this build process document.

---

## Platforms & Tools Used

| Platform/Tool | Purpose |
|--------------|---------|
| Python 3.11 | Scoring model and Excel generation |
| pandas | Data manipulation and analysis |
| openpyxl | Excel file creation with formatting |
| Claude (Anthropic) | AI-assisted content generation, research |
| VS Code + Claude Code | Development environment |
| ChatGPT (OpenAI) | Custom GPT creation platform |
| Git/GitHub | Version control and code hosting |

---

## What Makes This Product Different

1. **Not a pitch deck**: This is a real, functional product bundle — an Excel file that opens and works, a guide with actionable frameworks, and an interactive GPT.

2. **Built on real data**: The 200-FO dataset behind this product was independently created and validated (Task 1), not scraped from a template or generated synthetically.

3. **Clear ascension logic**: Every component deliberately creates a natural next step toward PolarityIQ. The static Excel makes users want live data. The guide teaches methodology but doesn't do the work. The GPT demonstrates the power of AI-queried FO intelligence.

4. **Priced for velocity**: At $197, the decision cost is trivial for the ICP. A placement agent earning 2% on a $50M raise ($1M) would spend $197 without hesitation if it helps them close one additional FO LP.
