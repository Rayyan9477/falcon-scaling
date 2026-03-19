# Task 1 — Dataset Creation: Methodology Documentation

## Overview

Created a validated dataset of **200 international family office intelligence records** with **45 fields per record**, covering 6 regions and 38 countries. The dataset prioritizes granularity and real-world accuracy over volume.

**Dataset creation date**: March 2026

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Primary programming language |
| openpyxl | XLSX reading/writing |
| pandas | Data manipulation, validation, statistics |
| Claude (AI) | Research assistance, data enrichment, pattern identification |
| Web research | Cross-referencing and validation against public sources |

---

## Data Acquisition Methodology

### Seed List Construction
1. **Tier 1 — Well-documented FOs** (Records 1-50): Started with the most visible family offices — those with public filings (SEC Form ADV, 13F), press coverage, and known portfolios. Examples: Walton Enterprises, Cascade Investment, Bezos Expeditions, Soros Fund Management.

2. **Tier 2 — Regionally significant FOs** (Records 51-150): Expanded to internationally important family offices across Europe (Grosvenor, KIRKBI, Wendel, Exor), Asia-Pacific (Li Ka-Shing, Son Family, Premji Invest), Middle East (Olayan, Mansour, Dubai Holding), Latin America (Slim, Lemann, Santo Domingo), and Africa (Motsepe, Dangote, Sawiris).

3. **Tier 3 — Specialized/niche FOs** (Records 151-200): Added multi-family offices, impact-focused FOs, next-gen FOs, and historically significant families (Portman Est. 1533, Grosvenor Est. 1677, Wendel Est. 1704).

### Source Hierarchy
- **Primary**: SEC EDGAR (Form ADV, 13F filings), regulatory databases (FCA, MAS, FINMA, ADGM)
- **Secondary**: Forbes billionaire rankings, Bloomberg, Financial Times, Reuters
- **Tertiary**: LinkedIn company profiles, Crunchbase, PitchBook public data
- **Quaternary**: Conference speaker lists (SuperReturn, SALT, Milken, FII), industry reports

---

## Data Enrichment Methodology

### 45-Field Schema (Organized by Section)

**Identity (7 fields)**: Family Office Name, Type (SFO/MFO), Founding Family, Year Established, HQ City, HQ Country, Region

**Contact (7 fields)**: Website, Primary DM LinkedIn, Email Pattern, Main Office Phone, LinkedIn Company URL, Contact Method, Conference Attendance

**People (4 fields)**: Primary Decision Maker, Primary DM Title, Secondary Decision Maker, Secondary DM Title

**Financials (2 fields)**: AUM ($B), Estimated Family Net Worth ($B)

**Operations (1 field)**: Employee Count (Est.)

**Investment (11 fields)**: Investment Strategy, Sector Focus, Geographic Focus, Asset Classes, Check Size Min ($M), Check Size Max ($M), Investment Stage, Direct Investment, Co-Invest Frequency, LP Status, GP/Direct Status

**Portfolio (1 field)**: Notable Portfolio Companies

**Relationships (3 fields)**: Fund Relationships, Co-Investor Relationships, ESG/Impact Level

**Signals (3 fields)**: Recent News (2024-2025), Recent Deals, Last Deal Date

**Governance (2 fields)**: Next-Gen Involvement, Philanthropy Focus

**Background (2 fields)**: Source of Wealth, Wealth Origin Sector

**Compliance (1 field)**: Regulatory Reference

**Meta (1 field)**: Data Confidence (High/Medium/Low)

### Enrichment Process
1. **Base data** populated from primary/secondary sources
2. **Investment profile** enriched from SEC filings, news, and portfolio databases
3. **Contact data** derived from LinkedIn, corporate websites, conference records
4. **Signal data** populated from 2024-2025 news and deal activity
5. **Relationship data** cross-referenced across records (co-investor networks)

---

## Validation Methodology

### AI Hallucination Safeguards
Claude AI was used for research assistance and data enrichment, but all AI-generated data was validated against primary sources before inclusion:
- Every family office name was verified to exist as a real entity via regulatory filings, press coverage, or corporate websites
- Decision maker names were cross-referenced against LinkedIn profiles and press releases
- AUM figures were checked against Forbes wealth rankings and regulatory filings — any AI-generated AUM that couldn't be corroborated was marked with "Data Confidence: Low"
- No AI-generated contact information (emails, phone numbers) was used without domain verification
- The Data Confidence field (High/Medium/Low) explicitly flags records where AI-assisted enrichment could not be fully validated

All AI-enriched fields were cross-referenced against at least one primary source (corporate website, SEC filing, or news article) to prevent hallucination. No AI output was accepted without human verification.

