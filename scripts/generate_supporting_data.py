import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

RAW_DIR = Path("data/raw")

rng = np.random.default_rng(20260920)


# ============================================================
# LOAD EXISTING SOURCE DATA
# ============================================================

patients = pd.read_csv(RAW_DIR / "patients.csv")
doctors = pd.read_csv(RAW_DIR / "doctors.csv")
appointments = pd.read_csv(RAW_DIR / "appointments.csv")

print("Loaded source datasets")
print(f"Patients      : {len(patients)}")
print(f"Doctors       : {len(doctors)}")
print(f"Appointments  : {len(appointments)}")


# ============================================================
# 1. LAB RESULTS
# ============================================================

lab_tests = [
    ("Hemoglobin", "g/dL", 12.0, 17.5),
    ("Blood Glucose", "mg/dL", 70.0, 140.0),
    ("WBC", "10^3/uL", 4.0, 11.0),
    ("Creatinine", "mg/dL", 0.6, 1.3),
    ("Total Cholesterol", "mg/dL", 120.0, 200.0),
    ("Platelets", "10^3/uL", 150.0, 450.0),
    ("CRP", "mg/L", 0.0, 10.0),
]

lab_rows = []
lab_counter = 1

completed = appointments[
    appointments["status"].eq("Completed")
]

for _, appointment in completed.iterrows():

    number_of_tests = int(
        rng.integers(2, 5)
    )

    selected_tests = rng.choice(
        len(lab_tests),
        size=number_of_tests,
        replace=False
    )

    for index in selected_tests:

        test_name, unit, lower, upper = lab_tests[index]

        abnormal = rng.random() < 0.15

        if test_name == "Blood Glucose":

            value = (
                rng.normal(175, 18)
                if abnormal
                else rng.normal(100, 15)
            )

        elif test_name == "WBC":

            value = (
                rng.normal(14, 1.5)
                if abnormal
                else rng.normal(7, 1)
            )

        elif test_name == "Creatinine":

            value = (
                rng.normal(1.8, 0.2)
                if abnormal
                else rng.normal(0.9, 0.15)
            )

        elif test_name == "CRP":

            value = (
                rng.uniform(10.5, 20)
                if abnormal
                else rng.uniform(1, 8)
            )

        else:

            value = rng.normal(
                (lower + upper) / 2,
                (upper - lower) / 7
            )

            if abnormal:

                value = rng.choice([
                    rng.uniform(lower * 0.7, lower * 0.95),
                    rng.uniform(upper * 1.05, upper * 1.3)
                ])

        value = round(float(value), 2)

        abnormal_flag = (
            "Abnormal"
            if value < lower or value > upper
            else "Normal"
        )

        lab_rows.append([
            f"LAB{lab_counter:04d}",
            appointment["patient_id"],
            appointment["appointment_id"],
            test_name,
            appointment["appointment_date"],
            value,
            unit,
            f"{lower:g}-{upper:g}",
            abnormal_flag
        ])

        lab_counter += 1


lab_df = pd.DataFrame(
    lab_rows,
    columns=[
        "lab_id",
        "patient_id",
        "appointment_id",
        "test_name",
        "test_date",
        "result_value",
        "unit",
        "reference_range",
        "abnormal_flag"
    ]
)


# ============================================================
# 2. WEARABLE DATA
# ============================================================

wearable_rows = []
reading_counter = 1

for _, patient in patients.iterrows():

    for day in range(1, 11):

        hour = int(
            rng.choice([7, 10, 14, 18, 22])
        )

        minute = int(
            rng.integers(0, 60)
        )

        heart_rate = float(
            np.clip(
                rng.normal(78, 10),
                48,
                125
            )
        )

        spo2 = float(
            np.clip(
                rng.normal(97.2, 1.2),
                88,
                100
            )
        )

        temperature = float(
            np.clip(
                rng.normal(36.8, 0.35),
                35.5,
                39.2
            )
        )

        steps = int(
            max(
                300,
                rng.normal(6200, 1800)
            )
        )

        sleep = float(
            np.clip(
                rng.normal(6.9, 1.1),
                3,
                10
            )
        )

        # Introduce a small number of abnormal readings
        # for data-quality/risk analytics.

        if rng.random() < 0.06:
            heart_rate = round(
                float(rng.uniform(105, 125)),
                1
            )

        if rng.random() < 0.05:
            spo2 = round(
                float(rng.uniform(88, 93.5)),
                1
            )

        if rng.random() < 0.04:
            temperature = round(
                float(rng.uniform(38, 39.2)),
                1
            )

        timestamp = (
            f"2026-09-{day:02d} "
            f"{hour:02d}:{minute:02d}:00"
        )

        wearable_rows.append([
            f"WR{reading_counter:05d}",
            patient["patient_id"],
            timestamp,
            round(heart_rate, 1),
            round(spo2, 1),
            round(temperature, 1),
            steps,
            round(sleep, 1)
        ])

        reading_counter += 1


wearable_df = pd.DataFrame(
    wearable_rows,
    columns=[
        "reading_id",
        "patient_id",
        "timestamp",
        "heart_rate_bpm",
        "spo2_percent",
        "temperature_c",
        "steps",
        "sleep_hours"
    ]
)


# ============================================================
# 3. CONSULTATION NOTES
# ============================================================

notes_rows = []
note_counter = 1

