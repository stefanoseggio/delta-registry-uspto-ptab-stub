# USPTO PTAB Trials Sample Puller (free stub)

This is a small, free, open-source Python script that does one thing: it makes a single call to the real **USPTO Open Data Portal (ODP) PTAB Trials "Search Proceedings"** endpoint (`POST https://api.uspto.gov/api/v1/patent/trials/proceedings/search`), asks for the 20 most recently filed Patent Trial and Appeal Board proceedings (Inter Partes Review, Post-Grant Review, Covered Business Method, and Derivation trials), and saves the result as a small local JSON file. It requires your own free USPTO ODP API key (BYOK) and runs once, on demand, from your own machine. It is not a monitoring service, a scheduler, or a delta-tracking tool -- see [What this doesn't do](#what-this-doesnt-do) below.

## Setup & run

1. Get a free USPTO Open Data Portal API key. This requires a USPTO.gov account with multi-factor authentication enabled: https://data.uspto.gov/myodp
2. Set the key as an environment variable:
   ```bash
   # macOS/Linux
   export USPTO_ODP_API_KEY=your_key_here

   # Windows cmd
   set USPTO_ODP_API_KEY=your_key_here

   # PowerShell
   $env:USPTO_ODP_API_KEY="your_key_here"
   ```
3. Install dependencies and run:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

The script prints its progress, writes up to 20 records to `sample_output.json` in the current directory, and prints the first 3 records to the console.

## Example output

A trimmed excerpt of `sample_output.json` (field names match the real USPTO PTAB Trials response, as documented at `https://data.uspto.gov/apis/ptab-trials/search-proceedings`):

```json
[
  {
    "trialNumber": "IPR2024-00123",
    "trialTypeCode": "IPR",
    "trialStatusCategory": "Instituted",
    "petitionFilingDate": "2024-01-15",
    "institutionDecisionDate": "2024-07-10",
    "terminationDate": null,
    "patentNumber": "10123456",
    "patentOwnerName": "Acme Widgets Inc.",
    "petitionerRealPartyInInterestName": "Globex Corp",
    "scraped_at": "2026-09-10T00:00:00+00:00"
  }
]
```

(The `trialNumber`, `patentNumber`, `patentOwnerName`, and `petitionerRealPartyInInterestName` values above are illustrative placeholders for the shape of the data, not real proceedings -- running the script against your own API key returns real, current PTAB records.)

## What this doesn't do

This stub is intentionally simple. It does **not** include:

- **Scheduling.** It runs once when you invoke `python main.py` and exits. There is no cron, no recurring trigger, no "run every N hours."
- **Delta / change-tracking.** Every run is a fresh, independent snapshot. It does not remember what it saw last time, so it cannot tell you what's new, what changed, or which trial just concluded.
- **Retries or backoff.** If the request to USPTO ODP fails (rate limit, timeout, server error), the script prints the error and exits. It does not retry, and it does not honor USPTO ODP's documented rate-limit or `Retry-After` guidance.
- **Dead-letter handling.** There is no mechanism for capturing, queuing, or replaying failed requests.

## Production version

For scheduled runs, delta/change-tracking, and reliability guarantees, see the production actor: https://apify.com/stefano_seggio/actor-21-patent-ip-enforcement-monitor
