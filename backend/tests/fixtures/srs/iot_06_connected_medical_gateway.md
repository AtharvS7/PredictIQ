# VitalLink Patient Vital Monitor Gateway SRS
Document Identifier: SRS-IOT_06_CONNECTED_MEDICAL_GATEWAY
Domain: Embedded / IoT / Systems
Target Classification: API/Backend
Status: Final Approved Specification

## 1. Project Overview & Scope
Project Name: VitalLink Patient Vital Monitor Gateway
This document formally specifies the software requirements for VitalLink Patient Vital Monitor Gateway.
The application is designed as a production-grade api/backend serving the embedded / iot / systems domain.
The system provides reliable capabilities, seamless workflows, and resilient architecture.

## 2. Technical Stack & Infrastructure
The target implementation utilizes the following technical components:
- Core Technologies: C++, Python, SQLite
- Architecture Paradigm: Cloud-native modular components
- Deployment Model: Modern runtime environment

## 3. Functional Requirements
The system shall deliver the following verified functional capabilities:
FR-01 Patient Vital Stream Ingestion: Ingests continuous 500 Hz ECG, SpO2, and respiratory rate from bedside medical monitors.
FR-02 Arrhythmia Detection & Warning Alert: Executes edge detection for irregular heartbeat patterns and extreme tachycardia.
FR-03 Nurse Station Visual Alarm Annunciator: Triggers visual bedside flashing alarms and sends wireless pager notifications to nurses.
FR-04 Clinical Observations Record Formatter: Translates raw sensor streams into standard clinical observations for hospital medical records.
FR-05 Bedside Medical Sensor Hub Pairing: Aggregates telemetry from wireless pulse oximeters and patient monitoring cuffs.
FR-06 Local Patient Data Buffering Loop: Persists continuous multi-waveform clinical data on local encrypted SSD during IT outages.
FR-07 Pseudonymized Clinical Research Telemetry: Strips patient medical record numbers from waveforms, transmitting pseudonymized streams for research.
FR-08 Medical Sensor Lead-Off Detector: Monitors ECG electrode impedance and alerts care staff immediately when a chest lead detaches.
FR-09 Encrypted Hospital Cloud Telemetry Backup: Streams encrypted vital telemetry to secure healthcare storage for post-discharge review.

## 4. External Integrations
The application connects to the following external third-party services:
1. **AWS S3**: External system interface integration.
2. **SendGrid**: External system interface integration.
3. **Auth0**: External system interface integration.

## 5. Quality Attributes & Security Constraints
- Medium complexity bedside patient monitoring gateway deployed in clinical ward rooms.
- HIPAA compliance with encrypted patient data storage and strict access controls.
- Continuous real-time sensor processing with local battery backup failover.
- Overall System Complexity: Evaluated as medium complexity based on operational requirements.

## 6. Staffing Model, Delivery Methodology & Timeline
- Delivery Methodology: Agile software delivery lifecycle with iterative milestones.
- Staffing Model: Cross-functional team of 5 full-time engineers and technical leads.
- Target Timeline: Estimated project duration of 4.5 months from kickoff to delivery.