templates = {

    "Consultation": [
        (
            "Patient reported routine symptoms.",
            "Routine clinical review",
            "Clinical assessment completed and care plan discussed."
        ),
        (
            "Patient presented for general consultation.",
            "General assessment",
            "Vital signs reviewed and treatment plan discussed."
        )
    ],

    "Checkup": [
        (
            "Patient attended routine health check.",
            "Routine check-up",
            "Preventive monitoring and follow-up recommendations discussed."
        ),
        (
            "Patient attended scheduled check-up.",
            "Preventive assessment",
            "Routine examination completed."
        )
    ],

    "Follow-up": [
        (
            "Patient returned for follow-up.",
            "Treatment follow-up",
            "Previous treatment response reviewed."
        ),
        (
            "Patient attended follow-up appointment.",
            "Progress assessment",
            "Symptoms and treatment progress reviewed."
        )
    ],

    "Emergency": [
        (
            "Patient presented with urgent symptoms.",
            "Urgent assessment",
            "Immediate clinical evaluation performed."
        ),
        (
            "Emergency consultation completed.",
            "Emergency evaluation",
            "Patient evaluated and monitoring plan established."
        )
    ],

    "Therapy": [
        (
            "Patient attended therapy session.",
            "Therapy assessment",
            "Response to therapy reviewed."
        ),
        (
            "Therapy visit completed.",
            "Therapy progress",
            "Treatment progress and continuation plan reviewed."
        )
    ]
}


for _, appointment in completed.iterrows():

    reason = appointment["reason_for_visit"]

    options = templates.get(
        reason,
        templates["Consultation"]
    )

    symptoms, assessment, note_text = options[
        int(rng.integers(0, len(options)))
    ]

    follow_up = (
        "Yes"
        if rng.random() < 0.30
        else "No"
    )

    notes_rows.append([
        f"NOTE{note_counter:04d}",
        appointment["patient_id"],
        appointment["appointment_id"],
        appointment["doctor_id"],
        appointment["appointment_date"],
        symptoms,
        assessment,
        note_text,
        follow_up
    ])

    note_counter += 1


notes_df = pd.DataFrame(
    notes_rows,
    columns=[
        "note_id",
        "patient_id",
        "appointment_id",
        "doctor_id",
        "consultation_date",
        "symptoms",
        "assessment",
        "notes",
        "follow_up_required"
    ]
)


# ============================================================
# 4. VISIT / WAITING EVENTS
# ============================================================

visit_rows = []
visit_counter = 1

for _, appointment in appointments.iterrows():

    status = appointment["status"]

    # Only patients who actually attended get visit events.
    if status != "Completed":
        continue

    appointment_date = appointment["appointment_date"]
    appointment_time = appointment["appointment_time"]

    appointment_datetime = pd.to_datetime(
        f"{appointment_date} {appointment_time}"
    )

    check_in = (
        appointment_datetime
        + pd.Timedelta(
            minutes=int(
                rng.integers(-10, 16)
            )
        )
    )

    waiting_time = int(
        np.clip(
            rng.normal(34, 16),
            5,
            90
        )
    )

    doctor_start = (
        check_in
        + pd.Timedelta(
            minutes=waiting_time
        )
    )

    consultation_duration = int(
        np.clip(
            rng.normal(24, 9),
            10,
            60
        )
    )

    doctor_end = (
        doctor_start
        + pd.Timedelta(
            minutes=consultation_duration
        )
    )

    check_out = (
        doctor_end
        + pd.Timedelta(
            minutes=int(
                rng.integers(5, 20)
            )
        )
    )

    visit_rows.append([
        f"VIS{visit_counter:04d}",
        appointment["appointment_id"],
        appointment["patient_id"],
        check_in.strftime("%Y-%m-%d %H:%M:%S"),
        doctor_start.strftime("%Y-%m-%d %H:%M:%S"),
        doctor_end.strftime("%Y-%m-%d %H:%M:%S"),
        check_out.strftime("%Y-%m-%d %H:%M:%S"),
        waiting_time,
        consultation_duration,
        "Completed"
    ])

    visit_counter += 1


visits_df = pd.DataFrame(
    visit_rows,
    columns=[
        "visit_id",
        "appointment_id",
        "patient_id",
        "check_in_time",
        "doctor_start_time",
        "doctor_end_time",
        "check_out_time",
        "waiting_time_minutes",
        "consultation_duration_minutes",
        "visit_status"
    ]
)


# ============================================================
# SAVE
# ============================================================

lab_df.to_csv(
    RAW_DIR / "lab_results.csv",
    index=False
)

wearable_df.to_csv(
    RAW_DIR / "wearable_data.csv",
    index=False
)

notes_df.to_csv(
    RAW_DIR / "consultation_notes.csv",
    index=False
)

visits_df.to_csv(
    RAW_DIR / "visit_events.csv",
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("SUPPORTING DATA GENERATION COMPLETED")
print("=" * 70)

print(f"Laboratory records       : {len(lab_df)}")
print(f"Wearable records         : {len(wearable_df)}")
print(f"Consultation notes       : {len(notes_df)}")
print(f"Visit events             : {len(visits_df)}")

print("\nAppointment status:")
print(
    appointments["status"]
    .value_counts()
    .to_string()
)

print("\nVisit events:")
print(
    visits_df["visit_status"]
    .value_counts()
    .to_string()
)

print("\nFiles regenerated inside:")
print(RAW_DIR)