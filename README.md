# BridgeBudget

BridgeBudget is a production-ready web application that helps people under financial pressure make a safer month-to-month recovery plan without creating an account. It focuses on immediate budget triage, debt prioritization, and trusted public-support pathways so users can act quickly when bills are outpacing income.

This version is optimized for U.S.-based households and uses U.S. support resources and ZIP-code input.

## 1. Product Definition

### Name
BridgeBudget

### Problem It Solves
Many households know they are short on cash but do not know which bills to protect first, how serious the situation is, or which support programs and debt actions to pursue right away.

### Target Audience
- Workers living paycheck to paycheck
- Students and early-career adults managing rent and debt
- Caregivers and single-income households
- Gig workers with irregular monthly income
- Community organizations that need a simple planning tool for clients

### Key Features
- No-login household budget triage tool
- Financial stress classification: stable, tight, or critical
- Essential-spending analysis and monthly cash-gap estimate
- Debt action strategy based on surplus, APR, and minimum payments
- 24-hour, 7-day, and 30-day action plan
- Trusted U.S. resource suggestions such as 211, Benefits.gov, SNAP, LIHEAP, and NFCC
- Shareable saved plan links backed by SQLite
- Responsive design with dark mode and accessibility basics

### Why It Matters To Society
Financial stress is tightly linked to eviction risk, food insecurity, mental strain, and missed healthcare. A simple triage tool can help users make safer decisions early, before a cash crunch becomes a crisis.

## 2. Architecture & Tech Stack

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript

### Backend
- Python 3.11+
- FastAPI
- Uvicorn

### Database
- SQLite

### Deployment
- Frontend: GitHub Pages
- Backend: Render

### Folder Structure

```text
bridgebudget/
├── README.md
├── frontend/
│   ├── assets/
│   │   └── social-preview.svg
│   ├── index.html
│   ├── robots.txt
│   ├── script.js
│   ├── sitemap.xml
│   └── styles.css
└── backend/
    ├── .env.example
    ├── app/
    │   ├── __init__.py
    │   ├── calculator.py
    │   ├── database.py
    │   ├── main.py
    │   ├── resources.py
    │   └── schemas.py
    ├── render.yaml
    └── requirements.txt
```

### API Structure
- `GET /api/health`
  - Health check for uptime monitoring
- `POST /api/analyze`
  - Accepts monthly household inputs and returns the full recovery analysis
- `POST /api/plans`
  - Saves an analyzed plan and returns a shareable link
- `GET /api/plans/{plan_id}`
  - Loads a previously saved plan for sharing or revisiting

### Data Flow
1. User opens the static site on mobile or desktop.
2. The browser validates the form and sends JSON to the FastAPI backend.
3. The backend validates and sanitizes inputs with Pydantic.
4. The calculation engine scores budget pressure, generates recommendations, and maps trusted support resources.
5. The frontend renders the results immediately.
6. If the user clicks save, the backend stores the request and analysis in SQLite and returns a share URL.

## 3. UI/UX Design

### Layout
- Hero section with clear value proposition
- Guided planner form with grouped monthly cost inputs
- Live preview cards for total essentials, debt minimums, and runway
- Results panel with stress status, action steps, debt strategy, and support resources

### Accessibility
- Semantic landmarks and headings
- Visible labels for every field
- Keyboard-accessible controls
- High-contrast colors and focus styles
- `aria-live` regions for loading, errors, and results updates
- Motion reduced when the user requests reduced motion

### Color Palette
- Ink: `#14222c`
- Teal: `#0d6d67`
- Coral: `#c15b34`
- Sand: `#f5edde`
- Mint: `#daf2ea`
- Slate: `#49606f`

### Typography
- Headings: `"Merriweather", serif`
- Body/UI: `"Manrope", sans-serif`

### UX Flow
1. Homepage explains the problem in plain language.
2. User enters income, essentials, savings, and debts.
3. User submits and sees a tailored recovery plan.
4. User optionally saves a shareable plan for a counselor, partner, or later review.

## 4. Backend Request Example

