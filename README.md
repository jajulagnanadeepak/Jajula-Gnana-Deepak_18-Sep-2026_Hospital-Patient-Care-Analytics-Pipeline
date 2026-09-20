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

## Data Engineering Architecture

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
