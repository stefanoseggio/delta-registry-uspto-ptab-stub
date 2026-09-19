"""
USPTO PTAB Trials -- one-off sample puller (free stub)

Pulls the most recently filed USPTO Patent Trial and Appeal Board (PTAB)
trial proceedings (Inter Partes Review / Post-Grant Review / Covered
Business Method / Derivation) from the real USPTO Open Data Portal (ODP)
"Search Proceedings" endpoint, and saves a small JSON sample to disk.

This is a free, one-off, local tool: run it once, get a snapshot. It does
NOT schedule recurring runs, track deltas between runs, retry failed
requests, or hold a dead-letter queue for failures -- see this repo's
README.md, "What this doesn't do", for the real gaps versus the paid,
hosted actor.

Setup:
    1. Get a free USPTO Open Data Portal API key (requires a USPTO.gov
       account with MFA enabled): https://data.uspto.gov/apikey
    2. Set it as an environment variable:
         macOS/Linux:  export USPTO_ODP_API_KEY=your_key_here
         Windows cmd:  set USPTO_ODP_API_KEY=your_key_here
         PowerShell:   $env:USPTO_ODP_API_KEY="your_key_here"
    3. pip install -r requirements.txt
    4. python main.py
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests

SEARCH_URL = "https://api.uspto.gov/api/v1/patent/trials/proceedings/search"
OUTPUT_FILE = "sample_output.json"
MAX_RECORDS = 20


def build_request_body(limit: int) -> dict:
    """Real USPTO ODP 'advanced syntax' request body shape (q / filters /
    rangeFilters / pagination / sort), documented at
    https://data.uspto.gov/apis/api-syntax-examples and applied here to the
    PTAB proceedings/search endpoint. This one-off pull asks for the most
    recently filed proceedings of any trial type, with no date or trial-type
    filtering -- just the newest `limit` records."""
    return {
        "q": "*",
        "filters": [],
        "rangeFilters": [],
        "pagination": {"offset": 0, "limit": limit},
        "sort": [{"field": "trialMetaData.petitionFilingDate", "order": "Desc"}],
    }


def flatten_proceeding(proceeding: dict, scraped_at: str) -> dict:
    """Pulls a small set of fields out of one raw PTAB proceeding record,
    using the real USPTO ODP PTAB Trials response field names (trialNumber,
    trialMetaData.*, patentOwnerData / regularPetitionerData, etc.)."""
    meta = proceeding.get("trialMetaData", {}) or {}
    owner = proceeding.get("patentOwnerData") or proceeding.get("respondentData") or {}
    petitioner = proceeding.get("regularPetitionerData") or proceeding.get("derivationPetitionerData") or {}

    return {
        "trialNumber": proceeding.get("trialNumber"),
        "trialTypeCode": meta.get("trialTypeCode"),
        "trialStatusCategory": meta.get("trialStatusCategory"),
        "petitionFilingDate": meta.get("petitionFilingDate"),
        "institutionDecisionDate": meta.get("institutionDecisionDate"),
        "terminationDate": meta.get("terminationDate"),
        "patentNumber": owner.get("patentNumber") or petitioner.get("patentNumber"),
        "patentOwnerName": owner.get("patentOwnerName"),
        "petitionerRealPartyInInterestName": petitioner.get("realPartyInInterestName"),
        "scraped_at": scraped_at,
    }


def main() -> None:
    api_key = os.environ.get("USPTO_ODP_API_KEY")
    if not api_key:
        print("ERROR: set the USPTO_ODP_API_KEY environment variable to your free USPTO ODP API key.")
        print("Get one at https://data.uspto.gov/apikey (USPTO.gov account with MFA required).")
        sys.exit(1)

    body = build_request_body(MAX_RECORDS)
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}

    print(f"Fetching up to {MAX_RECORDS} PTAB trial proceedings from {SEARCH_URL} ...")

    try:
        response = requests.post(SEARCH_URL, headers=headers, json=body, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        # Honest one-off behavior: report the failure and stop. No retry, no
        # exponential backoff, no dead-letter queue -- see README.md's "What
        # this doesn't do" section for why that's a real, named gap here.
        print(f"ERROR: request to USPTO ODP failed: {exc}")
        sys.exit(1)

    data = response.json()
    proceedings = data.get("patentTrialProceedingDataBag", [])

    if not proceedings:
        print("No proceedings returned for this query.")
        return

    scraped_at = datetime.now(timezone.utc).isoformat()
    sample = [flatten_proceeding(p, scraped_at) for p in proceedings[:MAX_RECORDS]]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sample, f, indent=2)

    print(f"Saved {len(sample)} record(s) to {OUTPUT_FILE}")
    print(json.dumps(sample[:3], indent=2))


if __name__ == "__main__":
    main()