### `POST /api/analyze`

```json
{
  "location_zip": "56001",
  "household_size": 3,
  "monthly_income": 4200,
  "savings": 600,
  "housing": 1450,
  "utilities": 230,
  "food": 650,
  "transport": 280,
  "healthcare": 120,
  "childcare": 300,
  "insurance": 140,
  "other_essentials": 90,
  "debts": [
    {
      "name": "Credit card",
      "balance": 3200,
      "apr": 29.9,
      "minimum_payment": 110
    },
    {
      "name": "Medical bill",
      "balance": 900,
      "apr": 0,
      "minimum_payment": 40
    }
  ]
}
```

## 5. SEO Optimization

Included in the frontend:
- Title and description meta tags
- Keywords meta tag
- Open Graph tags
- Twitter card tags
- JSON-LD structured data for `SoftwareApplication`
- `robots.txt`
- `sitemap.xml`
- Fast-loading static assets and minimal JavaScript

Performance best practices used:
- Lightweight static frontend
- No blocking frameworks
- Systematic CSS variables and small asset footprint
- SVG social preview
- Reduced-motion support

## 6. Security & Best Practices

- Pydantic validation and numeric bounds on all user inputs
- Text length limits on debt labels
- CORS configured through environment variables
- Optional saved-plan persistence only when the user clicks save
- Backend never executes or renders raw user HTML
- Basic in-memory rate limiting for POST routes
- Environment variable support for API origins and frontend base URL

### Suggested Production Hardening
- Replace in-memory rate limiting with Redis-backed throttling
- Add request logging and structured monitoring
- Move from SQLite to PostgreSQL for higher concurrency
- Use HTTPS-only cookies if accounts are added later

## 7. Deployment Guide

### Frontend On GitHub Pages
1. Create a GitHub repository and push the `frontend/` folder contents.
2. In `frontend/index.html`, set the `bridgebudget-api-base` meta tag to your Render backend URL.
3. In GitHub, open `Settings` → `Pages`.
4. Choose the branch and root folder that contains the frontend files.
5. Save and wait for the GitHub Pages URL.
6. Update `sitemap.xml` and canonical URLs with your final domain.

### Backend On Render
1. Create a new Web Service on Render from the `backend/` folder.
2. Use Python 3.11+.
3. Set the build command to `pip install -r requirements.txt`.
4. Set the start command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Add environment variables from `.env.example`.
6. Deploy and copy the Render URL.

### Connect Frontend To Backend
1. Paste the Render URL into the `bridgebudget-api-base` meta tag in `frontend/index.html`.
2. Redeploy the frontend.
3. Add the GitHub Pages origin to `ALLOWED_ORIGINS` in Render.

### Local Environment Setup

```bash
cd bridgebudget/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Serve the frontend using any static server, for example:

```bash
cd bridgebudget/frontend
python3 -m http.server 5500
```

## 8. Scalability & Future Improvements

### Product Improvements
- State-specific assistance rules and eligibility guidance
- Scenario comparison mode for income loss or bill shocks
- Export to PDF for case workers and nonprofit intake
- Multilingual support
- SMS or email reminders for action-plan deadlines
- Optional account system for returning users

### Ethical Monetization
- Sponsored employer financial-wellness access
- White-label nonprofit and community-center deployments
- Premium counselor dashboard for organizations, not for vulnerable end users
- Grant-funded local resource packs and outreach integrations

### Scaling Plan
1. Move to PostgreSQL and managed object storage for documents.
2. Add Redis for rate limiting and caching.
3. Introduce background jobs for report generation and localization updates.
4. Build region-specific resource datasets and eligibility engines.
5. Add analytics focused on aggregate usage patterns, not sensitive personal profiling.

## 9. Deliverables

- Full frontend code in `frontend/index.html`, `frontend/styles.css`, and `frontend/script.js`
- FastAPI backend with calculation and persistence logic
- SEO files: `robots.txt`, `sitemap.xml`, and JSON-LD
- Deployment configuration and setup instructions
- Product, architecture, UX, security, and scaling documentation