### Cross-Reference Protocol
Each record was validated against:
1. **Entity existence** — Confirmed the family office exists as a real entity (not fabricated)
2. **Decision maker verification** — Cross-referenced names against LinkedIn, press releases
3. **AUM plausibility** — Checked against Forbes wealth rankings, regulatory filings
4. **Location accuracy** — Verified HQ city and country
5. **Type accuracy** — Confirmed SFO vs. MFO classification

### Data Quality Issues Found and Fixed
- **Row 69 (Nair Pte Ltd)**: Complete column misalignment — all 45 fields were shifted. Reconstructed and realigned.
- **6 questionable entries replaced**:
  - "Mitsubishi Estate Family-Connected Office" → **HAL Investments** (Van der Vorm Family, Netherlands) — original was a public company, not a family office
  - "Mubadala-Adjacent Family Office (Al Mubarak)" → **Dallah Albaraka Group** (Kamel Family, Saudi Arabia) — original was sovereign fund adjacent, not a standalone FO
  - "Wellcome Trust Family-Connected Office" → **Reuben Brothers** (Reuben Family, UK) — original was a charitable foundation, not a family office
  - "Alibaba Co-Founders Family Offices (Various)" → **Yunfeng Capital** (Jack Ma, Hong Kong) — original was too vague ("Various" is not a specific entity)
  - "Rabobank-linked Family Offices (Dutch Agricultural)" → **JAB Holding** (Reimann Family, Luxembourg) — original was a bank cooperative, not a family office
  - "Wallenberg-Connected EQT Family Office" → **Hoffmann Family Office** (Roche, Switzerland) — original was a duplicate concept (Wallenberg already in dataset as Row 79)
- **Encoding**: Verified all non-ASCII characters (European accented names) render correctly.

### Confidence Scoring
Each record was assigned a Data Confidence level:
- **High (116 records)**: Multiple cross-referenced sources, verified decision makers
- **Medium (65 records)**: Single source or partial verification
- **Low (19 records)**: Limited public information, estimated fields

---

## Sources Used

| Source | Records Informed | Data Types |
|--------|-----------------|------------|
| SEC EDGAR (Form ADV, 13F) | ~50 US-based FOs | Entity verification, AUM, investment holdings |
| Forbes Global Billionaires | ~100 records | Net worth, source of wealth verification |
| LinkedIn | ~150 records | Decision maker names/titles, company profiles |
| Bloomberg / Reuters | ~80 records | Recent news, deal activity |
| Crunchbase | ~60 records | Portfolio companies, investment rounds |
| Regulatory databases (FCA, MAS, FINMA) | ~30 records | Regulatory status, jurisdiction |
| Conference records | ~40 records | Conference attendance, networking intel |
| Corporate websites | ~120 records | Website verification, email patterns |

---

## Challenges Faced

1. **Opacity of family offices**: By definition, FOs are private. Many lack websites, public filings, or press coverage. This is the fundamental challenge of FO intelligence.

2. **AUM estimation difficulty**: Unlike public funds, FO AUM is rarely disclosed. Estimates derived from Forbes net worth rankings may not reflect actual managed assets.

3. **Decision maker verification**: Family office leadership changes frequently. Names verified at time of creation may be outdated.

4. **International coverage bias**: US and UK FOs have more public data (SEC, FCA filings). Asia-Pacific, Middle East, and African FOs are harder to validate.

5. **Contact information sensitivity**: Real phone numbers and direct emails are sensitive data. Dataset uses email format patterns rather than verified personal emails.

6. **Temporal decay**: News and deal data represents a point-in-time snapshot. "Recent" signals become stale quickly.

---

## Key Insights

1. **SFO dominance**: 185/200 (92.5%) are single-family offices. Multi-family offices are rarer at scale.

2. **US concentration**: 52/200 (26%) are US-based, reflecting the country's wealth concentration and data availability.

3. **AUM distribution**: Highly skewed — median $15B vs. mean $28.2B. Top FOs (Walton $224.5B, Cascade $170B) pull the average up significantly.

4. **Co-investment trend**: 69 FOs rated "High" co-invest frequency, 73 "Medium" — suggesting co-investment is mainstream among large FOs.

5. **ESG gap**: 152/200 (76%) classified as "Traditional/Not Disclosed" for ESG. Despite industry rhetoric, most large FOs haven't publicly committed to ESG frameworks.

6. **Next-gen transition**: 87 FOs are multi-generational (3rd+), 75 are founder-led, 35 have 2nd generation emerging. The generational transition is a major industry dynamic.

---

## Dataset Summary

| Metric | Value |
|--------|-------|
| Total Records | 200 |
| Total Fields | 45 |
| SFO/MFO Split | 185 / 15 |
| Regions Covered | 6 (North America, Europe, Asia-Pacific, Middle East, Latin America, Africa) |
| Countries Covered | 38 |
| AUM Range | $0.2B - $224.5B |
| AUM Average | $28.2B |
| High Confidence | 116 (58%) |
| Medium Confidence | 65 (32.5%) |
| Low Confidence | 19 (9.5%) |
