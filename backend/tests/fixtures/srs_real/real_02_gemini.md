# Gemini 8m Telescopes Control System Software Requirements Specification

> **Dataset:** PURE Dataset (Zenodo 7118517 / IEEE RE 2017)
> **Original Document Title:** Gemini Software Requirements Specification
> **Domain:** Scientific Observatory Control
> **License:** Open Access (NSF/AURA)
> **Source/Project:** https://www.gemini.edu
> **Version:** 1.0

---

## 1 Introduction

### 1.1 Purpose

The document defines the operational requirements for Gemini Control System software. The goal of the SRS is to provide a functional tool for 
guiding the development of controls and data acquisition systems in a manner consistent with their operation within the Gemini System. 
It establishes both general criteria and specific functional requirements for software and controls design in the Gemini Project.

### 1.2 Scope

It is oriented toward the developers of control and data acquisition systems, not toward the science user of the Gemini telescopes. 
As such, it logically follows the Operational Concepts document, which addresses the control of the Gemini system from a more general 
perspective. The impacts of the science requirements, as well as requirements of control system design are covered in this document.

## 2 General Description

### 2.1 System Users

The users of the Gemini system are classified into the following categories.

### 2.2 Operational Levels

The Gemini system, when powered on, exists in one of several disjoint operational 
levels. Access to the system is restricted according to the current level of operation.
The operational levels are:

### 2.3 Access modes

At any level, but particularly during observing level operation, the software imposes
on the Gemini system a series of access modes. These access modes balance ease and
convenience of use against flexibility, control, and the security of the system.
The access modes provided by the Gemini system are:

### 2.4 Locations of users of the system

Users of the system will be located at one or more facilities. These are referred to in general
as Gemini 8m Telescopes operations facilities. The Gemini 8m Telescopes enclosure
and Gemini 8m Telescopes control facility are referred to collectively as the Gemini 8m
Telescopes site.

#### 2.4.1 Gemini 8m Telescopes Enclosure

This is the enclosure housing the telescope. In general such use would be limited to maintenance
and engineering.

#### 2.4.2 Gemini 8m Telescopes Control Facility

This is the facility collocated with the enclosure. It is from here that nightly operations
would take place.

#### 2.4.3 Gemini 8m Telescope Site Support Facility

This is the facility where off duty personnel reside while stationed on the summit.
This would be the Hale Pohaku facility on Mauna Kea and Cerro Tololo in Chile
(assuming no support facility is constructed on Cerro Pachon).

#### 2.4.4 Gemini 8m Telescopes Base Facility

This is the facility where offices, shops, etc. are located. On Hawaii this would be
with the JACH in Hilo and in Chile it would be either the La Serena or Cerro Tololo
facilities.

#### 2.4.5 Gemini 8m Telescopes Base Facility

These are super sites, in general located in partner countries, which have direct links
to the telescopes via communications lines. They may or may not be collocated with
any administrative organization associated with the Gemini telescopes. These sites
have remote operations capability

#### 2.4.6 Satellite Site Facility

These are sites with high bandwidth connections to the super sites. They have remote
operations capability but at a reduced level.
Will these high bandwidth connections be private or public, or doesn’t it matter? I
don’t understand the different between a remote operations facility and a satellite site.
Why does the satellite site not just connect directly to the telescope? — Steven.

#### 2.4.7 Institutional Site Facility

These are sites, generally located at existing observatories, universities, etc. that have
some form of connectivity, perhaps via satellite sites and/or super sites, to the telescopes.
Although they have remote operations capability, the link capacity will determine
at what level.

### 2.5 User-level requirements

#### 2.5.8 User Needs

Each class of users has different needs of the system. The general requirements of each
user class are summarized below.

#### 2.5.9 Users of the System

Unless the contrary is explicitly stated, all requirements and modes presented are
intended to be available to all users of the system.
It should also be noted that what the system has to guarantee in terms of operations
must fulfill all possible requirements, but it does not mean that all features will be
made available to all users at all locations at all times.
The available capabilities will have to be adapted to the operational needs both
locally and remotely and these decisions can only be taken later in the life of the
project.

##### 2.5.9.1 Astronomers and observers

##### 2.5.9.2 Operations staff

##### 2.5.9.3 SOftware development and maintenance staff

### 2.6 Operational context

This section derives directly from Gemini 8m Telescopes program requirements 
and speciﬁes the operational context, which is a direct consequence of the structure of the Gemini 8m Telescopes system.
The Gemini 8m Telescopes operation has to cope with a complex environment produced by:

#### 2.6.1 Multi-telescope context

Although there are two telescopes as part of the 
Gemini system there are no plans to support concurrent use 
of them as if they were a single facility. It is, however, a long term goal 
of the Gemini project to be capable of being used in conjunction with nearby, 
perhaps non-Gemini, telescopes on the same site (for instance for interferometry).

#### 2.6.2 Multi-instrument context

Normally three scientiﬁc instruments are mounted on the cassegrain 
focus of the telescope. The Gemini 8m Telescopes are thus characterized all the 
time as in a multi-instrument context.
Parallel access to all the mounted instruments shall be provided, though only 
one instrument has access to the telescope beam (active instrument).Instruments 
which feed two detectors by using beam splitters or ﬁeld splitters is considered as a 
single active instrument. Feeding two separate instruments via beam splitters or 
ﬁeld splitters and providing separate control nodes is not a requirement.
Various situations are possible for the other (inactive) 
instruments:

Regardless of the status of an inactive instrument, it shall not be possible for any of its permitted 
actions to adversely impact the active instrument

#### 2.6.3 Visitors instrument context

The requirement to provide for support, installation, and operation of outside instruments brought by the observer has several implications for the system. Due to the specialized nature of visitor instrumentation it is unlikely that complete integration into the Gemini environment is either feasible or warranted. In this case a subset of the available functionality must be made available through a standardized interface. The Gemini Telescopes view all instruments as operating as servers, responding to commands from the upper levels of the system. Visitor instruments must be capable of operating in this mode to be adequately supported.
It should be the goal of this interface that it be a 
subset of the existing instrumentation interface 
(rather than a separate system). At a minimum this interface should support:

It should be a goal, but not a requirement, that the interface provide support for

Due to the nature of visitor instrumentation it is unlikely that 
more complicated functionality can be supported. In particular coordinated 
motions of the Gemini system components with those of the visitor instrument (other than simple raster scans) will not be supported.
This does not mean that more complicated functionality will not be 
possible for visitor instruments that require it. Such functionality will 
not be offered as a standard service but will require a joint effort on the part
 of Gemini and the visitor instrument team. As more complicated functionality 
will be supported via standardized interfaces for the Gemini instruments, such 
as coordinated motions, it should be possible to adapt visitor instruments to this 
standard. The difﬁculty with offering such services as an externally supported standard, 
as opposed to an internally supported standard, is that decisions to change internal 
standards do not impact external users.
It is important that the visitor instrument interface be stable and long-lived, as the 
time between successive uses of the same visitor instrument can be as long as one or two years.
The support of visitor instrumentation is made simpler if the visitor equipment 
adheres to the Gemini standards. However it must be recognized that:

For these reasons it is probably not possible to establish a combined standard to which all instruments, 
both Gemini and visitor, adhere to completely. It is much better to establish a subset of Gemini facilities which will be
 made available to visitor instruments via long lived, stable interfaces. 
Visitor requirements outside of these would be handled on an as needed basis.
The support of both Gemini and visitor instruments would beneﬁt by 
the provision of a Gemini observatory simulator. This simulator, 
appearing to the instrument as a standard set of hardware and 
software interfaces, would present a functional deﬁnition of the observatory

#### 2.6.4 Multi-user context

The requirements to have instruments operated as single units 
imply that several user stations will be active at the same time on the Gemini 
8m Telescopes. On these user stations, different kinds of users may be working at the 
same time with the Gemini 8m Telescopes software.
Independently of the location of users at the telescope site, they shall be able to access
 (according to their privileges) any part of the whole setup with a simple logon and conﬁguration operation. 
