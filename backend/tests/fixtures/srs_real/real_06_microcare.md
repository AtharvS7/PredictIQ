# Microcare Voucher Management Health System Software Requirements Specification

> **Dataset:** PURE Dataset (Zenodo 7118517 / IEEE RE 2017)
> **Original Document Title:** Software Requirements Specification  For Voucher Management System
> **Domain:** Healthcare Management
> **License:** Open Source
> **Source/Project:** https://microcare.org
> **Version:** 1.0

---

## 1 Introduction

### 1.1 General overview of the VMUS (Voucher Maintenance Unit System)

#### Diagram Functional Flow Diagram:

### 1.2 Purpose

The purpose of this document is to explain the flow and the requirement 
of Voucher Management System (VMU) required by Marie Stopes International Uganda
(MSIU) during the various meetings held between MSIU and Microcare from 28th of Nov 
2005 to 30th of Nov 2005. This document is purely based on the Functional Flow Diagram 
designed by Microcare. The document will explain every small 
entity of the system including various code generations, Bar-coding and Graphical User 
Interface etc. This document will help the system development team to understand the 
overall and detailed functions of every small entity in VMU and to design the system that 
will meet every requirement of the VMU program.  This document will help the testing team 
to prepare the Test Cases and will help them to test every module in the system and overall 
testing of the system, so that the testing team will have confidence on the quality of this 
system.

### 1.3 Project Scope

#### 1.3.1 about MSIU and OBA Program

Past experiences with development aid showed, that financing inputs, 
e.g. facilities and equipment, does not result in the necessary improvement of health 
outcomes. Thus as a change of paradigm, the OBA concept finances agreed outputs 
with predefined quality rather than pre-defined inputs by selling vouchers for STD 
services at subsidised prices to patients. These vouchers will be refunded to service 
providers in the private sector (medical doctors, qualified nurses and midwives), 
government hospitals, NGOs, and faith-based organisations.  
The major advantages of the OBA approach are, that it allows

The approach was successfully applied in the sixties/seventies in South 
Korea and Taiwan. In recent years also a programme was run in Nicaragua but the OBA 
has not been 
implemented in larger scale programs.

The principles of the voucher, the contents of the health care services, 
their required quality, the standards to be met by the providers and their infrastructure, 
as well as the measures for monitoring the 
quality have been defined in the PDS.

The main structures and processes in the STD voucher programme are:

Distribution follows certain rules:

The client may honour the voucher at any approved provider of his choice.  
STD treatment according to the National Treatment Algorithms for STD in Uganda (NTA), 
adapted for this voucher scheme (TA-OBA, treatment algorithms for STD treatment in the 
OBA scheme), 
is given to clients for free for the syndromes of

In line with the NTA the voucher includes

At the end of each month they hand in – respectively the claims processing 
agency (CPA) collects –

#### 1.3.2 About Voucher Management system

The voucher management system VMS is designed to atomize 
the process of Voucher Management Unit (VMU) to minimize the manual process 
to maximize the quality of the project to understand the 
progress and timely out come of the project to take necessary steps by the MSIU 
Admin team to plan for the future and to increase the quality of the STD voucher 
service. The system will also control the existence of fraud in claims and will help
 the service provider to reach their payments in time without delay. 
The other features and details of system will be explained in below sections in the 
document.   The voucher management system is subdivided into following modules to 
make the system easy for understanding, developing, testing and to implement.

Each of the above modules are again subdivided into subsystems, those details are explained in 
below sections in the document

### 1.4 References

The preparation of SRS is purely based on the following documents

## 2 Overall Description

### 2.1 System Perspective

This section of the document is going to explain the functionalities of 
the system, its subsystems and how it’s integrated and working together. 
During the system study, it was understood that the first pilot period, twenty 
thousand vouchers will be sold, but the VMU-system has the provision to upgrade to meet 
the additional market and projects needs.

#### 2.1.1 Outline of entire system

As mentioned above the entire system is sub-divided into six modules 
and again the each module 
is subdivided into different subsystems.

#### 2.1.2 2.1.2 Voucher Management System Modules

##### 1. Voucher Creation / Preparation

Voucher creation – the voucher numbers are system generated 
and created with unique identification numbers with security protocols in-built. 
The created unique numbers are then printed out in the form of bar-codes, which will 
complement (or stuck on the voucher) the voucher. Then at every level on the voucher 
cycle this number is captured, on distribution, retail sales, point of treatment, enclosed 
along with claim forms, at the claims processing and finally for the payment. 
Such tracking records will be utilized for reports as well. Each voucher should have the 
following properties, which will have sub-elements to get the batch numbers, voucher 
numbers, and the project codes. Project code – Group batch code – Batch number – 
Voucher number – Security code.

