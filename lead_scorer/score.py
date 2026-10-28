"""Gate, dedupe, then score. A lead is either rejected with a reason or scored with reasons."""
from .checks import domain_matches, is_free_mail, is_role_inbox, norm, valid_syntax

POINTS = {"persona": 40, "headcount": 25, "keywords": 25, "domain": 10}


def gate(lead: dict, icp: dict, seen_emails: set, seen_people: set):
    """Return a reject reason, or None if the lead may be scored. Mutates the seen sets."""
    email = (lead.get("email") or "").strip().lower()
    if not valid_syntax(email):
        return "invalid_email"
    if is_free_mail(email):
        return "free_mail"
    if is_role_inbox(email) and not icp.get("allow_role_inboxes", False):
        return "role_inbox"
    if email in seen_emails:
        return "duplicate_email"
    person = norm(lead.get("first_name", "") + lead.get("last_name", "") + lead.get("domain", ""))
    if person and person in seen_people:
        return "duplicate_person"
    seen_emails.add(email)
    if person:
        seen_people.add(person)
    return None


def fit_score(lead: dict, icp: dict) -> tuple[int, list[str]]:
    score, why = 0, []
    title = (lead.get("title") or "").lower()
    if any(p.lower() in title for p in icp["personas"]):
        score += POINTS["persona"]
        why.append("title matches ICP persona")
    elif title:
        why.append("title off-persona")
    try:
        n = int(lead.get("employees") or 0)
    except ValueError:
        n = 0
    lo, hi = icp["employees"]
    if lo <= n <= hi:
        score += POINTS["headcount"]
        why.append(f"{n} employees in band")
    else:
        why.append(f"{n} employees outside {lo}-{hi}")
    text = (lead.get("description") or "").lower()
    hits = [k for k in icp["keywords"] if k.lower() in text]
    if icp["keywords"]:
        pts = POINTS["keywords"] * min(len(hits), 2) / 2
        score += pts
        why.append(f"keywords {', '.join(hits) or 'none'}")
    if domain_matches(lead.get("email", ""), lead.get("domain", "")):
        score += POINTS["domain"]
        why.append("email on company domain")
    return round(score), why


def process(leads: list[dict], icp: dict) -> tuple[list[dict], list[dict]]:
    clean, rejected = [], []
    seen_emails, seen_people = set(), set()
    for lead in leads:
        reason = gate(lead, icp, seen_emails, seen_people)
        if reason:
            rejected.append({**lead, "reject_reason": reason})
            continue
        score, why = fit_score(lead, icp)
        clean.append({**lead, "score": score, "why": "; ".join(why)})
    clean.sort(key=lambda r: -r["score"])
    return clean, rejected