In other words. any subsection of the whole Gemini 8m Telescopes system should be accessible and controllable from 
any single point (but of course with protection ensuring security and safety).
A particularly simple case of multi-use of the system is multi-point monitoring. By this it 
is meant that, while some (active) user is in control of the Gemini 8m Telescopes, someone 
else can follow what they are doing by monitoring all the relevant data from telescope and 
instruments. This will typically be needed by the operation supervisor. All other users wishing 
to monitor Gemini 8m Telescopes operations have to go through the procedures set up by 
Operations and get permission to do so.
The multi-point monitoring mode might also be important when certain difﬁcult or rare problems 
occur, when expert advice is needed and can only be obtained from colleagues situated remotely.
 Multi-point monitoring allows them to follow directly the results of tests performed and 
investigate how the system is working (e.g. by selecting different display pages with the
 up-to-date status information on different parts of the system).
Multi-point monitoring also allows a local observer to be monitored and advised by a remote 
supervisor.
Monitoring shall exist both in the form of automatic displays of status information at different 
locations, and in the form of explicit access to the required status information from any point.
Monitoring shall not affect the performance of ongoing observations.

### 2.7 Observing model requirements

The different observing modes (interactive, queue-based, 
remote-operations and service) impose constraints on software design.

#### 2.7.1 Interactive observing

Requirements:

Interactive observing with time allocation for full nights is a ﬁrst basic
 requirement of the Gemini 8m Telescopes. It is therefore an essential requirement
 that telescope operation is supported by the software in a smooth and very friendly way 
in this mode.
Interaction will normally be via an automatic sequencer 
(see Section 2.5.9 on page 2-6). This is clearly a top priority requirement and one 
which will have to be realized before implementing any other mode. The initial implementation 
of the automatic sequencer will operate in a “pass through”mode where
 all commands are accepted and transmitted with
 minimal checking and delay.

#### 2.7.2 Queue-based

Queue-based observing is the primary observation mode used with the Gemini 
telescopes, as it is the best means of providing sound science data while maximizing 
efﬁcient use of the telescope. While its requirements include all those given below for service 
observing, it has the following special requirements.

Thus queue scheduling is a superset of preprogrammed 
observing, with similar requirements. As the costs of implementing 
such a scheduler are currently difﬁcult to estimate it may prove 
necessary to implement it in a future phase of the project. The system design, 
if it does not include a scheduler, should speciﬁcally allow for its future 
implementation.

#### 2.7.3 Remote operations

Remote operations includes both remote observing, 
with the science observer offsite, and remote telescope operation, with 
control of the telescope also off- site. It also covers remote eavesdropping, 
monitoring, conﬁguration, and diagnosis. (There will always be support staff 
on-site during observations, however.) The requirements for supporting remote 
operations are:

The choice of the name remote operations is meant to suggest an entire category of operations, such as remote observing but also remote access for diagnostic support. In this sense it is more general than pure remote observing.
Despite the obvious limitations introduced by the link bandwidths available at the different locations, the system shall be totally transparent to local or remote use.   It is only necessary that the functionality of the system be transparent, it is accepted that the speed of the link will determine the perceived transparency of the system. However the system design should minimize the impact of link bandwidth on transparency.
Security of operation shall be considered and might imply different operation levels and privileges at different sites.
It is required that the remote operations software be considered from the 
beginning in the Gemini 8m Telescopes software design, to avoid redesign later. 
This should reduce the amount of speciﬁc software needed for remote operations, 
as the common layers of software shall cope from the beginning with a 
distributed environment.

##### 2.7.3.1 Remote control

Remote control means that the function normally associated with a
 local Telescope Operator, that of entering telescope control commands, would be
 available from a remote site. In practice remote control will be restricted to the 
Gemini 8m Telescopes Enclosure and Gemini 8m Telescopes Control Facility. The philosophy
behind this is that, for safety considerations, telescope control commands cannot be issued 
without a staff member (not necessarily the same person) having direct access to:

##### 2.7.3.2 Remote Observing

Remote observing means that users shall be able to observe from a
 remote site such as Cerro Tololo, Hilo or even home Institutes. This possibility 
has to be provided on the Gemini 8m Telescopes.
The extent to which realistic observing conditions can be reproduced depends,
 of course, largely on the link bandwidth available. Experience with previous 
telescopes at other
OBSERVING MODE REQUIREMENTS
observatories shows, however, that, even with very limited bandwidths, 
remote observing can be implemented, provided the software is suitable for this.
Remote observing, as meant in this context, does not mean remote control. 
Remote users shall normally interact with the system via

In the last case they will use a remote User interface to 
submit commands to the Gemini 8m Telescopes scheduler at the Gemini 
8m Telescopes site.

##### 2.7.3.3 Multipoint Monitoring

In this mode the monitor's screen appears as a duplicate of 
that seen by the observer. The monitor's keyboard would not have 
any effect on the observer's environment

##### 2.7.3.4 Remote Monitoring

Remote monitoring is the simplest level of remote observing. It is 
sometimes called 'eavesdropping'. It is a requirement for the Gemini 8m Telescopes
operation and will complement service observing, making it friendlier for users. Remote 
monitoring coincides to a large 
extent with multipoint monitoring, 
but allows the remote user to “pick and choose” the information that is displayed
 on the remote screen. There is no requirement that the remote screen be a duplicate
 of the local screen. The remote keyboard will have no effect on the local user's environment.
A remote observer might also need a real-time video and voice link with the operator
 in the control room, perhaps using a portable video camera which the operator can 
position as necessary. It is assumed this facility is provided entirely by hardware, and 
is beyond the scope of the Gemini software.

##### 2.7.3.5 Remote Access

Quite apart from remote observing, remote access to the Gemini 8m 
Telescopes and its instruments is required for monitoring and diagnostic purposes. 
This might be necessary to back up local users expertise and to help in case of problems. 
Remote access, in this case, must be possible from the Gemini 8m Telescopes base facility.
Distributed access to the Gemini 8m Telescopes software, once implemented. also allows, 
without extra requirements, local access (at the Gemini 8m Telescopes site) or remote access 
(Gemini 8m Telescopes support, base, and remote operations facilities).

#### 2.7.4 Service

Service observing implies that the Gemini staff 
are responsible for performing the actual data collection for the astronomer. 
A special case of service observing, queue-based, is given earlier, and assumes 
that the observing program can be executed with minimal interaction with the client 
astronomer. The more general case, where a science observer is present on site and the client 
astronomer is remotely connected, is considered here. The requirements speciﬁc to service 
observing are:

Observing, as such, is the purpose of the Gemini 8m Telescopes system. 
But interactive observing is perhaps, in some cases, not the most efﬁcient way to achieve 
this, although it will be necessary for certain kinds 
of observations (such as adaptive optics) and in certain phases (such as commissioning 
and test periods).
Service observing, on the other hand, means that the observing 
program can be performed by someone other than the proposing
 astronomer. It will be done on his behalf at a convenient moment 
that is not exactly predeﬁned and may be intermixed with programs from other users.
Service observing requires switching during the night among telescope modes and instruments. 
This might typically be a few times (2) per night, when sky conditions change.
It requires also that the observing program is so well speciﬁed that it can be executed by 
someone else. In other words, it requires a computer executable observing program.
Service observing requires a suitable organization to support it, and ﬁrst of all, considerable 
experience with a smooth running system. For these reasons it can only be applied to the 
Gemini 8m Telescopes once the Classical observing requirement has been fulﬁlled and been 
in operation for a while. Nevertheless, the software and data structures to support classical 
observing which have to be present in a system that is only interactive at the start might 
require considerable redesign to be adapted later to the service observing requirement

### 2.8 Observing Support

#### 2.8.1 Planned Observing

To achieve efﬁcient service observing, queue observing, and ﬂexible scheduling, 
it should be possible to carry out observations automatically, in accordance with predeﬁned 
sequences of exposures, as is commonly done in space observatories.
This corresponds to what is meant by planned observing, which still requires competent 
monitoring at the Gemini 8m Telescopes site or remotely.
At the same time, one does not want to lose the advantages and the extra
ﬂexibility of ground-based astronomy. So whichever scheme is adopted to
perform automatic sequences, interaction shall be allowed at the desired 
level (for example, only on error conditions, 
any time the user is allowed to break a sequence, etc.).

