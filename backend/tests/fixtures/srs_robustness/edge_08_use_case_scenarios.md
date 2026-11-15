# System Use Case Specifications
## System: Core Banking Multi-Currency Settlement Engine

### Use Case: UC-01 International Wire Transfer
- **Primary Actor**: Retail Customer
- **Preconditions**: Customer account holds sufficient funds and KYC verification is active.
- **Main Flow**:
  1. Customer selects beneficiary, currency, and transfer amount.
  2. System queries live exchange rate from foreign exchange feed.
  3. System performs sanctions screening against OFAC watchlist.
  4. System debits origin account and routes message to SWIFT gateway.
  5. System generates transaction reference code and notifies customer via SMS.

### Use Case: UC-02 Automated Liquidity Sweep
- **Primary Actor**: Treasury Automated Service
- **Preconditions**: End-of-day cutoff time reached.
- **Main Flow**:
  1. System queries balances across all subsidiary operating accounts.
  2. System compares balances to target zero-balance threshold.
  3. System initiates concentration sweeps to master treasury account.
  4. System records intercompany loan ledgers and calculates daily interest.

### Use Case: UC-03 Merchant QR Point of Sale Settlement
- **Primary Actor**: Merchant POS Terminal
- **Preconditions**: Customer scans terminal dynamic QR code.
- **Main Flow**:
  1. POS sends tokenized payment payload to settlement gateway.
  2. Gateway authenticates merchant identity and signs authorization request.
  3. Core ledger executes sub-second debit-credit split.
  4. POS displays payment confirmed checkmark to cashier.

### Use Case: UC-04 Chargeback Dispute Adjudication
- **Primary Actor**: Dispute Resolution Officer
- **Preconditions**: Cardholder submits chargeback affidavit.
- **Main Flow**:
  1. Officer reviews transaction history, IP logs, and courier proof of delivery.
  2. Officer requests supporting documentation from acquiring merchant.
  3. System tracks 30-day regulatory arbitration window.
  4. System disburses provisional credit upon favorable ruling.
