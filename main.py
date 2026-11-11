import re
import os
import json
from dotenv import load_dotenv
from google import genai
from datetime import datetime, timedelta

ROOM_PATTERN = r"^[A-D][1-4](0[1-9]|1[0-9]|20)$"

def is_valid(room):
    if room is None:
        return False
    return re.match(ROOM_PATTERN, room) is not None

print(is_valid("B214"))
print(is_valid("E210"))
print(is_valid("A25"))
print(is_valid("C321"))
print(is_valid(None))

def check_room(room, complaint_text):
    if not is_valid(room):
        return None
    if room not in complaint_text:
        return None
    return room

print(check_room("B214", "Fan not working in B214"))
print(check_room("B214", "Fan not working in the room"))

SAFETY_WORDS = ["spark", "shock", "overflowing", "burning smell", "near the switch"]

TEAMS = {
    "electrical": "Electrician",
    "plumbing": "Plumber",
    "carpentry": "Carpenter",
    "cleaning": "Housekeeping",
    "internet": "IT Support",
    "other": "Warden Office",
}

def apply_safety_net(issue, complaint_text, llm_urgent):
    text = complaint_text.lower()
    urgent = llm_urgent
    for word in SAFETY_WORDS:
        if word in text:
            urgent = True
    if "water" in text and "switch" in text:
        issue = "electrical"
        urgent = True
    return issue, urgent

def assign(issue):
    return TEAMS.get(issue, "Warden Office")

def due_date(urgent, opened_date):
    start = datetime.strptime(opened_date, "%Y-%m-%d")
    if urgent:
        return start.strftime("%Y-%m-%d")
    return (start + timedelta(days=2)).strftime("%Y-%m-%d")

print(apply_safety_net("plumbing", "Sparks from switch", False))
print(assign("electrical"))
print(due_date(False, "2026-11-05"))
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
print("Key loaded:", os.getenv("GEMINI_API_KEY") is not None)
def classify(complaint_text):
    prompt = (
        "Extract from this hostel complaint: room (like B214 or null), "
        "issue (electrical, plumbing, carpentry, cleaning, internet, other), "
        "urgent (true or false), summary (10 words or fewer). "
        "Copy the room exactly from the text. Water near switches is electrical. "
        "Reply with JSON only.\n\nComplaint: " + complaint_text
    )
    response = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
    text = response.text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
import csv
import time

def process_all():
    tickets = {}
    results = []
    needs_info = []

    with open("open_tickets.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["room"], row["issue"])
            tickets[key] = {"ticket": row["ticket"], "room": row["room"], "issue": row["issue"],
                            "opened": row["opened"], "urgent": False,
                            "complaints": [row["ticket"]], "summaries": ["pre-existing"]}

    with open("complaints.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cid, cdate, text = row["id"], row["date"], row["complaint"]
            try:
                result = classify(text)
            except Exception as error:
                print("AI call failed:", error)
                result = None
            if result is None:
                needs_info.append([cid, cdate, text, "AI reply unreadable"])
                results.append([cid, "needs_info", ""])
                continue
            room = check_room(result.get("room"), text)
            if room is None:
                needs_info.append([cid, cdate, text, "room missing or not written in complaint"])
                results.append([cid, "needs_info", ""])
                continue
            issue, urgent = apply_safety_net(result.get("issue", "other"), text, result.get("urgent", False))
            key = (room, issue)
            if key in tickets:
                t = tickets[key]
                t["complaints"].append(cid)
                t["summaries"].append(result.get("summary", ""))
                if urgent:
                    t["urgent"] = True
                status = "duplicate"
            else:
                t = {"ticket": "T%03d" % (len(tickets) + 1), "room": room, "issue": issue,
                     "opened": cdate, "urgent": urgent,
                     "complaints": [cid], "summaries": [result.get("summary", "")]}
                tickets[key] = t
                status = "new_ticket"
            results.append([cid, status, t["ticket"]])
            time.sleep(5)

    with open("work_orders.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ticket", "team", "room", "issue", "urgent", "opened", "due_date", "complaints"])
        for t in sorted(tickets.values(), key=lambda x: (not x["urgent"], assign(x["issue"]))):
            w.writerow([t["ticket"], assign(t["issue"]), t["room"], t["issue"], t["urgent"],
                        t["opened"], due_date(t["urgent"], t["opened"]), " ".join(t["complaints"])])

    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "status", "ticket"])
        w.writerows(results)

    with open("needs_info.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "date", "complaint", "reason"])
        w.writerows(needs_info)

    teams, blocks = {}, {"A": 0, "B": 0, "C": 0, "D": 0}
    for t in tickets.values():
        team = assign(t["issue"])
        teams[team] = teams.get(team, 0) + 1
        blocks[t["room"][0]] = blocks.get(t["room"][0], 0) + 1
    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write("Tickets by team:\n")
        for team, n in teams.items():
            f.write(f"  {team}: {n}\n")
        f.write("Tickets by block:\n")
        for b, n in blocks.items():
            f.write(f"  Block {b}: {n}\n")
        f.write("Repeat rooms:\n")
        for t in tickets.values():
            if len(t["complaints"]) > 1:
                f.write(f"  {t['room']} ({t['issue']}): {len(t['complaints'])} complaints\n")

    print("Done. Written: work_orders.csv, results.csv, needs_info.csv, summary.txt")

process_all()