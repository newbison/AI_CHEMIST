# VOC Idea Generator — Design Spec

## Context

FORGE AI currently requires users to bring their own VOC. This is a barrier: users may not know what questions are worth asking. The VOC Idea Generator adds an upstream "explore" path where AI proactively generates research questions from a product category and industry context.

## User Flow

```
Home Page
  ├─ "I have a research question" → existing VOC input → normal pipeline
  └─ "I need fresh ideas" → Explore form → 10 AI-generated VOCs → user picks one → normal pipeline
```

## Frontend Changes

### 1. Home Page (`InputStep.tsx`)

Two entry cards:

| Card | Label | Subtitle | Action |
|------|-------|----------|--------|
| Existing | "I have a research question" | "Enter your VOC and start analysis" | Opens existing VOC textarea |
| **New** | "I need fresh ideas" | "AI generates research questions from your product and industry" | Opens ExploreStep |

### 2. New Component: `ExploreStep.tsx`

**Form fields:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Product category | `<input>` | Yes | e.g., "UV-curable hard coats for automotive glazing" |
| Industry context | `<textarea>` | No | e.g., market pain point, competitor moves, constraints |
| Direction | Chips (4 options) | No | "Next-gen performance" / "Cost-down" / "Adjacent markets" / "All directions" |

**Results display:**

After `/api/explore-voc` returns, show 10 VOC cards. Each card:

- **VOC title** — bold, ~1-2 sentences
- **Why this matters** — 1-2 sentence subtitle explaining technical or commercial importance
- **Click to select** — user picks one, it pre-fills the existing VOC input, phase switches to `keywords` (the existing keywords confirmation step)

**Edge cases:**
- Loading state: spinner + "AI is generating research ideas..."
- Empty results: error banner + retry button
- Network failure: error banner + retry button

## Backend Changes

### 3. New Endpoint: `POST /api/explore-voc`

**Request:**
```json
{
  "product": "UV-curable hard coats for automotive glazing",
  "context": "Our formulation yellows after 2 years. Competitor X launched 5-year weatherable.",
  "direction": "next-gen"  // optional
}
```

**Response:**
```json
{
  "ideas": [
    {
      "voc": "We need a UV-curable acrylate-silicone hybrid hard coat...",
      "why": "Patent EPXXXXXX achieved 5-year weatherability with pure silicone but low hardness. No one has combined high-hardness acrylate with weatherable silicone in a dual-layer UV-cure system. This captures both the durability and longevity value propositions."
    }
    // ... 9 more
  ]
}
```

### 4. New Function: `generate_voc_ideas()` in `voc_analyzer.py`

**Input:** product category, industry context, direction
**Output:** list of 10 `{voc, why}` dicts

**Implementation:** Uses existing DeepSeek client with a prompt that:
1. Searches relevant patent landscape for the product category
2. Identifies white space, emerging technologies, and unsolved problems
3. Generates 10 VOCs, each with a why-this-matters subtitle
4. Returns structured JSON

### 5. Prompt Design

The system prompt for VOC generation should instruct the AI to:

- Draw from its training knowledge of materials science and patent landscapes
- Generate VOCs that are specific (materials, properties with numbers, test methods)
- Vary the VOCs across different technical approaches, not just minor variations
- Write "why" subtitles that cite specific technologies, patents, or market gaps
- Label the most promising VOC as index 0 (user sees it first)

### 6. Routing

The existing `/api/analyze-voc` endpoint already decomposes a VOC into search strategies. The explore flow should **not** call this — it generates the VOC itself. After the user selects a VOC, the existing InputStep `handleAnalyze` flow takes over (calls `/api/analyze-voc` on the selected text, then user confirms strategies, then searches).

## States & Edge Cases

| State | Behavior |
|-------|----------|
| Loading | Spinner + "AI is generating research ideas..." |
| Success (10 ideas) | Display cards, user clicks one |
| Success (fewer than 10) | Display what returned (AI may return fewer if product category is too narrow) |
| LLM failure | Error banner + "AI generation failed. Please try again or enter your own VOC." |
| LLM timeout | Same as failure |
| User clicks "Back" | Returns to home page two-card view |

## What This Does NOT Do

- Does NOT modify the existing patent search, report generation, or DOE design flows
- Does NOT require new Python dependencies
- Does NOT connect to external APIs beyond DeepSeek
- Does NOT cache generated VOCs (stateless — each request is fresh)

## Verification

1. Load home page → see two cards
2. Click "I need fresh ideas" → ExploreStep form appears
3. Enter "UV-curable hard coats" + context → click Generate
4. See 10 VOC cards with titles and why-this-matters subtitles
5. Click one card → VOC pre-fills → enters existing keywords confirmation phase
6. Continue through existing search → patent → report pipeline