#### 2.8.2 Flexible Scheduling

Flexible scheduling means the possibility of reacting to 
changes in weather and other conditions by allocating the current use of the 
telescope to the optimal observing program for those conditions.
It will require the use of service and/or remote observing, as 
users cannot stay around indeﬁnitely waiting for the conditions required by 
their program. This can be complemented by remote monitoring, if users can be 
on standby at a suitably equipped remote site.
Flexible scheduling requires the possibility to change telescope scheduling 
quickly, exchanging observing programs. This can be achieved only with the 
help of appropriate scheduling software, which must advise the operations team 
on the best choice to make which is compatible with the relative priorities of the 
various observing programs. It should be recognized that such ‘expert scheduling’ 
software does not currently exist - it should be a requirement of such software that 
it have an operational mode which merely supports the decision making process by 
presenting appropriate information.
Flexible scheduling requires switching during the night among telescope modes and 
instruments (typically 2 times per night). Thus ﬂexible scheduling is a superset of 
queue scheduling, with similar requirements.

### 2.9 General Softwar Requirements

#### 2.9.1 Control information flow

These requirements apply to the commands and replies 
between sub-systems (including status information requests and replies), 
information ﬂow to and from on-line databases, and commands 
and software for the IOCs.

##### 2.9.1A Requirements

#### 2.9.2 Astronomical data flow

The following requirements apply to the control and transfer of 
astronomical data in all forms (science, engineering, reference, etc.)

##### 2.9.2.1 Requirements

#### 2.9.3 Video information Flow

Video information originates from target acquisition, guiding, and site 
monitoring cameras. The requirements for transferring video data are:

### 2.10 Operation Privileges, Protections, and Procedures

To preserve the integrity of the system, there must be a system of privileges 
established at each operating level of the system. These privileges should be determined in 
a simple manner during logging into the system.
Protection against accidental interference is to be implemented using an Access Mode Allocation 
system that dynamically identiﬁes and assigns resources as needed. Critical resources 
(those that can support only a restricted number of simultaneous uses) are assigned solely 
through this allocation system. The allocation system must ensure that the system cannot 
remain deadlocked with respect to this resource allocation.
Finally, procedures must be implemented for convenience and system integrity, to simplify 
and codify common tasks. The tasks that require such procedures include:

### 2.12 Test and checkout Requirements

The telescope and instrument software shall contain built-in test (BIT) 
facilities to verify Gemini 8m Telescopes system and Gemini 8m Telescopes software 
performances.
Every Gemini 8m Telescopes software module shall have corresponding test speciﬁcations 
to check normal operation of releases, to be used both for acceptance tests and as an on-line 
test procedure.
The Gemini 8m Telescopes control software shall also provide for execution of self-test 
sequences of the Gemini 8m Telescopes system and subsystems. These shall automatically 
exercise all subsystems present in a given operational conﬁguration.
Regression tests should be a part of every Gemini 8m Telescopes software package

### 2.13 Contingencies

#### 2.13.1 Fault Notification

Subsystems must notify the user when faults occur. This notiﬁcation must be 
speciﬁc as to origin and problem. The notiﬁcation must also be capable of being electronically 
logged. It may also prove useful to have multiple levels of fault notiﬁcation such as detailed, 
verbose, short, etc. to aid in tracking down problems.

#### 2.13.2 Fault tollerance

Should a subsystem fail (e.g. one detector, one instrument) predeﬁned 
procedures must exist to redeﬁne the environment in such a way that operation can 
restart with the remaining equipment.
In case of computer hardware failure concerning the user station equipment, it shall 
be possible to transfer control from one user station to another via a simple software 
reconﬁguration procedure.
In the case of IOC failure, no transfer of control to another IOC will be possible, due to 
the local connections and interfaces to the control electronics. In this case there shall be 
a procedure to replace faulty cards and/or assemblies. If it is possible to observe with that 
particular IOC in a failed state (in general, this is limited to IOCs that are associated with 
individual scientiﬁc instruments) then it must be possible to reconﬁgure the system 
to do so.

#### 2.13.3 Redundancy

Full redundancy is not a requirement of the Gemini 8m Telescopes and it will 
be acceptable to have to replace units in case of failure.
There are subsystems which are relatively inexpensive to support as redundant systems, 
such as telescope control computers. For each area where redundancy is decided to be cost 
effective, procedures for switching to the backup system will be established. There is no 
requirement for automatic switching to the backup system.
All communication shall be based on the use of standard communication protocols, where 
retry procedures are applied (a form of software redundancy) as part of the protocol.
Certain network concepts may be preferable as they offer intrinsic redundancy 
(e.g. double loops) and re-routing possibilities in case of node failures 
(single point failure protection).

### 2.14 Constraints

The Gemini system software is designed 
under the following constraints.

#### 2.14.1 User constraints

#### 2.14.2 Hardware constraints

Hardware constraints are covered in the individual chapters
 the Software Design Description.

#### 2.14.3 Software constraints

There are a number of general constraints placed on the Gemini Software. 
These are:

#### 2.14.4 Design constraints

## 3 General Requirements

### 3.1 Data Specifications

The ﬁnal purpose of the Gemini 8m Telescopes software is the acquisition 
of astronomical data in digital form in the most efﬁcient way.
To achieve this, many other data concerning the telescope and instruments (parameters) 
and control commands will have to be exchanged between different processing units in 
order to setup and control telescope and instruments. Additionally, video and voice data 
are also necessary (for example, ﬁeld monitors).

#### 3.1.1 Control Information Flow

Control information must be transferred, typically in the form of commands 
and replies from users, to telescope and instruments. Replies might contain status 
information and, in general, data concerning instruments and telescopes, to be stored 
together with the astronomical data. Control information on all controlled variables must
 be provided by all subsystems on request. No request for information shall produce a delay
 of control activities or locking, even if the corresponding equipment is not available or faulty.
Delay times for the exchange of control information must stay within precise time limits 
to be deﬁned in “General Description” in Chapter 2. One can afford to retransmit commands 
in case of transmission error or collision, but the protocol has to be predictable in that
 commands cannot get lost and replies have to come back reliably. In a number of cases, 
synchronization with the Time Reference System at the Gemini 8m Telescopes site is also
necessary. Access to control parameters, telescope and instrument information
 for monitoring or other use makes a signiﬁcant contribution to the control ﬂow, and
 may be logged at quite high rates for short periods (i.e. up to 200 Hz for some information).
It is explicitly required that all such information is available to the Gemini 8m Telescopes 
software and is capable of being available to all users of the Gemini 8m Telescopes, subject 
only to restrictions with respect to updating. It must also be possible to restrict user access 
to such information. In particular also, the meteorological information coming from a 
weather station should be available centrally.

#### 3.1.2 Astronomical Data Flow

##### 3.1.2.1 Data Flow

Detector data must be acquired and stored in the most effective way technology
 will allow; effectiveness should be evaluated in terms of cost, space requirements, longevity, 
and speed. This shall lead to the deﬁnition of a Gemini 8m Telescopes standard, used on all 
instruments. In general, operational overheads must be kept as low as possible, to maximize 
actual observing times. Intermediate storage of raw data in memory on different nodes and
 in different formats should be kept to a minimum. However, there must be at least two
copies - one to secure data as acquired and one to do assessment of data quality on-line 
(this last copy preferably on removable media). The link chosen to transfer data should 
represent as small a bottleneck as possible for data acquisition.

##### 3.1.2.2 Format Od Data Acquisition

Normally, raw data will be acquired and stored as such for quick look evaluations.
 There might, however, be cases (for example, infrared detectors) where fast preprocessing is 
needed and where, therefore, raw data will not be stored
 as such, but in a preprocessed format.

##### 3.1.2.3 Transport Data Format

Astronomical data will have to be transported between GEMINI and 
the home institutes of visiting astronomers in FITS format (as deﬁned by NOST 100-1.0,
 “Deﬁnition of the Flexible Image Transport System (FITS)”, NASA Science Ofﬁce of Standards
 and Technology).

#### 3.1.3 Other Information Flow

