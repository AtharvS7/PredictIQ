# Gamma J Radiation Therapy Treatment Planning System Software Requirements

> **Dataset:** PURE Dataset (Zenodo 7118517 / IEEE RE 2017)
> **Original Document Title:** Gamma J Radiation Therapy Treatment Planning System Software Requirements
> **Domain:** Radiation Therapy Planning
> **License:** Open Access (Medical Physics)
> **Source/Project:** https://medicalphysics.org
> **Version:** 0.0

---

## 1 Introduction

### 1.1 Purpose

This is the Software Requirements Specification for GAMMA-J’s Web Store. This Web Store is designed to allow new online store owners a quick and easy means to setup and perform sales and other core business over the internet. This document will outline all of the functions, capabilities and requirements for Version 1 of GAMMA-J’s Web Store. Version 1 is planned for implementation on a “plug and play” USB Key. Future versions will be based on other network appliances.

### 1.2 Document Conventions

None

### 1.3 Intended Audience, Reading Suggestions

This document is intended to flush out the requirements by the customer GAMMA-J. The customer can review this document to ensure their needs along with the needs of their user’s are being met in their new Web Store program. The development team will also use this document for guidance on overall design and implementation of the Web Store system. The test and verification team can reference this to ensure the requirements are being meet for the customer. Finally, the tech writer will use this to assist with user documentation. This document is designed to be review from beginning to end; however, readers who are new to technical documentation may want to refer to Appendix E: Data Dictionary first.

### 1.4 Project Scope

According to GAMMA-J’s Functional Needs Statement this Web Store will:

### 1.5 References

This document draws insight from the Web Store System Overview, Functional Needs Statement, and Stakeholder Goals List.

## 2 Overall Description

### 2.1 Product Perspective

Web Store is a new system designed for users new to the online E-commerce. This will be a plug and play device with its own CPU and operating system. The Web Store will be a quick and easy means to setup and operate an online Web Store. The Figure 2.1 is a context diagram showing external system interfaces.

### 2.2 Product Features

### 2.3 User Classes

### 2.4 Operating Environment

### 2.5 Design and Implementation Constraints

### 2.6 User Documentation

### 2.7 Assumptions and Dependencies

## 3 System Features

### 3.1 Customer Accounts

#### 3.1.1 Description And Priority

Customers will be able to create accounts to store their profiles, contact information, purchase history, and confirm orders. This is a high priority system feature. Security methods will ensure that customer accounts remain confidential and resistant to tampering.

#### 3.1.2 Stimulus/Response Sequences

#### 3.1.3 Functional Requirements

Customers will be able to create accounts to store their customer profiles, configure contact information, view their purchase history, and confirm orders. Customers will be able to register, log in, and log out of their accounts. Furthermore, Customer profiles will also include payment information, such as the ability to store credit card information, and address information.

### 3.2 Inventory Management

#### 3.2.1 Description And Priority

Inventory management will allow for the placement of products into multi-tiered categories. This is a medium priority system feature.

#### 3.2.2 Stimulus/Response Sequences

Same as

#### 3.2.3 Functional Requirements

Products will be stored in multi-tiered categories; a category can contain sub categories or products. The inventory management will allow for administrators to update the categories, the products placed in categories, and the specific product details.

### 3.3 Shopping Cart

#### 3.3.1 Description And Priority

Customers will be able to add and store products for purchase within the shopping cart. This feature is a medium priority system feature.

#### 3.3.2 Stimulus/Response Sequences

Same as

#### 3.3.3 Functional Requirements

Customers will also be able to add products into the shopping cart. The shopping cart will clearly display the number of items in the cart, along with the total cost. The customer will also be able to add to or remove products from the shopping cart prior to checkout and order confirmation.

### 3.4 Order Confirmation

#### 3.4.1 Description And Priority

Order confirmation will allow the customer to review their order after checkout prior to confirmation. This is a medium priority system feature.

#### 3.4.2 Stimulus/Response Sequences

Same as

#### 3.4.3 Functional Requirements

Customers will be able to confirm the order after checkout. If the order is incorrect, the customer will be able to revise and update their order. The customer will then receive a confirmation email with the specific order details.

### 3.5 Interface

#### 3.5.1 Description And Priority

The interface will be presented to the customer in a web browser. The interface must remain consistent among various web browsers and be intuitive to the customer. This is a medium priority system feature.

#### 3.5.2 Stimulus/Response Sequences

Same as

#### 3.5.3 Functional Requirements

Customers will be presented with an unambiguous interface to assist in browsing the categories and products. Customers will be able to search for products matching their search criteria. The interface will be compatible with all major web browsers such as Internet Explorer, Mozilla Navigator, Mozilla Firefox, Opera, and Safari.

### 3.6 Interface

#### 3.6.1 Description And Priority

The system will feature an API to allow customers to build custom plug-ins to be able to meet their needs. This is a high priority system feature as it ensures the flexibility of the system to be tailored to specific needs.

#### 3.6.2 Stimulus/Response Sequences

#### 3.6.3 Functional Requirements

The system will implement an Application Interface to allow for various plug-ins to interact with the system. The plug-in API will be well documented and specifications will be provided to plug-in developers.

## 4 External Interface Requirements

### 4.1 User Interfaces

FIGURES

### 4.2 Hardware Interfaces

### 4.3 Software Interfaces

#### SI-1: WebOrder Browser Interface

### 4.4 Communications Interfaces

## 5 Quality Attribute Requirements


### 5.2 Safety Requirements

