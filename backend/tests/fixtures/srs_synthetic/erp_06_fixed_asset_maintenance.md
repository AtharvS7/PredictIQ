# AssetGuard Simple Equipment Registry MVP SRS
Document Identifier: SRS-ERP_06_FIXED_ASSET_MAINTENANCE
Domain: Enterprise / ERP Systems
Target Classification: Enterprise Software
Status: Final Approved Specification

## 1. Project Overview & Scope
Project Name: AssetGuard Simple Equipment Registry MVP
This document formally specifies the software requirements for AssetGuard Simple Equipment Registry MVP.
The application is designed as a production-grade enterprise software serving the enterprise / erp systems domain.
The system provides reliable capabilities, seamless workflows, and resilient architecture.

## 2. Technical Stack & Infrastructure
The target implementation utilizes the following technical components:
- Core Technologies: Python, Flask, SQLite, HTML
- Architecture Paradigm: Cloud-native modular components
- Deployment Model: Modern runtime environment

## 3. Functional Requirements
The system shall deliver the following verified functional capabilities:
FR-01 Fixed Asset Registry Form: Permits workshop managers to record tool serial numbers, purchase date, and cost.
FR-02 Asset Category & Location Assignment: Assigns machinery to workshop bays and categorizes by equipment type.
FR-03 Scheduled Maintenance Reminder: Flags equipment due for oil changes or safety checks based on calendar months.
FR-04 Equipment Status Toggle: Updates asset status between active, undergoing repair, and decommissioned.
FR-05 Maintenance Log Entry Form: Allows technicians to write simple notes on repairs completed and date serviced.
FR-06 Export Equipment List to CSV: Downloads a spreadsheet list of active shop assets and warranty expiration dates.

## 4. External Integrations
The application connects to the following external third-party services:
1. **SendGrid**: External system interface integration.

## 5. Quality Attributes & Security Constraints
- Straightforward proof of concept and simple prototype for small factory equipment tracking.
- Minimal MVP application running on a local desktop server.
- Small user base with lightweight local SQLite database storage.
- Overall System Complexity: Evaluated as low complexity based on operational requirements.

## 6. Staffing Model, Delivery Methodology & Timeline
- Delivery Methodology: Agile software delivery lifecycle with iterative milestones.
- Staffing Model: Cross-functional team of 2 full-time engineers and technical leads.
- Target Timeline: Estimated project duration of 2.0 months from kickoff to delivery.
