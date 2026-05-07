# SKILL.md — Agri MCP Server
## Rural Intelligence Layer for Chhattisgarh

---

## What This Server Does

An MCP (Model Context Protocol) server that makes agricultural intelligence 
conversationally accessible. Connects live mandi prices, weather data, 
government schemes, and crop advisory into a single AI-queryable interface.

Built for Chhattisgarh. Expandable across India.

---

## Architecture

```
User asks Claude a question in plain English
           ↓
Claude identifies which MCP tools to call
           ↓
Agri MCP Server fetches from multiple APIs simultaneously
    ├── Agmarknet (mandi prices via data.gov.in)
    ├── OpenWeatherMap (weather data)
    ├── Government scheme database
    └── ICAR crop advisory database
           ↓
Claude synthesises and presents actionable insight
```

---

## Tools Available

### 1. get_mandi_prices
Fetch live commodity prices from Chhattisgarh mandis

**Parameters:**
- `commodity` (optional): paddy, maize, soybean, wheat, arhar
- `district` (optional): Any CG district
- `state` (default: Chhattisgarh)

**Example query:** "What is the current paddy price in Raipur mandi?"

**Returns:** Price data with MSP comparison and gap analysis

---

### 2. get_weather_advisory
Weather + agricultural action advisory for a district

**Parameters:**
- `district`: Raipur, Bastar, Surguja, Bilaspur etc.

**Example query:** "Should farmers in Bastar irrigate today?"

**Returns:** Temperature, humidity, rainfall + specific crop actions

---

### 3. get_agri_schemes
Government scheme matcher for farmer profiles

**Parameters:**
- `farmer_type`: small / marginal / large
- `crop`: paddy / maize / soybean
- `district`: Any CG district

**Example query:** "What schemes is a small paddy farmer in Surguja eligible for?"

**Returns:** Matched schemes with benefits, deadlines, and how to apply

---

### 4. get_crop_advisory
Stage-specific crop advisory for CG conditions

**Parameters:**
- `crop`: paddy / maize / soybean
- `stage`: sowing / growing / harvesting
- `district`: Any CG district

**Example query:** "How should I prepare for paddy sowing in Raipur?"

**Returns:** Varieties, seed rates, fertiliser, pest watch, tips

---

### 5. assess_distress_risk
Cross-layer farmer distress risk assessment

**Parameters:**
- `district`: Any CG district (required)
- `crop`: paddy / maize / soybean
- `landholding_acres`: Farm size as number

**Example query:** "How at-risk are paddy farmers with 2 acres in Bastar?"

**Returns:** Risk score, financial impact estimate, immediate actions

---

### 6. get_district_dashboard
Complete single-view intelligence for a district

**Parameters:**
- `district`: Any CG district

**Example query:** "Give me a full agriculture report for Surguja district"

**Returns:** Prices + weather + schemes + risk in one unified view

---

## Setup Instructions

### Step 1: Get API Keys (Do This First)

| API | URL | Cost | Time |
|-----|-----|------|------|
| data.gov.in | data.gov.in/user/register | Free | 10 mins |
| OpenWeatherMap | openweathermap.org/appid | Free | 5 mins |
| MyScheme API | api.myscheme.gov.in | Free | 2-7 days |
| NGO Darpan | ngodarpan.gov.in | Free | 3-10 days |

### Step 2: Install on Your Mac

```bash
# Clone or copy the project folder
cd agri-mcp-server

# Copy environment file
cp .env.example .env

# Add your API keys to .env file
nano .env

# Install Node.js MCP SDK
npm install @modelcontextprotocol/sdk

# Test Python server works
python3 src/agri_mcp_server.py
```

### Step 3: Connect to Claude Desktop

Add to your Claude Desktop config file:
`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agri-intelligence": {
      "command": "node",
      "args": ["/full/path/to/agri-mcp-server/index.js"],
      "env": {
        "DATA_GOV_API_KEY": "your_key_here",
        "OPENWEATHER_API_KEY": "your_key_here"
      }
    }
  }
}
```

Then restart Claude Desktop. The tools will appear automatically.

### Step 4: Test It

Open Claude Desktop and ask:
- "What are the mandi prices in Raipur today?"
- "Give me an agriculture dashboard for Bastar district"
- "What government schemes is a small farmer in Surguja eligible for?"

---

## Data Sources

| Source | Data | Update Frequency | Cost |
|--------|------|-----------------|------|
| Agmarknet / data.gov.in | Mandi prices | Daily | Free |
| OpenWeatherMap | Weather | Hourly | Free (1000/day) |
| Government scheme DB | Scheme details | Monthly | Free (built-in) |
| ICAR / KVK | Crop advisory | Seasonal | Free (built-in) |
| IMD (future) | Rainfall data | Daily | Free with registration |

---

## Expansion Roadmap

### Phase 2 — Social Layer
- NGO Darpan integration
- CSR fund mapping
- Beneficiary tracking

### Phase 3 — Government Layer  
- MyScheme live API
- PM Kisan beneficiary checker
- MGNREGS work availability

### Phase 4 — Cross-Layer Intelligence
- Farmer distress early warning system
- NGO-scheme convergence finder
- CSR fund to ground need matcher

### Phase 5 — Other States
- Madhya Pradesh
- Odisha
- Maharashtra
- Pan-India scale

---

## Revenue Model

| Tier | Users | Price | Features |
|------|-------|-------|---------|
| Free | Individual farmers, NGOs | ₹0 | 3 tools, 100 queries/day |
| Pro | Agri consultants, KVKs | ₹999/month | All tools, 2000 queries/day |
| Enterprise | State govt, large NGOs | Custom | Unlimited, white-label, API access |

---

## Contacts for Chhattisgarh Partnerships

- **CREDA**: creda.in — Renewable + rural energy
- **Agriculture Department CG**: agri.cg.gov.in
- **KVK Network**: 12 KVKs across CG districts
- **MARKFED**: Government procurement agency
- **IIM Raipur**: Research partnership potential

---

## File Structure

```
agri-mcp-server/
├── index.js              ← Node.js MCP entry point (Claude Desktop)
├── package.json          ← Dependencies
├── .env.example          ← API key template
├── SKILL.md              ← This file
└── src/
    └── agri_mcp_server.py ← Core Python logic + all tools
```

---

*Built with Python 3.12 + Node.js 22. No database required. No paid infrastructure.*
*Running cost: $0 until 1,000+ daily queries.*