TV data concerning site monitoring and voice need to be capable of being 
available at all operations facilities. It will be a question of interfacing and bandwidth 
costs whether such information is actually available at a speciﬁc location. It is not a 
requirement that point to point video be available between Gemini 8m Telescopes operations
 facilities. It is a requirement that voice connectivity, perhaps point to point, be available
 on a permanent connection. Other astronomical information such as that coming 
from sky ﬁeld monitors, autoguider cameras and sky monitoring devices such as cloud 
and seeing monitors shall also be capable of being available.

### 3.2 Operation

#### 3.2.1 Operations levels

Operation of telescope, instruments and subsystems can be carried out 
at three different levels. There will be parameters associated with each level of operation 
which deﬁne the status of the system and / or control the system. The speciﬁc access by
 different types of users to particular parameters of the different levels are given in Section 
2.5.8 on page 25.

##### 3.2.1.1 Observing level

This is the normal operational mode. It allows a certain number of
 embedded tests, normally at a fairly high level. Monitoring is also done at this level.
It is anticipated that all user categories have access to this level.

##### 3.2.1.2 Maintenance level

This allows maintenance
 tables (for example, with instrument parameters) to be updated. It is anticipated that the 
majority of parameters at this level will be accessed by 
operations and development staff.

##### 3.2.1.3 Test level

This allows the installation and testing of new packages or new releases.
 Any low level test can be performed in this mode. It shall be possible to update
 all non-protected parameter values, i.e. those not used by operations at observing level.
Access to this level will be extremely limited.

#### 3.2.2 privilege and protection levels

Privileges and protections are also important parameters
 to deﬁne user operations.

##### 3.2.2.1 Privileges

A further subdivision within the levels can be achieved by implementing 
privileges associated with categories of users or with the location of the user station 
(local or remote). For example some users might only be allowed monitoring, as 
a subsystem is in use by someone else.

##### 3.2.2.2 Protections

Protections must also be enforced (see also Security in Section 3.5.6
 on page 3- 20) among users and the operational software should indicate clearly
 to users the current operation level and check the compatibility between subsystems
 in different modes.

#### 3.2.3 Capacity

The capacity of the system can be expressed in terms of nodes, which is deﬁned 
as the number of workstations, or in terms of users, which is deﬁned as the sum total of users 
at all the nodes. The capacity requirements will be expressed in terms of nodes.
Each node will have the capability to run at all operation levels.
When the Gemini 8m Telescopes telescope is used in its normal observing mode, there will be 
a single operator node for the telescope and two data acquisition and instrument control nodes.
OPERATION
Some tests might be run in parallel on instruments that do not have the light beam at that 
moment, so in principle additional nodes might be working at the same time. The system will 
provide for one auxiliary data acquisition and instrument control nodes.
In addition, the system must support off-site observing modes. The system will provide for a 
single off-site data acquisition and instrument control node - to be located at either the 
Gemini 8m Telescopes Site Support or Base Facility.
One supervisor will monitor the system, and other users might need to monitor the running 
of observing programs, locally or remotely. The system will provide for a single local monitoring 
node and a single remote monitoring node.
As a conclusion, the Gemini 8m Telescopes control software shall allow simultaneous operation 
of up to six active control nodes and up to two more monitoring nodes (one local and one remote) without 
appreciable degradation of performance.
In practice the operation and facilities foreseen so far for the Gemini 8m Telescopes will limit 
this number to a maximum in the order of three active nodes, but the Gemini 8m Telescopes 
computers and software shall be capable of coping with the load of 10 active nodes, should the 
case arise

#### 3.2.4 Performance criteria

This section is intentionally kept at the level of performance criteria rather than 
response times (found in Section 2.11.2 on page 2- 22). Every command must be acknowledged 
in a positive or negative way before the occurrence of the corresponding action within given 
response times.

#### 3.2.5 Procedures

There must be automatic procedures to implement startup and shutdown of the 
telescope and instruments. These must allow startup and shutdown of instruments 
independently of the telescope and without affecting the telescope operation.
Reconﬁguration procedures must exist, to change the observing environment.
The deﬁnition of the observing environments must be dynamic, i.e. feasible during 
operations without the need to restart everything. The same applies to the related light path.
Operations staff have privileges to change the environment, meaning selecting a suitable 
combination of instrumentsThe operational software should know which subsystems are 
installed and operational at any given time.

### 3.3 External Iterface Requirements

#### 3.3.1 User Interface (UIF)

The user interface deﬁnes the way users see the Gemini 8m 
Telescopes system. Given the large number of instruments, there can be many different 
stations which are active at the same time. It is essential for operational and maintenance 
reasons that, in spite of the obvious differences of the setups and commands available, the 
same philosophy is applied throughout. 
This calls for a homogeneous user interface, which can be achieved only by applying the same 
user interface tools to the whole project, providing the Gemini 8m Telescopes user 
interface's ‘look and feel’.
The user interface should not be seen as a package linked to a speciﬁc computer. Given the 
requirement to be able to access the Gemini 8m Telescopes from several points, the user 
interface should rather be seen as a package to be callable from a large number of stations, 
depending on where a user is. It should also be network transparent so that it does not matter 
where it is being run.
The user interface tools shall be based on standards, deﬁned in Section 4.2.5 on page 4- 7, 
which will be portable across different computer hardware platforms (Portable User Interface 
Toolkit). The intent of a portability requirement is to facilitate migrating existing and future 
Gemini systems to different hardware as the need arises. It is the current intent to limit the 
selection of computer hardware platforms to as few as is practical

#### 3.3.2 Hardware interface

Main processor computer hardware requirements will be deﬁned in the Hardware 
constraints (see Section 3.4.2 on page 3- 12).
This section deals instead with external hardware interfaces, namely the ones from the 
microprocessors to the control electronics. The deﬁnition of these terms is as follows:

Standard interfaces to the control electronics shall be available, in the form of:

The existence of hardware standards is clearly essential for maintenance and 
repairs. It is also essential to avoid software duplication, and to simplify the Gemini 8m 
Telescopes software. Microprocessor software in particular tends to contain hardware speciﬁc 
software, though one should try to keep it as hardware independent as possible, isolating 
different software layers.
The standard software must be adequate for the real-time requirements and must offer drivers 
to the standard electronics to be used on all the Gemini 8m Telescopes software subsystems 
and instruments.
Links between electronics interfaces and main processors must meet the requirements imposed 
by the data speciﬁcations (see Section 3.1 on page 3- 1).

#### 3.3.3 Software iterfaces

The Gemini 8m Telescopes software covers all aspects of control and data 
acquisition related to the telescope, instruments, and auxiliary instrumentation.
It also covers all the operational aspects of the Gemini 8m Telescopes, including on-line 
scheduling and rescheduling.
There is also software which, although it will be interfaced to the Gemini 8m Telescopes, 
is referred to as external. The external software consists of:

The Gemini 8m Telescopes software must interface to the external software 
and clearly the interfaces are fully part of the 
Gemini 8m Telescopes software.

##### 3.3.3.1 On-line image processing interfaces

In order to make efﬁcient use of the telescope, to support different observing 
modes, and to support the versatility requirements, some form of on-line image (or pixel) 
quick-look analysis is required. The following statements are proposed:

The above statements deﬁne the goal of quick-look analysis for the Gemini 
8m Telescopes.
Quick-look data processing should be provided on the Gemini 8m Telescopes, with procedures
 suitable for fast on-line data preprocessing. A prerequisite for this is that acquired data are 
