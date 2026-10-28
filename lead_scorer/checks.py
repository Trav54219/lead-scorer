"""Data-quality checks. Each returns True when the lead PASSES that check."""
import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@([A-Za-z0-9\-]+\.)+[A-Za-z]{2,}$")
FREE_MAIL = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com",
             "proton.me", "protonmail.com", "live.com", "msn.com"}
ROLE_LOCALS = {"info", "sales", "support", "admin", "contact", "hello", "office", "team",
               "marketing", "help", "billing", "careers", "jobs", "press", "noreply", "no-reply"}


def valid_syntax(email: str) -> bool:
    return bool(EMAIL_RE.match((email or "").strip()))


def email_domain(email: str) -> str:
    return (email or "").strip().lower().rpartition("@")[2]


def is_free_mail(email: str) -> bool:
    return email_domain(email) in FREE_MAIL


def is_role_inbox(email: str) -> bool:
    return (email or "").strip().lower().partition("@")[0] in ROLE_LOCALS


def domain_matches(email: str, company_domain: str) -> bool:
    """Email domain equals (or is a subdomain of) the company's own domain."""
    d, c = email_domain(email), (company_domain or "").strip().lower().removeprefix("www.")
    return bool(c) and (d == c or d.endswith("." + c))


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())
