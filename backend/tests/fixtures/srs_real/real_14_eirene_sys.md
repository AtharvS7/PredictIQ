# EIRENE System Requirements Specification for European Railway Telecommunications

> **Dataset:** PURE Dataset (Zenodo 7118517 / IEEE RE 2017)
> **Original Document Title:** UIC Projec t EIRENE System Requirements Specification
> **Domain:** Rail Telecommunications & GSM-R
> **License:** Open Standard (UIC / ERA)
> **Source/Project:** https://www.era.europa.eu
> **Version:** 1.0

---

## 1 Introduction

### 1.1 General

This specification has been developed within UIC Project EIRENE. It specifies a digital
radio standard for the European railways. It forms part of the specification for
technical interoperability. (I)

### 1.2 Scope

The EIRENE System Requirements Specification defines a radio system satisfying the
mobile communications requirements of the European railways [EIRENE FRS]. It
encompasses ground-train voice and data communications, together with the groundbased
mobile communications needs of trackside workers, station and depot staff and
railway administrative and managerial personnel. (I)

Figure 1-1 shows how the EIRENE system is covered in this specification, by
associating each element of the system with its corresponding section number(s).
References specifying the main interfaces are also cited, and are detailed more
extensively in Appendix A. (I)


The application of this specification will ensure interoperability for trains and staff
crossing national or other borders between systems. It also intends to provide
manufacturing economies of scale wherever practical. (I)

### 1.3 Appliccability

The EIRENE System Requirements Specification defines the set of requirements which
a railway radio system shall comply with in order to ensure interoperability between
national railways. (I)

The EIRENE Functional Requirements Specification [EIRENE FRS] specifies the
functional requirements for EIRENE. (I)

The specification distinguishes between requirements affecting a railway’s network
infrastructure, onto which mobiles will roam, and the requirements concerning
mobiles which may be used in any EIRENE compliant network. (I)

The statements made in the specification are assigned to one of three categories: (I)

### 1.4 System Overview

#### 1.4.1 Extent of specification

The system is based on the ETSI GSM standard. To meet additional functionality and
performance requirements, this standard is to be supplemented by: (I)

The scope of the specification is shown in figure 1-2, showing the hierarchy of the
GSM, and railway features to be implemented. (I)


A list of ETSI and 3GPP specifications is provided in the normative references
section of this document. (I)

Compliance to the list of normative documents is mandatory for all of the GSM
services necessary to provide the functionality specified in the [EIRENE FRS]. (M)

Later releases of these specifications may be used, providing that the system is
backwards-compatible with the versions listed. (I)

#### 1.4.2 Outline Architecture

The system is based on the GSM architecture which is summarised in figure 1-3. (I)


The system comprises the following elements: (I)

Signalling within the NSS and between NSSs is carried out according to signalling
system number 7, SS7, making specific use of the mobile application part (MAP) of that
standard. (I)

Railway networks may implement a short message service centre to be interfaced to
the GSM network in order to support railway specific messaging applications. (I)

A railway GSM network is also likely to have external interfaces to: (I)

EIRENE will provide the radio bearer for ERTMS/ETCS. The EURORADIO layers are
responsible for ensuring the overall safety of the transmission link between train-borne
and trackside ERTMS/ETCS applications. (I)

In addition to a GSM capability, a direct mode capability may be provided for railway
mobiles for set-to-set operation. (I)

Standardised interface protocols are to be provided to allow applications external to
EIRENE to access EIRENE bearer services. (I)

Applications may include: (I)

#### 1.4.3 Railway specif services and facilities

To meet the specific railway requirements, a number of additional features are
required some of which have been incorporated in the GSM Standard. The main
aspects are summarised in the following paragraphs. (I)

##### 1.4.3.2 Frequency:

Equipment is to be capable of operation in the following frequency bands:
(I)

Note: the R-GSM band includes the Public GSM (P-GSM) and Extended GSM (E-GSM)
bands.

##### 1.4.3.3 Voice broadcast and group call facilities:

All mobiles are to support these services as
defined in the relevant GSM specifications. The services will mainly be used to: (I)

##### 1.4.3.4 Enhanced multi-level precedence and pre-emption:

This GSM specification is to be
implemented in order to achieve the high performance requirements necessary for
emergency group calls. It is also necessary to meet different grades of service
requirements for different types of communications traffic on the system (eg safety (eg
train control system), operational and administrative communications). (I)

##### 1.4.3.5 Functional numbering:

Many railway staff need to be addressed by functional rather
than personal numbers. The functional numbers may change on a regular basis. The
principal example is that of train drivers, who need to be addressed by train numbers
which change with each journey. To overcome this difficulty a translation facility will
be provided to allow calls to functional numbers to be forwarded to the most
appropriate personal number at that time. Thus calls made to a train number are
forwarded by the network to the appropriate driver or locomotive for that train at that
time. (I)

A follow-me service will be implemented in the EIRENE network using the GSM
Unstructured Supplementary Service Data (USSD) facility to allow users to establish
and terminate the forwarding of calls from a functional number to their personal
number. (I)

##### 1.4.3.7 Location dependent addressing:

Train drivers need to be able to contact controllers
and other staff at the push of a single button. As the train moves through different
areas, controllers are liable to change. As a consequence it is necessary to provide a
means of addressing calls from a train to certain functions based on the location of the
train. (I)

The only source of location information available within the GSM network is the cell
that the train is in. However, there are a number of external sources from which more
accurate location information may be derived: (I)

Within EIRENE, the primary means of determining the location of a train for the
purpose of location dependent addressing will be based on the cell dependent routing.
This may be supplemented with additional information from external systems to
provide a greater degree of accuracy. (I)

##### 1.4.3.10 Direct mode:

Railway mobiles may support a direct communications mode whereby a
mobile can communicate with all other railway mobiles in a local area without the use
of GSM infrastructure. Such a mode is required for use where: (I)

### 1.5 Structure of the specification

The specification is divided into the following separate sections: (I)

Section 2 lists the services and facilities which are to be supported by GSM-R networks.
Section 3 provides requirements and recommendations concerning the configuration,
planning and implementation of networks. (I)

Sections 4, 5, 6, and 7 are concerned with mobile equipment. Section 4 provides
specifications applicable to all GSM-R mobiles. Sections 5, 6, and 7 detail the additional
requirements for Cab radio, General purpose radio, and Operational radio equipment
respectively. Note that for the handheld version of the General purpose radio,
commercial standards apply. (I)

Section 8 covers controller equipment. Section 9 is concerned with a numbering plan
for the variety of functional numbers which are required. Section 10 details the
handling of other information, such as priority, closed user groups and encryption
algorithms, which must be applied consistently in all networks. (I)

Section 11 specifies functional and location dependent addressing. Section 12 refers to
the possible use of pre-defined text messages (not required for interoperability). (I)

Sections 13 to 15 describe the implementation of emergency calls, shunting mode and
direct mode. (I)

References for all sections are included in appendix A. (I)

## 2 Network requirements

### 2.1 Introduction

The network services necessary to meet the range of UIC requirements are detailed
below. These services are to be considered as a minimum set for implementation
within each GSM-R standard network. Railways may implement additional network
services as desired. (I)

### 2.2 GSM teleservices

The GSM teleservices [EN 301 515, Index [24]] to be supported are indicated in table 2-1.


### 2.3 GSM bearer services

The GSM bearer services [EN 301 515, Index [23]] to be supported are listed in table 2-2.


Note: The Adaptive Multi-Rate (AMR) CODEC is not suitable for voice group calls or
for voice broadcast calls. (I)

### 2.4 GSM supplementary services

The GSM supplementary services [EN 301 515, Index [9]] to be supported are listed in table
2-3. The applicability of these supplementary services to GSM basic services will be as
indicated in [GSM 02.81-02.89 and EN 301 515, Index [28]]. (I)


### 2.5 Railway specific services

The railway specific services to be supported are listed in table 2-4.

### 2.6 Alerting duration

The call waiting service (CW) permits a party A to be notified of an incoming call from
party C whilst the traffic channel is not available for the incoming call and party A is
engaged in an active call with party B. However call waiting does not operate during
the prior set up of the call between the parties A and B (including alerting if used).
Therefore the alerting duration has to be as short as possible in order to minimize the
risk for the party A of missing notification of an incoming call from party C with a
higher eMLPP priority. Taking into account technical and operational aspects, it is
recommended to set the relevant timer(s) in the network in such a way that the
maximum alerting duration is limited to 60s. (I)

## 3 Network configuration

### 3.1 Introduction

EIRENE mobiles are specified to conform to a common minimum standard of
performance. It is the responsibility of national railways to design their EIRENE
networks to provide the required level of service to EIRENE compliant mobiles. (I)

