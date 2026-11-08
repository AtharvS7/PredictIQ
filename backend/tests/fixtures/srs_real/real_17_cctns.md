# Crime and Criminal Tracking Network & Systems (CCTNS) Functional Specification

> **Dataset:** PURE Dataset (Zenodo 7118517 / IEEE RE 2017)
> **Original Document Title:** Crime and Criminal Tracking Network & Systems (CCTNS) Functional Specification
> **Domain:** Public Safety & Law Enforcement
> **License:** Open Government Data
> **Source/Project:** https://ncrb.gov.in
> **Version:** 1.0

---

## 1 INTRODUCTION

The Functional Requirements Specifications (FRS) report provides the detailed description of the functionalities required for the first version of the CCTNS. The key guiding principle behind the functional design of CCTNS V1.0 is to focus on the critical functionality that provides value to the police personnel at the cutting edge which in turn can improve the outcomes in the areas of “Investigation of Crime” and “Detection of Criminals”.

## 2 FUNCTIONAL OVERVIEW

CCTNS V1.0 functionality is designed to focus on delivering value to IOs, records room staff and citizens within the broad crime investigation area. Based on the guiding principles stated above, nine different function blocks have been identified and the detailed functionality of each block was determined.

## 3 DESCRIPTION OF THE MODULES AND FUNCTIONAL REQUIREMENTS

The functionality of the CCTNS application is focused on providing value to the police personnel, especially the officers operating at the cutting edge and easing the day to day operations of the police function.

### Registration

Citizens can register their complaints with police and then based on the evidence, facts and following investigation, police shall take the complaint forward. The Registration module acts as an interface between the police and citizens and it eases the approach, interaction and information exchange between police and complainants.

### Investigation

After a complaint is initiated, police initiates the investigation process. The Investigation module of the CCTNS facilitates the investigation process and introduces operational efficiencies by automating most of the tasks that take place after initial entries are made during Registration.

### Prosecution

Interfacing with the courts during the prosecution of cases is an integral part of the responsibilities of police personnel. A designated constable from each police station constantly interfaces with the courts. The Prosecution module of the CCTNS aids this interfacing by providing a platform to record entries of the court interactions.

### Search

The Search module of the CCTNS gives police personnel the ability to execute a basic or advanced search on cases. Using the search functionality, police personnel can search for a particular person, type of crime, modus operandi, property etc. It also gives the user the ability to customize the results view by criminal/accused or by cases. It makes reporting easy for police by enabling them to execute different types of queries such as monthly reporting, RTI related etc.

### Citizen Interface

The Citizen Interface module of the CCTNS acts as a conduit for the information exchange between citizens and police units/personnel. Citizens can use it as a tool to get information or acknowledgements from police. The police in turn can use it to respond to citizens with very little turnaround time. It improves overall productivity by helping citizens and police to cut short the drudgery of large amounts of paperwork.

### Navigation

The Navigation module of the CCTNS provides role based landing pages which help in navigating through the CCTNS application. It shows information such as cases assigned, alerts, pending tasks etc hence helping police personnel to plan better and execute with greater efficiency.

### Application Configuration

The Configuration module of the CCTNS helps keep the application configured according to the states’ requirements in addition to keeping data elements/rules up to date. With a proper configuration, information such as act and sections, state specific data, castes, tribes, property information etc. can be created updated and deleted.
        The functional requirements for each of the modules are provided as A1 to A7 in separate enclosures.

## 4 NON-FUNCTIONAL REQUIREMENTS

The non-functional requirements specify the qualitative attributes such as user-friendliness and performance of the system that are critical for the increased user-acceptance of the application.

### Help Module


### Audit Module

### Access Module

The requirements specify the requirements to control the user access to correspondences, files, and records and various functionalities provided within the system.

### Ease of Use

### Usability

### System Availability

### Performance and Scalability

## 5 FUNCTIONAL ARCHITECTURE RECOMMENDATIONS

The proposed functional architecture is modeled around centralized deployment to facilitate ease of maintenance and leverage advancement in open standards and web technologies.
        The 3 C’s (Core-Configuration-Customization) forms the guiding principle for the architecture. The functional architecture of the CCTNS solution is given in the figure below. The functional architecture is composed of 4 major components based on SOA principles. Each of the components contains multiple services as defined by Service Definition. The core services, support layer and security and access control components can be deployed as standard components with necessary configuration changes. The customization layer can override and add to the core services based on the specific state requirements and can be plugged with the core services.
        The deployment of the application will be at state level and will be configured and customized as per the state specific extensions.
        The systems should be designed with the following broad guidelines:

### System Functionality
