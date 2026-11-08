Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Enterprise Readiness & Security Compliance Gaps

This document provides a transparent and objective evaluation of PredictIQ's current enterprise security posture, identifying implemented capabilities alongside known compliance gaps and technical roadmap priorities.

---

## 1. Compliance & Security Posture Overview

| Capability Domain | Implemented Baseline (v2.0.0-rc.3) | Enterprise Target | Status / Gap |
|-------------------|-----------------------------------|-------------------|--------------|
| **Data Encryption** | TLS 1.3 in transit; AES-256 at rest (Neon PostgreSQL & AWS S3). | Customer-Managed Encryption Keys (CMEK / AWS KMS). | **Partial Gap**: Provider-managed encryption active; CMEK not yet supported. |
| **Authentication** | Firebase Identity Platform (Email/Password, Google OAuth). | Enterprise SAML 2.0 / WS-Fed (Okta, Azure AD) + SCIM. | **Gap**: Enterprise SSO requires upgrading to Firebase Identity Platform Enterprise tier. |
| **Access Control (RBAC)**| 3-tier hierarchical RBAC (`admin`, `editor`, `viewer`) with database override. | Custom role builder, fine-grained attribute-based access control (ABAC). | **Met Baseline**: Standard 3-tier model satisfies core operational needs. |
| **Audit Logging** | `AuditLogMiddleware` captures all mutating requests, user IDs, IPs, and Request IDs. | Real-time SIEM streaming (Splunk, Datadog) with tamper-evident log hashing. | **Partial Gap**: Emits structured JSON to stdout; requires external log forwarder. |
| **Model Security** | Fail-closed SHA-256 verification, zero-pickle pure JSON deserialization. | Continuous adversarial model drift and poisoning monitoring. | **Met Baseline**: Zero-pickle architecture eliminates critical RCE threat vectors. |
| **Tenant Isolation** | Logical row-level tenant isolation enforced via parameterized SQL. | Physical database separation or dedicated schemas per enterprise tenant. | **Gap**: Shared multi-tenant database cluster with logical isolation. |
| **Third-Party Audits** | Automated release gates (lint, static typing, unit tests, secret scanning). | Independent SOC 2 Type II and ISO/IEC 27001 certifications. | **Gap**: Formal external audit observation window is currently pending. |

---

## 2. Detailed Gap Analysis & Technical Roadmap

### 1. SOC 2 Type II Attestation Status
- **Current State**: PredictIQ has engineered the technical controls mandated by the AICPA Trust Services Criteria for Security and Confidentiality:
  - Automated CI/CD release gates (`scripts/release_gate.py`) preventing untested code deployments.
  - Secret scanning eliminating credentials from Git history.
  - Fail-closed cryptographic integrity checks for machine learning artifacts.
  - Role-based access control and immutable request audit logs.
- **Identified Gap**: A formal SOC 2 Type II examination requires an independent audit by an accredited CPA firm over a minimum 6-month observation window. The formal observation window has not yet concluded.
- **Roadmap**: Engagement with an external auditor is scheduled following the general availability release.

---

### 2. Enterprise Single Sign-On (SSO) & SCIM Directory Sync
- **Current State**: Authentication relies on standard Firebase Authentication, supporting email/password and Google OIDC providers.
- **Identified Gap**:
  - Direct integration with enterprise identity providers (IdPs) via SAML 2.0 (e.g. Okta, Microsoft Entra ID / Azure AD, PingFederate) is not yet enabled.
  - Automated user lifecycle provisioning and deprovisioning via SCIM 2.0 is not implemented.
- **Roadmap**: Migration to Firebase Identity Platform Enterprise tier or Okta/Auth0 integration is slated for Q1 2027 to provide self-service SAML/OIDC configuration and SCIM sync.

---

### 3. SIEM & Centralized Log Export
- **Current State**: Application events and audit records are formatted using `structlog` and emitted as JSON lines to `stdout` and `stderr`.
- **Identified Gap**: The application does not natively stream events to enterprise Security Information and Event Management (SIEM) systems (e.g., Splunk HEC, Datadog, Sumo Logic, AWS OpenSearch) via application-level protocols.
- **Workaround & Roadmap**: In production environments, log streaming must be handled at the container/infrastructure layer using AWS CloudWatch Logs subscription filters, Datadog Agent, or FluentBit sidecars. Native syslog/webhook streaming will be added in a future release.

---

### 4. Tenant Isolation & Data Residency
- **Current State**: Tenants share common Neon PostgreSQL database clusters and AWS S3 buckets. Multi-tenancy is enforced logically by application-level authorization and parameterized SQL filters (`WHERE user_id = $2`).
- **Identified Gap**:
  - High-compliance customers requiring physical database isolation (database-per-tenant or dedicated PostgreSQL schemas) cannot be accommodated in the multi-tenant SaaS deployment.
  - Customer-Managed Encryption Keys (CMEK) via AWS KMS or HashiCorp Vault are not currently supported.
- **Roadmap**: An enterprise single-tenant VPC deployment package (AWS CloudFormation / Terraform) is under development for regulated customers.

---

### 5. Regulatory & Industry Certifications
- **Current State**: Self-attested compliance with GDPR and CCPA requirements for data access, portability, and erasure.
- **Identified Gap**:
  - **HIPAA**: PredictIQ is not currently certified for processing Protected Health Information (PHI) and does not execute Business Associate Agreements (BAAs).
  - **PCI-DSS**: Out of scope, as PredictIQ does not process, store, or transmit payment card data (all billing is handled via third-party processors).
  - **FedRAMP**: Not certified for US Federal government deployments.
