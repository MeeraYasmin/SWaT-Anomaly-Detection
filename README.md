# Invariant Extraction from HMI Diagrams for Anomaly Detection in Cyber-Physical Systems

## Overview
This project presents an automated framework for anomaly detection in cyber-physical water treatment systems using Human-Machine Interface (HMI) diagrams.

Traditional invariant-based anomaly detection relies heavily on manual engineering effort and detailed system knowledge. This work automates the process by leveraging Large Language Vision Models (LLVLMs) to extract system dependencies and generate physical invariants directly from HMI images.

The approach is evaluated on the Secure Water Treatment (SWaT) testbed.

---

## Key Contributions
- Automated component and dependency extraction from HMI diagrams
- Graph-based representation of system structure
- Template-driven invariant generation
- Observability-aware filtering of dependencies
- Evaluation using real-world SWaT datasets
- Achieved very low false positive rates (≤ 0.02%)

---

## Pipeline

### 1. Dependency Extraction
- HMI images are processed using vision-language models
- Components and relationships are extracted

### 2. Observability Filtering
- Removes non-measurable or inactive components

### 3. Graph Construction
- Directed graph representation of system

### 4. Invariant Generation
- Template-based logical conditions

### 5. Evaluation
- Metrics: False Positive Rate, Window Size

---

## Results
- Maximum false positive rate: 0.02%
- Robust across datasets

---

## Tech Stack
- Python
- NetworkX
- Pandas / NumPy
- Vision-Language Models

---

## How to Run
pip install -r requirements.txt
python main.py

---

## Author
Meera Yasmin
