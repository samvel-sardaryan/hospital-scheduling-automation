import json, random, re
from datetime import datetime, timedelta

doctors = [
    {"id": "D001", "name": "Dr. Anna Mkrtchyan", "specialty": "General Practitioner"},
    {"id": "D002", "name": "Dr. Arman Petrosyan", "specialty": "Cardiology"},
    {"id": "D003", "name": "Dr. Lilit Grigoryan", "specialty": "Dermatology"},
    {"id": "D004", "name": "Dr. Karen Hakobyan", "specialty": "Orthopedics"},
    {"id": "D005", "name": "Dr. Mariam Sargsyan", "specialty": "ENT"},
]

# availability (skip any slot that is already in the past)
now = datetime.now()
base = now.replace(hour=0, minute=0, second=0, microsecond=0)
slots = []
for day_offset in range(0, 3):
    day = base + timedelta(days=day_offset)
    for hour in (9, 14):
        t = day + timedelta(hours=hour)
        if t > now:
            slots.append(t.isoformat())

doctor_availability = {d["id"]: list(slots) for d in doctors}

# simple keyword-based mapping
SPECIALTY_KEYWORDS = {
    "Cardiology": ["chest pain", "palpitations", "shortness of breath", "heart", "bp"],
    "Dermatology": ["rash", "skin", "acne", "itch"],
    "Orthopedics": ["knee", "hip", "sprain", "fracture", "bone", "back"],
    "ENT": ["ear", "throat", "sinus", "nose", "hearing"],
    "General Practitioner": ["fever", "cold", "cough", "headache", "nausea"],
}
kw_to_spec = {}
for s,kws in SPECIALTY_KEYWORDS.items():
    for kw in kws:
        kw_to_spec[kw] = s

def matches(keyword, text):
    # match keywords at the start of a word so "ear" doesn't fire on "heart"
    return re.search(r"\b" + re.escape(keyword), text) is not None

def classify_symptoms(text):
    t = text.lower()
    counts = {}
    for kw,spec in kw_to_spec.items():
        if matches(kw, t):
            counts[spec] = counts.get(spec,0) + 1
    return max(counts, key=counts.get) if counts else "General Practitioner"

def detect_urgency(text):
    urgent = ["chest pain", "bleeding", "difficulty breathing", "severe", "unconscious"]
    t = text.lower()
    return "urgent" if any(matches(u, t) for u in urgent) else "routine"

def schedule_appointment(patient, text):
    spec = classify_symptoms(text)
    urgency = detect_urgency(text)
    # find a doctor for spec
    cand = [d for d in doctors if d["specialty"].lower() == spec.lower()]
    if not cand:
        cand = [d for d in doctors if d["specialty"] == "General Practitioner"]
        spec = "General Practitioner"
    # pick earliest slot across candidates
    chosen_doc = None
    chosen_slot = None
    for d in cand:
        avail = doctor_availability.get(d["id"], [])
        if avail:
            s = min(avail)
            if chosen_slot is None or s < chosen_slot:
                chosen_doc = d
                chosen_slot = s
    if not chosen_slot:
        return {"status":"failed", "reason":"No available slots"}
    # book (remove slot)
    doctor_availability[chosen_doc["id"]].remove(chosen_slot)
    appointment = {
        "id": f"A{random.randint(1000,9999)}",
        "patient": patient,
        "doctor": chosen_doc["name"],
        "specialty": spec,
        "slot": chosen_slot,
        "urgency": urgency
    }
    return {"status":"ok", "appointment": appointment}

# example patients
examples = [
    {"name":"Anna", "phone":"+37499123456", "text":"I've had chest pain and palpitations for 2 days."},
    {"name":"Vardan", "phone":"+37494111222", "text":"I have a rash on my arms and constant itching."},
    {"name":"Narine", "phone":"+37493333444", "text":"My knee hurts after a fall; severe pain when walking."},
]

appointments = []
# schedule urgent patients first so they get the earliest available slots
examples.sort(key=lambda e: detect_urgency(e["text"]) != "urgent")
for e in examples:
    res = schedule_appointment({"name": e["name"], "phone": e["phone"]}, e["text"])
    if res["status"] == "ok":
        appt = res["appointment"]
        appointments.append(appt)
        print(f"CONFIRMED: {appt['id']} | {appt['patient']['name']} -> {appt['doctor']} | {appt['slot']} | {appt['urgency']}")
    else:
        print("Failed to schedule:", res.get("reason"))

# save results
with open("appointments.json", "w", encoding="utf-8") as f:
    json.dump(appointments, f, indent=2, ensure_ascii=False)

# print contents of appointments.json for easy viewing
print("\nSaved appointments.json content:")
print(json.dumps(appointments, indent=2, ensure_ascii=False))
