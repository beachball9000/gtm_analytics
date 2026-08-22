"""
generate_seeds.py
-----------------
Generates synthetic, Salesforce-shaped CRM seed data for a dbt project modeling
a subscription business that sells software to real estate agents and brokerages.

Outputs six CSVs into ./seeds/ :
    raw_leads.csv
    raw_accounts.csv
    raw_contacts.csv
    raw_opportunities.csv
    raw_opportunity_stage_history.csv
    raw_subscriptions.csv

Deliberate data-quality problems are injected so that dbt tests have something
real to catch. See DIRTY DATA section at the bottom of this docstring.

Usage:
    python generate_seeds.py

DIRTY DATA INJECTED (on purpose):
    - NULL lead_source on ~8% of leads
    - Duplicate contacts sharing the same email (~2%)
    - ~1% of opportunities have close_date BEFORE created_date
    - A handful of opportunities skip pipeline stages
    - Inconsistent casing/whitespace in lead_source and account industry
    - A few orphan contacts pointing at non-existent accounts
"""

import csv
import os
import random
from datetime import date, timedelta

random.seed(42)

OUT_DIR = "seeds"
START = date(2023, 1, 1)
END = date(2026, 6, 30)

N_LEADS = 4000
N_ACCOUNTS = 900

# ----------------------------------------------------------------- reference data

LEAD_SOURCES = [
    "Paid Search", "Organic Search", "Referral", "Webinar",
    "Conference", "Cold Outreach", "Partner", "Social",
]

# messy variants intentionally introduced later
LEAD_SOURCE_DIRTY = {
    "Paid Search": ["paid search", "Paid Search ", "PAID SEARCH"],
    "Referral": ["referral", " Referral"],
    "Organic Search": ["organic search"],
}

LEAD_STATUS = ["New", "Working", "Nurturing", "Qualified", "Disqualified"]

STAGES = [
    "Prospecting",
    "Discovery",
    "Demo",
    "Proposal",
    "Negotiation",
    "Closed Won",
    "Closed Lost",
]
OPEN_STAGES = STAGES[:5]

PLAN_TIERS = ["Launch", "Brand", "Scale", "All In"]
PLAN_MRR = {"Launch": 500, "Brand": 900, "Scale": 1600, "All In": 2800}
PLAN_WEIGHTS = [0.34, 0.33, 0.22, 0.11]

SEGMENTS = ["Solo Agent", "Small Team", "Large Team", "Brokerage"]
SEGMENT_WEIGHTS = [0.46, 0.30, 0.16, 0.08]

INDUSTRIES = ["Residential Real Estate", "Luxury Residential", "Commercial Real Estate", "Property Management"]

REGIONS = ["West", "Southwest", "Midwest", "Southeast", "Northeast"]

STATES_BY_REGION = {
    "West": ["CA", "WA", "OR", "NV"],
    "Southwest": ["TX", "AZ", "NM", "CO"],
    "Midwest": ["IL", "OH", "MI", "MN", "MO"],
    "Southeast": ["FL", "GA", "NC", "TN", "SC"],
    "Northeast": ["NY", "MA", "NJ", "CT", "PA"],
}

FIRST_NAMES = [
    "Avery", "Jordan", "Riley", "Morgan", "Casey", "Quinn", "Skyler", "Rowan",
    "Elena", "Marcus", "Priya", "Devin", "Noel", "Tessa", "Julian", "Camille",
    "Owen", "Sasha", "Bianca", "Theo", "Naomi", "Grant", "Maya", "Felix",
]
LAST_NAMES = [
    "Whitfield", "Okonkwo", "Kaplan", "Moreau", "Castellanos", "Nakamura",
    "Delgado", "Bergstrom", "Ahmed", "Lindqvist", "Vasquez", "Thornton",
    "Petrova", "Osei", "Rinaldi", "Halvorsen", "Bautista", "Kearney",
]

BROKERAGE_WORDS = [
    "Summit", "Harbor", "Ridgeline", "Cornerstone", "Blackwood", "Lakeshore",
    "Ironwood", "Beacon", "Cypress", "Meridian", "Foxglove", "Stonebridge",
]
BROKERAGE_SUFFIX = ["Realty", "Properties", "Group", "Partners", "Real Estate", "& Co."]


def rand_date(start=START, end=END):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def weighted(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def person_name():
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)


def email_for(first, last, i):
    domain = random.choice(["gmail.com", "outlook.com", "realtyco.com", "kw.com", "compass.com"])
    return f"{first.lower()}.{last.lower()}{i}@{domain}"


def brokerage_name():
    return f"{random.choice(BROKERAGE_WORDS)} {random.choice(BROKERAGE_SUFFIX)}"


def write_csv(filename, fieldnames, rows):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  {path}  ({len(rows)} rows)")


# ----------------------------------------------------------------- accounts