This system has high security feature as far as the user access to the 
system, including all the modules, 
sub-modules and even at the screen level.

##### 2. Marketing / Sales

The marketing and sales is the next step and the next module in the system. 
This module will take care of following sub modules.

##### i Distributor Master Information

The system will capture the master details of every distributor so that 
the users can get the details of any distributor and sales details at any time. Each 
distributor will have unique code and detailed descriptions such as name, address, 
locations and type of business etc. such valid information will help us track 
information related to sales and distributions. 
Following fields will be captured at this master.

All fields with * are mandatory!

The address field will capture the geographical location of the distributor, 
such as District, Sub-District, County, Sub-County or Village / Town, road or street. All 
the level of details will have a master table in order to update as per the program 
requirements.  
The system will check the duplicated ID for the distributors. The system can allow 
the duplicate names of the Distributor. On capture of any duplicate name the system 
will give a warning message to have the duplicate name or to change the name. 
For better reporting purposes it is better to have a differentiating indicator on the name.  
System will have a provision to print the distributor master details.  
The distributor screen will have a provision to view the Sales History of a 
particular distributor with following summary details.  
Distributor Name as Report Header and following as the report footer

There will be a provision to select a particular distributor to view the details 
(e.g. sales) by double clicking on the grid.  
Print option of above report is based on User Login Permission only.  
There will be an option for doing the following at every screen.

There will also be a provision for the other users to view the details of a
 distributor with purchase and sales details.

The system will capture the details of MSIU Salesman; this would help 
the MSIU management team to understand the performance of each Team or salesman. 
During every distribution transaction the user should select the name of the sales man 
listed from Team Master. 
The Salesman master should capture following information’s.

The sales team master is for the future development of this program, 
if this program is extended to a country-wide network, 
this master will help understand and tack sales information.

The system will check the duplicated ID for the salesman and team. 
The system can allow the duplicate names of the salesman. On capture of any duplicate 
name the system will give a warning message to have the duplicate name or to change 
the name. For better reporting purposes 
it is better to have a differentiating indicator on the name

##### iii Distribution Transactions (Sales from MSIU to Distributor)

The system will capture the details of voucher sales between MISU 
sales team and Distributors. During the distribution the system will capture the 
following details, to make Distribution process easily. With the below details the 
user can get the details of Distributor-wise and Salesman-wise 
and Batch No wise sales details as reports.

The mandatory information required during a distribution transaction is 
mentioned below.

The system will generate an auto-generated number as Distribution 
Invoice No.  
Suppose the distributor or salesman name is not available in the system, then the 
system has a provision to navigate quickly to its master screen and enter the new 
Distributor and Salesman details, 
without closing the present screen.  
While entering the No of vouchers required, the system should automatically 
pick the Batch No’s with voucher No’s from the available voucher stock and list the 
details of each voucher with below information’s as a grid format.

The date of distribution will be current (system) date. But the date of sale 
can be the past dates. 
There will be a future date sale validation check available.

#### 3. Claim Entry/Processing

The program will take maximum care in this form and table, as it 
become a vital transaction to be captured. In this module you will see that every 
capture of data will be 
validated and checked on saving into the database. For e.g. the capture of voucher 
number, clinical information, diagnosis details, drug and investigation details and 
the costs are going to provide the program a vital report information. The system 
development team will focus its attention in making this module/table function 
efficiently.  For the easy understanding and designing of the system, this module is 
subdivided into following sub-modules. The division of sub-module is purely based 
on the sub-level categories of the data information.

##### i Voucher Service Provider (VSP) Master Information

The VSP master will have the following information:

Other than Contact No and E-Mail Id all other information are mandatory 
during the creation of a new Service Provider.  
The VSP code is a digit code with suffix SP, would be automatically generated by the 
system.  
The system should generate message with two option “Continue – Yes/No” while the 
user trying to create a new VSP with an existing name, If the user press Yes the 
system will allow the user to enter the same, if not the system wont allow the new 
entry to save.  
The system will list District, Sub-District, County, Sub-County, Village / Town 
from the master during VSP creation, if any of them are not available in the system, 
then the system will have the provision to navigate quickly to its master screen and 
do enter master details and back to VSP screen.   
The values of Health Sub – District, Locality, Level Of Facility, Type of facility, 
Registration Body would be list from their own master and should select the details 
based on the VSP. If any of the information is not available in existing master of 
above, then the system will have the provision to navigate quickly to its form to 
enter the master details and back to VSP Screen. The system will populate Active VSP 
only on other screen during data entry process, 
but the system will also populate all VSP for report purpose.  
Activation and In-activation of VSP is purely based on the MSIU Management decision. 
But if the system is found more than two fraud entries during the claim process of 
particular VSP, then the system would automatically change the status of that particular 
VSP as In-activate. Activation of that particular VSP is again purely based on MSIU 
Management decision.  
The VSP Master Information screen should have a provision to enter the payment terms 
agreed between MSIU and VSP. The system will capture following master details to fill 
the payment terms.

