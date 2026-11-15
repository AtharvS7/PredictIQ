# Functional Requirements Matrix
## Platform: Smart Hospital Patient Monitoring System

| Requirement ID | Module | Description | Priority | Integration Point |
| :--- | :--- | :--- | :--- | :--- |
| REQ-MON-01 | Telemetry | Ingest continuous pulse oximetry and ECG streaming data at 100 Hz | High | MQTT / Kafka |
| REQ-MON-02 | Alerting | Trigger audible nursing station alarm when heart rate exceeds 140 bpm | Critical | Twilio / WebSockets |
| REQ-MON-03 | Patient Record | Automatically write triage vital sign summaries to HL7 FHIR EHR | High | Epic FHIR API |
| REQ-MON-04 | Bedside Display | Render waveform graph on bedside tablet monitor with <50ms latency | Medium | React Native |
| REQ-MON-05 | Pharmacy Sync | Cross-reference patient telemetry trends with scheduled IV medications | High | Cerner API |
| REQ-MON-06 | Discharge Summary| Generate automated PDF discharge report upon doctor sign-off | Medium | AWS S3 |
| REQ-MON-07 | Access Control | Enforce biometric and NFC badge access for ICU monitor configuration | Critical | Keycloak OAuth2 |
| REQ-MON-08 | Compliance | Encrypt stored telemetry data at rest using AES-256 GCM | High | Vault |