This section draws together specifications and information related to the planning of
an EIRENE network and provides guidance on target performance levels. Additional
information on communication requirements for the ERTMS/ETCS application is
provided in [ERTMS COMMS]. (I)

### 3.2 Coverage

For network planning, the coverage level is defined as the field strength at the antenna
on the roof of a train (nominally a height of 4m above the track). An isotropic antenna
with a gain of 0dBi is assumed. This criterion will be met with a certain probability in
the coverage area. (The target coverage power level is dependent on the statistical
fluctuations caused by the actual propagation conditions.) (I)

The following minimum values shall apply: (M)

The following minimum values are recommended: (I)

The EIRENE mobile installation shall be designed to operate in a network meeting the
criteria in 3.2.2 and 3.2.3. (M)

### 3.3 Handover and cell selection

The handover success rate should be at least 99.5% over train routes under design load
conditions (as given in [EN 301 515, Index [30]]). (O)

To avoid the necessity for large cell overlaps to accommodate high speed train
operations, optimisation of the handover process for such trains is considered
necessary. Suitable algorithms will be tested and refined as necessary during the trials
process. (I)

The proposed events for measurement of the start and stop of the handover execution
at the mobile are: (I)

There is a quality of service requirement for handover executions (eg a break of 10s
would clearly be unacceptable to the user). 300ms represents our current best estimate
of the QoS figure, although this will need to be confirmed through user trials. (I)

An additional option is available to reduce the handover break period, namely the use
of the synchronous handover capability to reduce the break period to about 150ms.
Synchronous handover requires the BTS transmissions in different cells to be
synchronised by the system. Each authority can decide whether it wishes to use
synchronised BTSs. (I)

### 3.4 Call setup time requirement

Call setup time requirement is dependent upon the eMLPP priority of a call [EN 301 515,
Index [27]]. The required priority level for each call type is given in section 10.2. (I)

Call setup times as defined in the EIRENE FRS shall be achieved with authentication
and ciphering procedures enabled. (M)

In order to achieve these times the passage of the call through any networks external to
GSM (eg from the GSM MSC to a controller linked by an ISDN connection) must take
less than 250ms. (I)

Achievement of fast call setup times requires information in the setup message to be
compressed. A maximum of 12 digits may be sent as mobile originator-to-dispatcher
information. (I)

### 3.5 Frequency band and channel arrangements

The network shall operate in a sub-band, or combination of sub-bands, of the R-GSM
band as defined in [EN 301 515, Index [35]]. (M)

The UIC frequency band for GSM-R is defined in [CEPT 25-09], [1999/569/EC] and
[ECC(02)05]: (I)

The carrier frequency is designated by the absolute radio frequency channel number
(ARFCN), and is defined in [EN 301 515, Index [35]]. For carriers in the UIC frequency
band the following convention shall be used, where Fl(n) is the frequency value of the
carrier ARFCN n in the lower band, and Fu(n) the corresponding frequency value in
the upper band: (M)

### 3.6 DTMF tones and signals

The minimum duration of a DTMF tone and the length of pause between tones
generated by the network (DTMF sender) and needed for the DTMF digit recognition
in the network (DTMF receiver) are specified in [3G TS 23.014, Support of Dual Tone Multi
Frequency (DTMF) signalling]. (I)

### 3.7 Termination of VGCS/VBS calls

An entitled controller may terminate a VGCS/VBS call based on DTMF signalling [EN
301 515, Index [4] & [5]]. (I)

The network shall terminate the ongoing VGCS/VBS call if it receives the 3-digit
sequence “***” transmitted via DTMF signals. (M)

In order to minimise the discomfort caused by the DTMF tone added in the voice
channel, the duration of the tone generated by the fixed line dispatcher shall be 70ms ±
5ms, and there shall be a minimum gap of 65ms between each tone. (M)

### 3.8 Muting and unmuting for VGCS calls

The muting and unmuting for VGCS shall be in line with 
[EN 301 515, Index [4]]. (M)

The network shall send the SET-PARAMETER message with the attribute “D-ATT =
T”1 [EN 301 515, Index [6]] to the mobile station of the talking subscriber if it receives the 3-
digit sequence “###” transmitted via DTMF or the group call SETUP message2 from a
controller terminal. However, receiving the 3-digit sequence “###” or the group call
SETUP message related to an additional controller while any other controller is talking
shall not result in sending another SET-PARAMETER message with the attribute “DATT
= T”. (M)

When the network has detected the 3-digit DTMF sequence “###” transmitted via
DTMF from a controller terminal and if the controller was not previously talking it
should indicate its recognition by playing a single DTMF grant tone “#” of duration of
100ms ± 5ms to be sent to that controller terminal only. (O)

The network shall send the SET-PARAMETER message with the attribute “D-ATT =
F”3 [EN 301 515, Index [6]] to the mobile of the talking subscriber only if it has received the
3-digit sequence “#**” transmitted via DTMF from all the talking controllers4. (M)

The duration of each tone (see 3.8.2 and 3.8.4) added in the voice channel, shall be 70ms
± 5ms, and there shall be a minimum gap of 65ms between each tone. (M)

## 4 Mobile equipment core specification

### 4.1 Introduction

To ensure interoperability, all EIRENE mobiles are specified with a common level of
basic services, facilities and features. This section of the specification gives details of
these core requirements, while sections 5-7 detail requirements specific to each of the
radio types. (I)

The logical architecture of an EIRENE mobile station (EIRENE MS) is shown in figure
4-1. The architecture consists of the following elements: (I)


The logical architecture comprises a number of interfaces between the different
EIRENE-MS elements. These are:

This specification defines three distinct mobile radio types according to the type of role
they will perform and the environment they will operate in, as follows: (I)

All SIM cards used in EIRENE mobiles shall comply with the requirements of the
MORANE FFFIS for GSM-R SIM Cards [MORANE SIM]. (M)

### 4.2 Radio interface aspects

All mobiles shall be capable of operation in the following frequency bands: (M)

The mobile radio antenna installation on vehicles shall be designed so as to ensure that
mobiles operate correctly in networks which conform to the design criteria defined in
section 3. (M)

Mobile radios shall be of the following power classes: (M)


### 4.3 Services and facilities

The following GSM teleservices, identified in section 2, are to be supported for each
type of mobile radio:


The following bearer services, identified in section 2, are to be supported for each type
of mobile radio:


The following supplementary services, identified in section 2, are to be supported for
each type of mobile radio:


The following EIRENE features are to be supported for each type of mobile radio:


If a Railway emergency call set up from an EIRENE radio is unsuccessful, the radio
shall automatically re-attempt the call setup until the call setup is successful, a retry
timer expires (duration 30 seconds, as specified in the [EIRENE FRS]) or the user
abandons the call. (M)
Note: For this, the higher layers of an EIRENE radio shall automatically repeat setup
requests to the layer 3 GCC or BCC entity as soon as an indication is given from the
layer 3 GCC or BCC entity on an abort of the establishment procedure without the
service being explicitly rejected by the network. No change of the related layer 3
procedures of GSM is intended. (M)

### 4.4 Core MMI requirements

A service availability indication shall be provided to radio users, as defined in [EN 301
515, Index [26]]. (M)

The user shall be prevented from entering direct mode if the GSM service is available.
(M)

If the attempt to establish a Railway emergency call is not successful after 2 seconds, an
indication shall be provided to the user of the status of the establishment request
procedure. (M)

### 4.5 Core environmental requirements

This subsection defines the core environmental and physical requirements for all
EIRENE mobile equipment. The requirements provided in this section are augmented
by those provided in later sections for each individual radio type, with each radio type
being specified by the superset of the core plus specific requirements. (I)

All EIRENE mobile equipment shall comply with all environmental, EMC and physical
specifications defined in the GSM standard, especially with reference to [GSM 05.90 and
EN 301 515, Index [2] & [35]]. (M)

All EIRENE mobile equipment shall conform to [EN 60950] (Safety of Information
Technology Equipment), including Electrical Business Equipment, 1993, plus
amendments A1 and A2. (M)

The categories of requirements defined in each section describing mobile equipment
are as follows: (I)

Any environmental and physical requirements stated may be superseded by national
requirements provided the national standards provide a higher level of environmental
and physical protection. Stricter national standards shall not prevent the use of other
EIRENE mobiles in that country. (M)

Many of the railway specific standards referenced are Pre-standards (eg [prEN 50155,
ENV 50121, prEN 50125]) and should be re-examined for their applicability to the EIRENE
system if any modifications are made to these standards in the future. (I)

All design, manufacturing, testing and installation of EIRENE mobile radio equipment
shall comply with the quality procedures defined in [ISO 9001]. (M)

