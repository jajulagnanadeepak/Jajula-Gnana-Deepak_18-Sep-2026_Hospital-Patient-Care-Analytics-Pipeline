import sqlite3
from pathlib import Path
import datetime


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "warehouse" / "hospital_analytics.db"


# ============================================================
# CONNECT
# ============================================================

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n" + "=" * 60)
print("HOSPITAL ANALYTICS STAR SCHEMA")
print("=" * 60)


# ============================================================
# REMOVE PREVIOUS ANALYTICAL OBJECTS
# ============================================================

objects = [
    "vw_patient_360",
    "vw_hospital_kpis",

    "fact_appointment",
    "fact_treatment",
    "fact_billing",
    "fact_lab_result",
    "fact_visit",
    "fact_wearable",
    "fact_consultation",

    "dim_patient",
    "dim_doctor",
    "dim_date",
    "dim_treatment",
]

for obj in objects:
    cursor.execute("""
        SELECT type
        FROM sqlite_master
        WHERE name = ?
    """, (obj,))

    result = cursor.fetchone()

    if result:
        if result[0] == "view":
            cursor.execute(f"DROP VIEW {obj}")
        elif result[0] == "table":
            cursor.execute(f"DROP TABLE {obj}")


# ============================================================
# DIMENSION: PATIENT
# ============================================================

print("\nCreating dim_patient...")

cursor.execute("""
CREATE TABLE dim_patient AS
SELECT
    patient_id,
    first_name,
    last_name,
    gender,
    date_of_birth,
    contact_number,
    address,
    registration_date,
    insurance_provider,
    insurance_number,
    email
FROM patients
""")

print("✓ dim_patient created")


# ============================================================
# DIMENSION: DOCTOR
# ============================================================

print("Creating dim_doctor...")

cursor.execute("""
CREATE TABLE dim_doctor AS
SELECT
    doctor_id,
    first_name,
    last_name,
    specialization,
    phone_number,
    years_experience,
    hospital_branch,
    email
FROM doctors
""")

print("✓ dim_doctor created")


# ============================================================
# DIMENSION: TREATMENT
# ============================================================

print("Creating dim_treatment...")

cursor.execute("""
CREATE TABLE dim_treatment AS
SELECT DISTINCT
    treatment_type,
    description
FROM treatments
""")

print("✓ dim_treatment created")


# ============================================================
# DIMENSION: DATE
# ============================================================

print("Creating dim_date...")

cursor.execute("""
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name TEXT,
    day INTEGER,
    day_of_week INTEGER,
    day_name TEXT
)
""")


# Collect dates from all major date columns
date_columns = [
    ("appointments", "appointment_date"),
    ("treatments", "treatment_date"),
    ("billing", "bill_date"),
    ("lab_results", "test_date"),
    ("consultation_notes", "consultation_date"),
]


all_dates = set()

for table, column in date_columns:

    cursor.execute(
        f"""
        SELECT DISTINCT DATE({column})
        FROM {table}
        WHERE {column} IS NOT NULL
        """
    )

    for row in cursor.fetchall():

        if row[0]:
            all_dates.add(row[0])