def build_accounts():
    accounts = []
    for i in range(1, N_ACCOUNTS + 1):
        region = random.choice(REGIONS)
        segment = weighted(SEGMENTS, SEGMENT_WEIGHTS)
        created = rand_date(START, END - timedelta(days=30))
        industry = random.choice(INDUSTRIES)

        # dirty: inconsistent casing on ~5% of industry values
        if random.random() < 0.05:
            industry = industry.lower()

        accounts.append({
            "account_id": f"ACC{i:05d}",
            "account_name": brokerage_name(),
            "segment": segment,
            "industry": industry,
            "billing_state": random.choice(STATES_BY_REGION[region]),
            "billing_region": region,
            "employee_count": {
                "Solo Agent": random.randint(1, 1),
                "Small Team": random.randint(2, 8),
                "Large Team": random.randint(9, 30),
                "Brokerage": random.randint(31, 400),
            }[segment],
            "created_date": created.isoformat(),
        })
    return accounts


# ----------------------------------------------------------------- contacts

def build_contacts(accounts):
    contacts = []
    cid = 1
    for acct in accounts:
        n = 1 if acct["segment"] == "Solo Agent" else random.randint(1, 3)
        for _ in range(n):
            first, last = person_name()
            contacts.append({
                "contact_id": f"CON{cid:06d}",
                "account_id": acct["account_id"],
                "first_name": first,
                "last_name": last,
                "email": email_for(first, last, cid),
                "title": random.choice(
                    ["Agent", "Broker", "Team Lead", "Managing Broker", "Marketing Director", "Owner"]
                ),
                "created_date": acct["created_date"],
            })
            cid += 1

    # dirty: duplicate contacts sharing an email (~2%)
    n_dupes = int(len(contacts) * 0.02)
    for _ in range(n_dupes):
        src = random.choice(contacts)
        dupe = dict(src)
        dupe["contact_id"] = f"CON{cid:06d}"
        cid += 1
        contacts.append(dupe)

    # dirty: a few orphan contacts pointing at accounts that don't exist
    for _ in range(6):
        first, last = person_name()
        contacts.append({
            "contact_id": f"CON{cid:06d}",
            "account_id": f"ACC{random.randint(90000, 99999)}",
            "first_name": first,
            "last_name": last,
            "email": email_for(first, last, cid),
            "title": "Agent",
            "created_date": rand_date().isoformat(),
        })
        cid += 1

    return contacts


# ----------------------------------------------------------------- leads

def build_leads(accounts):
    leads = []
    # ~35% of leads eventually convert to an account
    converting = random.sample(accounts, k=int(N_ACCOUNTS * 0.95))
    convert_pool = list(converting)

    for i in range(1, N_LEADS + 1):
        first, last = person_name()
        created = rand_date(START, END - timedelta(days=10))
        source = random.choice(LEAD_SOURCES)

        # dirty: NULL source on ~8%
        if random.random() < 0.08:
            source = ""
        # dirty: messy casing/whitespace variants
        elif source in LEAD_SOURCE_DIRTY and random.random() < 0.12:
            source = random.choice(LEAD_SOURCE_DIRTY[source])

        converted_account = ""
        converted_date = ""
        status = weighted(LEAD_STATUS, [0.22, 0.24, 0.16, 0.26, 0.12])

        if status == "Qualified" and convert_pool and random.random() < 0.72:
            acct = convert_pool.pop()
            converted_account = acct["account_id"]
            converted_date = (created + timedelta(days=random.randint(3, 60))).isoformat()

        leads.append({
            "lead_id": f"LEAD{i:06d}",
            "first_name": first,
            "last_name": last,
            "email": email_for(first, last, i),
            "company": brokerage_name(),
            "lead_source": source,
            "lead_status": status,
            "is_mql": "true" if status in ("Qualified", "Working", "Nurturing") and random.random() < 0.65 else "false",
            "created_date": created.isoformat(),
            "converted_account_id": converted_account,
            "converted_date": converted_date,
        })
    return leads


# ----------------------------------------------------------------- opportunities

