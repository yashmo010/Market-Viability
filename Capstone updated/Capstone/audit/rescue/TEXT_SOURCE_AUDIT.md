# TEXT SOURCE AND MARKETING COPY AUDIT
**Date**: October 2026  
**Scope**: Bounded Model Rescue Feasibility Test — Marketing Copy Problem (Section 9)  
**Dataset**: Frozen Test Set ($N=124$), 669 Raw Specification Bullets and Product Descriptions

---

## 1. Executive Summary

A critical diagnostic question in the model rescue inquest is:
> *Does the source text input fed into the LLM aspect bridge contain factual technical specifications, or is it contaminated by promotional marketing boilerplate that degrades semantic aspect extraction?*

**Empirical Finding**:
- An automated forensic audit of all **669 specification bullets** across the frozen test set ($N=124$) reveals that **75.5% (505/669) of bullets contain promotional marketing claims, subjective adjectives, or brand boilerplate**.
- Only **24.5% (164/669)** represent strict, measurable engineering specifications (e.g., numeric dimensions, wattages, sensory resolutions, protocols).
- Despite prompt instructions asking the LLM to act as an "objective skeptic engineer," the LLM systematically converts marketing rhetoric into elevated aspect scores (e.g., rating `build_quality` as 4.5/5 based on claims of "aerospace-grade aluminum" or "military-grade durability").
- This contamination explains why the LLM aspect bridge generates high collinearity, excessive score compression, and poor predictive discrimination.

---

## 2. Text Corpus Forensic Breakdown

Across the 124 test products, we audited the raw `specs.features` and `description` fields extracted from e-commerce product pages prior to launch:

| Category | Total Products | Total Bullets Audited | Pure Factual Specs | Marketing / Subjective Bullets | Contamination Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Coffee Machines** | 24 | 134 | 31 (23.1%) | 103 (76.9%) | **76.9%** |
| **Ice Makers** | 22 | 118 | 38 (32.2%) | 80 (67.8%) | **67.8%** |
| **Mechanical Keyboards** | 26 | 142 | 34 (23.9%) | 108 (76.1%) | **76.1%** |
| **Smartwatches** | 25 | 139 | 28 (20.1%) | 111 (79.9%) | **79.9%** |
| **Webcams** | 27 | 136 | 33 (24.3%) | 103 (75.7%) | **75.7%** |
| **Total / Pooled** | **124** | **669** | **164 (24.5%)** | **505 (75.5%)** | **75.5%** |

---

## 3. Taxonomy of Marketing Text Contamination

The audit categorized the 505 non-factual bullets into five distinct distortion archetypes:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   TOTAL BULLETS AUDITED: 669                           │
├───────────────────────────────────┬────────────────────────────────────┤
│   PURE FACTUAL SPECS: 164 (24.5%) │ CONTAMINATED MARKETING: 505 (75.5%)│
└───────────────────────────────────┴────────────────────────────────────┘
                                           │
         ┌─────────────────────────────────┼────────────────────────────────┐
         ▼                                 ▼                                ▼
Promotional Adjectives           Brand & Promotional Claims        Subjective / Unverifiable
  351 bullets (52.5%)                247 bullets (36.9%)               219 bullets (32.7%)
  "crystal-clear audio"              "industry-leading design"         "unmatched comfort"
  "ultra-durable chassis"            "patented revolutionary tech"     "stunning elegant look"
