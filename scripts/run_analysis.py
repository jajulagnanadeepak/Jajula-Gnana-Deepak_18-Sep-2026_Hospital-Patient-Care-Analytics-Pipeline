import sqlite3
from pathlib import Path
import pandas as pd


# ==============================
# PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "warehouse" / "hospital_analytics.db"
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(exist_ok=True)


# ==============================
# CONNECT TO DATABASE
# ==============================

conn = sqlite3.connect(DB_PATH)

print("\n" + "=" * 60)
print("HOSPITAL ANALYTICS")
print("=" * 60)


# ==============================
# 1. APPOINTMENT STATUS
# ==============================

print("\n1. APPOINTMENT STATUS")

query = """
SELECT
    status,
    COUNT(*) AS appointment_count
FROM fact_appointment
GROUP BY status
ORDER BY appointment_count DESC
"""

df = pd.read_sql_query(query, conn)

print(df.to_string(index=False))

df.to_csv(
    REPORT_DIR / "appointment_status.csv",
    index=False
)


# ==============================
# 2. DOCTOR APPOINTMENTS
# ==============================

print("\n2. DOCTOR APPOINTMENTS")

query = """
SELECT
    d.doctor_id,
    d.first_name || ' ' || d.last_name AS doctor_name,
    d.specialization,
    COUNT(a.appointment_id) AS total_appointments
FROM fact_appointment a
JOIN dim_doctor d
    ON a.doctor_id = d.doctor_id
GROUP BY
    d.doctor_id,
    doctor_name,
    d.specialization
ORDER BY total_appointments DESC
"""

df = pd.read_sql_query(query, conn)

print(df.to_string(index=False))

df.to_csv(
    REPORT_DIR / "doctor_appointments.csv",
    index=False
)


# ==============================
# 3. WAITING TIME BY DOCTOR
# ==============================

print("\n3. WAITING TIME BY DOCTOR")

query = """
SELECT
    d.doctor_id,
    d.first_name || ' ' || d.last_name AS doctor_name,
    ROUND(AVG(v.waiting_time_minutes), 2)
        AS average_waiting_minutes
FROM fact_visit v
JOIN fact_appointment a
    ON v.appointment_id = a.appointment_id
JOIN dim_doctor d
    ON a.doctor_id = d.doctor_id
GROUP BY
    d.doctor_id,
    doctor_name
ORDER BY average_waiting_minutes DESC
"""

df = pd.read_sql_query(query, conn)

print(df.to_string(index=False))

df.to_csv(
    REPORT_DIR / "waiting_time_by_doctor.csv",
    index=False
)


# ==============================
# 4. TREATMENT REVENUE
# ==============================

print("\n4. TREATMENT REVENUE")

query = """
SELECT
    treatment_type,
    COUNT(*) AS treatment_count,
    ROUND(SUM(cost), 2) AS total_revenue
FROM fact_treatment
GROUP BY treatment_type
ORDER BY total_revenue DESC
"""

df = pd.read_sql_query(query, conn)

print(df.to_string(index=False))

df.to_csv(
    REPORT_DIR / "treatment_revenue.csv",
    index=False
)


# ==============================
# 5. PAYMENT STATUS
# ==============================

print("\n5. PAYMENT STATUS")

query = """
SELECT
    payment_status,
    COUNT(*) AS bill_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM fact_billing
GROUP BY payment_status
ORDER BY total_amount DESC
"""

df = pd.read_sql_query(query, conn)

print(df.to_string(index=False))

df.to_csv(
    REPORT_DIR / "payment_status.csv",
    index=False
)


# ==============================
# 6. TOP PATIENTS BY APPOINTMENTS
# ==============================

print("\n6. PATIENT APPOINTMENTS")

query = """
SELECT
    patient_id,
    first_name || ' ' || last_name AS patient_name,
    total_appointments,
    completed_appointments,
    no_show_count
FROM vw_patient_360
ORDER BY total_appointments DESC
LIMIT 10
"""

df = pd.read_sql_query(query, conn)

print(df.to_string(index=False))

df.to_csv(
    REPORT_DIR / "patient_appointments.csv",
    index=False
)


# ==============================
# 7. PATIENT FOLLOW-UP
# ==============================

print("\n7. PATIENT FOLLOW-UP")

query = """
SELECT
    patient_id,
    first_name || ' ' || last_name AS patient_name,
    follow_up_count,
    total_appointments,
    abnormal_lab_count
FROM vw_patient_360
WHERE follow_up_count > 0
ORDER BY follow_up_count DESC
"""

df = pd.read_sql_query(query, conn)

print(df.to_string(index=False))

df.to_csv(
    REPORT_DIR / "patient_followup.csv",
    index=False
)


# ==============================
# 8. PATIENT 360
# ==============================

print("\n8. PATIENT 360")

query = """
SELECT *
FROM vw_patient_360
ORDER BY total_appointments DESC
"""

df = pd.read_sql_query(query, conn)

print(
    f"Patient 360 records: {len(df)}"
)

df.to_csv(
    REPORT_DIR / "patient_360.csv",
    index=False
)


# ==============================
# CLOSE
# ==============================

conn.close()

print("\n" + "=" * 60)
print("ANALYSIS COMPLETED")
print("=" * 60)

print("\nReports saved to:")
print(REPORT_DIR)