# Local Demo Script

> Use this script only for a local, private evaluation with fictional inputs. It deliberately selects deterministic demo mode: no OpenAI key, external provider, live data, or network-based plan generation is required.

## Prepare on Windows PowerShell

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock
$env:WEEKENDIA_MODE = "demo"
$env:FLASK_HOST = "127.0.0.1"
$env:FLASK_PORT = "5000"
$env:FLASK_DEBUG = "false"
python main.py
```

Open `http://127.0.0.1:5000` in a browser. Process environment variables override any optional `.env` values. Keep the server on loopback and stop it with `Ctrl+C` after the session.

## Two-minute walkthrough

1. Point out **Demo mode** in the header. Explain that this is configuration status, not a live-provider health claim.
2. Select **How it works**. Show the three-step explanation, close it with `Escape`, and note focus returning to the trigger.
3. Move to the planner and use fictional data:

   - City or area: `Sample City`
   - Interests: `parks, photography, and cafes`
   - Total budget: `$60`
   - Group size: `2`
   - Available time: `Saturday from 1 PM to 5 PM`
   - Weather: `cool with possible rain`
   - Transportation: `Public transit`
   - Constraints: `Prefer short, step-free routes and quiet spaces`

4. Submit the form. Explain that the waiting state reports only real request state, not a simulated completion percentage.
5. Review the five-part result: snapshot, recommendations, schedule, backup, and checklist.
6. Highlight the result disclaimer: demo output has no current venue, price, availability, weather, transport, or accessibility knowledge.
7. Exercise **Copy plan**, **Save as text**, and **Create another plan**.
8. Switch themes and, if useful, resize to a narrow viewport to show the responsive form.

## Truthful narration

Use language such as:

- “The deterministic demo exercises the product flow without external processing.”
- “The plan is illustrative; real-world details must be checked independently.”
- “OpenAI mode is available in the code but is not part of this local demo.”
- “The current repository is a private evaluation and is not represented as production-ready.”

Do not claim live recommendations, verified accessibility, guaranteed costs, formal compliance, a production deployment, public licensing, ownership, or name/logo clearance.

## Optional local verification

In a second PowerShell window with the demo server running:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health
```

Expected fields include `configured: true`, `mode: demo`, and `external_processing: false`. The endpoint does not assert external-provider reachability.

For repeatable technical checks, use [Validation](VALIDATION.md). For data-boundary details, use [Security Model](SECURITY_MODEL.md).