### 5.3 Security Requirements

### 5.4 Availability Requirements

### 5.5 Efficiency Requirements

### 5.6 Usability Requirements

#### 5.7 Maintainability Requirements

#### 5.8 Portability Requirements

#### 5.9 Testability Requirements

## 6 Other Requirements

## Glossary

## Appendix B: Use Cases

### Customer Use Cases

#### Register Customer

##### Goal

Register a new customer account with the system.

##### Actors:

##### Preconditions:

Customer must be able to access the web order system via a web browser with HTTPS.

##### Triggers:

Customer clicks button or link to "Register"

##### Basic Scenario:

##### Alternative Scenario:

##### Postconditions:

The Customer registers and creates a new customer account with the system.

#### Login Customer

##### Goal

Login to a customer account with the system.

##### Actors:

##### Preconditions:

Customer account must already be registered.

##### Triggers:

Customer clicks button or link to "Login"

##### Basic Scenario:

##### Alternative Scenario:

##### Postconditions:

The Customer is logged into the system.

#### Edit Customer Details

##### Goal

Edit the customer account details.

##### Actors:

##### Preconditions:

Customer must be logged-in on the system.

##### Triggers:

Customer clicks on the button or link to "Edit Account"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

The Customer has changed the account details.

#### Logout Customer

##### Goal

Logout the customer account on the system.

##### Actors:

##### Preconditions:

Customer must be logged-in on the system.

##### Triggers:

Customer clicks on the button or link to "Logout"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

The Customer is logged out of the system.

#### Add Item To Cart

##### Goal

Customer adds item(s) in the cart

##### Actors:

##### Preconditions:

The customer must be logged-in on the system.

##### Triggers:

Customer clicks the button or link to "Add To Cart".

##### Basic Scenario:

##### Alternative Scenario:

##### Postconditions:

The Customer has added item(s) to the shopping cart.

#### Checkout An Order

##### Goal

Customer places and confirms an order for the checkout process.

##### Actors:

##### Preconditions:

##### Triggers:

Customer clicks button or link to "Ckeckout"

##### Basic Scenario:

##### Alternative Scenario:

##### Postconditions:

The Customer has placed and confirmed an order.

### Administrator Use Cases

#### Login Administrator

##### Goal

Login to an Administrator account with the system.

##### Actors:

##### Preconditions:

Administrator account must already be registered.

##### Triggers:

Administrator clicks button or link to "Login"

##### Basic Scenario:

##### Alternative Scenario:

##### Postconditions:

The Administrator is logged into the system.

#### Logout Administrator

##### Goal

Logout the Administrator account on the system.

##### Actors:

##### Preconditions:

Administrator must be logged-in on the system.

##### Triggers:

Administrator clicks button or link to "Logout"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

The Administrator is logged out of the system.

#### Add User

##### Goal

Register a new customer, sales person, or administrator account with the system

##### Actors:

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks button or link to "Add Users"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

A new customer account is created within the system.

#### Remove User

##### Goal

Remove a user from the system.

##### Actors:

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks button or link to “Remove User"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

An account has been deleted within the system.

#### Change User Properties

##### Goal

Alter properties such as passwords and privileges of the user.

##### Actors:

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks button or link to “Change User Properties"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

An account has been altered within the system.

#### Install Plug-ins

##### Goal

Install a new plug-in to the application.

##### Actors:

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks the button or link to "Install Plug-ins "

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

A new plug-in is installed in the application.

#### Remove Plug-ins

##### Goal

Remove a plug-in from the application.

##### Actors:

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks the button or link to "Install Plug-ins"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

A plug-in is removed from the application.

#### Manage Plug-in Options

##### Goal

Make changes to an installed plug-in.

##### Actors:

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks button or link to "Manage Plug-ins "

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

A plug-in’s options have successfully been changed.

#### Install patch process

##### Goal

Install patches or software updates to the web store.

##### Actors:

##### Preconditions:

Administrator must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Administrator clicks the button or link to "Install Patch"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

The web store was successfully updated.

### Sales Person Use Cases

#### Login Sales Person

##### Goal

Login to an account with the system.

##### Actors:

##### Preconditions:

Sales Person account must already be registered.

##### Triggers:

Sales Person clicks button or link to "Login"

##### Basic Scenario:

##### Alternative Scenario:

##### Postconditions:

The Sales Person is logged into the system.

#### Logout Sales Person

##### Goal

Logout the Sales Person account on the system.

##### Actors:

##### Preconditions:

Sales Person must be logged-in on the system.

##### Triggers:

Sales Person clicks the button or link to "Logout"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

The Sales Person is logged out of the system.

#### Add Product

##### Goal

Add a product to the system.

##### Actors:

##### Preconditions:

Sales Person must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Sales Person clicks the button or link to "Add Product"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

A new product is created within the system.

#### Remove Product

##### Goal

Remove a product from the system.

##### Actors:

##### Preconditions:

Sales Person must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Sales Person clicks the button or link to "Remove Product"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

A product is deleted from the system.

#### Update Product Attributes

##### Goal

Update Product attributes within the system.

##### Actors:

##### Preconditions:

Sales Person must be able to access the weborder system via a web browser with HTTPS.

##### Triggers:

Sales Person clicks the button or link to "Update Product Attributes"

##### Basic Scenario:

##### Alternative Scenario:

None

##### Postconditions:

The product attributes have been changed.

## Appendix C: Analysis Models

None

## Appendix D: Issues List

## Appendix E: Data Dictionary