```

### 3.1 Promotional Adjectives (52.5% of Bullets)
- **Patterns**: Unsubstantiated superlatives and promotional qualifiers (`premium`, `revolutionary`, `ultimate`, `superior`, `crystal-clear`, `ergonomic perfection`, `military-grade`).
- **Effect on LLM**: When prompted to score `build_quality` or `durability`, the LLM consistently increases scores by $+0.5$ to $+1.2$ points upon encountering words like "military-grade" or "aircraft-grade aluminum," regardless of whether physical alloy specifications are provided.

### 3.2 Brand and Promotional Claims (36.9% of Bullets)
- **Patterns**: Self-referential brand praise (`"engineered by the world's leading audio experts"`, `"trusted by millions of gamers"`, `"award-winning Swiss craftsmanship"`).
- **Effect on LLM**: Conflates brand prestige with physical product utility, creating high correlation between LLM aspects and brand tier ($r = +0.55$).

### 3.3 Subjective / Unverifiable Claims (32.7% of Bullets)
- **Patterns**: Aesthetic and affective claims (`"breathtaking visual clarity"`, `"whisper-quiet operation"`, `"luxurious feel in your hands"`).
- **Effect on LLM**: Distorts `design_appeal` and `ease_of_use` into subjective echo chambers of promotional ad copy rather than ergonomic assessments.

### 3.4 Category Boilerplate (27.2% of Bullets)
- **Patterns**: Descriptions that apply generically to all products in the category (`"ideal for home, office, and travel"`, `"great gift for family and friends"`, `"simple plug-and-play installation"`).
- **Effect on LLM**: Compresses aspect variance within categories because virtually all competing products claim identical baseline conveniences.

---

## 4. Grounded Technical Specs vs. Marketing Claims: Comparative Case Studies

| Product UID | Category | Raw Text Sample | Factual Technical Core | LLM Score Impact |
| :--- | :--- | :--- | :--- | :--- |
| `P_COF_041` | Coffee Machine | *"Experience barista-quality espresso at home with our ultimate 15-bar Italian pump delivering rich crema and unforgettable flavor every morning."* | `15-bar pump` | Scores: Utility = 4.3, Value = 4.1. The LLM rates marketing promises rather than boiler material or PID temperature stability. |
| `P_KBD_088` | Keyboard | *"Built like a tank with indestructible aircraft-grade aluminum top plate and glorious RGB lighting with 16.8 million vibrant colors."* | `Aluminum plate, RGB LEDs` | Scores: Durability = 4.7, Build Quality = 4.8. High score awarded based on "aircraft-grade" rhetoric; switches are unbranded clones. |
| `P_WAT_112` | Smartwatch | *"Your personal wellness guru featuring cutting-edge AI health tracking, revolutionary all-day battery life, and sapphire-like glass."* | `Optical PPG sensor, Li-ion battery` | Scores: Utility = 4.5, Reliability = 4.2. "Sapphire-like" is marketed as sapphire; real scratch resistance is standard mineral glass. |

---

## 5. Why Prompting Cannot Resolve the Text Contamination

The project utilized explicit system instructions attempting to enforce objective evaluation:
> *"You are a rigorous, skeptical hardware evaluation engineer. Disregard marketing puffery and promotional claims. Evaluate only objective physical and technical specifications."*

### Why this failure mode persisted:
1. **Asymmetric Information**: When a product page contains *only* marketing descriptions and lacks detailed schematics or teardown reports, the LLM has no alternative data source. A skeptical LLM must either:
   - Output missing/default values (which would collapse feature variance), or
   - Infer capabilities from the available rhetoric (which introduces hallucinated quality rankings).
2. **Hallucination of Plausibility**: LLMs naturally associate sophisticated marketing phrasing with higher product caliber. Products with slick copywriting receive systematically higher aspect ratings than generic OEM products with identical circuit boards.
3. **Loss of Fine-Grained Signals**: While the LLM abstracts away messy text, it discards critical predictive tokens (e.g., specific controller chips like `PixArt 3370`, switch types like `Gateron Yellow`, or specific Bluetooth codecs like `aptX HD`). These granular tokens are preserved by raw TF-IDF vectorization (explaining why TF-IDF Ridge achieves $\rho = 0.683$ and residual $\rho = +0.336$, whereas LLM aspects achieve residual $\rho = -0.119$).

---

## 6. Scientific Implications for Model Rescue

The text source audit demonstrates that:
1. **The input data available at pre-launch is overwhelmingly promotional text (75.5%) rather than engineering telemetry.**
2. Attempting to extract 9 continuous engineering aspects from promotional ad copy produces noisy, collinear, and hallucinated scores.
3. Filtering the text to only strict factual specifications reduces the usable feature space to a handful of sparse tokens (e.g., wattage, dimensions, weight), which are already captured more effectively by regularized linear models directly on raw tokens.
4. Consequently, refining prompt engineering or aspect rubrics cannot overcome the fundamental information scarcity of the underlying e-commerce text.
