# Agile User Stories and Acceptance Criteria
## Project: Velocity Fleet Dispatch

### Epic 1: Driver Shift Management
- **US-01**: As a driver, I want to clock in at the start of my shift so that my hours and availability are accurately recorded.
  - Given the driver is authenticated and within 50 meters of depot
  - When the driver taps "Start Shift"
  - Then the system updates driver state to Available and logs GPS coordinates

- **US-02**: As a driver, I want to receive real-time dispatch alerts so that I can accept high-priority delivery routes.
  - Given a driver is marked Available
  - When a dispatcher assigns Route #402
  - Then an audible push notification is sent to the driver's device within 3 seconds

### Epic 2: Route Optimization & Navigation
- **US-03**: As a fleet manager, I want to calculate dynamic shortest delivery paths so that fuel consumption is minimized.
  - Given 20 delivery destinations with delivery time windows
  - When the route optimizer runs
  - Then delivery orders are sequenced with lowest total mileage using Google Maps integration

- **US-04**: As a customer, I want to track the courier on a live map so that I know when my package will arrive.
  - Given a package is in transit
  - When the customer opens the tracking link
  - Then vehicle location updates every 5 seconds via WebSockets

### Epic 3: Proof of Delivery & Payments
- **US-05**: As a courier, I want to capture digital signatures and photos of delivered goods so that dispute rates are reduced.
- **US-06**: As an accounting officer, I want to charge customer payment cards automatically upon successful delivery confirmation.
  - Given delivery confirmation is signed
  - When courier marks status Delivered
  - Then Stripe charges the pre-authorized amount and sends a receipt via SendGrid