EIRENE mobile equipment shall be capable of operating over a standard range of
temperatures from -20°C to +55°C. (M)

EIRENE mobile equipment shall be capable of being stored (ie without being
operational) at temperatures down to -40°C without any permanent damage. (M)

The equipment shall be capable of coping with temperature variations of up to +/-
1°C/minute. (M)

EIRENE mobile equipment shall be capable of operating between altitudes of -100m
and 1800m, referenced to sea level. (M)

The equipment shall be able to cope with relative humidities of 100% for short periods,
although the yearly average is expected to be 75%. The equipment shall also cope with
95% humidity for 30 days in the year. (M)

Operationally caused infrequent and slight moisture condensation shall not lead to any
malfunction or failure. (M)

All equipment shall not degrade photochemically when exposed to solar radiation of
up to 1200 W/m2. (M)

In normal operation of a mobile radio unit, it shall be expected that a combination of
the above environmental conditions will be experienced. (M)

All EIRENE mobile equipment shall be protected against shock and vibration in
compliance with standards defined in [prEN 50125] using tests defined in [prEN 50155].
(M)

All handheld mobile equipment shall be capable of withstanding the following shocks:
(M)

EIRENE mobile equipment shall be capable of being subjected to both sinusoidal and
random vibration. (M)

Handheld mobile equipment shall be capable of withstanding the following levels of
continuous sinusoidal vibration: (M)

The random vibrations to be withstood by mobile equipment shall be 0.25g in all three
axes of freedom. (M)

For determining battery requirements, the transmit/receive duty cycles used shall be
as shown in table 4-7 for each call type. (M)


Battery requirements shall be provided without the use of discontinuous reception or
transmission (DTX/DRX). (M)

Battery requirements shall be met based on full power during transmission and
assuming hourly periodic location updating. (M)

All railway and generic EMC standards define a maximum level of radiated EMC for a
range of frequencies. However, the nature of radio equipment implies a certain level of
EM emission in the transmission band. (I)

Guidelines concerning the effects of GSM emissions on hearing aids, pace makers and
other sensitive electrical equipment are provided in [GSM 05.90]. (I)

All EIRENE mobile equipment shall be immune to external EMC as defined in [ENV
50121 part 4]. (M)
NOTE: EIRENE mobile equipment cannot comply with the emission requirements defined in
this standard except outside the GSM transmission band.

The transmission of EM radiation from all EIRENE mobile equipment shall comply
with the radio frequency transmission masks defined in [EN 301 515, Index [35]] for the
range of GSM frequencies defined in section 1 of this document. (M)

Where the emission levels defined by [EN 301 515, Index [35]] exceed those stated in [ENV
50121 part 4], the GSM specification shall take precedence. (M)

Mobile equipment shall comply with the generic standard for EMC in the industrial
environment as defined in [ENV 50081 part 2], except for emissions at GSM frequencies as
noted above. (M)

The emission and immunity standards for the general railway environment and
ancillary services as defined in [ENV 50121 parts 1, 2, 3-1, 3-2 and 5] shall be considered. (M)

EIRENE mobiles will generate EM emissions in the GSM frequency band. It is the
responsibility of national railways operating EIRENE networks to ensure that EIRENE
equipment does not interfere with the normal operation of any on-train or ground
based systems. (I)

In particular, EIRENE equipment could interfere with: (I)

The environmental and physical tolerance of the EIRENE mobile radio units shall be
tested at a facility in accordance with [EN 45001]. (M)

All EMC emission and immunity tests shall be performed in accordance with
guidelines defined in the [EN 61000-4] series and in [EN 50140]. (M)

Environmental testing procedures shall follow guidelines defined in [IEC 68 part 1]. (M)

Specific environmental test procedures to be followed for EIRENE mobile equipment
shall include the following tests as defined in the [IEC 68] series: (M)

## 5 Cab radio

### 5.1 Introduction

This section identifies the system requirements for the EIRENE Cab radio. It defines
how the functionality is to be provided by the Cab radio system and the man-machine
interface. (I)

### 5.2 System components

Figure 5-1 shows the logical architecture of an EIRENE Cab radio. The architecture
comprises the following elements: (I)

The architecture comprises a number of interfaces between the different EIRENE-MS
elements. These are:

### 5.3 Driver call-related functions

Upon an appropriate MMI action, the radio shall initiate a call to the appropriate
controller with ‘Railway operation’ priority (see section 10.2). (M)

The calling driver’s functional number shall be passed to the network using UUS1. (M)

On receipt of a ‘Call other drivers in area’ request, the radio shall initiate a group call
using the ‘all trains’ group identification (see section 9) with eMLPP priority level 2
(see section 10.2). (M)

The calling driver’s functional number shall be passed to the network using UUS1. (M)

Activation of the ‘Railway emergency call’ function shall cause the radio to initiate a
Railway emergency call as defined in section 13. (M)

The calling driver’s functional number shall be passed to the network using UUS1. (M)

Many trains employ multiple active traction vehicles. Where these vehicles are not
connected by on-train wiring, it shall be possible for a permanent radio connection to
be established between each of the active cabs. (I)

Where there is more than one active cab, the radio connection shall be provided using
the GSM Multi-Party service. (M)

The call will be established from the active cab of the lead traction vehicle. Each of the
other cabs on the train will be contacted using its functional number (registered by the
other drivers prior to the establishment of the call). The procedure for setting up a
multi-party call is outlined in figure 5-2. The multi-party call shall have ‘Railway
operation’ priority (see section 10.2) and whilst on-going a ‘multi-drivers’ indication
shall be displayed permanently at all Cab radios. (M)

Upon activation of the function ‘Call train staff’, the radio shall determine the
appropriate functional number based on the staff member selected and the train
number (see section 9). A GSM point-to-point voice call at ‘Railway operation’ priority
(see section 10.2) shall then be initiated. (M)

The Cab radio shall be capable of being used as a standard GSM telephone, such that
the driver is able to call any valid number subject to closed user group, call barring or
other restrictions. (M)

The Cab radio shall be able to receive, display and store incoming short (SMS) text
messages (see section 12). (M)

The Cab radio shall support shunting mode communications as defined in section 14.
(M)

The Cab radio should support direct mode communications as defined in section 15.
(O)

### 5.4 MMI functions

When switched on, the radio shall initiate automatic self-testing using the GSM IMSI
attach procedure (including the automatic selection of the default loudspeaker volume
– see table 5-1). (M)

Upon switch on, the Cab radio shall be registered with a mobile network (see section
10.5). (M)

If registration is not successful an audible and visual indication shall be provided. (M)

Upon registration, the mobile shall be accessible by calling the MSISDN or the Engine
or Coach number with which it is associated. This shall require the home network
database to maintain this correlation. (M)

The following table provides details of the three volume adjustment ranges to be
provided. (O)

The numbers 1 to 5 give the five levels of adjustment possible for each volume range
setting. The default setting is the pre-defined level automatically selected when the
MMI is switched on. (I)

Upon activation of the registration function, a USSD message (see section 11) shall be
sent by the Cab radio. (M)

Upon activation of the deregistration function, a USSD message (see section 11) shall
be sent by the Cab radio. (M)

Upon detection (automatically or based on a list stored in the Cab radio) of the
additional on-train functions for equipment physically connected to the Cab radio, a
USSD message (see section 11) shall be sent by the Cab radio after activation of the
registration or deregistration function. (M)

This procedure shall take place at the installation of the Cab radio. It shall be initiated
by an external device or by a member of a maintenance team. (M)

On-train functions for equipment physically connected to the Cab radio shall be
registered or deregistered automatically based on a USSD message (see section 11) sent
by the Cab radio. (M)

### 5.5 Handling of calls

The sequence of actions required for a mobile originated call to another user shall be as
follows: (M)

The sequence of actions for a mobile terminated call to a driver shall be as follows: (M)

The Cab radio system shall provide a means for the driver to terminate established
calls which he is authorised to terminate. (M)

It shall be possible to initiate outgoing voice calls in one of four ways depending on the
intended recipient(s) of the call: (M)

Emergency access shall be provided to initiate the following call: (M)


Priority access shall be provided to initiate the following: (M)


On activation of the “call other drivers on the same train” function, the MMI shall
provide additional guidance to the user in the establishment and management of a
Multi-Party call. (M)

(*) When there are several controllers of the same type associated with a cell, and no
external means of selecting the appropriate one, the choice may be given by the system
to the driver, or a VGCS call may be established to all of the relevant controllers after
initiating the ‘Call controller’ function. (I)

The driver shall be able to initiate a call by selecting a name/number from stored
number information in the radio. (M)

