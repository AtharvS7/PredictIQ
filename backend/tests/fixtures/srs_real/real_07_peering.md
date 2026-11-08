# Peering Internet Exchange Service Specification

> **Dataset:** PURE Dataset (Zenodo 7118517 / IEEE RE 2017)
> **Original Document Title:** Software Requirements   Specification   for   Internetworking of   Content Delivery Networks   through Peering
> **Domain:** Telecommunications & Peering
> **License:** Open Standard (IETF)
> **Source/Project:** https://www.ietf.org
> **Version:** 0.1
> **Issue Date:** 2010-03-08

---

## 1 Introduction

### 1.1 Purpose

This document describes the requirements specification (SRS) for the software infrastructure (or
      product) that enables the internetworking of Content Delivery Networks (CDNs) through peering,
      henceforth termed as ‘CDN peering’, and provides an overall description of it. It presents a means for
      distinct CDNs to coordinate and cooperate with other CDNs, by investigating and developing (a)
      models for effective internetworking between CDNs though peering; (b) protocols for service
      delivery in a cooperative environment of CDNs; (c) some concrete examples (technology trends) that
      exhibits the notion of content networking; and (d) policies for autonomic management of service level
      through resource negotiation in an on-demand basis. Thus, this document provides a basis for
      evaluating the proposal for internetworking between CDNs. This is the version 0.1 of the software
      requirements specification.

### 1.2 Document Conventions and Terminology

When writing this SRS for CDN peering, the following terminologies are used:

### 1.3 Intended Audience and Reading Suggestions

This document is written for the researchers, software developers, advanced practitioners,
      documentation writers, and users involved in CDN domain to initiation an open discussion for
      exploring development opportunities regarding the internetworking between CDNs. Section 2
      discusses the steps that are to be undertaken to “bring-up” or “cease” an internetworking arrangement
      between CDNs. In the next section, system features with their functional requirements are presented
      to highlight the major services provided by the intended product. Then the external interface
      requirements highlighting the logical characteristics of each interface between the software product
      and the users are discussed. Finally, this specification is concluded with the reference documents on
      which this document is based on.

### 1.4 Project Scope

The final product enabling CDN peering assists in coordinated and cooperative content delivery via
      internetworking among distinct CDNs to allow providers to rapidly “scale-out” to meet both flash
      crowds and anticipated increases in demand, and remove the need for a single CDN to provision
      resources. An ad-hoc or planned peering of CDNs requires fundamental research to be undertaken to
      address the core problems of measuring and disseminating load information, performing request
      assignment and redirection, enabling content replication and determining appropriate compensation
      among participants on a geographically distributed “Internet” scale. In contrast to a single CDN, for
      which these issues are deeply interrelated and co-dependent, the main thrust for the final product
      enabling CDN peering is to consider them in a coordinated and cooperative manner among many
      peered CDNs, whilst satisfying the complex multi-dimensional constraints placed on each individual
      provider. Each provider must ensure that their individual SLAs are met when serving content for its
      own customers to end users, while meeting any obligations it has made when participating in a group
      of many providers.

### 1.5 References

This document builds on the following references:

## 2 Overall Description

### 2.1 Product Perspective

CDN peering allows different CDN providers to share resources in order to provide larger scale
      and/or reach to each participant than they could not achieve otherwise. It is formed by a set of
      autonomous CDNs, which cooperate through a mechanism that provides facilities and infrastructure
      for cooperation in order to virtualize multiple providers. It is expected that an effective peering
      arrangement between CDNs would require multiple steps to occur.


### 2.2 Product Features

The software infrastructure enabling peering between CDNs can be featured with the following major
      goals:

### 2.3 User Classes and Characteristics

The users of the software infrastructure enabling CDN peering can be differentiated by using their
      membership and contributions to the system. A given peering arrangement consists of explicit and
      implicit members. Explicit members include the primary CDN, which is the initiator of a peering
      relationship, and any peering CDNs who cooperate for resource sharing. Implicit members are content
      providers and end-users. Implicit members are transparent to a peering arrangement but they share the
      benefit from it. In addition, users can vary based on the purpose, size, scope and duration of peering.
      For instance, a short-term peering arrangement is to be automated to react within a tight time
      frameas it is unlikely that a human directed negotiation would occur quickly enough to satisfy the
      evolved niche. On the other hand, establishment of a long-term peering arrangement calls for a
      human-directed agent to ensure that any resulting decisions comply with participating CDNs’
      strategic goals. Users can also be classified because of the preferential treatment that they may receive
      due to the policy that pertains to a particular provider’s business logic. Moreover, individual users (or
      a group of users) can have dynamic QoS requirements depending on the situations that will result in
      “customized” content delivery. Thus, users (or class of users) can be differentiated based on userdefined
      QoS specifications while accessing the service.

### 2.4 Operating Environment