The below details may periodically change depends on the MSIU management decision.

The above mentioned payment terms will help the MSIU to make the 
payment detail easy and also help the VSP to get their payment in timeThe system will 
control the payment process and terms.  The allowed users only can able to Add, Modify 
or delete the VSP master information including payment terms.  
The VSP screen will have the provision to view the Claim Status of selected VSP. The 
system will facilitate to show the user following details if necessary.  
VSP Name (as the report header and below as the details part of report)

Cumulative Total Amount will show in Report footer for the previous payment done.

##### ii VSP Staff Master Information

The system will have the facility to capture the details of VSP staff 
details and the necessary master information 
while entering the claim into the system.

The system will generate message while creating a new staff with 
existing name, but the system will allow 
the user to save that new staff if its required. 
All above information’s other than Qualification are mandatory during 
the creation of new staff under any VSP.  
The system will automatically create Staff Code with Suffix as VSP Code 
+ SC + 3 digit. For example HP0001SC0001  
Staff type (should be select from list of staff type listing from Staff Type Master)  
If any of the staff type is not available in the system, then the system should 
have the provision to navigate quickly to staff type master 
to enter the new staff type and then back to Staff Master screen.

##### iii Claim (Treatment Form) Submission

Depends on the payment terms (Bi-monthly / Monthly) mentioned in 
the VSP master the VSP should submit the Claim (Treatment form) to the MISU Field 
office. While submitting the Claim (Treatment Form) to MSIU, the system will have 
the provision to capture the following details. These information is vital and 
shall be used for compared with the processed claims.

The system should print a receipt document based on the information 
entered during claim submission. 
The document should have the following information.

The above details would print in the report header and below details 
will print 
in the detailed part of the report

The claim entry is purely based on the Treatment (claims) Form submitted 
by the VSP. Before the claim entry the user should check the form manually to understand 
whether any mandatory information is missed in the Claim or not. If yes, then the user 
should mark that Claim (Treatment Form) status as Rejected and send back to VSP.  
During the claim entry the system should capture the following information.

The above details are the master informationd and below listed information
are the transaction details of a Claim.



The system will have the provision to enter any number of Syndrome, 
Clinical Examinations, Diagnosis, Lab Test, Drugs and Other Measures in 
any treatment level based on MSIU treatment master.

All above master level information are mandatory other than 
Contact No during the entry of claim into the system. The following part will 
explain how the systems 
will validate every information during claim entry.

If it is a First visit Claim

If Claim is for first follow up

If Claim is for second follow up

The system captures the thump impression available in each claim 
form, and needs to compare it with the same voucher numbers previous visits 
if available. If the thump impression are mismatching for the same patient 
(Client / Partner) on same voucher the system would automatically make a count on it.  
 If the claim from same VSP having more than two times of Thump Impression 
mismatching, then the system should automatically produce a warning message 
and the same time the system should In-Activate the VSP. 
The authorized user can alter / amend the Claim if required.



#### 4. Voucher Sales Return

Voucher Sales return is feature used when a distributor is planning to 
return the vouchers back to the MSIU sales team. The system will 
capture the following information during the sales return transaction.

The above details are the master part and following are captured as 
transaction part

All above information are mandatory during the sales return

While entering return vouchers details the system will check weather 
the returned voucher was sold to this particular Distributor or not. 
If not the system won’t accept those vouchers as return.

MSIU team collects the client feed back from the clients who 
got treatment through the voucher system. 
The Client Feed back form should capture the following details

Based on the Voucher No the system will populate the following details


#### 6. Reports (Standard and Customized)

The system has the provision to provide various analytical, medical, 
financial and statistical 
reports. Such reports can be designed later.

#### 7. Security and User Privileges

The security setting of the entire system is based on User Group. 
The roles available in the system are allocated to user group. 
The user group creation would capture the following Information

The above is the masters part information and below are 
the transaction part information.

Allow above information are mandatory while creating a new User Group.

All the above are mandatory entry