for date_value in sorted(all_dates):

    try:

        d = datetime.datetime.strptime(
            date_value,
            "%Y-%m-%d"
        )

        date_key = int(d.strftime("%Y%m%d"))

        year = d.year
        quarter = ((d.month - 1) // 3) + 1
        month = d.month
        month_name = d.strftime("%B")
        day = d.day
        day_of_week = d.weekday() + 1
        day_name = d.strftime("%A")

        cursor.execute("""
        INSERT INTO dim_date
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date_key,
            date_value,
            year,
            quarter,
            month,
            month_name,
            day,
            day_of_week,
            day_name
        ))

    except ValueError:
        pass


print(
    f"✓ dim_date created ({len(all_dates)} dates)"
)


# ============================================================
# FACT: APPOINTMENTS
# ============================================================

print("Creating fact_appointment...")

cursor.execute("""
CREATE TABLE fact_appointment AS
SELECT
    appointment_id,
    patient_id,
    doctor_id,
    DATE(appointment_date) AS appointment_date,
    appointment_time,
    reason_for_visit,
    status,
    appointment_datetime
FROM appointments
""")

print("✓ fact_appointment created")


# ============================================================
# FACT: TREATMENTS
# ============================================================

print("Creating fact_treatment...")

cursor.execute("""
CREATE TABLE fact_treatment AS
SELECT
    t.treatment_id,
    t.appointment_id,
    a.patient_id,
    a.doctor_id,
    DATE(t.treatment_date) AS treatment_date,
    t.treatment_type,
    t.description,
    t.cost
FROM treatments t

JOIN appointments a
    ON t.appointment_id = a.appointment_id
""")

print("✓ fact_treatment created")


# ============================================================
# FACT: BILLING
# ============================================================

print("Creating fact_billing...")

cursor.execute("""
CREATE TABLE fact_billing AS
SELECT
    bill_id,
    patient_id,
    treatment_id,
    DATE(bill_date) AS bill_date,
    amount,
    payment_method,
    payment_status
FROM billing
""")

print("✓ fact_billing created")


# ============================================================
# FACT: LAB RESULTS
# ============================================================

print("Creating fact_lab_result...")

cursor.execute("""
CREATE TABLE fact_lab_result AS
SELECT
    lab_id,
    patient_id,
    appointment_id,
    test_name,
    DATE(test_date) AS test_date,
    result_value,
    unit,
    reference_range,
    abnormal_flag,
    validated_flag
FROM lab_results
""")

print("✓ fact_lab_result created")


# ============================================================
# FACT: VISITS
# ============================================================

print("Creating fact_visit...")

cursor.execute("""
CREATE TABLE fact_visit AS
SELECT
    visit_id,
    appointment_id,
    patient_id,
    DATE(check_in_time) AS visit_date,
    check_in_time,
    doctor_start_time,
    doctor_end_time,
    check_out_time,
    waiting_time_minutes,
    consultation_duration_minutes,
    visit_status
FROM visit_events
""")

print("✓ fact_visit created")


# ============================================================
# FACT: WEARABLE DATA
# ============================================================

print("Creating fact_wearable...")

cursor.execute("""
CREATE TABLE fact_wearable AS
SELECT
    reading_id,
    patient_id,
    timestamp AS reading_timestamp,
    heart_rate_bpm,
    spo2_percent,
    temperature_c,
    steps,
    sleep_hours
FROM wearable_data
""")

print("✓ fact_wearable created")


# ============================================================
# FACT: CONSULTATION NOTES
# ============================================================

print("Creating fact_consultation...")

cursor.execute("""
CREATE TABLE fact_consultation AS
SELECT
    note_id,
    patient_id,
    appointment_id,
    doctor_id,
    DATE(consultation_date) AS consultation_date,
    symptoms,
    assessment,
    notes,
    follow_up_required
FROM consultation_notes
""")

print("✓ fact_consultation created")


# ============================================================
# PATIENT 360 VIEW
# ============================================================

print("\nCreating vw_patient_360...")

cursor.execute("""
CREATE VIEW vw_patient_360 AS

SELECT

    p.patient_id,

    p.first_name,
    p.last_name,

    p.gender,
    p.date_of_birth,
    p.insurance_provider,

    /* ==========================
       APPOINTMENTS
       ========================== */

    COALESCE(a.total_appointments, 0)
        AS total_appointments,

    COALESCE(a.completed_appointments, 0)
        AS completed_appointments,

    COALESCE(a.cancelled_appointments, 0)
        AS cancelled_appointments,

    COALESCE(a.no_show_count, 0)
        AS no_show_count,


    /* ==========================
       TREATMENTS
       ========================== */

    COALESCE(t.total_treatments, 0)
        AS total_treatments,

    COALESCE(t.total_treatment_cost, 0)
        AS total_treatment_cost,


    /* ==========================
       BILLING
       ========================== */

    COALESCE(b.total_billed_amount, 0)
        AS total_billed_amount,

    COALESCE(b.paid_amount, 0)
        AS paid_amount,

    COALESCE(b.pending_amount, 0)
        AS pending_amount,


    /* ==========================
       WAITING TIME
       ========================== */

    COALESCE(v.avg_waiting_minutes, 0)
        AS avg_waiting_minutes,

    COALESCE(v.max_waiting_minutes, 0)
        AS max_waiting_minutes,


    /* ==========================
       LAB RESULTS
       ========================== */

    COALESCE(l.abnormal_lab_count, 0)
        AS abnormal_lab_count,


    /* ==========================
       WEARABLES
       ========================== */

    ROUND(
        COALESCE(w.avg_heart_rate, 0),
        2
    ) AS avg_heart_rate,

    ROUND(
        COALESCE(w.avg_spo2, 0),
        2
    ) AS avg_spo2,

    ROUND(
        COALESCE(w.avg_temperature, 0),
        2
    ) AS avg_temperature,

    ROUND(
        COALESCE(w.avg_steps, 0),
        2
    ) AS avg_steps,

    ROUND(
        COALESCE(w.avg_sleep_hours, 0),
        2
    ) AS avg_sleep_hours,


    /* ==========================
       CONSULTATIONS
       ========================== */

    COALESCE(
        c.follow_up_count,
        0
    ) AS follow_up_count


FROM dim_patient p


/* ==========================
   APPOINTMENT AGGREGATION
   ========================== */

LEFT JOIN (

    SELECT

        patient_id,

        COUNT(*) AS total_appointments,

        SUM(
            CASE
                WHEN status = 'Completed'
                THEN 1
                ELSE 0
            END
        ) AS completed_appointments,

        SUM(
            CASE
                WHEN status = 'Cancelled'
                THEN 1
                ELSE 0
            END
        ) AS cancelled_appointments,

        SUM(
            CASE
                WHEN status = 'No-show'
                THEN 1
                ELSE 0
            END
        ) AS no_show_count

    FROM fact_appointment

    GROUP BY patient_id

) a

ON p.patient_id = a.patient_id


/* ==========================
   TREATMENT AGGREGATION
   ========================== */

LEFT JOIN (

    SELECT

        patient_id,

        COUNT(*) AS total_treatments,

        SUM(cost) AS total_treatment_cost

    FROM fact_treatment

    GROUP BY patient_id

) t

ON p.patient_id = t.patient_id


/* ==========================
   BILLING AGGREGATION
   ========================== */

LEFT JOIN (

    SELECT

        patient_id,

        SUM(amount) AS total_billed_amount,

        SUM(
            CASE
                WHEN payment_status = 'Paid'
                THEN amount
                ELSE 0
            END
        ) AS paid_amount,

        SUM(
            CASE
                WHEN payment_status = 'Pending'
                THEN amount
                ELSE 0
            END
        ) AS pending_amount

    FROM fact_billing

    GROUP BY patient_id

) b

ON p.patient_id = b.patient_id


/* ==========================
   VISIT AGGREGATION
   ========================== */

LEFT JOIN (

    SELECT

        patient_id,

        AVG(waiting_time_minutes)
            AS avg_waiting_minutes,

        MAX(waiting_time_minutes)
            AS max_waiting_minutes

    FROM fact_visit

    GROUP BY patient_id

) v

ON p.patient_id = v.patient_id


/* ==========================
   LAB AGGREGATION
   ========================== */

LEFT JOIN (

    SELECT

        patient_id,

        SUM(
            CASE
                WHEN LOWER(abnormal_flag) = 'true'
                     OR abnormal_flag = '1'
                THEN 1
                ELSE 0
            END
        ) AS abnormal_lab_count

    FROM fact_lab_result

    GROUP BY patient_id

) l

ON p.patient_id = l.patient_id


/* ==========================
   WEARABLE AGGREGATION
   ========================== */

LEFT JOIN (

    SELECT

        patient_id,

        AVG(heart_rate_bpm)
            AS avg_heart_rate,

        AVG(spo2_percent)
            AS avg_spo2,

        AVG(temperature_c)
            AS avg_temperature,

        AVG(steps)
            AS avg_steps,

        AVG(sleep_hours)
            AS avg_sleep_hours

    FROM fact_wearable

    GROUP BY patient_id

) w

ON p.patient_id = w.patient_id


/* ==========================
   CONSULTATION AGGREGATION
   ========================== */

LEFT JOIN (

    SELECT

        patient_id,

        SUM(
            CASE
                WHEN LOWER(follow_up_required) = 'true'
                     OR follow_up_required = '1'
                     OR LOWER(follow_up_required) = 'yes'
                THEN 1
                ELSE 0
            END
        ) AS follow_up_count

    FROM fact_consultation

    GROUP BY patient_id

) c

ON p.patient_id = c.patient_id

""")

print("✓ vw_patient_360 created")


# ============================================================
# HOSPITAL KPI VIEW
# ============================================================

print("Creating vw_hospital_kpis...")

cursor.execute("""
CREATE VIEW vw_hospital_kpis AS

SELECT

    /* PATIENTS */

    (
        SELECT COUNT(*)
        FROM dim_patient
    ) AS total_patients,


    /* DOCTORS */

    (
        SELECT COUNT(*)
        FROM dim_doctor
    ) AS total_doctors,


    /* APPOINTMENTS */

    (
        SELECT COUNT(*)
        FROM fact_appointment
    ) AS total_appointments,


    (
        SELECT COUNT(*)
        FROM fact_appointment
        WHERE status = 'Completed'
    ) AS completed_appointments,


    (
        SELECT COUNT(*)
        FROM fact_appointment
        WHERE status = 'No-show'
    ) AS no_show_appointments,


    (
        SELECT COUNT(*)
        FROM fact_appointment
        WHERE status = 'Cancelled'
    ) AS cancelled_appointments,


    /* NO-SHOW RATE */

    ROUND(

        100.0 *

        (
            SELECT COUNT(*)
            FROM fact_appointment
            WHERE status = 'No-show'
        )

        /

        NULLIF(
            (
                SELECT COUNT(*)
                FROM fact_appointment
            ),
            0
        ),

        2

    ) AS no_show_rate,


    /* TREATMENT REVENUE */

    (
        SELECT COALESCE(SUM(cost), 0)
        FROM fact_treatment
    ) AS total_treatment_revenue,


    /* BILLING */

    (
        SELECT COALESCE(SUM(amount), 0)
        FROM fact_billing
    ) AS total_billed_amount,


    (
        SELECT COALESCE(SUM(amount), 0)
        FROM fact_billing
        WHERE payment_status = 'Paid'
    ) AS total_paid_amount,


    (
        SELECT COALESCE(SUM(amount), 0)
        FROM fact_billing
        WHERE payment_status = 'Pending'
    ) AS total_pending_amount,


    /* WAITING */

    (
        SELECT ROUND(
            AVG(waiting_time_minutes),
            2
        )
        FROM fact_visit
    ) AS average_waiting_minutes,


    (
        SELECT MAX(waiting_time_minutes)
        FROM fact_visit
    ) AS maximum_waiting_minutes,


    /* LAB */

    (
        SELECT COUNT(*)
        FROM fact_lab_result
        WHERE
            LOWER(abnormal_flag) = 'true'
            OR abnormal_flag = '1'
    ) AS abnormal_lab_results

""")

print("✓ vw_hospital_kpis created")


# ============================================================
# INDEXES
# ============================================================

print("\nCreating analytical indexes...")

indexes = [

    """
    CREATE INDEX idx_fact_appointment_patient
    ON fact_appointment(patient_id)
    """,

    """
    CREATE INDEX idx_fact_appointment_doctor
    ON fact_appointment(doctor_id)
    """,

    """
    CREATE INDEX idx_fact_appointment_date
    ON fact_appointment(appointment_date)
    """,

    """
    CREATE INDEX idx_fact_treatment_patient
    ON fact_treatment(patient_id)
    """,

    """
    CREATE INDEX idx_fact_billing_patient
    ON fact_billing(patient_id)
    """,

    """
    CREATE INDEX idx_fact_lab_patient
    ON fact_lab_result(patient_id)
    """,

    """
    CREATE INDEX idx_fact_visit_patient
    ON fact_visit(patient_id)
    """,

    """
    CREATE INDEX idx_fact_wearable_patient
    ON fact_wearable(patient_id)
    """,

    """
    CREATE INDEX idx_fact_consultation_patient
    ON fact_consultation(patient_id)
    """
]

for index_sql in indexes:
    cursor.execute(index_sql)

print("✓ Indexes created")


# ============================================================
# COMMIT
# ============================================================

conn.commit()


# ============================================================
# VERIFICATION
# ============================================================

print("\n" + "=" * 60)
print("ANALYTICAL MODEL VERIFICATION")
print("=" * 60)

tables = [
    "dim_patient",
    "dim_doctor",
    "dim_date",
    "dim_treatment",
    "fact_appointment",
    "fact_treatment",
    "fact_billing",
    "fact_lab_result",
    "fact_visit",
    "fact_wearable",
    "fact_consultation",
]

for table in tables:

    cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    count = cursor.fetchone()[0]

    print(
        f"{table:<25} {count:>6} rows"
    )


print("\nHospital KPIs:")

cursor.execute("""
SELECT
    total_patients,
    total_doctors,
    total_appointments,
    completed_appointments,
    no_show_appointments,
    cancelled_appointments,
    no_show_rate,
    total_treatment_revenue,
    total_billed_amount,
    total_paid_amount,
    total_pending_amount,
    average_waiting_minutes,
    maximum_waiting_minutes,
    abnormal_lab_results
FROM vw_hospital_kpis
""")

kpi = cursor.fetchone()

kpi_names = [
    "Total patients",
    "Total doctors",
    "Total appointments",
    "Completed appointments",
    "No-show appointments",
    "Cancelled appointments",
    "No-show rate %",
    "Treatment revenue",
    "Total billed amount",
    "Total paid amount",
    "Total pending amount",
    "Average waiting minutes",
    "Maximum waiting minutes",
    "Abnormal lab results",
]

for name, value in zip(kpi_names, kpi):

    print(
        f"{name:<30}: {value}"
    )


cursor.execute("""
SELECT COUNT(*)
FROM vw_patient_360
""")

patient_360_count = cursor.fetchone()[0]

print(
    f"\nPatient 360 records       : "
    f"{patient_360_count}"
)


# ============================================================
# CLOSE
# ============================================================

conn.close()

print("\n" + "=" * 60)
print("ANALYTICAL MODEL COMPLETED")
print("=" * 60)