The product (i.e. prototype system) enabling CDN peering is expected to be deployed it in a realworld
      test bed such as PlanetLab for global testing, observations, and for performance evaluation. In
      this regard, existing Web services technologies will be studied in detail to examine the feasibility of
      leveraging them. A modular implementation stack could be developed on top of the existing standard
      application layer (e.g. Apache, Tomcat) and protocols (e.g. HTTP, CDI, HTPC). A modular
      implementation approach would be useful to perform testing on modules at different stages to ensure
      correct implementation. It is anticipated that a cryptographically secure auction-based framework will
      be used to assist content replication among peered CDNs to allow incentives for all participants. Load
      information could be measured and disseminated within individual CDNs and among other CDNs
      using distributed load indices such as Distributed Hash Table (DHT) or variations of it. Request
      assignment and redirection could predominantly rely on DNS-level end-user assignment combined
      with a rudimentary request assignment policy such as weighted round-robin or least-loaded-first,
      which updates the DNS records to point to the most appropriate replica server of the peers.

### 2.5 Design and Implementation Constraints

The challenges in developing the product include virtualization of multiple providers and offloading
      end-user requests from the primary CDN provider to peers based on cost, performance and load. Due
      to the proprietary nature of existing CDNs, limited information about response time or service cost is
      typically available from individual CDNs, and load balancing control is retained by an individual
      provider within its own Web servers. Therefore, request-redirections must occur over distributed sets
      of Web servers belonging to multiple CDN providers, without the benefit of the full information
      available, as in the single provider case. Moreover, an implementation model for the product enabling
      CDN peering could be based on a complex combination of attributes such as Web server
      responsiveness or load, expected network delay, or geographic location. Several of these potential
      attributes vary over time and there is no single repository for listing the value of attributes such as
      geographic location or expected delay for all Internet-connected systems. It is anticipated that the
      values used in a CDN peering implementation model are likely to be based on heuristics.

### 2.6 User Documentation

Along with the software product, a user manual would be written to help people understand the
      working methodology and usage of the developed prototype system. It would be written for nontechnical
      individuals and the level of content or terminology would differ considerably from, for
      example, a System Administration Guide, which is more detailed and complex. The user manual
      would follow common user documentation styles capturing purpose and scope of the product along
      with key system features and operations; step-by-step instructions for using the system including
      conventions, messaging structures, quick references, tips for errors and malfunctions; pointers to
      reference documents; and glossary of terms.

### 2.7 Assumptions and Dependencies

The product would build on leveraging existing systems. In this regard, necessary inspirations could
      be obtained by analyzing related systems such as CoDeeN, Coral, Globule, and MotusNet. In
      particular, the design and implementation approach of MotusNet could be helpful to draw a clear
      guideline for developing the intended prototype.

## 3 System Features

The major services and functional requirements for the product can be illustrated by system features.
      This section is organized by use cases for major system features. In the following, necessary
      description is provided for each use cases in the system. Each use case description provides
      information of the associated actors, triggering condition, preconditions, postconditions, response
      sequences, exceptions and functional requirements (assumptions). Being a major important section of
      the SRS, this section is expected to go through iterative improvement to make the most logical sense
      for the intended product.

### 3.1 Service Registration

This feature is associated with the registration of resource and service information of each CDN to its
        SR. The use case for this feature is shown in Figure 2.


#### 3.1.1 Actors

WS: Publishes its resource and service information to the SR.
          SR: Registers available local resources at the CDN provider and updates them.
          Mediator: Collects up-to-date resource information from SR.

#### 3.1.2 Trigger

Service registration is triggered when either one of the following occurs: (a) resources
          are available as a provider starts operating; (b) previously registered resource
          information needs to be updated; (c) available local resource information is required in
          the event of traffic surges; and (d) local and delegated external resource information is
          to be encapsulated in an SR instance included in an established peering arrangement.

#### 3.1.3 Preconditions

Available local resources of a CDN provider are detected along with their service
          information such as CPU, storage, upload and download rate, etc. These resources
          could be provisioned and reserved to satisfy SLAs.

#### 3.1.4 Postconditions

Resources are registered in the service registry and being updated in a regular basis.

#### 3.1.5 Stimulus/Response Sequences

#### 3.1.6 Exceptions

If a resource fails, its service information is removed from SR and the resource ID counter is decremented.

#### 3.1.7 Functional Requirements

### 3.2 Request Initiation to Trigger Peering

This feature relates to the initialization of peering between CDNs. The use case for this feature is
        shown in Figure 3.


#### 3.2.1 Actors

End-user: Requests for content.
          Mediator: Receives initiation request from WS to trigger peering.

#### 3.2.2 Trigger

It is invoked when a (primary) CDN realizes that it cannot handle a part of the
          workload on its WS(s). The triggering condition considers the expected and
          unexpected load increases in the initiating (primary) CDN.

#### 3.2.3 Preconditions

Exceptional circumstances such as flash crowds have occurred to place unanticipated
          load on CDN WSs.

#### 3.2.4 Postconditions

An initialization request is sent to the mediator to trigger peering.

#### 3.2.5 Actors

#### 3.2.6 Exceptions

If the user requests experience service timeout (threshold), initiation request is
          cancelled.

#### 3.2.7 Exceptions

### 3.3 Mediator Invokes Creation of Negotiated Relationship

On receipt of the initialization request to trigger peering, the mediator of the primary CDN invokes
        negotiation. Figure 4 shows use case for this feature.


#### 3.3.1 Actors

SR: Sends resource and access information.
          PR: Sends policy information for establishing negotiated relationships
          PA: Receives service requirements from the mediator.

#### 3.3.2 Trigger

Upon receiving the initialization request to trigger peering, the mediator generates
          service requirements and passes it to local PA.

#### 3.3.3 Preconditions

Initialization request is received.

#### 3.3.4 Postconditions

Service requirements are generated and they are sent to the local PA.

#### 3.3.5 Stimulus/Response Sequences

#### 3.3.6 Exceptions

If the user requests can not be accepted according the provider policies, service
          requirements are not passed to the local PA.

#### 3.3.7 Exceptions

### 3.4 Resource Discovery through PA

The PA of a given primary CDN negotiates with PAs of the peers to perform external resource
        discovery. Figure 5 shows the use case related to this feature.

#### 3.4.1 Actors

External PA: Negotiates with the PA of the primary CDN.
          PR: Receives negotiated policies from the local PA.

#### 3.4.2 Trigger

Local PA communicates with the PAs of peers to discover external resources.

#### 3.4.3 Preconditions

Service requirements are received from the mediator.

#### 3.4.4 Postconditions

Negotiation is performed and a peering arrangement is established through inter-PA communications.

#### 3.4.5 Stimulus/Response Sequences


#### 3.4.6 Exceptions

If the user requests can not be accepted according the provider policies, service
          requirements are not passed to the local PA.

#### 3.4.7 Exceptions

### 3.5 Operational Management

This feature is responsible for the inter-CDN protocol configuration, resource initialization and for
        ensuring effective operations of the established peering arrangement. The use case for this feature is
        shown in Figure 6.

##### 3.5.1 Actors

External PA: Exchanges configurations and content availability information, and
            accepts requests to an optimal peer.
            PR: Assists in enforcing negotiated policies.

##### 3.5.2 Trigger

Once policies are negotiated and a peering arrangement is established, PAs interact
            each other in the execution of common goal(s).

##### 3.5.3 Preconditions

A peering arrangement is established.

##### 3.5.4 Postconditions

Necessary functions policies are deployed and administration for effective operations.

##### 3.5.5 Stimulus/Response Sequences

##### 3.5.6 Exceptions

If a peered CDN provider refuses to accept user requests, a given peering arrangement
            ceases.

##### 3.5.7 Exceptions

### 3.6 Disband or Re-arrangement

There could be circumstances under which a given peering arrangement may need to disband or rearranges
        itself. This feature is associated with the use case shown in Figure 7.

#### 3.6.1 Actors

External PA: Interactions with local PA of the primary CDN.

#### 3.6.2 Trigger

Any of the termination condition holds.

#### 3.6.3 Preconditions

There is an established peering arrangement.

#### 3.6.4 Postconditions

A given peering arrangement is disband or it is re-arranged.

#### 3.6.5 Stimulus/Response Sequences


#### 3.6.6 Exceptions

If there are exceptional circumstances such as natural disaster, theft, etc. for which any peer is unable to honor the negotiated relationships, a given peering arrangement is not disband or re-arranged and SLA conditions are bypassed.

#### 3.6.7 Exceptions

## 4 External Interface Requirements

### 4.1 User Interfaces

This section describes the logical characteristics of each interface between the intended software
    product and the users. For user interface design, common GUI standards will be followed along with
    the presence of keyboard shortcuts, error message display standards etc., and standard buttons and
    functions (i.e. help) will appear on every screen. Details of the user interface design are intended to be
    documented in a separate user interface specification.

### 4.2 Communications Interfaces

As mentioned earlier, the intended product to exploit existing Web service technologies to leverage
      existing infrastructures through building an overlay. The communication among software component
      would be performed through message passing over the IP network. From a technical point of view,
      TCP/IP will be used as the transport protocol, where each CDN server establishes a TCP connection
      to the network elements using a well-known port number. Messages can then be sent bi-directionally
      between the server and network elements. All messages consist of a fixed length-header containing
      the total data length and a request followed by a reply or an acknowledgement. Interaction among
      surrogates will be performed using HTTP or FTP.

## 5 References
