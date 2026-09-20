import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

RAW_DIR = Path("data/raw")
REPORT_DIR = Path("reports")

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATASETS
# ============================================================

DATASETS = [
    "patients.csv",
    "doctors.csv",
    "appointments.csv",
    "treatments.csv",
    "billing.csv",
    "consultation_notes.csv",
    "lab_results.csv",
    "visit_events.csv",
    "wearable_data.csv",
]


# ============================================================
# PRIMARY KEYS
# ============================================================

PRIMARY_KEYS = {
    "patients.csv": "patient_id",
    "doctors.csv": "doctor_id",
    "appointments.csv": "appointment_id",
    "treatments.csv": "treatment_id",
    "billing.csv": "bill_id",
    "consultation_notes.csv": "note_id",
    "lab_results.csv": "lab_id",
    "visit_events.csv": "visit_id",
    "wearable_data.csv": "reading_id",
}


# ============================================================
# PROFILE FUNCTION
# ============================================================

def profile_dataset(file_name):

    file_path = RAW_DIR / file_name

    print("\n" + "=" * 70)
    print(f"DATASET: {file_name}")
    print("=" * 70)

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    try:
        df = pd.read_csv(file_path)

    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    print(f"\nRows        : {len(df):,}")
    print(f"Columns     : {len(df.columns)}")
    print(f"Memory      : {df.memory_usage(deep=True).sum() / 1024:.2f} KB")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print("\nData Types:")
    print(df.dtypes)

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\nMissing Values:")

    missing = df.isnull().sum()

    missing = missing[missing > 0]

    if missing.empty:
        print("  ✓ No missing values")
    else:
        for column, count in missing.items():

            percentage = (count / len(df)) * 100

            print(
                f"  - {column}: "
                f"{count} ({percentage:.2f}%)"
            )

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    duplicate_rows = df.duplicated().sum()

    print("\nDuplicate Rows:")
    print(f"  {duplicate_rows}")

    # --------------------------------------------------------
    # Primary key validation
    # --------------------------------------------------------

    primary_key = PRIMARY_KEYS.get(file_name)

    if primary_key and primary_key in df.columns:

        null_pk = df[primary_key].isnull().sum()

        duplicate_pk = df[primary_key].duplicated().sum()

        print("\nPrimary Key Check:")
        print(f"  Key             : {primary_key}")
        print(f"  Null IDs        : {null_pk}")
        print(f"  Duplicate IDs   : {duplicate_pk}")

        if null_pk == 0 and duplicate_pk == 0:
            print("  ✓ Primary key looks valid")

        else:
            print("  ⚠ Primary key needs attention")

    # --------------------------------------------------------
    # Unique values for categorical columns
    # --------------------------------------------------------

    print("\nCategorical Summary:")

    for column in df.select_dtypes(include="object").columns:

        unique_count = df[column].nunique()

        if unique_count <= 15:

            values = df[column].dropna().unique()

            print(
                f"  {column}: "
                f"{list(values)}"
            )

    # --------------------------------------------------------
    # Numeric statistics
    # --------------------------------------------------------

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) > 0:

        print("\nNumeric Statistics:")

        print(
            df[numeric_columns]
            .describe()
            .round(2)
            .to_string()
        )

    # --------------------------------------------------------
    # Save individual profile
    # --------------------------------------------------------

    report = []

    report.append(f"DATASET: {file_name}")
    report.append("=" * 70)

    report.append(f"Rows: {len(df)}")
    report.append(f"Columns: {len(df.columns)}")

    report.append("\nCOLUMNS")
    report.append("-" * 30)

    for column in df.columns:

        report.append(
            f"{column} | "
            f"{df[column].dtype} | "
            f"missing={df[column].isnull().sum()} | "
            f"unique={df[column].nunique()}"
        )

    report.append("\nDUPLICATES")
    report.append("-" * 30)

    report.append(
        f"Duplicate rows: {duplicate_rows}"
    )

    if primary_key in df.columns:

        report.append(
            f"Duplicate {primary_key}: "
            f"{df[primary_key].duplicated().sum()}"
        )

    report_path = (
        REPORT_DIR /
        f"{file_name.replace('.csv', '')}_profile.txt"
    )

    report_path.write_text(
        "\n".join(report),
        encoding="utf-8"
    )


# ============================================================
# FOREIGN KEY CHECK
# ============================================================

def foreign_key_check():

    print("\n")
    print("=" * 70)
    print("FOREIGN KEY / RELATIONSHIP CHECK")
    print("=" * 70)

    datasets = {}

    for file_name in DATASETS:

        path = RAW_DIR / file_name

        if path.exists():

            datasets[file_name] = pd.read_csv(path)

    # --------------------------------------------------------
    # Patients → Appointments
    # --------------------------------------------------------

    if (
        "patients.csv" in datasets
        and "appointments.csv" in datasets
    ):

        patients = set(
            datasets["patients.csv"]["patient_id"]
        )

        appointment_patients = set(
            datasets["appointments.csv"]["patient_id"]
        )

        invalid = appointment_patients - patients

        print("\nappointments → patients")

        if invalid:
            print(
                f"  ❌ Invalid patient IDs: "
                f"{len(invalid)}"
            )
        else:
            print("  ✓ All patient IDs valid")

    # --------------------------------------------------------
    # Doctors → Appointments
    # --------------------------------------------------------

    if (
        "doctors.csv" in datasets
        and "appointments.csv" in datasets
    ):

        doctors = set(
            datasets["doctors.csv"]["doctor_id"]
        )

        appointment_doctors = set(
            datasets["appointments.csv"]["doctor_id"]
        )

        invalid = appointment_doctors - doctors

        print("\nappointments → doctors")

        if invalid:
            print(
                f"  ❌ Invalid doctor IDs: "
                f"{len(invalid)}"
            )
        else:
            print("  ✓ All doctor IDs valid")

    # --------------------------------------------------------
    # Treatments → Appointments
    # --------------------------------------------------------

    if (
        "treatments.csv" in datasets
        and "appointments.csv" in datasets
    ):

        appointments = set(
            datasets["appointments.csv"]["appointment_id"]
        )

        treatment_appointments = set(
            datasets["treatments.csv"]["appointment_id"]
        )

        invalid = (
            treatment_appointments -
            appointments
        )

        print("\ntreatments → appointments")

        if invalid:
            print(
                f"  ❌ Invalid appointment IDs: "
                f"{len(invalid)}"
            )
        else:
            print("  ✓ All appointment IDs valid")

    # --------------------------------------------------------
    # Billing → Treatments
    # --------------------------------------------------------

    if (
        "billing.csv" in datasets
        and "treatments.csv" in datasets
    ):

        treatments = set(
            datasets["treatments.csv"]["treatment_id"]
        )

        billing_treatments = set(
            datasets["billing.csv"]["treatment_id"]
        )

        invalid = (
            billing_treatments -
            treatments
        )

        print("\nbilling → treatments")

        if invalid:
            print(
                f"  ❌ Invalid treatment IDs: "
                f"{len(invalid)}"
            )
        else:
            print("  ✓ All treatment IDs valid")


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("🏥 HOSPITAL PATIENT CARE ANALYTICS")
    print("DATA PROFILING PIPELINE")
    print("=" * 70)

    for dataset in DATASETS:

        profile_dataset(dataset)

    foreign_key_check()

    print("\n")
    print("=" * 70)
    print("✅ PROFILING COMPLETED")
    print("=" * 70)

    print("\nReports created in:")
    print(REPORT_DIR)


if __name__ == "__main__":
    main()