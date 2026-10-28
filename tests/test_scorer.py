import unittest

from lead_scorer.checks import domain_matches, is_free_mail, is_role_inbox, valid_syntax
from lead_scorer.score import fit_score, gate, process

ICP = {"personas": ["founder", "head of growth"], "employees": [11, 200],
       "keywords": ["outbound", "saas"], "allow_role_inboxes": False}


def lead(**kw):
    base = {"first_name": "Ana", "last_name": "Lee", "title": "Founder", "company": "Acme",
            "domain": "acme.example", "email": "ana@acme.example", "employees": "50",
            "description": "B2B SaaS with outbound"}
    base.update(kw)
    return base


class CheckTests(unittest.TestCase):
    def test_syntax(self):
        self.assertTrue(valid_syntax("a.b+c@x.co"))
        self.assertFalse(valid_syntax("ana.leeatacme.example"))
        self.assertFalse(valid_syntax(""))

    def test_free_and_role(self):
        self.assertTrue(is_free_mail("x@Gmail.com"))
        self.assertTrue(is_role_inbox("Info@acme.example"))
        self.assertFalse(is_role_inbox("ana@acme.example"))

    def test_domain_match_allows_subdomain_not_lookalike(self):
        self.assertTrue(domain_matches("a@mail.acme.example", "acme.example"))
        self.assertFalse(domain_matches("a@notacme.example", "acme.example"))


class GateTests(unittest.TestCase):
    def run_gate(self, leads):
        e, p = set(), set()
        return [gate(l, ICP, e, p) for l in leads]

    def test_reasons(self):
        out = self.run_gate([lead(), lead(email="info@acme.example"), lead(email="bad"),
                             lead(email="ana@gmail.com")])
        self.assertEqual(out, [None, "role_inbox", "invalid_email", "free_mail"])

    def test_duplicates(self):
        out = self.run_gate([lead(), lead(), lead(email="ana.lee@acme.example")])
        self.assertEqual(out, [None, "duplicate_email", "duplicate_person"])

    def test_allow_role_inboxes_flag(self):
        icp = {**ICP, "allow_role_inboxes": True}
        self.assertIsNone(gate(lead(email="info@acme.example"), icp, set(), set()))


class ScoreTests(unittest.TestCase):
    def test_perfect_fit(self):
        score, _ = fit_score(lead(), ICP)
        self.assertEqual(score, 100)

    def test_off_persona_and_band(self):
        score, _ = fit_score(lead(title="Accountant", employees="5000"), ICP)
        self.assertLess(score, 50)

    def test_bad_headcount_text_does_not_crash(self):
        fit_score(lead(employees="n/a"), ICP)

    def test_process_sorts_and_splits(self):
        clean, rej = process([lead(email="info@acme.example"), lead(title="Accountant", email="b@acme.example"),
                              lead(first_name="Bo", email="bo@acme.example")], ICP)
        self.assertEqual(len(rej), 1)
        self.assertGreaterEqual(clean[0]["score"], clean[1]["score"])


if __name__ == "__main__":
    unittest.main()
