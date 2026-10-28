"""Generate a synthetic, deliberately messy lead list. Fully fictional: no real people or companies."""
import csv
import random

random.seed(7)
FIRST = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Riley", "Morgan", "Jamie", "Avery", "Quinn", "Drew", "Reese"]
LAST = ["Nguyen", "Patel", "Garcia", "Kim", "Okafor", "Silva", "Novak", "Haddad", "Larsen", "Mori", "Reyes", "Brandt"]
TITLES = ["Founder", "CEO", "Head of Growth", "VP Marketing", "VP Sales", "Head of Revenue Operations",
          "GTM Engineer", "Office Manager", "Recruiter", "Software Engineer", "Customer Support Lead", "Accountant", ""]
WORDS = ["Northwind", "Bluepeak", "Lumen", "Harbor", "Ironleaf", "Quartz", "Tidal", "Foxglove", "Summit", "Kestrel"]
KINDS = ["Labs", "Systems", "Works", "Analytics", "Cloud", "Logistics", "Health", "Studio"]
DESC = ["B2B SaaS platform for revenue teams with outbound and pipeline tooling",
        "demand generation agency for B2B software companies",
        "regional landscaping and snow removal service",
        "dental practice management",
        "SaaS analytics product for logistics teams",
        "boutique restaurant group",
        "B2B marketplace focused on pipeline visibility"]

rows = []
for i in range(300):
    co = f"{random.choice(WORDS)} {random.choice(KINDS)}"
    dom = co.lower().replace(" ", "") + ".example"
    f, l = random.choice(FIRST), random.choice(LAST)
    email = f"{f.lower()}.{l.lower()}@{dom}"
    r = random.random()
    if r < 0.08:
        email = f"{random.choice(['info', 'sales', 'hello', 'support'])}@{dom}"
    elif r < 0.14:
        email = f"{f.lower()}{l.lower()}@gmail.com"
    elif r < 0.18:
        email = f"{f.lower()}.{l.lower()}at{dom}"
    elif r < 0.22:
        email = f"{f.lower()}.{l.lower()}@othermail-{random.randint(1, 9)}.example"
    rows.append({"first_name": f, "last_name": l, "title": random.choice(TITLES), "company": co,
                 "domain": dom, "email": email, "employees": random.choice([3, 8, 15, 40, 90, 150, 400, 2000]),
                 "description": random.choice(DESC)})
rows += random.sample(rows, 25)          # exact duplicates
random.shuffle(rows)
with open("sample_data/leads.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows written")