made available as directly as possible in a common format, and that all additional data related
to an exposure and logging information are made available on-line at the same time.
Quick-look should be usable within exposure sequences to provide results and feedback 
parameters to the control software in a programmed way, without the need for manual 
intervention. This document does not try to be speciﬁc about the requirements for Quick-look 
other than that it should be synchronous.
Near-line processing should be available for simple data reductions required for data integrity 
validation (i.e. remove instrument and observatory effects so the observer can make decisions 
about further observing actions). This data reduction proceeds sequentially through requests, 
but asynchronously from data acquistion. In particular, data acquisition takes precedence over 
near-line data reduction.
Off-line pixel processing for full data reduction should also exist at the Gemini 8m Telescopes 
site, but does not have any interface to the Gemini 8m Telescopes software. The Astronomical 
communities have made considerable investments in image processing software, and therefore, 
compatibility with and adaptations to these packages must be sought.
EXTERNAL INTERFACE REQUIREMENTS
It should also be noted that some Gemini 8m Telescopes subsystems, such as adaptive optics, 
may require their own special on-line pixel processing software, which is better deﬁned in the 
requirements for those subsystems. This is largely due to the difﬁculty of applying on-line the 
same algorithms used for full off-line reductions — in general due to the time critical nature of 
the image processing needs.
The same situation might also occur with other instruments, where speciﬁc observer support 
software has to be foreseen for on-line use.
In all these cases the speciﬁc on-line (quick-look) software development shall be seen as a 
subset of the development for the off-line data reduction system, to avoid as far as possible 
duplication of development effort.

##### 3.3.3.2 On-line access to catalogules and previous data

The output format of the Gemini 8m Telescopes data must be compatible with 
the GEMINI archive requirements.
As comparisons with previous data might be of great value and affect the actual observing 
program, on-line interactive access to the data archiving system should exist, so that access 
to this database is possible for Gemini 8m Telescopes users.
The speciﬁc types of data available; ﬂat ﬁelds, calibrations, science exposures, etc.; the amount 
of a speciﬁc exposure available; header only, averaged exposure, complete raw data set; and the 
time frame within which such data will be made available; same night, weekly, after proprietary 
period; will be established by the Gemini Archiving Requirements.
Computer access to star catalogues is also required, so that an automatic selection of candidate 
guide and standard stars can be made.

##### 3.3.3.3 Access to other packages

The Gemini 8m Telescopes software must be able to interface with all commercial 
software packages available on the Gemini 8m Telescopes and integrated into the 
Gemini 8m Telescopes operation.
A relevant example of such a package is a general database management system (DBMS), where 
operational information such as schedules, logs, problem reports and maintenance information 
related to various pieces of equipment should be kept.Being in itself a distributed telescope 
system and having a large number of instruments, the Gemini 8m Telescopes 
system has internal communication needs

#### 3.3.4 Communication interface

Being in itself a distributed telescope system and having a large number of 
instruments, the Gemini 8m Telescopes system has internal communication needs.

##### 3.3.4.1 Local area network (LAN)

The LAN shall support the majority of the Gemini 8m Telescopes system internal 
communication needs. This LAN must be capable of dealing both with the data bandwidths 
required (at peak and on average) and with the required response times and synchronization 
needs. This LAN shall be supplemented with a Local Time Bus, for distribution of absolute and 
relative time signals, and both a digital reﬂective memory bus and an analog event-based bus, 
for distribution of signals with requirements not satisﬁed by a LAN.
Independently of the physical layout of such a network, its functional requirements can be split 
into several categories:

No distinction is made here between WAN and point to point links as there 
shall be no difference in the software between the two cases. However the system 
architecture will be designed so as to minimize the communication load placed on peer
 and higher level networks.
Control data and astronomical data have already been deﬁned in the Data speciﬁcations 
(see Section 3.1 on page 3- 1). The reason for repeating them here is to have a complete 
view of the required network functionality.To eliminate conceptual access problems, while 
coping with different bandwidths, LAN and WAN interfaces shall be homogeneous and shall 
be based on standards which allow migration on different media, should they become required 
during the Gemini 8m Telescopes project life.
For maintenance reasons and hardware independence, a clear hierarchical model must be 
implemented, supporting separation of logical and physical layers, e.g. ISO/OSI model. 
It is recognized that this hierarchy may need to be violated for (in general) performance reasons. 
This results in point-to-point connections between peer systems or direct connections 
bypassing the hierarchy.
Network redundancy should also be considered in the design phase as a way to increase 
reliability and security, in particular for control information.
Due to the uncertain future of the Internet, only non-essential tasks may employ it. 
All essential tasks, not including remote observing, must take place on resources 
controlled by the project (such as leased lines).
Violation of the hierarchical nature of the system can lead to testing and maintenance 
problems. The use of these features must be limited and constrained by the following 
guidelines:

### 3.4 General constraints

#### 3.4.1 User constraints

It is envisaged that observing astronomers who have travelled to the Gemini 
8m Telescopes site will make use of the Gemini 8m Telescopes control room facilities. 
This will allow centralized support and coordination of their operations, providing both 
operations support for individual instruments and supervision for all of them.
However, even at the Gemini 8m Telescopes site there will be users (e.g. software development
 and maintenance staff) installing or enhancing other parts of the system, possibly working
 directly at the telescope. Finally, in the case of remote operations, other users 
(e.g. support staff) might be on Cerro Tololo or in Hilo. To allow coordination both locally
 at the Gemini 8m Telescopes site between the various users and with remote users, the 
software shall support access to the system from any user station. It will then be an operational
 decision, implying privileges and priorities for the various categories of users, and deﬁnition 
of what a given user can actually do. Access from any user station will make user stations
 in principle identical and software conﬁgurable as the user station of this or that subsystem. 
This should greatly simplify the coordination problem posed by the 
large number of simultaneous users (as already described in the Capacity requirements, 
Section 3.2.2).

#### 3.4.2 Hardware constraints

There are a number of constraints for the Gemini 8m Telescopes computer
 hardware. Although some of these constraints may appear redundant 
the project recognizes that:

These constraints recognize that the majority of the expense in changing
 hardware standards is the cost of the software. Particular constraints are:

Depending on funding, it is probably reasonable here to make a minimum 
and a desirable speciﬁcation. The minimum situation could also coincide with what is
needed in the test period before coming to full remote operation. In any case, remote 
operation must include remote monitoring from the Gemini 8m Telescopes base facilities, 
together with access tools for diagnostic and test use. It should be a goal to support remote 
observing from the Gemini 8m Telescopes base facilities.

#### 3.4.3 Software constraints

Some of the general requirements which have a direct effect on the software 
are here explicitly transformed into software constraints. These are:

Whether the software is table driven, message driven, or a combination of 
both is a function of the individual work packages and deﬁned in the appropriate work
 package description. Changing system constants, such as arcseconds/bit for an encoder,
 shall not require recompiling but will be updated as part of system startup, and, for some 
constants, will be modiﬁable during operation. System status parameters will be maintained 
to an extent that will allow restarting the system and regaining the previous state. The extent 
of duplication of the previous state will be dictated by safety and practical considerations.
Strict checking should be applied on this to preserve maintainability and reconﬁguration of
the system.

### 3.5 Attributes

Regardless of application, the software and control systems produced as part 
of the Gemini Project Work Packages exhibit numerous common attributes. The speciﬁc 
attributes described in this document are:

#### 3.5.1 Simplicity

I think you should include Rick’s information about complexity criteria here,
 so show that we are aiming to achieve as simple as system as we can which meets the
 requirements. — Steven.

#### 3.5.2 Supportability

A supportability plan will be part of the Gemini Control System. The goals 
and issues to be addressed by this plan and the elements of the plan are detailed below.
The plan is TBD.

##### 3.5.2.1 Goals

##### 3.5.2.2 Issues

##### 3.5.2.3 Elements

#### 3.5.3 Reliability and Availability

A reliability program is part of the Gemini Control System. The requirements
 for this program and some measures of reliability are detailed below. The plan is as provided 
by Glen Heriot of the Canadian Gemini Project Ofﬁce.

##### 3.5.3.1 Reliability and availability Requirements

