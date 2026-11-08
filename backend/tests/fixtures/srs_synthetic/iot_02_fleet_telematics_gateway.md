# FleetPulse Commercial Vehicle Telematics & ELD Gateway SRS
Document Identifier: SRS-IOT_02_FLEET_TELEMATICS_GATEWAY
Domain: Embedded / IoT / Systems
Target Classification: API/Backend
Status: Final Approved Specification

## 1. Project Overview & Scope
Project Name: FleetPulse Commercial Vehicle Telematics & ELD Gateway
This document formally specifies the software requirements for FleetPulse Commercial Vehicle Telematics & ELD Gateway.
The application is designed as a production-grade api/backend serving the embedded / iot / systems domain.
The system provides reliable capabilities, seamless workflows, and resilient architecture.

## 2. Technical Stack & Infrastructure
The target implementation utilizes the following technical components:
- Core Technologies: Go, Python, PostgreSQL, Redis, Kafka, Docker
- Architecture Paradigm: Cloud-native modular components
- Deployment Model: Modern runtime environment

## 3. Functional Requirements
The system shall deliver the following verified functional capabilities:
FR-01 CAN-Bus Engine Diagnostic Reader: Decodes real-time engine RPM, coolant temperature, fuel consumption rate, and odometer readings.
FR-02 Certified Electronic Logging Device: Logs driver Hours of Service (HOS) automatically based on vehicle motion detection.
FR-03 GPS & Heading Position Logging: Captures vehicle GPS coordinates and heading at 1 Hz with dead-reckoning during tunnel loss.
FR-04 Harsh Driving Event Detection: Utilizes 3-axis accelerometer to detect severe braking, rapid acceleration, and cornering maneuvers.
FR-05 Automated Diagnostic Trouble Code Clearninghouse: Captures check engine fault codes, cross-references severity, and alerts fleet mechanics.
FR-06 Geofence Boundary Entry Alarms: Evaluates polygon geofences at edge to detect vehicle arrivals at customer depots and unauthorized detours.
FR-07 Remote Vehicle Cargo Lock Control: Enables authorized dispatchers to issue secure commands locking cargo doors or preventing restarts.
FR-08 Cellular Store-and-Forward Buffer: Buffers telematics records in persistent flash memory during cellular dead zones, syncing upon reconnect.
FR-09 Driver Identification via NFC Badge: Authenticates commercial drivers before enabling ignition via NFC card reader.
FR-10 Fuel Theft & Tank Level Drop Detection: Monitors fuel float sensor readings while parked to detect unauthorized diesel fuel siphoning.
FR-11 Tire Pressure Monitoring System Integration: Receives wireless TPMS sensor broadcasts, warning drivers of impending tire blowouts.
FR-12 Driver Safety Scorecard & Metrics: Calculates composite safety scores per driver based on speeding infractions and seatbelt compliance.
FR-13 Over-the-Air Telematics Unit Configuration: Permits remote updating of telemetry sampling rates and CAN-bus PID filters over cellular.
FR-14 Emergency Crash Notification Dispatch: Detects high-G collision impacts and transmits vehicle location and impact severity to emergency responders.

## 4. External Integrations
The application connects to the following external third-party services:
1. **Mapbox**: External system interface integration.
2. **AWS S3**: External system interface integration.
3. **Twilio**: External system interface integration.
4. **SendGrid**: External system interface integration.

## 5. Quality Attributes & Security Constraints
- Ruggedized automotive telematics gateway installed in 80,000 heavy commercial trucks nationwide.
- FMCSA 49 CFR Part 395 regulatory compliance with tamper-evident cryptographic event signing.
- Harsh environment operational resilience with automotive grade temperature tolerances.
- Overall System Complexity: Evaluated as high complexity based on operational requirements.

## 6. Staffing Model, Delivery Methodology & Timeline
- Delivery Methodology: Agile software delivery lifecycle with iterative milestones.
- Staffing Model: Cross-functional team of 7 full-time engineers and technical leads.
- Target Timeline: Estimated project duration of 6.0 months from kickoff to delivery.
