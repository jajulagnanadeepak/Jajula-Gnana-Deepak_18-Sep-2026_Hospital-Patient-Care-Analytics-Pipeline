# Hospital Patient Care Analytics Pipeline

An end-to-end data engineering and analytics project that processes hospital data from multiple sources, cleans and validates the data, stores it in a SQLite data warehouse, builds an analytical star schema, and presents insights through an interactive Streamlit dashboard.

## Project Objective

The goal of this project is to build a simple hospital analytics pipeline that helps understand:

- Patient activity
- Appointment performance
- Doctor workload
- Waiting times
- Treatment revenue
- Payment status
- Patient 360 information

## Architecture

```text
Raw CSV Data
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
Streamlit Dashboard