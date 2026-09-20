# 🏥 Hospital Patient Care Analytics Pipeline

## 🚀 Live Dashboard
🔗 **[Open Hospital Patient Care Analytics Dashboard](https://jajula-gnana-deepak18-sep-2026hospital-patient-care-analytics.streamlit.app)**
The application is deployed using Streamlit Community Cloud and provides interactive hospital operational and patient analytics.

An end-to-end **Data Engineering and Analytics project** that transforms raw hospital data from multiple operational sources into a centralized analytical data warehouse and an interactive dashboard.

The project demonstrates the complete journey of hospital data:

**Raw Data → Data Quality → Transformation → Data Warehouse → Analytics → Patient 360 → Dashboard**

The pipeline provides insights into patient activity, appointments, doctor workload, waiting times, treatments, billing, payments, and patient follow-up requirements.

---

## 🎯 Project Objective

The objective of this project is to build a reliable and structured hospital analytics pipeline that converts raw operational data into **clean, validated, analysis-ready information**.

The system is designed to answer practical hospital operational questions such as:

- How many patients and appointments are being handled?
- What is the appointment completion, cancellation, and no-show pattern?
- Which doctors handle the highest appointment volumes?
- Which doctors have higher patient waiting times?
- Which treatments generate the most revenue?
- What is the current payment status?
- Which patients require follow-up?
- Can information from different hospital systems be combined into a Patient 360 view?

---

# 🏗️ Data Engineering Architecture

```text
                    Hospital Operational Sources
                              │
                              ▼
                     ┌─────────────────┐
                     │   Raw CSV Data  │
                     └────────┬────────┘
                              │
                              ▼
                     Data Profiling
                              │
                              ▼
                 Data Cleaning & Validation
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
             Valid Records        Invalid Records
                    │                   │
                    ▼                   ▼
             Processed Layer       Quarantine
                    │
                    ▼
             SQLite Data Warehouse
                    │
                    ▼
              Dimensional Model
              / Star Schema
                    │
                    ▼
               SQL Analytics
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      Hospital KPIs       Patient 360
          │                   │
          └─────────┬─────────┘
                    ▼
          Streamlit Dashboard
