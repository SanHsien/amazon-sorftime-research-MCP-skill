# amazon-sorftime-research: Open-Source Amazon AI Product Research & Operations Toolkit

**English** | [繁體中文](README.md)

> **An open-source intelligent product research and operations toolbox built for Amazon cross-border e-commerce sellers. Automate competitor teardown, negative review mining, and high-converting listing creation using slash commands.**

---

## Key Highlights

- **Quadruple E-Commerce MCP Data Integration**: Seamlessly integrates **Sorftime**, **SellerSprite**, **Xiyou Insight**, and **Sif** Model Context Protocol data streams.
- **14 Amazon Marketplaces & Multi-Platform Influencer Analysis**: Supports US, EU, UK, JP, and other major marketplaces, extended with TikTok video analysis, creator insights, and 1688 supply-chain cost extraction.
- **Automated Competitor Teardown via Slash Commands**: Trigger full-dimension penetration analysis with simple commands like `/amazon-analyse` and `/product-research`.
- **Negative Review Mining & Actionable Improvements**: Analyzes thousands of customer reviews across 6 pain-point dimensions, generating tangible product iteration roadmaps and customer support templates.
- **Built-in 8-Step Workflow for High-Converting Listings**: Complete pipeline from keyword/question/evidence libraries to title, bullets, A+ content, and search terms.
- **Optimized for Modern Conversational Search Algorithms**: Tailored for Amazon's Cosmo semantic algorithm and Rufus / Alexa AI shopping assistants to maximize organic visibility.
- **Automated Visual Dashboards & Deep Excel Reports**: Automatically produces interactive HTML dashboards, comprehensive Excel workbooks, and detailed Markdown reports.
- **Ready to Run with Claude Code & Codex**: Simply configure your MCP credentials in `.mcp.json` and get started immediately.

---

## Core Skills & Slash Command Reference

All 9 AI skills are located under `SKILLS/skills/`:

| Skill | Target | Slash Command | Core Features & Outputs |
|---|---|---|---|
| **amazon-analyse** | Single Listing | `/amazon-analyse {ASIN} {SITE}` | Full-dimension competitor penetration: sales estimates, traffic sources, keyword layout, review sentiment clustering, 1688 cost breakdown. |
| **category-selection** | Entire Category | `/category-select "{Category}" {SITE}` | Category selection analysis: Top 100 data, 5-dimensional scoring model (Scale, Growth, Competition, Barrier, Profitability), Markdown/Excel/HTML outputs. |
| **keyword-research** | Keyword Database | `/keyword-research {ASIN} {SITE}` | Deep keyword discovery: collects 1,500+ keywords, 8-dimensional intelligent categorization (Brand, Material, Scenario, Feature, Negative words, etc.). |
| **review-analysis** | Reviews | `/review-analysis {ASIN} {SITE}` | Customer review mining: deep analysis of negative feedback, 6-dimension pain-point matrix, and mitigation strategies. |
| **product-research** | Product Intelligence | `/product-research "{Keyword}" {SITE}` | LLM-driven research: market opportunities, buyer personas, price distribution, and entry barrier warnings. |
| **sif-amazon-research** | Comprehensive Research | `/sif-amazon-research` | Powered by Sif MCP: market validation, competitor traffic penetration, advertising audits, and launch roadmaps. |
| **xiyou-insight** | Traffic & Advertising | `/xiyou-insight` | Xiyou Insight 7 scenarios: ad monitoring, traffic gaps, competitor ad teardown, and launch budget planning. |
| **sellersprite-amazon-research** | Full-Funnel Tools | `/sellersprite-research` | Leverages 43 SellerSprite tools for blue-ocean discovery, keyword reverse lookup, pricing strategy, and listing audits. |
| **amazon-listing-builder** | Listing Creation | `/listing-builder` | Cosmo semantic algorithm + Rufus conversational search: 8-step pipeline for top-tier Amazon listings. |

---

## 8-Step Listing Builder Workflow

```text
1. Layered Keyword Library
   └── Core terms, long-tail terms, scenario terms, high-conversion terms
2. Customer Question Library
   └── Natural language queries modeled for AI shopping assistants (Rufus)
3. Evidence & Proof Library
   └── Spec validations, test benchmarks, certifications, use-case proof
4. Title Design
   └── Optimized for the first 60 characters on mobile + search weight
5. Feature Bullet Points
   └── Scenario-based pain points + solutions + concrete proof
6. Description & A+ Content
   └── Modular copy and conversational search semantic embedding
7. Backend Search Terms (ST)
   └── Strict 250-byte constraint, zero repetition with frontend copy
8. Strategic Q&A Design
   └── Proactively addresses high-frequency customer hesitations
```

---

## Quick Start

### 1. Installation & Environment Setup

```powershell
git clone https://github.com/SanHsien/amazon-sorftime-research-MCP-skill.git
cd amazon-sorftime-research-MCP-skill
gh repo set-default SanHsien/amazon-sorftime-research-MCP-skill
pip install -r requirements.txt
```

### 2. Configure MCP Servers

Edit `.mcp.json` in the root directory (see `.env.example` for template):

```json
{
  "mcpServers": {
    "sorftime": {
      "type": "streamableHttp",
      "url": "https://mcp.sorftime.com?key=YOUR_SORFTIME_API_KEY",
      "name": "Sorftime MCP"
    },
    "sif-mcp": {
      "type": "http",
      "url": "https://mcp.sif.com/mcp",
      "headers": {
        "secret-key": "YOUR_SIF_SECRET_KEY"
      }
    },
    "xydc-mcp": {
      "type": "http",
      "url": "https://mcp.xydc.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_XIYOU_TOKEN"
      },
      "name": "Xiyou Insight MCP"
    },
    "sellersprite": {
      "url": "https://mcp.sellersprite.com/mcp",
      "headers": {
        "secret-key": "YOUR_SELLERSPRITE_SECRET_KEY"
      },
      "name": "SellerSprite MCP"
    }
  }
}
```

### 3. Run with Claude Code / Codex

Launch Claude Code or Codex:
```bash
claude
```

Run skills directly in the chat:
```text
> /amazon-analyse B0D9ZTW7PS US
> /category-select "Wireless Earbuds" US
> /keyword-research B0D9ZTW7PS US
> /listing-builder
```

---

## Quality Gate & Governance

```powershell
# Run test suite & integrity checks
python -m pytest tests -v

# Verify upstream updates
python tools/check_upstream_updates.py --strict

# Windows One-Click Dev Check Gate
pwsh -NoProfile -File tools/dev_check.ps1 -Quick
```

---

## Fork Credits

- Forked from original author **liangdabiao**: [`liangdabiao/amazon-sorftime-research-MCP-skill`](https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill).
- Maintained by [SanHsien](https://github.com/SanHsien) with Windows-first enhancements, Traditional Chinese localization, test integrity, and automated governance.

