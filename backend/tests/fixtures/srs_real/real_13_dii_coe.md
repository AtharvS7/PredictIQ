# Defense Information Infrastructure Common Operating Environment (DII COE) SRS

> **Dataset:** PURE Dataset (Zenodo 7118517 / IEEE RE 2017)
> **Original Document Title:** DRAFT SOFTWARE REQUIREMENTS SPECIFICATION (SRS) FOR THE DEFENSE INFORMATION INFRASTRUCTURE (DII) COMMON OPERATING ENVIRONMENT (COE) XML SERVICES (XS)
> **Domain:** Distributed Infrastructure
> **License:** Public Domain (US DoD DISA)
> **Source/Project:** https://www.disa.mil
> **Version:** 1.0

---

## 1 Scope

### 1. IDENTIFICATION OF FUNCTIONAL AREA

This Software Requirements Specification (SRS) establishes the functional, 
performance, and verification requirements for the XML Services (XS) functional area of 
the Defense Information Infrastructure (DII) Common Operating Environment (COE). 
The XS functional area includes Registration of terms (tags and structures), 
Design of XML schemas, Generation and Consumption of XML documents.

### 2. FUNCTIONAL AREA OVERVIEW

XML Services provide infrastructure services for mission and 
support applications using XML technology. These services isolate vendor-unique 
implementations of data access and provide applications a means of avoiding 
dependencies on physical access models. These services also provide data 
management functions for access to distributed (local and remote) 
database management systems as one of the solutions for interoperablity.

### 3. DOCUMENT OVERVIEW

This document outlines the software capabilities required for the XS 
components for the DII COE. Section 2 lists the documents that are applicable to 
this specification. Section 3 provides a list of functional capabilities. Section 4 
identifies the qualification requirements. Section 5 outlines the requirements and 
verification traceability matrix. 
Section 6 contains the applicable notes associated with the XS component.

## 2 APPLICABLE DOCUMENTS

### 1. GOVERNMENT DOCUMENTS

Defense Information Infrastructure (DII), Shared Data Environment 
(SHADE), CAPSTONE DOCUMENT Version 1.0, 11 July 1996


### 2. NON-GOVERNMENT DOCUMENTS

Petrucci, Steve, "Cross-Platform Power Tools, Application Developers 
for the Macintosh, Windows, and Windows NT", Random House Electronic Publishing, 
1993.Donald Lewine,"POSIX Programmer's Guide", O'Reilly & Associates, Inc. 1991.
W3C Working Draft "Namespaces in XML"


## 4. REQUIREMENTS

### 4.1 REQUIRED STATES AND MODES

### 4.2 XML SERVICES CAPABILITY REQUIREMENTS

The XS shall deliver inter-related components as shown
 in figure 3.2-1

##### 1 Register Terms and Structures (e.g., tags, DTDs, DCDs)

### 4.4 REGISTRY SERVICES

The Registry shall provide standard APIs as specified in Appendix B.

### 4.5 DATA ACCESS SERVICES INTERNAL INTERFACE REQUIREMENTS

The XS function shall provide standard APIs as specified in Appendix C.

The XS shall internally interface (transparent to the operator) with the 
existing data elements 
of the DBIF, DAC, and COTS RDBMS products.

### 4.7 REGISTRY SERVICES ENVIRONMENT REQUIREMENTS

The Registry software shall be portable and required to 
execute on COE-compliant platforms.

### 4.8 PERSONNEL-RELATED REQUIREMENTS

Not applicable. Personnel requirements shall be determined by the developers of 
the system in which the XS module is embedded

### 4.9 TRAINING-RELATED REQUIREMENTS

Not applicable. Training requirements shall be determined by the developers of the 
system in which the XS module is embedded.

### 4.10 LOGISTICS-RELATED REQUIREMENTS

The XS developer is responsible for software maintenance, software 
support, and software updates. The DISA Configuration Manager (CM) is responsible 
for distribution of the XS 
product to system developers.

### 4.11 OTHER REQUIREMENTS

None

### 4.12 PACKAGING REQUIREMENTS

The XS software shall be delivered in accordance with DII COE guidelines.


### 4.14 PRECEDENCE AND CRITICALITY OF REQUIREMENTS

