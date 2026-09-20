import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


# ==========================================
# PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "hospital_analytics.db"
)


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Hospital Analytics",
    page_icon="🏥",
    layout="wide"
)


# ==========================================
# DATABASE
# ==========================================

conn = sqlite3.connect(DB_PATH)


# ==========================================
# TITLE
# ==========================================

st.title("🏥 Hospital Patient Care Analytics")

st.write(
    "Data engineering and analytics dashboard "
    "for hospital operations, patients and finance."
)


# ==========================================
# HOSPITAL KPIs
# ==========================================

kpi = pd.read_sql_query(
    """
    SELECT *
    FROM vw_hospital_kpis
    """,
    conn
).iloc[0]


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Patients",
    int(kpi["total_patients"])
)

col2.metric(
    "Appointments",
    int(kpi["total_appointments"])
)

col3.metric(
    "No-show Rate",
    f'{kpi["no_show_rate"]}%'
)

col4.metric(
    "Avg Waiting",
    f'{kpi["average_waiting_minutes"]} min'
)


st.divider()


# ==========================================
# SECOND KPI ROW
# ==========================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Completed",
    int(kpi["completed_appointments"])
)

col2.metric(
    "Cancelled",
    int(kpi["cancelled_appointments"])
)

col3.metric(
    "Treatment Revenue",
    f'₹{kpi["total_treatment_revenue"]:,.2f}'
)

col4.metric(
    "Pending Payments",
    f'₹{kpi["total_pending_amount"]:,.2f}'
)


st.divider()


# ==========================================
# APPOINTMENT STATUS
# ==========================================

st.subheader("Appointment Status")

appointments = pd.read_sql_query(
    """
    SELECT
        status,
        appointment_count
    FROM (
        SELECT
            status,
            COUNT(*) AS appointment_count
        FROM fact_appointment
        GROUP BY status
    )
    """,
    conn
)

fig = px.pie(
    appointments,
    names="status",
    values="appointment_count",
    title="Appointment Status"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# DOCTOR APPOINTMENTS
# ==========================================

st.subheader("Appointments by Doctor")

doctor_data = pd.read_sql_query(
    """
    SELECT
        d.first_name || ' ' || d.last_name
            AS doctor_name,
        COUNT(a.appointment_id)
            AS total_appointments
    FROM fact_appointment a
    JOIN dim_doctor d
        ON a.doctor_id = d.doctor_id
    GROUP BY
        d.doctor_id,
        doctor_name
    ORDER BY total_appointments DESC
    """,
    conn
)

fig = px.bar(
    doctor_data,
    x="doctor_name",
    y="total_appointments",
    title="Appointments by Doctor"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# TREATMENT REVENUE
# ==========================================

st.subheader("Revenue by Treatment")

revenue = pd.read_sql_query(
    """
    SELECT
        treatment_type,
        ROUND(SUM(cost), 2)
            AS total_revenue
    FROM fact_treatment
    GROUP BY treatment_type
    ORDER BY total_revenue DESC
    """,
    conn
)

fig = px.bar(
    revenue,
    x="treatment_type",
    y="total_revenue",
    title="Treatment Revenue"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# PAYMENT STATUS
# ==========================================

st.subheader("Payment Status")

payments = pd.read_sql_query(
    """
    SELECT
        payment_status,
        ROUND(SUM(amount), 2)
            AS total_amount
    FROM fact_billing
    GROUP BY payment_status
    """,
    conn
)

fig = px.bar(
    payments,
    x="payment_status",
    y="total_amount",
    title="Billing by Payment Status"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# WAITING TIME BY DOCTOR
# ==========================================

st.subheader("Average Waiting Time")

waiting = pd.read_sql_query(
    """
    SELECT
        d.first_name || ' ' || d.last_name
            AS doctor_name,
        ROUND(
            AVG(v.waiting_time_minutes),
            2
        ) AS average_waiting_minutes
    FROM fact_visit v
    JOIN fact_appointment a
        ON v.appointment_id = a.appointment_id
    JOIN dim_doctor d
        ON a.doctor_id = d.doctor_id
    GROUP BY
        d.doctor_id,
        doctor_name
    ORDER BY average_waiting_minutes DESC
    """,
    conn
)

fig = px.bar(
    waiting,
    x="doctor_name",
    y="average_waiting_minutes",
    title="Average Waiting Time by Doctor"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# PATIENT 360
# ==========================================

st.subheader("Patient 360")

patients = pd.read_sql_query(
    """
    SELECT
        patient_id,
        first_name || ' ' || last_name
            AS patient_name,
        total_appointments,
        completed_appointments,
        no_show_count,
        total_treatments,
        total_billed_amount,
        pending_amount,
        avg_waiting_minutes,
        follow_up_count
    FROM vw_patient_360
    ORDER BY total_appointments DESC
    """,
    conn
)

st.dataframe(
    patients,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption("🏥 Hospital Patient Care Analytics | Jajula Gnana Deepak")


conn.close()