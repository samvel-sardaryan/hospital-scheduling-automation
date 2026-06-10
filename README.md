# Hospital Scheduling Automation

A small Python prototype that reads a patient's symptom description, routes them to
the right specialist, flags urgent cases, and books the earliest available
appointment slot — all from the command line, with no external dependencies.

## How it works

For each patient the script runs three steps:

1. **Symptom classification** — the free-text complaint is matched against a
   keyword list to pick a specialty (Cardiology, Dermatology, Orthopedics, ENT,
   or General Practitioner). Keywords are matched at the start of a word, so
   `"ear"` matches *earache* but not *heart*.
2. **Urgency detection** — phrases like *chest pain*, *bleeding*, or *severe*
   mark the case as `urgent`; everything else is `routine`. Urgent patients are
   scheduled first so they get the earliest slots.
3. **Booking** — the patient is assigned the earliest free slot for a matching
   doctor, and that slot is removed from availability. Slots in the past are
   never offered.

Confirmed appointments are printed to the console and saved to
`appointments.json`.

## Requirements

- Python 3.8+ (standard library only — nothing to install)

## Usage

```bash
python main.py
```

## Example output

```
CONFIRMED: A6974 | Anna -> Dr. Arman Petrosyan | 2026-06-10T09:00:00 | urgent
CONFIRMED: A6211 | Narine -> Dr. Karen Hakobyan | 2026-06-10T09:00:00 | urgent
CONFIRMED: A9930 | Vardan -> Dr. Lilit Grigoryan | 2026-06-10T09:00:00 | routine
```

The same appointments are written to `appointments.json`:

```json
[
  {
    "id": "A6974",
    "patient": { "name": "Anna", "phone": "+37499123456" },
    "doctor": "Dr. Arman Petrosyan",
    "specialty": "Cardiology",
    "slot": "2026-06-10T09:00:00",
    "urgency": "urgent"
  }
]
```

Appointment IDs are random and slots are based on the current date, so your exact
output will differ.

## Project structure

```
main.py     # doctors, availability, classification, urgency, and booking logic
```

## Limitations

This is a demonstration prototype, not a production system:

- Doctors, availability, and the sample patients are hard-coded in `main.py`.
- Classification is keyword-based, not a real NLP model.
- State lives in memory for a single run; there is no database.

## Possible next steps

- Load doctors and patients from a file or database instead of hard-coding them.
- Replace keyword matching with a proper symptom-to-specialty model.
- Expose the scheduler over a small REST API.