Facilities shall be provided to support a list of stored names/numbers of up to a
minimum of 100 entries. (M)

Stored number access shall be provided to initiate the following calls: (M)


Unless otherwise indicated at time of entry, calls from the stored numbers list shall be
initiated as voice calls. (M)

By default, calls will have a priority of railway information calls (eMLPP priority
designation 4). It shall be possible to store a priority in association with a stored
number. (M)

The driver shall be able to initiate a call by dialling any valid telephone number or
functional number. (M)

Dial access shall be provided to initiate the following calls: (M)


Abbreviated dialling facilities shall be supported. (M)

Dialled calls from the MMI shall be point-to-point voice calls unless otherwise entered
from the MMI at the time of initiation. (M)

By default, dialled calls shall have a priority of railway information calls (eMLPP
priority designation 4). (M)


The Cab radio shall arbitrate between calls when:

The Cab radio shall apply the arbitration rules outlined in Table 5A-1 in Appendix 5A.
(M)

Once a call has been established the connected parties shall be able to communicate.
(M)

Replacing the handset shall result in the outcomes listed in Tables 5A-2 and 5A-3. (M)

Calls shall be able to be terminated by either party subject to the requirements shown
in tables 5A-2 and 5A-3. (M)

Table 5A-2 in Appendix 5A shows the effect of replacing the handset or initiating the
‘Call clear’ procedure for the different types of outgoing calls. (M)

Table 5A-3 in Appendix 5A shows the effect of putting down the handset or initiating
the ‘Call clear’ procedure for the different types of incoming calls. (M)

### 5.6 Other Cab radio functions

Incoming calls to the Cab radio shall be routed to the correct on-train user or device
using information contained in the sub-addressing field. (M)

Using the GSM “Manual” network selection procedure, the Cab radio application shall
allow the driver to access a prioritised list of authorised networks (to be displayed as
stated in section 10.5) and shall allow the driver to select a desired network from this
list. This function shall not be available if there is an ongoing voice call involving the
Cab radio. (M)

As a train approaches the limits of the coverage of the PLMN it is registered with, it
will be necessary for it to register with the next PLMN providing coverage. (I)

A means of directed network selection should be provided to ensure that the MS
registers with the required network. (O)

If directed network selection is implemented, the directed network selection procedure
shall be initiated by an external trigger mechanism, which instructs the Cab radio
application to select the required network unless a voice call is ongoing. (M)

If directed network selection is implemented and voice calls are ongoing at the time
when the external device attempts to trigger a network change, an audible and visual
indication shall be given to the driver and network change shall be deferred until the
call is terminated or until coverage of the current network is lost. (M)

If directed network selection is implemented, the Cab radio application shall use the
GSM “Manual” network selection procedure (through the AT interface [EN 301 515, Index
[19]]) to instruct the MT to register with the required network. (M)

The Cab radio should be capable of selecting the most appropriate mobile radio
network automatically using the selection criteria stated in section 10.5. (O)

If automatic network selection is implemented, the driver shall be capable of
deactivating and/or re-activating this function using simple MMI actions. (M)

Whilst automatic network selection is enabled, the MMI shall display an indication.
(M)

In idle mode, if the GSM Service Indicator (see [EN 301 515, Index [26]]) is lost, the mobile
shall give an audible and visual indication. (M)

### 5.7 Environmental and physical

Train-mounted equipment including the Cab radio terminal equipment, MMI and
antenna shall comply with all specifications in section 4 and all of those defined in this
section, with those defined in this section taking priority. (M)

Two types of mobile radio equipment will be mounted in rolling stock: in-cab
equipment and external equipment. Each type of equipment has slightly different
requirements placed upon it in terms of EMC and climate. ([UIC 651] is a useful
reference concerning the layout of cab equipment.) (I)

The Cab radio shall be capable of operating within a temperature range of -20°C to
+70°C. (M)

The aerial and any other equipment mounted external to the train shall be capable of
withstanding extremes of temperature from -40C to +70C. (M)

The aerial and any other equipment mounted external to the train shall function
correctly during rapid temperature fluctuations of up to 3°C/second. (M)

Any equipment mounted external to the train cab shall withstand the following
additional physical conditions: (M)

Measures should be taken to reduce the risk of theft of radio equipment. Examples of
such measures include physical protection, alarms and access control measures. (O)

Ease of maintenance should be taken into account in the design and installation of
radio equipment. For example, maintenance access to antennas on vehicles should be
provided. (O)

The “Subscriber Identity Module” (SIM card) shall be physically integrated with the
radio set and shall not be able to be removed except by maintenance staff. (M)

The Cab radio should be mounted in the train cab in compliance with [prEN 50261]. (O)

Any equipment mounted inside the train cab shall be capable of withstanding the
following maximum levels of sinusoidal vibration: (M)

Any equipment mounted external to the train cab shall withstand the following
maximum levels of sinusoidal vibration: (M)

The Cab radio shall comply with draft European standard [prEN 50124 part 1] concerning
insulation co-ordination with reference to clearances and creepages. (M

An emergency power supply should be provided for Cab radios which will enable the
driver’s radio to continue to operate for a period of 6 hours in the event of failure of the
train’s main power supply, based on the following cycle (see section 4.5.21): (O)

The Cab radio equipment shall be capable of withstanding the following changes to the
main and backup power supplies without interrupting normal operation: (M)

The Cab radio shall withstand the effects of power supply transients as defined in
[prEN 50155]. (M)

The driver and other in-cab equipment shall be protected against all electrical hazards
arising from EIRENE mobile equipment as defined in [EN 50153]. (M)

Requirements on EMC emissions for the Cab radio are to be more stringent than those
defined for other radio types due to close proximity to other train mounted control and
protection equipment, and higher transmission power. (I)

EMC emission from the Cab radio shall comply with [ENV 50121 parts 1, 2, 3-2 and 4]. (M)

Emissions from the train mounted antenna associated with the Cab radio shall be
limited to those specified by [EN 301 515, Index [35]]. (M)

Any emissions radiating into the driver’s cab and other on-board equipment from the
exterior aerial shall meet the requirements defined in [ENV 50121 parts 1, 2, 3-1, 3-2 and 4] to
the highest possible degree. (M)

The Cab radio shall pass electrical tests as defined in [IEC 571 parts 1, 2 and 3]. (M)

Additional guidelines on testing procedures may be taken from [prEN 50129] and [IEC
1508 part 1]. (I)

### 5.8 Cab radio interfaces to on-train systems


Where implemented, these interfaces are subject to the requirements stated in the
following sections. (I)

### 5.9 Train borne recorder

The Cab radio and the train borne recorder may be connected via the Train Interface
Unit (TIU) or may be connected directly by means of a nationally determined interface.
(I)

### 5.10 ERTMS/ETCS interface

Some Cab radios will be required to provide communications for ERTMS/ETCS. (I)

If ERTMS/ETCS communications are required, an interface as defined in the FFFIS for
EURORADIO [MORANE EURO FFFIS] shall be implemented. (M)

### 5.11 Public Address interface

If implemented, the Public Address interface should comply with the specifications of
the UIC Fiche [UIC 568]. (O)

### 5.12 UIC Intercom

If implemented, the UIC interface should comply with the specifications of the UIC
Fiches [UIC 558, 568]. (O)

### 5.13 Driver’s Safety Device

The Cab radio and the Driver’s Safety Device may be connected via the Train Interface
Unit (TIU) or may be connected directly by means of a nationally determined interface.
(I)

### 5.14 Other interfaces

Other interfaces may take the form of additional audio and data inputs and outputs. (I)

Where other data interfaces are implemented, they should be of the RS422 standard.
(O)

### 5.15 Train Interface Unit (TIU)

Where necessary, a Train Interface Unit may be implemented to adapt on-train systems
to the standard interfaces provided by the Cab radio. (I)

The interfaces between the TIU and the on-train systems are outside of the scope of
EIRENE standardisation. (I)

Figure 5-3 shows an example of how the Train Interface Unit may be implemented: (I)


### 5A Handling of calls

#### 5A1 Call arbitration table


#### 5A2 Call termination of outgoing calls table


#### 5A3 Call termination of incoming calls table


## 6 General purpose radio

### 6.1 Introduction

This section identifies the EIRENE applications which may be used in the General
purpose radio and the functionality to be provided by the General purpose radio is
detailed. (I)

### 6.2 System components

The logical architecture of the General purpose radio is illustrated in figure 6-1. (I)


A standard data interface shall be provided to allow a computer to be connected to the
radio. (M)

The General purpose radio shall operate as a standard GSM terminal, supplying
mobile services as defined in section 4. (M)

### 6.3 General purpose radio functions

Automatic self-testing of the radio shall use the GSM IMSI attach procedure. (M)

Upon switch on, once the radio is connected to a mobile network, it shall be able to
receive all calls made using the MSISDN or appropriate group call number. (M)

It shall be possible to register and deregister a functional number by the user entering
his functional number, which is transmitted to the ground along with the subscriber’s
IMSI, using USSD (see section 11). (M)

### 6.4 Environmental and physical

The full environmental and physical specification of the General purpose shall be as
close as possible to that of a Commercial-Off-The-Shelf (COTS) GSM mobile whilst
adhering to the specifications provided in section 4. (M)

The General purpose radio shall comply with the core climatic conditions defined in
section 4. (M)

SIM cards should be fixed into the radio to protect against accidental loss. (O)

No specific mechanical requirements need to be placed upon the General purpose
radio over and above those defined in section 4. (I)

General purpose radios shall be equipped with rechargeable batteries capable of
providing a minimum of eight hours operation over the temperature range +18°C to
+25°C from a single charge, based on the following cycle (see section 4.5.21): (M)

Changing the battery shall not result in the loss of data stored in the radio. (M)

The General purpose radio shall be suitable for use with a car adapter kit. (M)

The General purpose radio should comply with [EN 50081] (generic EMC for residential,
commercial and light industry). (O)

No specific testing procedures need to be used on the General purpose radio over and
above those given in section 4. (I)

## 7 Operational radio

### 7.1 Introduction

This section identifies the EIRENE applications which may be used in the Operational
radio and the functionality to be provided by the Operational radio is detailed. (I)

The logical architecture of the Operational radio is illustrated in figure 7-1. (I)


A standard data interface shall be provided to allow a computer to be connected to the
radio. (M)

The Operational radio shall operate as a standard GSM terminal, supplying mobile
services as defined in section 4. (M)

### 7.3 Operational radio functions

Automatic self-testing of the radio shall use the GSM IMSI attach procedure. (M)

Upon switch on, once the radio is connected to a mobile network, it shall be able to
receive all calls made using the MSISDN or appropriate group call number. (M)

It shall be possible to register and deregister a functional number by the user entering
his functional number, which is transmitted to the ground along with the subscriber’s
IMSI, using USSD (see section 11). (M)

Upon receipt of the call establishment request, the radio shall retrieve the stored
number for the appropriate controller from the SIM or other storage location. (M)

Once an appropriate number has been obtained, the radio shall initiate a call to this
number with ‘Railway operation’ priority (see section 10.2). Any functional number
associated with the user shall be passed to the network using UUS1 (see section 11.5).
(M)

Activation of the ‘Railway emergency call’ function shall cause the radio to initiate a
Railway emergency call as defined in section 13. (M)

The calling user’s functional number, if there is one, shall be passed to the network
using UUS1. (M)

The Operational radio should support direct mode communications as defined in
section 15. (O)

The Operational radio should support shunting mode communications as defined in
section 14. (O)

### 7.4 Shunting radio requirements

The requirements for shunting operations are detailed in section 14. (I)

### 7.5 Environmental and physical

The Operational radio shall comply with the basic standards defined for all EIRENE
mobile equipment in section 4. In addition, the Operational radio is specified to allow
its use in the operating environment experienced on the operational railway (eg
shunting and maintenance), with the specifications in this section taking priority over
those in section 4 where any discrepancy is identified. (M)

The Operational radio shall cope with rapid temperature fluctuations of up to
3°C/second. (M)

The Operational radio shall be capable of withstanding exposure to extreme
environmental conditions [IEC 721 part 1]. (M)

The Operational radio shall conform to IP 54 [IEC 529/EN 60529] as a minimum. (M)

SIM cards shall be fixed into the radio such that they can only be removed by the use of
a tool. (M)

The Operational radio shall be capable of withstanding the following shocks: (M)

The Operational radio user shall be protected against all electrical hazards arising from
the mobile equipment as defined in [EN 50153]. (M)

Operational radios shall be equipped with rechargeable batteries capable of providing
a minimum of eight hours operation over the temperature range -10°C to +55°C from a
single charge, based on the following cycle (see section 4.5.21): (M)

Changing the battery shall not result in the loss of data stored in the radio. (M)

The Operational radio shall be suitable for use with a car adapter kit. (M)

The Operational radio should comply with [EN 50081 part 2] (generic EMC for the
industrial environment). (O)

No specific testing procedures need to be used on the Operational radio over and
above those given in section 4. (I)

## 8 Controller equipment specifications

### 8.1 General

Functional requirements relating to controller equipment specifications can be found in
the EIRENE Functional Requirements Specification [EIRENE FRS]. (I)

### 8.2 Termination of VGCS/VBS calls

An entitled controller may terminate a VGCS/VBS call based on DTMF signalling [EN
301 515, Index [4] & [5]]. (I)

To terminate a VGCS/VBS call by DTMF signalling, the 3-digit sequence “***” shall be
used. (M)

In order to minimise the discomfort caused by the DTMF tone added in the voice
channel, the duration of the tone generated by the fixed line dispatcher shall be 70ms ±
5ms, and there shall be a minimum gap of 65ms between each tone. (M)

### 8.3 Muting and unmuting for VGCS calls

Muting and unmuting shall be in line with [EN 301 515, Index [4]]. (M)

A group call controller who wishes to start talking (except in the case of an originator,
a joiner or a re-joiner speaking for the first time5) shall indicate his wish, for example
by pressing the PTT button, whereupon the 3-digit DTMF sequence “###” shall be
transferred. (M)

The terminal of the controller should receive a single DTMF grant tone “#” of duration
100ms ± 5ms sent by the network if it has detected the 3-digit DTMF sequence “###”
and if the controller was not previously talking. (O)

Any group call controller who wishes to stop talking shall indicate his wish, for
example by releasing the PTT button, whereupon the 3-digit DTMF sequence “#**”
shall be transferred. (M)

The duration of each tone (see 8.3.2 and 8.3.4) added in the voice channel, shall be 70ms
± 5ms, and there shall be a minimum gap of 65ms between each tone. (M)

## 9 Numbering plan

### 9.1 General

International standardisation of the numbering plan is required to ensure interworking
between networks. Furthermore, standardised allocation of numbers to subscribers is
likely to facilitate schemes for identification, barring etc. (I)


The precise details of the numbering plan to be chosen for particular railways will
depend upon the railway network configuration, its interconnection with other
railway networks and its interconnection with public telecommunication networks.
Equipment design must therefore be such as to give maximum flexibility in numbering
arrangements. However, it may be generally assumed that numbers (excluding access
prefixes) will not exceed 15 digits in length and will consist entirely of the digits 1 to 9
and 0. (I)

Characters * and # may be used locally to gain access to special facilities such as short
code dialling. However, these arrangements do not form part of the network
numbering plan. (I)

Procedures for handling the relationship between EIRENE Numbers and MSISDN
numbers (ie registration, deregistration and re-registration) are specified in section 11.
(I)

Each railway should have appropriate call-barring facilities to prevent unintended
access to the GSM-R network by non-authorised users. (O)

### 9.2 Numbering plan requirements

Within each GSM-R network, each Train Number shall be unique for the period of the
journey. (M)

Every On-Train Function shall be identified by a standard code and shall conform to
the list of functions given in Appendix 9A of this section. (M)

All Train Function Numbers and their associated MSISDN numbers shall be stored in
the same routing database, which is the database of the GSM-R network in which the
train is currently operating. (M)

Every On-Engine Function shall be identified by a standard code and shall conform to
the list of functions given in Appendix 9A of this section. (M)

The Engine Function Number(s) and associated MSISDN numbers shall at any time be
stored as an entry in the routing database of the home GSM-R network6 of the engine.
(M)

The Coach Function Number(s) and associated MSISDN number(s) shall at any time
be stored as an entry in the routing database of the home GSM-R network of the coach.
(M)

Every Function shall be identified by a standard code and shall conform to the list of
functions given in Appendix 9A of this section. (M)

The functional numbers of the Shunting Team Members, Maintenance Team Members
and Train Controller (and any associated MSISDN numbers) shall be stored as entries
in the routing database of the home GSM-R network. (M)

Implementation of the EIRENE numbering plan shall not prohibit any authorised
caller from using the MSISDN number where known, thus enabling mobiles to be
assigned to particular personnel where this is appropriate. (M)

Service areas shall be defined within each railway network. (M)

The numbering of Service Areas for group calls and broadcast calls shall be made in
accordance with GSM Technical Specifications [EN 301 515, Index [21] & [4]] and [EN 301 515,
Index [22] & [5]] respectively. (M)

### 9.3 Numbering plan limitations

The EIRENE network can not be considered as a fully private network, as some parts
of either the mobile or fixed networks may be provided by public operators. This leads
to certain restrictions on the implementation of a numbering plan. These restrictions
are given below. (I)

To achieve integration of the EIRENE numbering plan with the national public
numbering plan, telephone numbers have to be allocated by the various numbering
regulatory bodies on a national basis. If functional numbers are to be used outside the
EIRENE network, they will require either a public number allocation or, alternatively,
an EIRENE Network Access Number (ENAN) may be used as described in 9.11 (I)

Each national railway should obtain a public numbering allocation for MSISDN
numbers from the relevant regulatory bodies. (O)

The EIRENE numbering plan shall be standardised to allow interoperability and shall
be implemented as a private numbering plan within the GSM-R network. (M)

In some countries Train Numbers are alphanumeric. These numbers do not comply
with a numbering plan that can be interpreted by telephone switches and are therefore
not supported by the call routing solution given in section 11. (I)

If alphanumerical numbering is required within a railway network, then these
numbers may either be translated at the user terminal into a subscriber number or
conveyed between the calling party and a routing database using a nationally
determined approach. (I)

### 9.4 Types of numbers


In addition, Breakout Codes (BCs) shall be used to allow users within the GSM-R
network to access external numbers. (M)

Access from the GSM-R network to external networks shall be as detailed in section
9.10. (M)

### 9.5 Use of National EIRENE Numbers

National EIRENE Numbers are used to set up calls within a single GSM-R network. (I)

Every railway network shall consider a number as a National EIRENE Number (NEN)
unless the number is preceded by an International Code, identifying another GSM-R
network. (M)

The National EIRENE Number shall consist of three distinct parts, as shown in figure
9-1: (M)



### 9.6 Use of International EIRENE Numbers

International EIRENE Numbers are used for calls between GSM-R networks.
Additional fields are added to the National EIRENE Number as routing indicators.
The use of such indicators is discussed in subsection 9.10. (I)

GSM-R networks shall recognise International EIRENE Numbers starting with the IC
of the GSM-R network in which the calling party is currently operating as National
EIRENE Numbers. (M)

The International EIRENE Number shall consist of three distinct parts, as shown in
figure 9-2: (M)

The fields of an International Functional Number shall be defined as follows: (M)

### 9.7 Use of MSISDN numbers

At least one MSISDN number shall be allocated to each mobile station. (M)

The structure of the MSISDN numbers shall comply with GSM Technical Specification
[GSM 03.03]. (M)

Within each GSM-R network, the following relationships between the MSISDN
Subscriber Number and the National EIRENE Number can be identified:

It shall be possible for authorised subscribers of fixed and mobile networks to call
mobiles using the appropriate MSISDN number. (M)

### 9.8 Use of Short Dialling Codes

For certain functions, standardised short codes shall be implemented for mobile
originated calls. (M)

Each short dialling code shall consist of four digits. (M)

Short dialling codes shall start with the first digit equal to 1 (ie CT=1). (M)

The short dialling codes can be defined on a national basis, but it is essential that
certain codes be used on an international basis in order to achieve interoperability.
These codes shall be as given in table 9-10. (M)

In addition, the network shall support the special short codes as defined in table 9-11.
(M)

### 9.9 Use of group addresses

Standardisation of UIC group addresses is required to provide interoperability
between the fixed railway networks within the GSM-R network. (M)

The group address consists of a Service Area (5 digits) and a Function Code (3 digits)
and has a Call Type 5 (see table 9-1). (M)

The Service Area shall be defined on a national basis. (M)

In network boundary areas, the Service Area shall be allocated on a bilateral basis. (M)

Function Codes shall be defined within the framework given in table 9-8 on an
international basis. (M)

### 9.10 Access to external networks

Access to other GSM-R networks shall be possible by using a Breakout Code (BC) as
part of the dialled number. (M)

Access to other GSM-R networks may be possible by using an Access Code (AC) as
part of the dialled number if the NSN (National Significant Number) following the CC
(Country Code) is assigned by the national telecommunication regulator to the GSM-R
operator. (O)
Note: NSN=NDC (National Destination Code) + SN (Subscriber Number)

The BC for access to other GSM-R networks is defined in table 9-12a, and is followed
by the full international EIRENE number of the called party. (M)


The AC for access to other GSM-R networks is defined in table 9-12b, and is followed
by the CC + NDC + SN of the other GSM-R network. The number format complies
with [ITU-T 164]. (M)


It is the responsibility of each individual GSM-R operator to acquire a public domain
NDC from their national telecommunications regulator. (I)

Access to private networks shall be performed by using a BC, defined in table 9-12c.
(M)

Note: All other CT9 numbers are reserved for railway national fixed networks and
systems.


The GSM-R network shall allow users direct access to public networks, subject to call
barring restrictions. (M)

Where access to public networks is allowed, this shall be performed by using an
Access Code (AC), defined in table 9-13, followed by the international or national
number of the called subscriber as defined in [ITU-T 164]. (M)

Deleted.


### 9.11 Calls from external networks to the GSM-R network

Access to the GSM-R network should be performed by dialling an EIRENE Network
Access Number (ENAN)8, followed by the relevant National or International
Functional Number as defined in subsections 9.5 and 9.6 respectively. (O)

Provision should be made to prevent unauthorised calls to mobiles from outside the
GSM-R network. (O)

### 9A Function Codes

Function Codes identify the actual user of a mobile. (I)

The Function Codes used in association with the Train Function Number (CT=2),
Engine Function Number (CT=3) and Coach Function Number (CT=4) shall conform
to table 9A-1. (M)


The Function Codes used in association with Maintenance Services Team Numbers
(CT=6) shall conform to table 9A-2. (M)


### 9B Numbering plan overview

This appendix provides an overview of the numbering plan as defined in this section
of the EIRENE SRS, detailing the allocation of numbers within the National and
International EIRENE Numbering plan. (I)


## 10 Subscriber management

### 10.1 Introduction

In order to provide a consistent level of service in each railway network and, in
particular, to ensure interoperability for train drivers and other users roaming between
networks, it is important to harmonise subscription details and other information
stored in the network. (I)

For the purposes of defining common subscription profiles, a number of subscription
types might be used, for example: (I)

### 10.2 Allocation of priorities

In order to provide a consistent international service, it is necessary to ensure that
priorities are allocated consistently across all railways. The following allocation of UIC
priority levels to eMLPP priority codes is mandatory: (M)


Levels 0 – 4 are designed to interwork with the ISDN MLPP service. (I)

### 10.3 Access classes

User access classes are defined in GSM so that under critical conditions, part of the
user population can be barred from accessing the network in order to avoid
congestion. However, such barring can be overridden by a user being a member of one
or more of the following special access classes: (I)

Access classes should not be used under normal network operating conditions, where
the GSM eMLPP may be used to provide a better grade of service to certain users. (O)

For consistent working on public networks and in international roaming, the use of
access classes in a railway network shall comply with the GSM specification. (M)

If special access classes (eg 12 - 14) are assigned within a railway’s network to certain
high priority users, it ought to be noted that when roaming, this will only have an
effect on a national public network, subject to bilateral agreement. (I)

### 10.4 Closed user groups

Closed User Groups (CUGs) may be employed by railways as an additional security
measure. Such facilities may be particularly important if public network access to the
radio system is provided (eg to prevent members of the public calling drivers and
drivers calling members of the public). (I)

Any implementation of CUGs must take account of requirements for interoperability.
(M)

### 10.5 Network selection

SIM cards shall contain a list of authorised networks so that networks shall be
displayed (or automatically selected if automatic network selection has been enabled)
in the following order of priority (see [MORANE SIM] for more details): (M)

In order to shorten the duration of the network selection procedure, Mobile Stations
designed for use in EIRENE networks shall give preference to the GSM frequency
band allocated for railway use (see 3.5.2). (M)

The use of “Over The Air” in conjunction with the SIM Application Toolkit [EN 301 515,
Index [36]] to update SIM cards in the home network is recommended (see [MORANE SIM]
for more details). (I)

### 10.6 Cell broadcast message identifiers

Railway mobiles shall be provided with cell broadcast message identifiers in order to
accept SMS-CB messages. (M)

### 10.7 Encryption and authentication

#### 10.7.1 Encryption.

Licensing of A5/x encryption algorithms is managed by the GSM
Association. (I)

In case of encryption, standardised ciphering algorithms shall be used. (M)

Deleted.

Mobiles shall be capable of operation using algorithms for all countries in which they
need to roam. (M)

#### 10.7.4 Authentication.

Each railway is free to implement its own authentication algorithms
without any resulting loss in cross-border interoperability. (I)

## 11 Functional numbering and location dependent addressing

### 11.1 Introduction

There is a requirement to be able to address communications to a ‘functional number’
rather than a more permanent subscriber number. Such numbers are generally only
associated with a user for a limited period of time. (I)

This is an important issue which will affect interoperability and the ability to use
public network services. There are specific features of individual railways which make
it difficult to develop a concise and universally acceptable system within GSM. (I)

To accommodate the different requirements of the individual railways, the following
approach has been adopted: (I)

### 11.2 Ground-train addressing

The ground-train addressing can be divided into two areas: (I)

The first is related to passing information to provide an association between a mobile’s
subscriber number and its functional number. The latter is concerned with ensuring
that calls from a mobile terminal (in particular, Cab radios) are routed to the correct
destination (ie primary controller, secondary controller), based on the current location
of the mobile. (I)

The numbering plan to be used with functional addressing shall be in accordance with
the numbering plan given in section 9. (M)

### 11.3 Functional numbering

Functional numbering provides the mechanism by which a mobile terminal, or an item
of equipment connected to a mobile terminal, can be addressed by a number
identifying the function for which it is being used. (I)

Mobile access to the functional numbering scheme for registration, deregistration and
re-registration shall apply the USSD messages and protocols over the air interface as
specified in the GSM Follow-me service. (M)

The implementation of functional numbering at a network level is left open for
national railways subject to the requirements for interconnecting EIRENE networks
identified in section 11.6. (I)

Further information may be obtained from [MORANE SSRS, MORANE FA FFFS, MORANE FA
FIS]. (I)

For communication over the (Um) air interface, the USSD messages and protocols as
specified in the GSM Follow-me service shall be used to manage the following types of
functional numbers: (M)

It shall be possible to limit user access to functional number registration and
deregistration facilities based on each of the types of functional number identified in
11.3.5. (M)

Mobile stations shall use the following sequences for the control of the functional
number management: (M)

Where SI Supplementary Information represents the International Functional Number
(also called the International EIRENE Number), as defined in section 9.6.3.
Note: This table is for information only. The Follow Me service control sequences are
based on the USSD specified in [EN 301 515, Index [15]].


The network operator shall implement the required functionality to validate the
information exchanged between the mobile and network on registration and
deregistration. (M)

The use of the forced de-registration mechanism (without notification) to achieve this
requirement is acceptable. (I)

The use of the forced de-registration mechanism (without notification) to achieve this
requirement is acceptable. (I)

The system shall require manual confirmation prior to the removal of the relationship
between Engine Number and MSISDN Number. (M)

The result of the registration procedure shall be sent back to the mobile. In the event of
a failure, an indication of the cause shall be provided. Information on the outcome shall
be provided to the mobile according to [EN 301 515, Index [17]] and [EN 301 515, Index [34]].
(M)

In the event of a registration procedure failing owing to the functional number already
being registered to another mobile, the Cab radio shall be capable of providing the user
with the ability to perform automatically the forced de-registration of the previously
registered mobile and the registration of this functional number to the user’s mobile.
This shall result in the following sequence of actions being performed by the user’s
Cab radio (see 11.3.7 for details of message structure): (M)

The functionality described in 11.3.9i should also be available for other types of
mobiles. (O)

In the cases described in 11.3.9i and 11.3.9ii, national rules may dictate that, prior to or
instead of performing the sequence described in 11.3.9i steps 1-7, the user shall
perform a specified action (e.g. call a dispatcher in the case of drivers). (I)

The sequence described in 11.3.9i steps 1-7 may be interrupted or may require
additional user action such as a confirmation. (I)

Deregistration shall only be performed by the subscription identified by the MSISDN
number which is associated with the functional number. (M)

Deleted.

The result of the deregistration procedure shall be sent back to the mobile. In the event
of a failure, an indication of the cause shall be provided. Information on the outcome
shall be provided to the mobile according to [EN 301 515, Index [17]] and [EN 301 515, Index
[34]]. (M)

Re-registration consists of a registration procedure followed by a deregistration
procedure. (I)

Re-registration of on-train functional numbers based on the train number shall be
performed every time a train leaves one EIRENE network and enters into another
EIRENE network. (M)

Deregistration of a functional number shall not be carried out until registration of the
functional number has been carried out and confirmed as being successful. (M)

Each railway should define a suitable time-out interval to be applied as part of the
deregistration procedure for on-train functional numbers. (O)

The exchange of information between EIRENE networks is handled by the GMSCs and
shall use the standardised protocol as detailed in section 11.6. (M)

### 11.4 Re-establishment of functional number correlation

In the event of losing correlation between functional numbers and MSISDNs, provision
for recovery from such a situation shall be made. (M)

Each national railway is responsible for implementing a suitable recovery mechanism
and ensuring that the use of unverified functional numbers is prevented. (I)

Deleted.

Deleted.

Deleted.

### 11.5 Presentation of functional identities

The called party functional identity shall be presented to the user initiating a call and
the calling party functional identity shall be presented to the user receiving a call. (M)

The calling party functional number shall be passed to the receiving mobile using the
User to User Signalling supplementary service (UUS1) during call setup. (M)

If the calling party functional number is not available or if the calling party is not
registered then the CLI of the calling party shall be displayed on the receiving mobile's
display. (M)

The user-to-user information element in the SETUP, ALERT or CONNECT messages,
as defined in [EN 301 515, Index [16]], shall be used to transfer the functional number of the
calling party to the called party. (M)

The user-to-user information element shall use the following format: (M)


If no valid functional number is available, a fixed length User-to-User Information
Element shall be used with the following format: (M)


Further information may be obtained from [MORANE PFN FFFS, MORANE PFN FIS]. (I)

### 11.6 Inter EIRENE network interfacing

Interconnection of EIRENE networks is required to allow international call routing. It
is not envisaged that any routing database information is exchanged between EIRENE
networks. (I)

The interconnection of EIRENE networks should take place by interconnecting GMSCs.
(O)

The protocol used for routing of calls shall be Signalling System No 7 (SS7) as defined
by the ITU-T. The signalling system suite shall include the Mobile Application Part
(MAP). (M).

Call setup between EIRENE networks using international functional numbers shall be
based on the combination of the Breakout-Code (BC) and International Code (IC) as
specified in section 9. (M).

The Country Code (CC) followed by the National Significant Number NSN (as
specified in ITU-T E.164, Chapter 6.2) shall be used as the Global Title, which forms
part of the Signalling Connection Control Part (SCCP) protocol messages and is used
for inter-network routing of messages. (M)

### 11.7 Location dependent addressing

Location dependent addressing may be provided in the following ways:

As a minimum, call routing using location dependent addressing shall be based on the
use of short codes in conjunction with cell dependent routing. (M)

Further information on cell dependent routing for location dependent addressing may
be obtained from [MORANE SSRS] [MORANE LDA FFFS] [MORANE LDA FIS]. (I)

Location information may be provided by systems external to the radio system, for
example ground-based systems such as track circuits. (I)

If a more accurate way of location determination is used, then position information
shall be provided to the radio system which shall be used to associate the short code
with the correct called party subscriber number. (M)

If implemented, the use of location information from train-based systems external to
the radio system shall comply with the requirements stated in the enhanced Location
Dependent Addressing FRS and IRS [eLDA FRS and eLDA IRS]. (M)

### 11.8 Calls from external networks to the EIRENE network

Facilities shall be provided to prevent unauthorised calls to mobiles either by
functional number or MSISDN number from outside the EIRENE network. (M)

## 12 Text messaging

### 12.1 Introduction

There is no requirement for an internationally standardised pre-defined messaging
application. However, it is anticipated that individual national railways may have a
requirement for pre-defined messages, in which case the application will be specified
as part of individual national procurements. (I)

### 12.2 System requirements

Where text messaging is implemented in the network, the Short Message Service (SMS)
shall be used. (M)

## 13 Railway emergency calls

### 13.1 Introduction

This section covers the use of the EIRENE radio system for Railway emergency calls.
The section also discusses the facility for confirmation of such emergency calls and the
storage of confirmation for post-incident analysis. (I)


A Railway emergency call is a high priority call for informing drivers, controllers and
other concerned personnel of a level of danger requiring all Railway movements in a
pre-defined area to stop. Two types of Railway emergency calls are defined: (I)

This section describes the handling of high priority voice calls for Railway operational
emergencies and does not cover public emergency calls (ie handling of ‘112’ calls). (I)

### 13.2 Provision of Railway emergency calls

Railway emergency calls are defined as those calls of ‘Railway emergency’ priority (see
section 10) which are routed to a pre-defined user or group of users due to a railway
operational emergency. (I)

All Railway emergency calls shall be implemented using GSM VGCS (Specifications
[EN 301 515, Index [21] & [4]]). (M)

It shall be possible to configure Railway emergency group call areas to contain
combinations of cells controlled by one or more MSC(s) within one or more network(s).
(M)

Where Railway emergency group call areas are controlled by more than one MSC
within one or more network(s), a unique anchor MSC is defined for each group call
area. (I)

For international Railway emergency calls, in order to minimise call set-up times, it is
recommended that the anchor MSC always directly controls the cell where the Railway
emergency call was originated. (I)

### 13.3 Initiation of Railway emergency calls

A Railway emergency call shall be initiated by using the appropriate function code for
the required type of Railway emergency call (see Table 9-8). (M)

The call area and list of train controllers for each emergency group call will be fixed in
the Group Call Register (GCR) of the anchor MSC. (I)

The Railway emergency group IDs required for interoperability are defined in section
9.5. The composition of each group is a matter for national implementation, although
all areas shall have a group defined for all mandated Group IDs. (M)

### 13.4 Receipt of Railway emergency calls

Each mobile shall store a list of emergency Group IDs in the SIM appropriate to its
function (the Cab radio will store Group ID 299 and 599 - see table 9-8). (M)

All Railway emergency group IDs required for interoperability and appropriate to the
operation of the mobile shall maintain active status whilst the mobile is powered up.
(M)

The fixed network user will only receive emergency voice calls if designated a
dispatcher or group member in any of the calls defined in the GSM GCR. (I)

On receipt of a Railway emergency call, the controller’s display should indicate the
location of the train. (O)

If the requirement in 13.4.4 is implemented, as a minimum the location information
shall be provided by the GSM network (eg current cell or base station serving the
mobile). (M)

The mechanism for transferring the functional number of the originating mobile to
controllers is defined in [EN 301 515, Index [6], Release 4] using the Information Element
“Compressed OTDI” in the Immediate Setup 2 message from the originating mobile.
(I)

If the GSM Release 99 capability and the Immediate Setup 2 feature defined in [EN 301
515, Index [6], Release 4] are supported by the network, the network shall set the MSC
Release bit in the “Control Channel Description” information element to “1”.
Otherwise, the MSC Release bit in the “Control Channel Description” information
element shall be set to “0” (zero) [EN 301 515, Index [41]]. (M)

### 13.5 Confirmation of Railway emergency calls

For post-incident analysis it is important that the initiation and receipt of Railway
emergency calls by mobiles is confirmed by a message sent to a ground-based location
(and also registered in the train borne recorder, in cases where a train borne recorder is
connected to the Cab radio). (I)

Not all calls require confirmation. The application must be able to deduce that a
confirmation is necessary from the call priority, as all calls of ‘Railway emergency’
priority must be confirmed. (M)

Confirmation of Railway emergency calls shall be implemented using the User to User
Signalling supplementary service (UUS1). (M)

After clear down of the Railway Emergency call, the mobile application shall start the
confirmation process by automatically originating a call. In order to avoid network
congestion the call set up shall be delayed by a random offset. (M)

Railway Emergency call confirmation messages shall be of eMLPP priority 4 -
“Railway information and all other calls” (see section 10.2). (M)

The user information contained in the confirmation message shall be: (M)

Confirmation messages shall be sent to a confirmation centre using a defined short
code (see table 9-10), which shall be associated with the GSM network. (M)

In the case of Cab radio, details of the confirmation shall be passed to the train borne
recorder if a train borne recorder is connected to the Cab radio. (M)

The user-to-user information elements in the following messages, as defined in [EN 301
515, Index [16]], shall be used for the confirmation of high priority calls: (M)

The SETUP and RELEASE COMPLETE user-to-user information element shall be as
specified in the [MORANE UUIE]. (M)

Confirmation centres shall be capable of decoding messages in either format A or B.
(M)

Deleted.

Deleted.

## 14 Shunting mode

### 14.1 Introduction

The purpose of shunting mode is to provide an effective means of communication to a
group of personnel who are involved with a shunting operation. (I)

The shunting group may comprise a shunting leader, a shunting driver, a controller
and up to three additional personnel (the shunting members). (I)

Further information about shunting mode may be obtained from [MORANE SM FFFIS]. (I)

### 14.2 System requirements: Operational Radio

On entering shunting mode, the operational radio shall determine if any shunting
group ID is already activated on the SIM. (M)

If a shunting group ID is activated, the operational radio shall proceed to re-establish
the group call. (M)

If no shunting group ID is activated, the operational radio shall initiate a “regular
shunting mode ON” procedure as detailed in table 14-1. (M)


After the “regular shunting mode ON” procedure has been completed, the procedures
shown in table 14-2 and 14-3 shall be used to register the shunting leader and shunting
members to a dedicated group call. (M)



Two possibilities shall be available to the shunting leader when leaving shunting
mode: (M)

On leaving shunting mode, the Operational radios of shunting members shall follow
the procedure shown in table 14-6. (M)

### 14.3 System requirements: Cab radio

On entering shunting mode, the Cab radio shall determine if any shunting group ID is
already activated on the SIM. (M)

If a shunting group ID is activated, the Cab radio shall proceed to re-establish the
group call. (M)

If no shunting group ID is activated, the Cab radio shall initiate a “regular shunting
mode ON” procedure as shown in table 14-7. (M)


The Cab radio shall exit shunting mode by means of the “Leave shunting mode”
procedure as defined in table 14-8. (M)


### 14.4 System requirements: Operational radio and Cab radio

On entering shunting mode, the terminal shall initially select the common shunting
group. (M)

The common shunting group provides a point of contact for leaders and team
members to set up a dedicated shunting group call for their shunting operation. (I)

The terminal application shall prevent members of a dedicated shunting team from
initiating a new call (unless they are registered as shunting team leader and have left
shunting mode using the “maintain group call” function described in 14.2.4). (M)

Deleted

### 14.5 Numbering plan

The full numbering plan for shunting mode group calls is defined in subsection 9.9. (I)

Valid group IDs shall be as defined in table 14-9. (M)

### 14.6 Control of shunting group membership

Users shall be prevented from joining a dedicated shunting group by the EIRENE
terminal application unless a valid functional number for the group has been
successfully registered to the GSM-R network by their terminal. (M)

Deleted.

Deleted.

### 14.7 Link assurance signal

Deleted

The link assurance tone shall be of the form specified in subsection 14.4.2 of the [EIRENE
FRS]. (M)

The mechanism for the generation of the link assurance signal shall be as specified in
[MORANE SM FFFIS]. (M)

Deleted.

The mechanism for the deactivation of the link assurance signal shall be as specified in
[MORANE SM FFFIS]. (M)

## 15 Direct mode

### 15.1 Introduction


### 15.2 System requirements

Implementation of direct mode is optional. However, where implemented, the
following requirements shall be mandatory. (I)

Frequency modulated equipment conforming to [ETS 300 086] shall be used for direct
mode. (M)

Direct mode equipment shall have a maximum transmit power of 1 Watt. (M)

Direct mode equipment sensitivity shall be at least –107dBm. (M)

Direct mode equipment shall be capable of operation in the channels defined in table
15-1. (M)

Direct mode shall operate in simplex mode, a radio link that uses a single frequency for
alternate transmission and reception. (M)

Voice transmission from direct mode equipment shall be possible only when the Push-
To-Talk (PTT) button is pressed. (M)

Continuous Tone Coded Squelch Systems (CTCSS) shall be implemented on all direct
mode equipment. (M)

The CTCSS tone shall be at a frequency of 203.5 Hz. (M)

The CTCSS modulation shall be within the limits defined in table 15-2. (M)


The purpose of the common access channel is to provide a point of contact and
information for all direct mode users. For example, if one direct mode user wished to
initiate contact with another user, communication would begin with a request for the
desired partner on the access channel. After receiving a reply, both parties may transfer
to a free direct mode channel and continue. (I)

Direct mode channel 1 (876.0125 MHz) shall serve as the common access channel. (M)

Equipment should default to operation on the common access channel (direct mode
channel 1) on entry into direct mode. (O)

Direct mode communications will only be used in the event of normal GSM-R services
being unavailable. (I)

The presence of the GSM-R network shall be indicated to direct mode users. (M)

All terminals shall ensure that when GSM-R services are available, the user is
prevented from entering direct mode. (M)

In the event of GSM-R causing disruption to ongoing direct mode communications,
each railway will define a protocol for re-establishing contact by means of GSM-R. (I)

All direct mode equipment shall provide the facility to broadcast an in-band audio
shunting link assurance signal as defined in subsection 14.4.2 of the [EIRENE FRS]. (M)

## A References

### A.1 List of normative references


### A.2 List of informative references