Reliability is deﬁned as “The duration or probability of failure-free performance 
under state conditions” or “The probability that an item can perform its intended function for 
a speciﬁed interval under stated conditions”. The [GSR] sets as a requirement 2% and a goal 1% 
for total system (mechanical, electrical, and software) downtime due to failures - this translates 
to a maximum of 15 minutes per night or 1 night per month of downtime. This in turn sets 
quite stringent requirements on both MTBF and MTTR for the software and controls.
To guarantee maximum availability of the control system, retry procedures must be embodied 
in the software in case of error or failure (e.g. time-out, hardware failure) to achieve recovery 
on-line whenever possible.
Should recovery also fail, the error or failure has to be reported in a clear form (to identify the 
cause of the problem) and the system shall put itself into a safe state, whenever a safety aspect 
might be involved.
To avoid unnecessary downtime, it must be possible for the system to reconﬁgure itself in order 
to continue observing, in a different mode if required, given the failure of a single non-critical 
subsystem.To increase software robustness, range checking and validity checking shall be 
supported before execution of any input command. This must be possible ahead of time, 
preparing observing sequences for automatic observations and simulating observations to 
estimate results.
On-line pre-checking of the operational status of equipment should be done prior to sending 
critical or time consuming commands. It must be possible to apply continuous monitoring to
all subsystems on request, both when in operation and when idle, to check their operational 
status.
A measure of fault rates should be done during commissioning to establish baseline rates 
for system reliability monitoring.
There are to be recovery procedures to restart after error failure.
The system should be constantly monitoring active subsystems to be sure they are operating 
correctly before sending command to each subsystem. This monitoring should continue on 
inactive subsystems.
The goal for recover and/or reconﬁguration is 5 minutes from onset of the error condition to 
observing again.
Speciﬁc requirements are:

#### 3.5.4 Maintainability

A detailed plan for maintaining and periodically upgrading the Control System 
over its lifetime will be part of the Gemini Control System. The plan will consider:

These issues will be addressed in the context of the mountain 
environment where the system will be operating. The plan will be delivered with 
the control system

##### 3.5.4.1 Maintenance Requirements

Maintenance of commercial software (Solaris, VxWorks) used by this work 
package is the responsibility of the WPR and the maintenance costs are not covered by
the work package budget.
Community software support (EPICS) is available nominally free-of-charge through the 
normal release and bug-ﬁx procedures used in the community.
All subsystem software is to include modules to aid in the maintenance and testing of 
the subsystem. For example, each subsystem is to include a simulator that provides a 
reference behavior for that subsystem. Simple mechanisms should exist for replacing 
a subsystem with its simulation.
The following self-check levels are to be supplied with sub-system software:

##### 3.5.4.2 Levels of Maintenance

The levels at which maintenance may be performed are:

##### 3.5.4.2.1 Organizational level

These should be done in situ during an observing session.

##### 3.5.4.2.2 intermediate Level

This could be done at an Gemini 8m Telescopes base facility 
during the day.

##### 3.5.4.2.3 Depot Level

This could be done at an Gemini 8m Telescopes base facility 
during the day.

##### 3.5.4.2.4 contractor

Done at the contractor/vendor’s site.

##### 3.5.4.3 Maintenace goals

The prime objectives are to minimize:

##### 3.5.4.4 Mainteinance issue

##### 3.5.4.5 Maintenance constraints

##### 3.5.4.6 Quantitative Maintenance Requirements

Quantitative maintenance requirements will be allocated to the system, 
subsystems, and each component. The requirements must be achievable and stated 
in such a way that veriﬁcation is permitted. The requirements will be expressed as:

All equipment shall support a programmed adjustment and maintenance 
interval of 30 days or longer

#### 3.5.5 Human engineering

All Gemini Software must be designed with human engineering requirements 
under consideration. The human engineering requirements for Gemini Software include:

#### 3.5.6 Security and Safety

The Gemini Control System development effort will obey and abide by both 
the letter and the spirit of all applicable engineering practices, laws, regulations, and policies. 
All necessary safety approvals will be obtained before devices will be accepted. 
The safety precedents and requirements are detailed below.

##### 3.5.6.1 Definition of safety and Risk

MIL-STD-822B, System Safety Program Requirements, deﬁnes safety and risk as:

In addition the Gemini project deﬁnes a hazard as:

##### 3.5.6.2 Security and Safety Requirements

The Gemini system must be self-monitoring to invoke safety monitoring 
to prevent risk to people or damage to equipment. The software should be able to quickly 
bring the Gemini system to a safe state upon notiﬁcation of such danger. Subsystems must 
be able to detect such danger and report it appropriately. In the event that the risk persists, 
subsystems must be able to move themselves into safe states to protect people and equipment 
(i.e. if there is a failure in the higher-level systems).
Safety protection must be applied whenever there is the risk that the actions of the control 
software could endanger people or cause damage to any Gemini 8m Telescopes subsystem, 
for example, by driving beyond limits or by overexposing detectors. This protection, where 
implemented, must be independent of the software. In general this will require mechanical 
hard stops, electrical interlocks, electrical hard limit switches, soft limit switches, software 
limits, and watch dogs,.
The order in which these systems will work is as follows:

The Gemini 8m Telescopes software shall be able to bring the Gemini 8m 
Telescopes system quickly to a safe state upon detection of danger. Safety aspects shall 
be analyzed during the functional speciﬁcation phase of the software.
Security must be provided in order to both prevent accidental mix-up of commands from 
different users on different parts of the system and to prevent intrusion from the wide area 
network into the Gemini 8m Telescopes. In particular, the astronomical database must be 
protected from intrusion, whether the purpose is to access private data or to be destructive. 
It is acceptable, and may well prove to be the best solution, to provide intrusion security by 
a well designed network gateway acting as a ﬁrewall.
A system that is operating in Engineering/Maintenance mode must ignore directives from 
other systems, though status information should still be provided for use by other systems.
There should be security preventing the intrusion into the system by unauthorized users, or 
users at unauthorized access levels.
All systems are appropriately interlocked. This interlock must not depend on any software for 
reliable operation. Details of the interlock system are found in the Mount Control System Work 
Package Deﬁnition.
The interlock philosophy is as follows:

The precedence for conforming to safety requirements will be:

The general safety requirements are:

#### 3.5.7 testabilty

A Controls Test Plan is part of the Gemini Control System. This plan will address 
all areas 
of testing from design, acceptance, commissioning through to hand-over. The objectives and 
requirements of this plan are detailed below.
MIL-STD-1309C, Deﬁnitions of terms for Test, Measurement and Diagnostic Equipment, has 
these deﬁnitions:

##### 3.5.7.1 Testability

The major objectives are:

The interpretation of this table is that we should discover the failure of a 
subsystem 90% of the time before the failure impacts observing.


#### 3.5.8 Expandability

Since the Gemini software will be developed in stages over a period of years, 
and since computer technology is expected to evolve rapidly over this same period, 
the software is to be designed to be easily extended and upgraded with modiﬁcations 
to non-changing components. The software itself, its installation process, and its 
documentation must be developed with this expandability in mind, using general industry 
standards.

#### 3.5.9 Modularity

All software is to be developed using typical modularization and 
standardization techniques. In particular, each module’s environment is strictly 
deﬁned by its interface to other components. No module can rely upon information 
outside of this interface. Module selection should be done in logical fashion to minimize 
the size of the interfaces between modules.
The on-line databases can be considered part of this interface, but are only accessible 
through their deﬁned interfaces.
The software must be strictly modular, i.e. the functionality of a subsystem should correspond 
to that which belongs to that subsystem and only to that, so that software for different 
subsystems can be installed and maintained independently 
of all the rest.This is needed in particular for multi-instrument operation, for example, as 
instruments share the same subsystems on the telescope.
At the same time, the possibility must exist to acquire information about other parts of the 
system (for example, telescope coordinates) (as mentioned in the control ﬂow requirements 
in Section 3.1.1).
It also important that there are no undesired interactions between subsystems. This may be 
enforced either at the client/server interface or at the message system level.

#### 3.5.10 Contingencies

#### 3.5.11 Concurrency

As much as possible, the system is to take advantage of parallel operation 
to improve efﬁciency. The Telescope Control System should be capable of detecting 
and invoking parallel operation as it is responsible for control of all of the telescope 
and enclosure subsystems.

The Gemini 8m Telescopes software has to be developed according to a 
structured and formally deﬁned development model. The purpose of this is to:

This has to be deﬁned in [SMP] and [SCP] (see Applicable Documents, Section 1.3),
 which will cover:

### 3.7 Development Environment

The development environment for the Gemini 8m Telescopes software 
consists of the computer hardware and system software 
(operating system, languages and tools) chosen optimally to support the development 
model presented in the previous section on life-cycle aspects.
The choice of such an environment has to be deﬁned, together with the choice of all the 
Gemini 8m Telescopes standards, but excluding the target computer hardware, 
in Section 4.2.5 on page 4- 7.
The following criteria for later selection shall be kept in mind:

### 3.8 Installation aspects

Test procedure methods have to be deﬁned in the Software Test Plan (STP), 
while test plans shall be written for all individual software packages and modules comprising 
the Gemini 8m Telescopes software.
Apart from the component and integration test procedures, a formal release system 
should exist at package and module level, which should be checkable on-line by the 
operational procedures for consistency. Every system must thus be able to supply its 
current version upon request.
The test operation level has already been discussed in Section 3.2.1 on page 3- 3.
The phasing of the various parts of the project is given in the [SMP].

## 4 Specific Requirements

This section presents the speciﬁc attributes and requirements for Gemini 
software. Only the high-level requirements for Gemini software are presented here.  
Detailed speciﬁcations for the subsystems are found in the individual chapters of the
 Software Design Description.

### 4.1 Attributes

Regardless of application, the Gemini software exhibits numerous common
 attributes. These attributes are described in this section.

#### 4.1.1 Maintenance

The Gemini system maintenance philosophy is described in the Software 
Management Plan (SMP). Preventative maintenance is scheduled as speciﬁed in the 
Gemini Design Requirements Speciﬁcation.

#### 4.1.2 Modularity

All software is to be developed using typical modularization and standardization
techniques.  In particular, each module's environment is strictly deﬁned by its interface to
other components.  No module can rely upon information outside of this interface. Module 
selection should be done in logical fashion to minimize the size of the interfaces between 
modules. The on-line databases can be considered part of this interface, but are only
accessible Reliability and availability A measure of fault rates should be done during 
commissioning to establish baseline rates for system reliability monitoring.
There are to be recovery procedures to restart after error failure.  See section Section 3.2.5 on 
page 3 - 5. During science planning, there should be validity and feasibility checks to
 help ensure effective and efﬁcient use of the telescope.  Where appropriate, these checks 
should also  be performed during operation. The system should be constantly monitoring 
active subsystems to be sure they are operating correctly before sending commands to each 
subsystem.  This monitoring should continue on inactive subsystems.

### 4.2 Other Controls and Software Requirements

#### 4.2.1 On-line database subsystems

All telescope and instrument parameters are kept in an on line database to 
permit easy implementation of table-driven  applications.  The interface between software 
control packages is normally done via interface calls to the on-line  database.
The requirements for this database package are:

The internal (within the IOC) implementation of this  database is to be based 
on EPICS. The implementation within the host workstation is TBD.

#### 4.2.2 Communication subsytems

##### 4.2.2.1 Remote Operations

A fundamental criteria of Gemini telescope operation is that it support a 
full implementation of remote operations.  This  includes remote observing, remote control
 of telescope, enclosure, and instruments, multipoint monitoring, remote monitoring, remote 
access for testing, development, diagnostics, and maintenance, It is expected that all 
operational capability found in on site operations is extended to remote operations, with 
some degradation in performance resulting from WAN bandwidth considerations. This means 
the video data signals must be encoded digitally and transferred via the WAN to remote sites.
There must be some form of security to control access to  system features, possibly 
restricting some operations to speciﬁc remote sites (e.g. Hale Pohaku or Hilo in Hawaii, Cerro 
Tololo in Chile, etc.)

#### 4.2.3 Data specification

The various types of data were presented earlier.  This section examines 
the input, output, and interrelationships of the various data types.

##### 4.2.3.1 Data framework

Final storage locations for the data types is presented here, along with
 a description of the different databases  that are available.

##### 4.2.3.2 Data inputs

Input data are all data that are predeﬁned at operation  start.  This includes 
catalogs, calibrations and ﬂat ﬁelds  available in archives, etc.
Observing commands (whether entered interactively or via the Sequencer) 
are input data that provide information on the
 course of operation and trigger events.

##### 4.2.3.3 Data output

Replies to commands, including status information, updates to parameters, 
video and astronomical information are considered data outputs.
These data end up in the different databases. Operational information, such as logging
 messages, alarms, and errors are special forms of output data, since they are  made
 available for later inspection and debugging.

##### 4.2.3.4 Inter-function data definitions

One criteria is that sufﬁcient information be recorded during an observation
 to recreate the sequence of events that  occurred during the observation.  This requires
 that all  input and output data be logged appropriately.
Given an initial set of conﬁguration parameters, the Gemini system operates via a 
sequence of commands.  This operation  is complemented by using previously stored 
data, calibrations, and star catalogs

#### 4.2.4 System operational requirements

##### 4.2.4.1 Normal operation

##### 4.2.4.2 Operation in failure mode

#### 4.2.5 Standards

##### 4.2.5.1 Software standards

##### 4.2.5.1.1 Software methods

All Gemini supported software is to be developed using a  
formally deﬁned model.  The Ward/Mellor approach to developing real-time 
systems is used and covers:

Functional analysis is done using a CASE tool suitable for use with 
Ward/Mellor techniques, such as TSEE, by Westmount Technologies.
The design is to use the techniques and diagrams introduced by  Ward and Mellor and 
reviewed by the Gemini staff.
Detailed design and development standards are not speciﬁed,  but expected to conform 
to system goals and established  practice.
An object-oriented approach is encouraged but not required.

##### 4.2.5.1.2 Operating system

The upper levels (User-interface and OCS) are assumed to not require a 
real-time operating environment.  However, the operating environment at these levels 
is expected to provide sufﬁcient performance for both human interaction and communications.
Real-time support is required at the IOC level.

##### 4.2.5.1.3 Languages and coding standards

Details of these standards can be found in the Software
 Programming Standards document.

##### 4.2.5.1.4 Software configurations and tools

These are deﬁned in the Gemini Conﬁguration Control Plan.

##### 4.2.5.1.5 Software communication standards

The following recommendations are made:

##### 4.2.5.1.6 Software interfaces

The recommendations are:

##### 4.2.5.1.7 External software packages

##### 4.2.5.1.8 Databases

Astronomical data are stored both in the Archiving system and in the data
 storage subsystem. IOC control databases are distributed across the IOC subsystems, 
with down-loadableinitialization copies available on the Gemini disks.
Conﬁguration, logging, maintenance schedules, and subsystem documentation 
are to be kept in the commercial relational database.

##### 4.2.5.2 Hardware standards

Only the development systems are considered here.  Installed systems
 are to be chosen later, based on available technology and experiences with the development 
systems.

##### 4.2.5.2.1 Harware requirements

The computer hardware used for development must conform to  the following:

##### 4.2.5.2.2 Development computers

The following recommendations are made:

##### 4.2.5.2.3 Electronics hardware interfaces

All accesses to the control electronics hardware will be  through VME IOC's, 
using the EPICS software.  No other control interfaces are permitted.

There are places in the Gemini system where software exists below the IOC 
level that is interfaced to IOC software.  The  standards for this interface is not part of 
this speciﬁcation.  The use of this software is to be explained and discussed on a 
case-by-case basis.
In cases where there is a distributed network of target  microprocessors involved at this 
level, it is appropriate to provide a standard sub-network.  This type of Fieldbus is to be 
implemented using an ALAN/BRADLEY bus, ProﬁBus, or other approved Fieldbus.
In cases where there is a distributed set of commercial equipment to be controlled the 
recommended method is to use an ALAN/BRADLEY system to control the equipment manually 
and interface to it using RS-422 or similar connection to an IOC.

##### 4.2.5.4 Communication hardware

All communication hardware must meet the data ﬂow requirements 
and software protocols deﬁned in this document.  The following recommendations 
are based on currently available technology.  It is entirely appropriate that changes 
will be  made to take advantages of changes to that technology.

##### 4.2.5.5 Re-use of existing software

Wherever possible, Gemini software is to take advantage of existing software.  
However, all existing software is to be evaluated in terms of the speciﬁcations given here.  
This helps reduce life-cycle costs and maintenance efforts.

#### 4.2.6 Life cycle constraints

Life cycle constraints are discussed in the 
Gemini Software Management Plan.

### 4.3 User Requirements for EPICS developers

The Experimental Physics and Industrial Control System (EPICS) toolkit is
 the foundation of the Gemini control system. EPICS was originally developed at the Los
 Alamos and Argonne National Laboratories for use in large accelerator control and 
diagnostics systems. It is now an established standard within the international High 
Energy Physics community and is gaining acceptance amongst astronomical sites.
Within the EPICS community there is understood to be an informal distinction between 
two classes of developers, labeled ‘Internals’ and ‘Applications’. Although these deﬁnitions
 are nowhere written down, this understanding serves as the basis for many 
discussions with the community and for the nature of training classes.

#### 4.3.1 EPICS Components

Note: The bulk of this section is taken from the EPICS document
 ‘EPICS Overview’. EPICS consists of a set of hardware and software components 
from which a control system can be created.

##### 4.3.1.1 Hardware Components

##### 4.3.1.2 Software Components

##### 4.3.1.2.1 IOC Software

##### 4.3.1.2.2 Channel Access

Channel access provides network transparent access to IOC databases.
 It is based on a client-server model. Each IOC provides a channel access server which 
is willing to establish communication with an arbitrary number of clients. Channel 
access client services are available on both OPIs and IOCs. A client can communicate
 with an arbitrary number of servers. It should be noted that channel access
 does not provide access to database records as records. This is a deliberate 
design decision. This allows new record types to be addedwithout impacting 
any software that accesses the database via channel access. A channel access
 client can communicate with multiple IOCs having differing 
sets of record types.

##### 4.3.1.2.3 OPI Tools

EPICS provides a number of OPI based tools. These can be divided 
into two groups based on whether or not they use channel access. Channel access
 tools are real time tools, i.e. they are used to monitor and control IOCs.

##### 4.3.1.2.4 EPICS Care Software

EPICS consists of a set of core software and a set of optional components. 
The core software, i.e. the components of EPICS without which EPICS would
not function, are:

All other software components are optional. Of course any application 
developer would be crazy to ignore tools such as MEDM (or EDD/DM). Likewise an
 application developer would not start from scratch developing record and device 
support. Most OPI tools do not, however, have to be used. Likewise any given record
 support module, device support module, or driver could be deleted from a particular
 IOC and EPICS will still function.

#### 4.3.2 Gemini Breakdown of tasks

Each of the Gemini Controls work packages will be involved with some 
aspect of EPICS development ranging from creation of new device drivers to database 
creation and the design of new CA clients.The details of the EPICS work required can be 
broken down into several broad categories which reﬂect the nature of the various work 
packages. This breakdown is given in the following subsections:

##### 4.3.2.1 Not covered by any work packages

##### 4.3.2.2 SIC work package only


##### 4.3.2.4 Real-time (IOC-based) work packages

#### 4.3.3 GEMINI definitions

For the purposes of work performed for the Gemini 8-m Telescopes 
Project the following deﬁnitions will be used to differentiate 
between the two ﬂavors of EPICS development work:

These are all topics that would be covered in an EPICS Basics, Building 
and Using Applications course.

#### 4.3.4 Required developer skills

For each class of developer a speciﬁc set of skills is required. 
The following sections list those that would be commonly used.

##### 4.3.4.1 Applications developer

##### 4.3.4.2 Internals Developer

##### 4.3.4.3 Expected Distribution of Developer Classes

##### 4.3.4.3.1 Current distribution within the high energy phisics community

The experience of the High Energy Physics community is that only a 
core group of Internals developers is required for maintenance and enhancement of 
EPICS IOC software and of the standard development and CA client tool set.  
Speciﬁcally, the IOC core software is almost exclusively in the domain of the 
Los Alamos AOT-8 ofﬁce.
Two major ﬂavors of development tools are in use with support coming from 
key groups within Los Alamos and Argonne.
Many sites contribute custom CA client tools as this generally involves C or 
C++ programming under a UNIX O/S to interface to the standard CA library.
In addition, many sites create their own database record types and new device 
support and driver layers.
Although there is presently a large amount of activity in the enhancement of 
EPICS Internals software especially in the ﬁelds of non-IOC core software, this is 
an order of magnitude less than the amount of Applications work under way at over 
20 distinct programs.

##### 4.3.4.3.2 The APS CATS Experience

Another large group of predominately Applications developers that are 
starting work are the Collaborative Access Teams (CATS) at 
Argonne’s Advanced Photon Source (APS).The APS is a facility to produce high brilliance 
X-rays for a variety of experiments and includes 36 experimental halls with 2 lines each. 
As of March 1994, there were 15 CATS at the APS with most CATS responsible for a single 
sector (2 beamlines). Each CAT has its own funding for designing/building/operating 
the physical beamline, instrumentation, controls, and data acquisition systems.
Because the experimental areas must be coordinated with the main facility control 
system and since 25% of the beamtime must be made available to independent investigators 
it was strongly recommended that EPICS be used as the toolkit for all CATS development 
work. Not only would this simplify the integration with the central control system but would 
also provide a common environment for facility visitors.
Typically, each CAT has 1 or 2 developers, and the major focus is not on the IOC software 
although some new records, like the Multichannel Analyser, have been created, but rather 
on the OPI CA client applications. Heavy use is being made of both Tcl/TK and IDL to 
support high-level sequencing and data reduction. This is similar to the Gemini architecture 
as the bulk of the control system intelligence is contained within OPI CA client tasks.
Other items of concern are:

##### 4.3.4.3.3 Planned distribution within the Gemini Project

The Standard Instrument Controller work package is tasked 
with laying the Internals ground work for all other Gemini control system work 
packages. In this project, the only required IOC-based Internals work is the 
creation of record, device, and driver support for three VME I/O cards. It is 
anticipated that all other IOC-related work packages will be performing exclusively 
Applications work.
In the advent of future work packages requiring Internals work it is planned the RGO 
SIC development staff will be made available. In this way the number of Internals staff 
is kept at a minimum.

## 5 Commands

### 5.1 Command Routing

There are several means of transmitting commands and data across the 
Gemini system:

### 5.2 Command structure

All commands contain the same general structure:

### 5.3 General purpose commands

This section presents the “generic” commands that all Gemini systems 
must respond to. There are also “Control Commands” common to all Gemini systems 
to provide speciﬁc functionality during observing. These control commands are presented 
in the Gemini Software Design Description. Speciﬁc commands are presented in the Software 
Design Descriptions for the individual subsystems.

#### 5.3.1 Status Commands

The following commands are “status” queries used to obtain information 
about the state of the subsystem.

The following commands affect the behavior of a subsystem 
independently of the speciﬁc task of that subsystem.

### 5.4 Data Communications

Communication of information is similar across all systems in 
the Gemini controls network. Instances of this communication is via routes, 
which may be direct channels, intelligent channels, or broadcasts. 
Communication via a route is typically asynchronous, with commands
available to establish synchronization as needed.

### 5.5 IOC Commands

The following commands are common to all IOC-based subsystems. 
(Most control subsystems are IOC-based.) These commands are processed by the 
IOC subsystem.

#### 5.5.1 Local Database Access

IOC crates in the Gemini system have local databases. Under the Gemini 
control system, it is expected that the majority of subsystem control is accomplished 
through these databases. The following commands provide access to those databases.

#### 5.5.2 Time Handling

Time synchronization is commonly required among control subsystems. 
These commands are to permit appropriate time synchronizations. Times will be 
provided in IRIG-B format as UTC.
TBD

#### 5.5.3 Remote DB Access

Some subsystems may need to obtain information from other systems 
within the Gemini control system. This access is accomplished using the same 
communication and database access commands as given above.

### 5.6 Command Implementation

Within the OCS, all commands are represented as ASCII strings. 
Fields within the command are labelled and nesting is permitted using braces ({ , }). 
For example, a typical command might be:

Details of the implementation are the province of the OCS work package 
developers, who are responsible for providing procedures for 
constructing/deconstructing/routing command strings. 
The mappings of speciﬁc IOC commands between ASCII strings and EPICS channel access 
calls are determined by the individual IOC subsystem developers. Work Package 
Descriptions include baseline command descriptions that 
need to be implemented for that speciﬁc work package.
