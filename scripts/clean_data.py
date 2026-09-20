import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
QUARANTINE_DIR = Path("data/quarantine")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# UTILITY
# ============================================================

def clean_strings(df):
    """
    Remove unnecessary whitespace from string columns.
    """

    for column in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        df[column] = df[column].astype("string").str.strip()

    return df


def report_dataset(name, df):
    print(
        f"{name:<25} "
        f"{len(df):>6} rows | "
        f"{len(df.columns):>3} columns"
    )


# ============================================================
# 1. PATIENTS
# ============================================================

def clean_patients():

    df = pd.read_csv(
        RAW_DIR / "patients.csv"
    )

    df = clean_strings(df)

    # Convert dates
    df["date_of_birth"] = pd.to_datetime(
        df["date_of_birth"],
        errors="coerce"
    )

    df["registration_date"] = pd.to_datetime(
        df["registration_date"],
        errors="coerce"
    )

    # Phone numbers must be strings
    df["contact_number"] = (
        df["contact_number"]
        .astype("string")
    )

    # Remove duplicate patient IDs
    df = df.drop_duplicates(
        subset=["patient_id"]
    )

    df.to_csv(
        PROCESSED_DIR / "patients.csv",
        index=False
    )

    return df


# ============================================================
# 2. DOCTORS
# ============================================================

def clean_doctors():

    df = pd.read_csv(
        RAW_DIR / "doctors.csv"
    )

    df = clean_strings(df)

    df["phone_number"] = (
        df["phone_number"]
        .astype("string")
    )

    df["years_experience"] = pd.to_numeric(
        df["years_experience"],
        errors="coerce"
    )

    df = df[
        df["years_experience"].between(
            0,
            60
        )
    ]

    df = df.drop_duplicates(
        subset=["doctor_id"]
    )

    df.to_csv(
        PROCESSED_DIR / "doctors.csv",
        index=False
    )

    return df


# ============================================================
# 3. APPOINTMENTS
# ============================================================

def clean_appointments(
    patients,
    doctors
):

    df = pd.read_csv(
        RAW_DIR / "appointments.csv"
    )

    df = clean_strings(df)

    df["appointment_date"] = pd.to_datetime(
        df["appointment_date"],
        errors="coerce"
    )

    # Combine date + time into one timestamp
    df["appointment_datetime"] = pd.to_datetime(
        df["appointment_date"].dt.strftime("%Y-%m-%d")
        + " "
        + df["appointment_time"],
        errors="coerce"
    )

    # Valid statuses
    valid_statuses = {
        "Scheduled",
        "Completed",
        "Cancelled",
        "No-show"
    }

    df.loc[
        ~df["status"].isin(valid_statuses),
        "status"
    ] = pd.NA

    # Referential integrity
    valid_patients = set(
        patients["patient_id"]
    )

    valid_doctors = set(
        doctors["doctor_id"]
    )

    df.loc[
        ~df["patient_id"].isin(valid_patients),
        "patient_id"
    ] = pd.NA

    df.loc[
        ~df["doctor_id"].isin(valid_doctors),
        "doctor_id"
    ] = pd.NA

    df = df.drop_duplicates(
        subset=["appointment_id"]
    )

    df.to_csv(
        PROCESSED_DIR / "appointments.csv",
        index=False
    )

    return df


# ============================================================
# 4. TREATMENTS
# ============================================================

def clean_treatments(
    appointments
):

    df = pd.read_csv(
        RAW_DIR / "treatments.csv"
    )

    df = clean_strings(df)

    df["treatment_date"] = pd.to_datetime(
        df["treatment_date"],
        errors="coerce"
    )

    df["cost"] = pd.to_numeric(
        df["cost"],
        errors="coerce"
    )

    # Costs cannot be negative
    df.loc[
        df["cost"] < 0,
        "cost"
    ] = np.nan

    valid_appointments = set(
        appointments["appointment_id"]
    )

    invalid = ~df[
        "appointment_id"
    ].isin(valid_appointments)

    if invalid.any():

        df[invalid].to_csv(
            QUARANTINE_DIR /
            "invalid_treatments.csv",
            index=False
        )

        df = df[~invalid]

    df = df.drop_duplicates(
        subset=["treatment_id"]
    )

    df.to_csv(
        PROCESSED_DIR / "treatments.csv",
        index=False
    )

    return df


# ============================================================
# 5. BILLING
# ============================================================

def clean_billing(
    treatments
):

    df = pd.read_csv(
        RAW_DIR / "billing.csv"
    )

    df = clean_strings(df)

    df["bill_date"] = pd.to_datetime(
        df["bill_date"],
        errors="coerce"
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    # Amount cannot be negative
    df.loc[
        df["amount"] < 0,
        "amount"
    ] = np.nan

    valid_treatments = set(
        treatments["treatment_id"]
    )

    invalid = ~df[
        "treatment_id"
    ].isin(valid_treatments)

    if invalid.any():

        df[invalid].to_csv(
            QUARANTINE_DIR /
            "invalid_billing.csv",
            index=False
        )

        df = df[~invalid]

    df = df.drop_duplicates(
        subset=["bill_id"]
    )

    df.to_csv(
        PROCESSED_DIR / "billing.csv",
        index=False
    )

    return df


# ============================================================
# 6. LAB RESULTS
# ============================================================

def clean_lab_results(
    appointments
):

    df = pd.read_csv(
        RAW_DIR / "lab_results.csv"
    )

    df = clean_strings(df)

    df["test_date"] = pd.to_datetime(
        df["test_date"],
        errors="coerce"
    )

    df["result_value"] = pd.to_numeric(
        df["result_value"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Validate against reference range
    # --------------------------------------------------------

    def validate_result(row):

        try:

            lower, upper = map(
                float,
                row["reference_range"].split("-")
            )

            value = row["result_value"]

            if value < lower or value > upper:
                return "Abnormal"

            return "Normal"

        except Exception:

            return "Invalid"

    df["validated_flag"] = df.apply(
        validate_result,
        axis=1
    )

    # --------------------------------------------------------
    # Quarantine impossible values
    # --------------------------------------------------------

    invalid = (
        df["result_value"].isna()
        | (df["result_value"] < 0)
    )

    if invalid.any():

        df[invalid].to_csv(
            QUARANTINE_DIR /
            "invalid_lab_results.csv",
            index=False
        )

        df = df[~invalid]

    valid_appointments = set(
        appointments["appointment_id"]
    )

    invalid_fk = ~df[
        "appointment_id"
    ].isin(valid_appointments)

    if invalid_fk.any():

        df[invalid_fk].to_csv(
            QUARANTINE_DIR /
            "invalid_lab_appointments.csv",
            index=False
        )

        df = df[~invalid_fk]

    df = df.drop_duplicates(
        subset=["lab_id"]
    )

    df.to_csv(
        PROCESSED_DIR /
        "lab_results.csv",
        index=False
    )

    return df


# ============================================================
# 7. CONSULTATION NOTES
# ============================================================

def clean_consultation_notes(
    appointments,
    doctors
):

    df = pd.read_csv(
        RAW_DIR /
        "consultation_notes.csv"
    )

    df = clean_strings(df)

    df["consultation_date"] = pd.to_datetime(
        df["consultation_date"],
        errors="coerce"
    )

    valid_appointments = set(
        appointments[
            appointments["status"] == "Completed"
        ]["appointment_id"]
    )

    invalid = ~df[
        "appointment_id"
    ].isin(valid_appointments)

    if invalid.any():

        df[invalid].to_csv(
            QUARANTINE_DIR /
            "invalid_consultation_notes.csv",
            index=False
        )

        df = df[~invalid]

    valid_doctors = set(
        doctors["doctor_id"]
    )

    invalid_doctor = ~df[
        "doctor_id"
    ].isin(valid_doctors)

    if invalid_doctor.any():

        df[invalid_doctor].to_csv(
            QUARANTINE_DIR /
            "invalid_consultation_doctors.csv",
            index=False
        )

        df = df[~invalid_doctor]

    df = df.drop_duplicates(
        subset=["note_id"]
    )

    df.to_csv(
        PROCESSED_DIR /
        "consultation_notes.csv",
        index=False
    )

    return df


# ============================================================
# 8. VISIT EVENTS
# ============================================================

def clean_visit_events(
    appointments
):

    df = pd.read_csv(
        RAW_DIR /
        "visit_events.csv"
    )

    df = clean_strings(df)

    datetime_columns = [
        "check_in_time",
        "doctor_start_time",
        "doctor_end_time",
        "check_out_time"
    ]

    for column in datetime_columns:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    numeric_columns = [
        "waiting_time_minutes",
        "consultation_duration_minutes"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Only completed appointments can have visits
    completed_appointments = set(
        appointments[
            appointments["status"] == "Completed"
        ]["appointment_id"]
    )

    invalid = ~df[
        "appointment_id"
    ].isin(completed_appointments)

    if invalid.any():

        df[invalid].to_csv(
            QUARANTINE_DIR /
            "invalid_visit_events.csv",
            index=False
        )

        df = df[~invalid]

    # Waiting time validation
    df.loc[
        df["waiting_time_minutes"] < 0,
        "waiting_time_minutes"
    ] = np.nan

    df.loc[
        df["consultation_duration_minutes"] <= 0,
        "consultation_duration_minutes"
    ] = np.nan

    df = df.drop_duplicates(
        subset=["visit_id"]
    )

    df.to_csv(
        PROCESSED_DIR /
        "visit_events.csv",
        index=False
    )

    return df


# ============================================================
# 9. WEARABLE DATA
# ============================================================

def clean_wearable_data(
    patients
):

    df = pd.read_csv(
        RAW_DIR /
        "wearable_data.csv"
    )

    df = clean_strings(df)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    numeric_columns = [
        "heart_rate_bpm",
        "spo2_percent",
        "temperature_c",
        "steps",
        "sleep_hours"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Validate patient relationship
    valid_patients = set(
        patients["patient_id"]
    )

    invalid = ~df[
        "patient_id"
    ].isin(valid_patients)

    if invalid.any():

        df[invalid].to_csv(
            QUARANTINE_DIR /
            "invalid_wearable_patients.csv",
            index=False
        )

        df = df[~invalid]

    # Basic physical bounds
    invalid_values = (
        (df["heart_rate_bpm"] <= 0)
        | (df["spo2_percent"] <= 0)
        | (df["spo2_percent"] > 100)
        | (df["temperature_c"] <= 0)
        | (df["steps"] < 0)
        | (df["sleep_hours"] < 0)
    )

    if invalid_values.any():

        df[invalid_values].to_csv(
            QUARANTINE_DIR /
            "invalid_wearable_values.csv",
            index=False
        )

        df = df[~invalid_values]

    df = df.drop_duplicates(
        subset=["reading_id"]
    )

    df.to_csv(
        PROCESSED_DIR /
        "wearable_data.csv",
        index=False
    )

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("HOSPITAL DATA CLEANING PIPELINE")
    print("=" * 70)

    patients = clean_patients()
    report_dataset("patients", patients)

    doctors = clean_doctors()
    report_dataset("doctors", doctors)

    appointments = clean_appointments(
        patients,
        doctors
    )
    report_dataset("appointments", appointments)

    treatments = clean_treatments(
        appointments
    )
    report_dataset("treatments", treatments)

    billing = clean_billing(
        treatments
    )
    report_dataset("billing", billing)

    labs = clean_lab_results(
        appointments
    )
    report_dataset("lab_results", labs)

    notes = clean_consultation_notes(
        appointments,
        doctors
    )
    report_dataset(
        "consultation_notes",
        notes
    )

    visits = clean_visit_events(
        appointments
    )
    report_dataset(
        "visit_events",
        visits
    )

    wearable = clean_wearable_data(
        patients
    )
    report_dataset(
        "wearable_data",
        wearable
    )

    print("\n")
    print("=" * 70)
    print("DATA CLEANING COMPLETED")
    print("=" * 70)

    print("\nProcessed data:")
    print(PROCESSED_DIR)

    print("\nQuarantined data:")
    print(QUARANTINE_DIR)


if __name__ == "__main__":
    main()