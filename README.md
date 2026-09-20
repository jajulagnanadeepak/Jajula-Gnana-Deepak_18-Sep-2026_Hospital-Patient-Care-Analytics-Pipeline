# Hospital Patient Care Analytics Pipeline

An end-to-end data engineering project that transforms raw hospital data from multiple operational sources into a centralized analytical data warehouse and interactive dashboard.

The pipeline performs data ingestion, profiling, cleaning, validation, transformation, dimensional modeling, SQL analytics, and visualization to provide insights into patient activity, appointments, hospital operations, treatments, waiting times, and billing.

## Project Objective

The objective is to build a reliable hospital analytics pipeline that converts raw operational data into structured, analysis-ready information.

The system provides insights into:

- Patient activity and Patient 360
- Appointment status and no-show patterns
- Doctor workload
- Patient waiting times
- Treatment and revenue analysis
- Billing and payment status
- Patient follow-up information

## Key Insights

The analytical layer produced the following insights from the hospital data:

### Appointment Insights

- The dataset contains **200 appointments**.
- **46 appointments were completed**, while **52 were marked as no-shows** and **51 were cancelled**.
- The overall no-show rate is **26%**.

### Doctor & Operations Insights

- **Sarah Taylor** has the highest number of appointments with **29 appointments**.
- **David Jones** has the highest average waiting time at **67 minutes**.
- The overall average patient waiting time is **41.02 minutes**.

### Treatment Insights

- **Chemotherapy** generated the highest treatment revenue at approximately **₹128,855.68**.
- MRI generated approximately **₹116,098.16**.
- X-Ray generated approximately **₹110,653.67**.

### Billing Insights

- Total treatment revenue is **₹551,249.85**.
- **₹173,424.90** is recorded as paid.
- **₹184,612.01** is recorded as pending.
- **₹193,212.94** is recorded under failed payments.

### Patient Insights

- The Patient 360 view contains records for all **50 patients**.
- Patient 360 combines appointment, treatment, billing, waiting-time, laboratory, wearable, and follow-up information.
- **14 patients** currently have a follow-up requirement recorded in the consultation data.

### Data Quality Insight

- The pipeline successfully performed validation and separated invalid records into the quarantine layer.
- The current analytical dataset contains **0 abnormal laboratory results** according to the `abnormal_flag` field. This is a characteristic of the current dataset and is not interpreted as a clinical conclusion.

- ## Business Value

The pipeline demonstrates how hospital operational data can be transformed into actionable analytical information.

It enables stakeholders to monitor:

- Appointment utilization
- No-show patterns
- Doctor workload
- Patient waiting times
- Treatment revenue
- Payment status
- Patient-level activity

Instead of analyzing separate CSV files manually, the data is integrated into a centralized warehouse and presented through an interactive dashboard.

## Data Engineering Architecture

```text
Multiple Hospital Data Sources
            ↓
       Data Ingestion
            ↓
      Data Profiling
            ↓
 Data Cleaning & Validation
            ↓
      Processed Data
            ↓
    SQLite Data Warehouse
            ↓
      Star Schema
            ↓
       SQL Analytics
            ↓
   Patient 360 & KPIs
            ↓
   Streamlit Dashboard