The following table depicts the mapping of the requirements in Section 3 to their corresponding precedence and criticality code and to other related requirements within the XS SRS. 
The precedence and criticality codes are the following:



#### 4.14.2 QUALIFICATION PROVISIONS

COE Software will be qualified through formal validation tests of the 
SRS level requirements. The Qualification Methods applied to the software shall include 
test, demonstration, 
analysis, and inspection (T, D, A, I).


#### 4.14.4 REQUIREMENTS TRACEABILITY

Provided under separate document.


#### 4.14.6 NOTES

##### 4.14.6.1 ACRONYMS & ABBREVIATIONS

##### 4.14.6.2 GLOSSARY OF TERMS

#### 4.14.7 APPENDIX A

The metadata and procedures are described for the current Information Resource Submittal Package .

##### table 1 information Resource Types

##### table 2 information Resource Association Types

For Developers may submit and use information resources within the 
Registry constitutes guidance in the generation and use of XML as an 
authoritative source for approved XML data and metadata components.

Zip and attach submission package to e-mail message to: ____________________

Establishing a new Information Resource. Follow these conventions for creating 
new information resources for the Registry

##### 1. Use "XML_Attributes" sparingly

If the term is well recognized outside its container term, designate 
it as an element. Example: CTRY_CD, CTRY_NM, CTRY_ABBRD_NM, CTRY_OFF_NM, 
CTRY_SCP_NT_TX, and CTRY_PSTL_NM 
are all characteristics (ER-attributes) for the entity CTRY. In the relational world, 
they are columns within the table ctry, attributes of the entity ctry in er-modeling, 
and member attributes in object modeling. It would be expected that a submitter 
would identify them as attributes rather than elements. But if they were identified as 
attributes of the element ctry, then the additional baggage (other attributes) must be 
carried, or submitted as separate elements. We wish to limit the proliferation of tags, 
so we strongly urge folks to use XML_Attributes sparingly.

Initially, the Registry will not have keyword, thesaurus, or ontology 
support but it will have a substring search for a number of fields, including definition. 
Therefore, we urge submitters to include enough expressive terms so that COE developers 
would easily find the term they might consider "natural" in the definition and find the 
desirable tag for expressing that concept. Example: If the 
registered tag is ORG_ID, the description that includes references

##### 4.14.7.1. APPENDIX B

##### 4.14.7.1.1 EXTERNAL PROGRAMMING INTERFACE

The External Interfaces for the XS SRS are defined as interfaces to non-COE 
components. Detailed information (as specified in paragraph 3.3 of the Data Item 
Description DI-IPSC-81433) defining these interfaces will be specified during the 
design phase of the COE XS architecture. 
At this time such detailed information is unavailable.


##### 4.14.7.3. APPENDIX C

##### 4.14.7.3.1. INTERNAL PROGRAMMING INTERFACES

The Internal Interfaces for the XS SRS are defined as interfaces to COE 
components. Detailed information (as specified in paragraph 3.4 of the Data Item 
Description DI-IPSC-81433) defining these interfaces will be specified during the 
design phase of the COE XS architecture. At this time such detailed information is 
unavailable.The COE components identified to-date are listed below.

##### 4.14.7.3.1.1. MANAGEMENT SERVICES API

It incorporates other interfaces to:

## 1. DISTRIBUTED SYSTEM SERVICES

### 1.1. COMMUNICATIONS SERVICES API

It incorporates other interfaces to:

#### 1.1.1. DISTRIBUTION AND OBJECT MANAGEMENT SERVICES

It incorporates other interfaces to:

## 1. APPLICATION SUPPORT SERVICES

### 1.1. PRESENTATION SERVICES

It incorporates other interfaces to:

## 1. COMMON SUPPORT APPLICATIONS

It incorporates other interfaces to:

## 1. SOFTWARE DEVELOPMENT SERVICES

It incorporates other interfaces to:


## 2. APPENDIX C

### 2.1. INTERFACES TO COMMERCIAL PRODUCTS

The Interfaces to Commercial Products for the XS SRS are identified below. 
Detailed information (as specified in paragraph 3.3 of the Data Item Description 
DI-IPSC-81433) defining these interfaces will be specified during the design phase of 
the COE XS architecture. At this time such detailed information is unavailable.
The three commercial products or environments identified for the COE are the following 
Relational Database engines:
