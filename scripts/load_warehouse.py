import pandas as pd
import sqlite3
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

PROCESSED_DIR = Path("data/processed")
WAREHOUSE_DIR = Path("data/warehouse")

WAREHOUSE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DB_PATH = WAREHOUSE_DIR / "hospital_analytics.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

connection = sqlite3.connect(DB_PATH)


# ============================================================
# DATASETS
# ============================================================

DATASETS = [
    "patients",
    "doctors",
    "appointments",
    "treatments",
    "billing",
    "lab_results",
    "consultation_notes",
    "visit_events",
    "wearable_data",
]


# ============================================================
# LOAD DATA
# ============================================================

print("\n")
print("=" * 70)
print("HOSPITAL DATA WAREHOUSE LOAD")
print("=" * 70)


for dataset in DATASETS:

    file_path = PROCESSED_DIR / f"{dataset}.csv"

    print(
        f"\nLoading: {dataset}.csv"
    )

    if not file_path.exists():

        print(
            f"❌ File not found: {file_path}"
        )

        continue

    df = pd.read_csv(
        file_path
    )

    # Replace existing table during development
    df.to_sql(
        dataset,
        connection,
        if_exists="replace",
        index=False
    )

    print(
        f"✓ Loaded {len(df)} records"
    )


# ============================================================
# CREATE INDEXES
# ============================================================

print("\n")
print("=" * 70)
print("CREATING INDEXES")
print("=" * 70)


indexes = {

    "appointments":
        [
            "patient_id",
            "doctor_id"
        ],

    "treatments":
        [
            "appointment_id"
        ],

    "billing":
        [
            "patient_id",
            "treatment_id"
        ],

    "lab_results":
        [
            "patient_id",
            "appointment_id"
        ],

    "consultation_notes":
        [
            "patient_id",
            "appointment_id",
            "doctor_id"
        ],

    "visit_events":
        [
            "appointment_id",
            "patient_id"
        ],

    "wearable_data":
        [
            "patient_id",
            "timestamp"
        ]
}


for table, columns in indexes.items():

    for column in columns:

        index_name = (
            f"idx_{table}_{column}"
        )

        connection.execute(
            f"""
            CREATE INDEX IF NOT EXISTS
            {index_name}
            ON {table} ({column})
            """
        )

print("✓ Indexes created")


# ============================================================
# VERIFY TABLES
# ============================================================

print("\n")
print("=" * 70)
print("WAREHOUSE VERIFICATION")
print("=" * 70)


tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """,
    connection
)


print("\nTables:")

for table in tables["name"]:

    count = pd.read_sql_query(
        f"SELECT COUNT(*) AS count FROM {table}",
        connection
    ).iloc[0]["count"]

    print(
        f"  {table:<25} {count:>6} rows"
    )


# ============================================================
# CLOSE
# ============================================================

connection.close()


print("\n")
print("=" * 70)
print("✅ WAREHOUSE LOAD COMPLETED")
print("=" * 70)

print(
    f"\nDatabase created at:\n{DB_PATH}"
)