def build_opportunities(accounts, leads):
    opps = []
    stage_history = []
    oid = 1
    hid = 1

    lead_by_account = {
        l["converted_account_id"]: l for l in leads if l["converted_account_id"]
    }

    for acct in accounts:
        # most accounts have one new-business opp; some have expansion opps too
        n_opps = 1 + (1 if random.random() < 0.28 else 0)

        for k in range(n_opps):
            opp_type = "New Business" if k == 0 else "Expansion"
            src_lead = lead_by_account.get(acct["account_id"])

            base = date.fromisoformat(acct["created_date"])
            created = base + timedelta(days=random.randint(0, 45) + (240 * k))
            if created > END:
                continue

            tier = weighted(PLAN_TIERS, PLAN_WEIGHTS)
            amount = PLAN_MRR[tier] * 12
            if opp_type == "Expansion":
                amount = int(amount * random.uniform(0.25, 0.7))

            cycle_days = random.randint(14, 120)
            close = created + timedelta(days=cycle_days)

            won = random.random() < (0.34 if opp_type == "New Business" else 0.52)
            final_stage = "Closed Won" if won else "Closed Lost"

            still_open = close > END
            if still_open:
                final_stage = random.choice(OPEN_STAGES)
                close = created + timedelta(days=random.randint(30, 150))

            # dirty: ~1% have close_date before created_date
            if random.random() < 0.01:
                close = created - timedelta(days=random.randint(1, 20))

            opps.append({
                "opportunity_id": f"OPP{oid:06d}",
                "account_id": acct["account_id"],
                "source_lead_id": src_lead["lead_id"] if src_lead and k == 0 else "",
                "opportunity_name": f"{acct['account_name']} - {tier} ({opp_type})",
                "opportunity_type": opp_type,
                "plan_tier": tier,
                "amount": amount,
                "stage_name": final_stage,
                "is_closed": "false" if still_open else "true",
                "is_won": "true" if final_stage == "Closed Won" else "false",
                "created_date": created.isoformat(),
                "close_date": close.isoformat(),
                "owner_region": acct["billing_region"],
            })

            # ---- stage history
            if still_open:
                path = OPEN_STAGES[: OPEN_STAGES.index(final_stage) + 1]
            else:
                # dirty: some opportunities skip stages
                if random.random() < 0.10:
                    path = ["Prospecting", "Demo", final_stage]
                else:
                    path = OPEN_STAGES + [final_stage]

            cursor = created
            for stage in path:
                stage_history.append({
                    "stage_history_id": f"SH{hid:07d}",
                    "opportunity_id": f"OPP{oid:06d}",
                    "stage_name": stage,
                    "entered_at": cursor.isoformat(),
                })
                hid += 1
                cursor = cursor + timedelta(days=max(1, cycle_days // max(1, len(path))))

            oid += 1

    return opps, stage_history


# ----------------------------------------------------------------- subscriptions

def build_subscriptions(opps):
    """One row per subscription term. Renewals produce additional rows."""
    subs = []
    sid = 1

    won = [o for o in opps if o["is_won"] == "true" and o["opportunity_type"] == "New Business"]

    for o in won:
        acct = o["account_id"]
        tier = o["plan_tier"]
        start = date.fromisoformat(o["close_date"])
        term = 0

        while start <= END and term < 4:
            end_date = start + timedelta(days=365)
            mrr = PLAN_MRR[tier]

            # renewal outcome for the NEXT term
            roll = random.random()
            if roll < 0.18:
                status = "Churned"
            elif roll < 0.34:
                status = "Downgraded"
            elif roll < 0.62:
                status = "Upgraded"
            else:
                status = "Renewed"

            if end_date > END:
                status = "Active"

            subs.append({
                "subscription_id": f"SUB{sid:06d}",
                "account_id": acct,
                "opportunity_id": o["opportunity_id"],
                "plan_tier": tier,
                "mrr": mrr,
                "term_number": term + 1,
                "start_date": start.isoformat(),
                "end_date": end_date.isoformat(),
                "end_status": status,
            })
            sid += 1

            if status in ("Churned", "Active"):
                break

            # move to next term, adjusting tier
            idx = PLAN_TIERS.index(tier)
            if status == "Upgraded" and idx < len(PLAN_TIERS) - 1:
                tier = PLAN_TIERS[idx + 1]
            elif status == "Downgraded" and idx > 0:
                tier = PLAN_TIERS[idx - 1]

            start = end_date
            term += 1

    return subs


# ----------------------------------------------------------------- main

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Generating seeds...")

    accounts = build_accounts()
    contacts = build_contacts(accounts)
    leads = build_leads(accounts)
    opps, stage_history = build_opportunities(accounts, leads)
    subs = build_subscriptions(opps)

    write_csv("raw_accounts.csv",
              ["account_id", "account_name", "segment", "industry",
               "billing_state", "billing_region", "employee_count", "created_date"],
              accounts)

    write_csv("raw_contacts.csv",
              ["contact_id", "account_id", "first_name", "last_name",
               "email", "title", "created_date"],
              contacts)

    write_csv("raw_leads.csv",
              ["lead_id", "first_name", "last_name", "email", "company",
               "lead_source", "lead_status", "is_mql", "created_date",
               "converted_account_id", "converted_date"],
              leads)

    write_csv("raw_opportunities.csv",
              ["opportunity_id", "account_id", "source_lead_id", "opportunity_name",
               "opportunity_type", "plan_tier", "amount", "stage_name",
               "is_closed", "is_won", "created_date", "close_date", "owner_region"],
              opps)

    write_csv("raw_opportunity_stage_history.csv",
              ["stage_history_id", "opportunity_id", "stage_name", "entered_at"],
              stage_history)

    write_csv("raw_subscriptions.csv",
              ["subscription_id", "account_id", "opportunity_id", "plan_tier",
               "mrr", "term_number", "start_date", "end_date", "end_status"],
              subs)

    print("\nDone. Move the seeds/ folder into your dbt project root, then run:")
    print("  dbt seed")


if __name__ == "__main__":
    main()
