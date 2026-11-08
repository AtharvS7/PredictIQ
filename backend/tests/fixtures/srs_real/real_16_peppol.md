# PEPPOL Pan-European Public Procurement On-Line Functional Requirements

> **Dataset:** PURE Dataset (Zenodo 7118517 / IEEE RE 2017)
> **Original Document Title:** Functional and non-functional requirements   specification for the VCD, including critical   synthesis, comparison and assessment of   national vs. pan-European needs
> **Domain:** E-Procurement & B2G Messaging
> **License:** Open PEPPOL AISBL / EU Commission
> **Source/Project:** https://peppol.org
> **Version:** 1.1
> **Issue Date:** 2009-11-09

---

## 0 Preface

This preface provides a short overview about the comments received from the EC and other sources
    and how these comments and remarks will be taken into consideration in future/ongoing work.
    The review reflected that WP2 presents with its deliverable D2.1 “an ambitious, high quality vision,
    reflected in a 4 stage maturity model, which is well argued.” The general feedback received for this
    document was positive, especially highlighting various insightful remarks. On the other hand the
    review process has generated some criticism which will be addressed by WP2 in future works. The
    following description responds to these comments and criticism by arguing how and where revisions
    and updates of the work presented in this deliverable will be implemented in subsequent results of WP
    2.
    First of all, D2.1 will be updated and improved in the following respects:

## 1 Introduction: Motivation for a Virtual Company Dossier

The effective use of Information and Communication Technology (ICT) to enable interoperability in
    public procurement is an area of great significance for achieving the Lisbon objectives, i.e. to become
    the most competitive and dynamic knowledge-based economy in the world (EC 2005). However, the
    current European public eProcurement infrastructure is inappropriate because it is characterized by a
    high market fragmentation and a lack of interoperability. Hence, a major objective of the European
    Commission is to enable European-wide eProcurement across borders by creating common principles
    and technical solutions that are applied within all Member States. eProcurement requires efforts to be
    done by public administrations, in particular to exploit new technologies for interoperability that enable
    easy information accessibility, improving the availability of pan-European services and interaction
    among citizens and businesses (European_Dynamics_S_A 2004).
    Governments are the largest buyer in the European Union which purchase at a level of approximately
    15-20% of GDP (Ministerial_Declaration 2005). Governments are lagging behind major industries in
    exchanging relevant data with key actors such as suppliers. Common standards for electronic data
    exchange seem to be a key element for companies to participate in public eProcurement. A Europeanwide
    eProcurement infrastructure could save governments up to 5% on expenditure and the
    transaction costs for both buyers and suppliers could be reduced by 50-80%. A greater competition
    and efficiency in eProcurement will influence the whole economy and may also play an important role
    in achieving the Lisbon objectives, e.g. to become the most competitive and dynamic knowledgebased
    economy in the world (Commission_of_the_European_Communitites 2004).
    The Manchester ministerial declaration of 24 November 2005 defines the target that
    ((Ministerial_Declaration 2005) p.4): “By 2010 all public administrations across Europe will have the
    capability of carrying out 100% of their procurement electronically, where legally permissible, thus
    creating a fairer and more transparent market for all companies independent of a company’s size or
    location within the single market. By 2010 at least 50% of public procurement above the EU public
    procurement threshold will be carried out electronically. Over the period 2006-2010 Member States
    will focus their efforts on delivering those high impact services in Europe which will contribute most to
    the achievement of the Lisbon Agenda.”
    It is expected that an interoperable eProcurement infrastructure ensures equal treatment and nondiscrimination
    and that it facilitates fairer and more effective competition in the European market by
    enabling suppliers to compete in an open and transparent way. However, current eProcurement
    infrastructures are inappropriate to reach this ambitious aim since these are characterized by a high
    market fragmentation. A lack of interoperability – different, non-operable and incompatible technical
    solutions – hinders suppliers in accessing eProcurement systems and discourages their participation
    cause of additional difficulties or increased costs (Commission_Staff_Working_Document
    08.07.2005).
    Across Europe, eProcurement systems have already been developed with a focus on the automation
    of different eProcurement procedures. Current systems reflect various country-specific public
    procurement needs and national laws, priorities, and practices. Systems are either centrally oriented
    or designed to reflect federated systems demands. In addition, varying terminologies are used within
    the European Member States. The lack of a unified eProcurement terminology is a major barrier which
    affects the possibility of a smooth collaboration between Member States and their eProcurement
    systems (Commission_of_the_European_Communitites 2004). Legal, technical and organisational
    barriers prevent the development of a common Procurement infrastructure and are one of the greatest
    challenges to be solved by politics, governments, ICT industry and research
    (European_Dynamics_S_A 2004).
    To facilitate EU-wide interoperability in public eProcurement, the European Commission co-funds the
    PEPPOL project in the ICT Policy Support Programme within the Competiveness and Innovation
    framework Programme (CIP). PEPPOL2 aims at setting up pan-European pilot solutions that
    conjointly exist with national infrastructures.
    Among the building blocks the PEPPOL consortium develops, the Virtual Company Dossier (VCD)
    focuses on an interoperable solution which contains the documents required from economic operators
    to evidence their qualification as well as qualitative selection or exclusion according to the directive
    2004/18/EC.

### 1.1 Need for a Virtual Company Dossier

A VCD will facilitate electronic Tendering by providing cross-border data and document solution that
      contains the necessary attestations and certificates typically required in eTendering. Thus it can be
      seen as a container for documents. Yet up to now, the tendering documents such as attestations and
      certificates required in public procurement procedures differ between Member States. When a
      contracting authority publishes a contract notice, it shall include the selection, qualification and nonexclusion
      criteria. The economic operators have to submit evidence and proof in respect of these
      criteria. Hence, during the preparation of the tender an economic operator needs to collect the
      respective evidences (i.e. certificates and qualification documents) from a number of issuing bodies
      (e.g. public registries, banks, pre-qualification bodies, etc.) to prove conformance with the given
      selection and exclusion criteria.
      The overall aims and expectations of a virtual company dossier solution as set out in the description of
      work can be described as follows:

### 1.2 1.2 Status quo of evidencing selection and exclusion criteria in generic tendering procedure

The status quo concerning the tendering process, observed in the European countries of this work
      package, is depicted in a generic status-quo procedure as shown in Figure 1.
      The procedure can be described as follows: A Contracting Authority prepares a call for tender
      based on a set of documents, usually consisting of a) the publication of a contract notice b) the tender
      contract documentation c) the (technical) specifications, d) additional documents. The contract notice
      is produced and transmitted to the official gazette such as the Tenders Electronic Daily (TED) when
      due. It should be noted that for public tenders above a certain threshold, the publication in the Official
      Journal of the European Union (TED) is mandatory. Public tenders below that threshold can use other
      channels for the contract notice (depending on national legislation; e.g. contract notices may be
      mandatory in national official gazettes). Also tendering platforms can be used by the contracting
      authority (1). The steps of publishing the contract notice are part of “eNotification”3.
      An Economic Operator can use means such as the TED system, existing tendering platforms or
      official national gazettes to search for contract notices (2) and to retrieve the relevant information
      about active tenders (3). The online TED system provides broad advertising and presence of “contract
      notices” within the TED database. TED publications of contract notices usually contain the tender and
      contract documentation including detailed criteria, specifications and conditions. Almost all the TED’s
      contract notices have a summary of the requirements in other languages set by the Contracting
      Authority. The mandatory publication of contract notices in TED is a means to ensure transparency for
      public procurement throughout Europe and to enable a well functioning inner market. For contract
      notices below threshold, TED can also complement existing national sources through widespread
      information across borders. Sometimes, the information on a contract notice provided in TED is not
      complete. Hence, the Economic Operator must directly get the authentic contract notice and exact
      conditions from the Contracting Authority in order to avoid a failure on interpreting the requirements for
      participation.
      If an Economic Operator decides to participate in a public tender across border, the appropriate
      selection and exclusion criteria have to be evaluated. This means that the Economic Operator has to
      match these criteria set out in the contract notice of another country with the evidences (attestations,
      statements and certificates) of his or her own country in order to prove compliance (4). The attestations can be retrieved from the appropriate issuing bodies such as certifiers, source registers,
      banks, public authorities, etc. in the country where the Economic Operator is established (5).
      The step of retrieving proofs of suitability and non-exclusion and collecting documents for the receiving
      entities becomes a necessary task and may take place at different times. In some European Member
      State countries the “self-declaration” (a statement issued by the Economic Operator) is adopted to
      claim an initial suitability for applying and attending a tender. In this case, Economic Operators may
      retrieve their proofs of suitability only at a later stage if necessary at all.
      In most cases an official translation of the documents submitted by the Economic Operator is required
      (6). Some European countries are also imposing the submission of legally attested documents. In this
      case, accredited official translators, lawyers or notaries have to issue such legally attested translations
      of evidences.
      The following flows of documents have to be considered specifically:


## 2 Vision and Scope of the VCD

### 2.1 Vision, Objectives and Maturity of the VCD

#### 2.1.1 Overall Vision of the VCD

A major point of discussion is a sustainable and reliable long-term vision for exchanging attestations
        among Member States. In the long-run the VCD should be able to adequately fulfil the contracting
        authorities’ need to prove suitability and non-exclusion of economic operators according to certain
        criteria while reducing the burden of proof for the economic operator. This requires a paradigm shift
        towards electronic exchange of evidence and a next generation of attestations and certificates that are
        currently just barely available in electronic form. The creation of uniform infrastructure in this
        heterogeneous domain will take some time as several different environments and stakeholders need
        to be involved, and change may not be enforceable to all of them. In this respect the VCD should
        support current practices of exchanging evidence in the short run and lead towards smooth, reliable
        and sustainable exchange of electronic evidences among Member States in the long run.
        In order to reach these goals we propose an approach with different stages of maturity that may be
        applied dependent on the readiness for the individual Member State. The aim is to support basic
        interoperability and exchange of documents on the lower maturity levels and leading towards direct
        electronic exchange of evidence in the higher maturity levels. Thereby each maturity level is built upon
        the lower ones thus allowing integration and step by step advancement.
        In the following we will introduce the staged maturity model for the VCD as depicted in Figure 2.
        The stages express different levels of maturity with respect to interoperability. A staged
        implementation approach is necessary in order to handle the complexity of the domain and to take into
        account the needs of the Member States. Every Member State should develop a solution that meets
        the demands of basic interoperability. Basic interoperability can thereby be defined as a state where
        organisational transparency of cross-border tendering requirements is established (stage 1- pre-VCD
        mapping tool). The efforts and expenses to develop a solution that ensures basic interoperability ought
        to be manageable and affordable.Member States, who would like to advance their solution towards a higher level of interoperability, can
        do so by adopting subsequent VCD maturity levels. The VCD specification must be generically and
        semantically extensible in order to reach a sustainable and fully-fledged solution in the final stage. An
        eTendering system and a contracting authority must be able to interpret a VCD package assembled by
        a VCD application regardless of the implementation stage of the VCD application and the eTendering
        system. Figure 2 illustrates the staged maturity model of the VCD that has been designed to show the
        different stages of implementation and development.
        In terms of construction and implementation, the VCD may be seen as a solution focusing on the
        European interoperability on the basis of European/national requirements and legislation. It is
        therefore necessary to ensure national transparency by gathering national requirements on certificates
        and qualification documents. The first implementation level (stage 1) is dependent upon these national
        requirements and will define a basic semantic interoperability model that supports the mutual
        recognition of certificates and qualification documents (pre-VCD mapping tool).
        The next step then is to define the structure of a VCD by adding several types of (meta)data into it
        (e.g. evidences, structural data of the evidences, translations etc.) and to build an application that is
        able to compile VCDs and enabling economic operators to submit this information electronically to
        contracting authorities (Stage 2).
        Stage 3 includes one of the most critical parts of a VCD which consist of making the evidences
        contained in a VCD comparable with regard to their contents to enable automated processing and
        understanding of its contents across borders (stage 3 – VCD advanced package). Beside this, stage 3
        will focus on additional services such as maintaining a VCD or composing a VCD from different
        economic operators in case of bidding consortia.
        Stage 4 (VCD networked package) will then provide a sophisticated method for changing the overall
        process from push to pull. A contracting authority will receive a VCD on the basis of stage 2 and 3
        (push) but the documents itself will not be submitted anymore. Instead a contracting authority can
        request those documents on demand from a database (pull) at national service provider who hosts
        VCD services, or directly from the very registration authority. The VCD networked package will provide
        the basis for further developments towards an electronic exchange of evidence.
        The stages follow a generic approach and may be seen as the evolution or development according to
        an underlying maturity model. The model as presented in Figure 2 is further described in the following
        subsection with the purpose to detail the various stages.
        For a future maturity path of a VCD Service one has to take into consideration the most important
        points of the vision and the goals of a VCD, which are:


#### 2.1.2 Objectives of the staged maturity level

The following preconditions and assumptions that define the context of VCD Services and VCD
        Packages should be taken into consideration:

#### 2.1.3 Level of Support and Level of Completeness (maturity model)

In accordance to the above mentioned major visions and requirements two important dimensions are
        to be considered in order to assess the benefits of a VCD Service and a VCD Package (cf. Figure 3):


##### 2.1.3.1 Level of Support given to economic operators and contracting authorities

The different levels of support address both the maturity of the service and the maturity of the VCD
          package, where the latter corresponds to the semantic richness of the provided information. On the
          Peppol/WP2 strategy there is explicit interest to have parallel increments on both sides, assuming that
          the semantic enrichment of the VCD package requires a corresponding enriched supporting system.
          This means, the higher the level of support, the higher the interoperability between the Member States
          (enabled by richer semantics of the information provided in the VCD Package).
          Information Support: Provides information about criteria and attestations including.

##### 2.1.3.2 Level of Completeness

A VCD Package will show its full potential when all the requested evidences (all that are necessary to
          prove all requested criteria) are contained in it. The range of evidences varies from self-declarations to
          official attestations or certificates issued by public authorities (see Figure 7 for a categorization). From
          a pragmatic point of view, it seems reasonable to focus on a subset of evidences in a first step and to
          complete the VCD Package later on. It is also reasonable to define a default package list that has to
          be provided in most public tenders by economic operators independently of particular criteria
          mentioned by the “Call for Tender”. This would reduce the burden of reading or interpreting the Call for
          Tender but would increase the need for interpreting other requirements and would not ensure a high
          level of completeness of a VCD. From these considerations we can derive the following approach:

#### 2.1.4 Criteria for qualification and selection and non-exclusion

The criteria for qualitative selection and non-exclusion as defined in the Directive 2004/18/EC are the
        common ground for building a cross border VCD service. The figure below shows the relevant criteria
        as defined in Articles 45-50 as these are regarded the most common ground when mapping any
        national criteria to the European ones.
        Mapping evidences to the criteria stated in Articles 45 and 46 may be regarded as sufficient for a first
        step since these can be further described within sub criteria and related atomic criteria . The personal
        situation of a candidate (Article 45) can be for example further described by:


#### 2.1.5 Steps on the path of development

### 2.2 Pre-VCD mapping tool (Stage 1)

The pre-VCD mapping tool introduces a procedure to collect information about the evidences for
      specific Call for Tenders. Thereby the Status quo procedure of section 1.2 remains unchanged, except
      that a pre-VCD mapping exists which is implemented and provided through a European service
      provider9 (see Figure 5). The mapping tool provides information to the economic operator on which
      national attestations of his or her country fulfill the criteria set by the procuring agency in the respective
      country (steps 4, 5). Likewise, the contracting authority can check evidences and authorizations
      provided by economic operators via the pre-VCD mapping tool (step 9).
      To fulfill a first precondition for a VCD package as introduced in Stages 2 and beyond, the pre-VCD
      mapping tool is the proposed function and the process that allows for its execution. It consists of a tool
      and of a data structure representing different contexts. These contexts are linked to the national public
      procurement domains and a single European common domain. For every domain we suppose to get a
      representation of a national index which provides an overview of national criteria demanded in public
      procurement, and how these are evidenced (i.e. which attestations and/or statements provide what
      evidence). This index also indicates structural data of evidence for example the issuer of the individual
      attestations or statements and the service it may activate for public or reserved access. In this respect,
      the European selection and exclusion criteria, which are derived from the European Directive
      2004/18/EC, can be considered the reference criteria, while the national criteria which are the basis for
      individual public tenders in respective countries are considered the local criteria. Figure 6 depicts the
      general taxonomy for the pre-VCD mapping concept, while Figure 7 shows a detailed taxonomy of the
      concept “evidence”. With this taxonomy, it is possible to map the fact that evidences can either be
      provided by the candidate himself (e.g. self-declaration, declaration on oath, solemn statement) or
      specific issuers as certified authorities and/or [authorized] third parties.
      Furthermore, evidences may be of different type such as statements, attestations or certificates, as
      indicated in Figure 7.
      Overall, the pre-VCD mapping tool supports in the proof of compliance of evidences of one country to
      the requested selection and exclusion criteria of another country via a mapping to the European
      exclusion and selection criteria.
      The respective retrieval of attestations and statements (6) and the subsequent steps (7-8) remain the
      ones as described in the status-quo description of section 1.2 above.




#### 2.2.1 Vision statement

Stage 1: Stage 1 can be seen as a minimal construction level. It implies the design and rolling out of a
        tool for supporting the basic interoperability between different legal conditions for providing evidence in
        public procurement procedures. As stated in the introduction, it can be seen as a minimum
        requirement for all Member States participating in the PEPPOL VCD work package.
        At this stage, a semantic model is introduced that supports guidance in applying the relevant
        community rules on mutual recognition of evidences (e.g. diplomas, certificates or other evidences of
        formal qualifications) in cross-border procurement procedures. The semantic model especially
        requires and provides for:


#### 2.2.2 Use Case description

The use case diagram in Figure 8 shows the main actors and functions of stage 1 (pre-VCD mapping)
        in the context of a public tender.
        A contracting authority sends a notification on a Call for Tender to a Publication body that publishes
        the call. The Call for Tender contains the definition of evidences and the specific criteria on qualitative
        selection and exclusion that are relevant to this particular call.
        If an economic operator decides to participate in a particular Call for Tender he can directly retrieve
        relevant information about evidences and criteria by using the information published in the Call for
        Tender. In cases below threshold or in the cases where the public notice is partial, the economic
        operator might send a direct request to the contracting authority in order to retrieve the required
        information. Having the relevant criteria in place the economic operator will be enabled to get a
        mapping to the national attestations that refer to those criteria via the pre-VCD mapping tool. Thesame process can be performed by the contracting authority in order to check whether the submitted
        attestations adequately fulfil certain criteria asked for.
        The pre-condition to the above flow of events is represented by the formal representation of imposed
        criteria, in particular for the qualification segments affecting, the technical, the financial and the quality
        criteria (as per directive 2004/18/EC_Arts. 47-50). Such formal representation has to be addressed
        along with the setting of the tool.
        Besides the use of the pre-VCD mapping in actual tendering and procurement procedures, a “system”
        needs to be maintained which implements the mapping of European and national laws, and the
        agreements of mutual recognition among Member States (see use-case diagram depicted in Figure 9).



#### 2.2.3 Major Features, Requirements and Quality Attributes

Major Feature: pre-VCD mapping tool
        The first feature to be addressed in this stage is the mapping between the criteria of qualitative
        selection and exclusion derived from Articles 45-50 of the Directive 2004/18/EC and the national
        attestations giving evidence to these criteria. To handle the large set of ruling articles, which may
        especially vary in the national implementations (articles 47-50), arts 45 and 46 shall get a higher
        priority for a smooth implementation at first hand, while arts 47 to 50 will only be selectively
        implemented on the basis of specific and deeper analysis in the PEPPOL pilot contexts. Due to the
        diversity and variability of evidences according to Art 51, this criterion will receive least priority in the
        implementations (if at all taken into consideration).
        This mapping includes at first hand an overview and transparency among national evidences and
        European criteria as shown in Figure 6 and Figure 7 above, including information about who issues
        specific evidence. Further on, this mapping needs to be implemented in the pre-VCD mapping tool as
        depicted in the use-case diagram in Figure 9, i.e. a list of criteria to be matched is submitted to the
        entity performing the mapping. Using the underlying technology, the mapping is done and its results,
        consisting of a list of the attestations giving evidence to the demanded criteria, can be transferred to a
        requester in case of a public tender.
        Requirements for the pre-VCD mapping tool
        The following requirements can be derived for stage 1:

##### 2.2.3.1 Create standard representation of European criteria of qualitative selection andexclusion

A major precondition for the enforcement of stage 1 is the definition of a standard representation of
          European criteria for qualitative selection and exclusion. These criteria should be derived directly from
          09/11/2009 – version 1.1 (approved by EC)
          the Articles 45-50 of the Directive 2004/18/EC in order to ensure employment in Pan-European public
          procurement procedures. The right granularity and consistency of criteria will be important to ensure
          legitimacy and to retrieve adequate mapping results. Thus the criteria may have to be iteratively redefined
          according to the results given by specific mappings.

##### 2.2.3.2 Appearance of European criteria within Call for tenders (Notification)

##### 2.2.3.3 Correspondence between national criteria for qualitative selection and exclusion and European criteria of qualitative selection and exclusion

National requirements of qualitative selection and exclusion for qualitative selection and exclusion
          have to adequately represent the national legal conditions. They have to be formulated in a way that
          they can be mapped to common European criteria for qualitative selection and exclusion mentioned by
          the Articles 45-50.

##### 2.2.3.4 Define a mapping template, perform mapping and ensure legitimacy

In a first step, all member states do have to establish a mapping of the criteria defined in the relevant
          EU directive 2004/18/EC to the national attestations giving evidence to these criteria. To ensure a
          degree of comparability and reliability among the results, the mapping should be based on a common
          template. For the overall activity it will be important to have the appropriate legal support in order to
          ensure legitimacy of mappings.

##### 2.2.3.5 Ensure legitimacy and trust of mapping

In order to achieve trust and an agreement on the mutual recognition of qualification documents as
          demanded in the directive, all artefacts and mapping results that relate to the mapping of evidence
          have to be approved from a legal point of view. Compliances to national and European conditions
          must be ensured in particular for the definition of a standard representation of common criteria of
          qualitative selection and exclusion, the definition of a mapping template and the mapping between
          national attestations and the common criteria for qualitative selection and exclusion.

##### 2.2.3.6 Ensure compatibility of the “mapping template” with existing check and verification procedures.

##### 2.2.3.7 Put in place a formal adoption and approval procedure for compliance and mutual recognition

##### 2.2.3.8 Specify an infrastructure and facility that provides the mapping service

The commonly approved national mappings have to be made accessible to the different stakeholders
          as especially economic operators, contracting authorities and national VCD service providers. For that
          purpose, a basic infrastructure or system architecture or a mapping facility has to be defined. The
          mapping facility, independent of how such as “system” is actually implemented, has to provide the
          services with regard to the pre-VCD mapping tool

##### 2.2.3.9 Define governing model with the necessary status and power to ensure fulfilment of functions like liability, sustainability and maintainability

A governing model has to be defined in order to deploy the infrastructure, to maintain its state and
          sustainability over time. In this respect the composition, structure and scope of the governing model
          has to be formally defined to ensure fulfilment of functions like liability, sustainability and
          maintainability. The dedicated governing model should have the necessary status and power to
          govern its assigned functions.
          A governing model with the necessary status and power MUST be formally defined in order to ensure
          fulfilment of functions like liability, sustainability and maintainability.

##### 2.2.3.10 Accessibility of mapping facility

Stage 1 is the key concept for ensuring interoperability between the different national systems of
          evidence provision in public procurement procedures. Every higher stage will be depended on the
          mapping model defined in this stage. Thus this stage will ensure the integration of different stages and
          interoperability as such. Therefore each national service provider that provides a VCD (stage 2-4) and
          all relevant key other stakeholder such as economic operators, contracting authorities and certifiers
          must be able to retrieve the latest mapping information from the mapping facility.
          The mapping facility MUST be accessible to all relevant key stakeholders such as economic
          operators, contracting authorities, certifiers and national service providers.

##### 2.2.3.11 Define the interaction among Publication Body and Contracting Authority

In order to derive sufficient mapping information the economic operator has to provide the criteria that
          are relevant to a particular call for tender. The overall procedure would be simplified dramatically when
          the relevant criteria for a particular call for tender could be fetched either from a publication body or
          directly from the contracting authority. The interaction with either the publication body or the
          communication with the contracting authority therefore has to be further defined.
          The interaction between mapping facility and Publication Body / Contracting Authority SHOULD be
          defined in order to simplify the procedure to retrieve the relevant criteria for a particular Call for
          Tender.

##### 2.2.3.12 Requirements regarding a Pre-VCD mapping tool

Attention has to be paid to a number of requirements such as reliability, accessibility, usability,
          maintenance, authenticity, actuality, compliance of mapping to laws and national structures, etc. The
          pre-VCD mapping tool has to be accredited by the European Union and the Member States.
          A number of functionalities of the mapping tool are:

#### 2.2.4 Expected Benefits for stakeholders

The pre-VCD mapping is the prerequisite for the VCD packages described in the subsequent stages. It
        requires that the European criteria and national criteria have to be elaborated and agreed upon by the
        different Member States. The major advantage and benefits of stage 1 are as follows:

#### 2.2.5 Scope, Limitations, Assumptions and Dependencies

As mentioned in the vision statement, this stage focuses on the preconditions for a VCD package, and
        hence provides only limited functionality. A mapping system is introduced, allowing the mapping of
        criteria to national evidences, thus omitting cumbersome manual and potentially error-prone selection
        of attestations/evidences by the economic operator across borders.
        The following statements describe the limitations of this stage, i.e. the functions that are not covered
        by this stage:

### 2.3 VCD simple package (Stage 2)

#### 2.3.1 Vision Statement

Stage 2 requires the establishment of a national VCD service provider which hosts the VCD system in
        order to provide economic operators with the services necessary to create an early VCD package.
        Thus, in stage 2, the concept of a VCD package is introduced. The national VCD service provider
        operates the VCD system and takes the role of a trusted third party (TTP) whose services can be
        partially trusted by contracting authorities. The VCD package relies on a set of automated, semiautomated
        and manual issuing services which are collected by the VCD system. Thereby issuing
        services that are automated through a direct access to national issuing bodies are reliable to the
        contracting authority while manual and semi-automated issuing service that have to be provided by the
        economic operator are not under control of the national VCD service provider. The VCD system wants
        to ensure completeness of a VCD package by acting as a single-point of contact for the economic
        operator that supports him in creating a VCD package from various sources.
        The VCD system in stage 2 will be capable to compile a VCD package from different types of data.
        Stage 2 defines the basic structure of a VCD package by including these types of data that give
        evidence for the suitability of an economic operator. Therewith the contracting authority will be enabled
        to check the validity of the evidences contained within the VCD and whether the requested evidence
        adequately represents the fulfilment of the demanded criteria. Thereby translation of evidences may
        be still necessary and has to be performed by the economic operator in dependence on national legal
        and organizational requirements because the VCD package does not provide any standardised
        context-specific data which provide common semantics. Checks concerning the content of the
        evidences are therewith not possible in this stage, as there is no context specific data available.
        Nevertheless a VCD simple package provides a set of other types of data that are introduced in the list
        below:


#### 2.3.2 Use Case description of VCD simple package (Stage 2)

The use case description of stage 2 contains several sub-diagrams that describe interactions that are
        needed firstly to authenticate to the systems and secondly to create, transport and view a VCD simple
        package. Figure 10 contains a general overview of the following systems and actors affected within
        the use case VCD simple package of stage 2 (VCD simple package):

##### 2.3.2.1 Identity and access management

The Identity and access management is an official procedure that handles roles for authorisation
          external to the VCD system and involves three actors, the economic operator, an officer and the VCD
          system itself as shown in Figure 11.
          Economic operators have to apply for a VCD account and therefore they have to provide sensitive
          economic operator data (for example by uploading attestations to verify these data). Sensitive
          economic operator data must initially be provided by an economic operator (e.g. company registration
          number, VAT number, social insurance number of the company etc.) in order to create an account and
          to start any VCD packaging service. An officer has to verify whether the provided data belongs to the
          economic operator and has to assure its correctness because either the VCD packaging service would
          not work or would deliver incomplete or wrong results. After verification the officer creates a VCD
          account where sufficient data about the economic operator is stored. In addition, identity and access
          management requires the possibility to delete an account within the VCD system and an official
          procedure to apply for a modification of the VCD account. An economic operator can authenticate to
          the VCD system only when the economic operator has sufficient user rights (e.g. authorized
          representative of economic operator) provided by identity and access management as shown in Figure
          12.



##### 2.3.2.2 VCD system

After authentication the economic operator can provide further tender specific data to the VCD system
          (e.g. TED ID) in order to start the creation of a VCD simple package. The VCD system creates a
          suggestion for compilation according to the results provided by the pre-VCD mapping tool and in turn
          the economic operator can edit and confirm the compilation suggestion that is given by the VCD
          system as shown in Figure 13.
          The function of creating a VCD package includes the collection of evidence (including translations)
          and structural evidence data through several sources. Evidence and structural evidence data is
          provided by issuing bodies which can submit evidence and structural evidence data to the VCD
          system via an interface. An important remark therefore is that economic operators can take the role of
          an issuing body by submitting for example candidate statements, manually collected evidence or
          translations of evidence. The interface to submit evidence is defined through a service definition that
          allows adding specific structural evidence data that belongs to that evidence. The collection of
          evidence is finalized when all required evidences are submitted and this requires waiting for those
          evidences that have to be provided manually or semi-automatically. The VCD system can now compile 
          the VCD package and creates a set of structural VCD package data that belong to the compilation
          process.

##### 2.3.2.3 VCD transportation system

The economic operator can submit the VCD simple package to the contraction authority by using the
          VCD transportation system which is part of the PEPPOL infrastructure. For using the VCD
          transportation system of WP8, both economic operators and contracting authorities have to
          authenticate to have access. An important remark hereby is the usage of procurement platforms
          where bids are typically uploaded according to a given Call for Tender. The transportation system of
          WP8 used by the VCD should be able to provide a possibility to send the VCD package directly to the
          contracting authority either by utilizing the upload functionality of a procurement platform or by directly
          sending the VCD to the contracting authority by using other means provided by the transportation
          system or typically used by the contracting authority. It is also important to state that the transportation
          system does not necessarily have to be used by the economic operator. The economic operator
          receives a VCD package by the VCD system and it is up to his choice how to submit the VCD package
          to the contracting authority.

##### 2.3.2.4 CD viewing system

After retrieving the VCD package from economic operators, contracting authorities may have to
          authenticate to the VCD viewing system in order to view the VCD package. In contrast economic
          operators do not have to authenticate to the VCD viewing system because they are taking the role of
          an owner of the VCD package.
          The VCD viewing system has to fulfil certain sub-functionalities for displaying the different kinds of
          data that are contained within a VCD package. In stage 2 the viewing system should provide the
          possibility to view the following types of data (see Figure 14):

#### 2.3.3 Major Features, Requirements and Quality Attributes

This subsection lists the major features, requirements and quality attributes that are significant for a
        VCD simple package. In particular the systems described above and their features are specified
        through requirements (functions and interfaces) as well as their quality attributes (non-functional
        requirements).

##### 2.3.3.1 Identity and access management

Feature: Application for VCD account
          This feature describes the necessary functionalities and interfaces that are needed to apply for a VCD account.
          Requirements: Application for VCD account

##### 2.3.3.2 VCD system

Feature: Initialization of VCD Request
          This feature describes the necessary functionalities and interfaces that are needed to request a VCD
          instance that is addressing a particular Call for Tender.
          Requirements: Initialization of VCD Request

##### 2.3.3.3 VCD transportation system

Feature: Authentication to VCD transportation system
          This feature describes the necessary functionalities and interfaces to authenticate to the VCD
          transportation system.
          Requirements: Authentication to VCD transportation system

##### 2.3.3.4 VCD viewing system

Feature: Authentication to VCD viewing system
          This feature describes the necessary functionalities and interfaces to authenticate to the VCD viewing
          system.
          Requirements: Authentication to VCD viewing system

#### 2.3.4 Expected Benefits for stakeholders

Table 3 shows the additional benefits of stage 2 (first stage in four-stage VCD concept containing documents):


#### 2.3.5 Scope, Limitations, Assumptions and Dependencies

The major aim of stage 2 is to draft logical systems that enable economic operators to create simple
        VCD packages and to submit them to contracting authorities. Thereby stage 2 focuses on the
        necessary different logical systems that either provide major functionalities with regard to creating and
        viewing a VCD packages (VCD system) or which support the entire process such as authentication
        (Identity and Access management), transportation (VCD transportations system) or translation (VCD
        translation system). The general assumption of stage 2 is that the former pre-VCD mapping tool (stage
        1) will be utilized as a module that is adequately integrated into the VCD system.
        Stage 2 also introduces the idea of a national VCD service provider which operates the different
        services necessary to create and view a VCD package. The national VCD service provider will provide
        a single-point of access to several attestations and issuing services that are electronically available.
        Nevertheless it will be necessary to include other evidences that have to be provided semiautomatically
        or manually by the economic operator. It also cannot be guaranteed that each
        evidentiary document required according to the criteria stated in the Call for Tender by the contracting
        authority can be pointed at with a particular mapping results of the pre-VCD mapping tool since some
        evidence diverge too much in their contents and scope. In those cases the VCD system will provide
        the possibility to add those documents into the VCD simple package through placeholders which may
        09/11/2009 – version 1.1 (approved by EC)
        have a very generic grounding for mapping defined through an abstract class of documents (e.g.
        evidence with regards to environmental management standards). When summarizing those points it
        can be generally stated that a VCD at stage 2 and beyond still relies on several manual processes that
        have to be generated by the economic operator and which cannot be automated in short or medium
        term. However, a reduced scope of a VCD is necessary in order to provide the possibility to submit a
        VCD that has a sufficient level of completeness.
        Another aim of stage 2 is to differentiate, define and structure the types of data that will constitute a
        VCD package. Stage 2 does not focus on the re-development of existing evidentiary documents but
        on their extension through a common standard representation within a VCD. The VCD package
        contains similar structural fields which likewise describe the evidences contained in it in similar
        manner, order and style. Having similar structural layout of a VCD it will be easier to understand the
        contents of it and potentially to translated those structural key information from the language of the
        issuer or economic to the language of the contracting authority. Nevertheless a translation of the
        contents of evidentiary documents is not focussed at in this stage and has to be provided manually by
        the economic operator through adding translations into the VCD simple package.
        Stage 2 lays the ground for the further development of a VCD package towards an advanced package
        within stages 3. The VCD package only focus on major functions that are necessary to create such a
        package and doesn’t make use of other service that are introduced in the subsequent phases such as,
        recompiling an existing VCD package, usage of context-specific data and merging VCD packages of
        different economic operators into a single one. The recompilation of existing VCD packages increases
        the maintainability of a VCD for the economic operator by for example indicating which evidence has
        to be replaced by a new one and which evidence has to be additionally provided in case preparing a
        bid for a different Call for Tender. The usage of context-specific data thereby is an important precondition
        since these data can provide real-time information about the status of contents of the VCD
        which is needed in terms of making update proposals. Also the merging of different VCD packages
        into a single unit to be used when consortia which prepare a bid as a multi-party group is not
        addressed in stage 2.

### 2.4 VCD advanced package (Stage 3)

#### 2.4.1 Vision Statement

Stage 3 represents a further step towards an optimised support for economic operators and
        contracting authorities. It is based on the features and functionalities of stage 2 and adds additional
        main features:


#### 2.4.2 Use Case description of VCD advanced package

Figure 15 shows the possible system interactions of the actors with the VCD system and the auxiliary systems.
        Figure 16 shows the possible interactions of the actors with the VCD system concerning the creation of a new VCD advanced package.
        Figure 17 shows the possible interactions of the actors with the VCD system concerning the recompilation of an existing VCD package into a new VCD advanced package.




##### 2.4.2.1 Create VCD advanced package

This use case contains the necessary steps an economic operator performs to create a new VCD
          advanced package. This use case is similar to the use case “Create VCD simple package” of stage 2
          but adds the necessary functionality regarding context specific data and merging existing VCD
          packages into the new VCD advanced package.

##### 2.4.2.2 Re-Compile VCD advanced package

This use case contains the necessary steps an economic operator performs to re-compile an existing
          VCD package into a new VCD advanced package. This use case contains the necessary functionality
          regarding context specific data and merging existing VCD packages into the new VCD advanced
          package.

##### 2.4.2.3 Provide VCD packages of consortium members

In order to merge VCD packages of several economic operators, acting as one economic operator
          (e.g. a consortium, contractor-subcontractor-relationships) into one VCD package, the economic
          operator has to be able to provide these VCD packages to the VCD system.

##### 2.4.2.4 Collect evidence, context specific data and structural evidence data

The stage 2-collection process for evidence and structural evidence data has to be extended to
          include the collection and processing of context specific data. It is important to understand that context
          specific data cannot be automatically extracted from unstructured data as scanned copies or text
          documents as this could lead to incorrect results due to the non-deterministic behaviours of such
          extraction mechanisms (OCR, etc). Valid deterministic approaches of providing (obtaining) context
          specific data are:

##### 2.4.2.5 Merge VCD packagess

In order to merge VCD packages of several economic operators, acting as a single economic operator
          (e.g. a consortium, contractor-subcontractor-relationships) into one VCD package, the VCD system
          has to be able to consider data from several existing VCD packages in the compilation process.

##### 2.4.2.6 Compile VCD advanced package

In order to be able to compile a VCD advanced package, the VCD compilation process must be
          extended to be able to process data from existing VCD packages of other economic operators and to
          process the context specific data that are included.

#### 2.4.3 Major Features, Requirements and Quality Attributes

This chapter contains the major features, requirements and quality attributes which are derived from
        the vision statement and the use-case descriptions of stage 3 and which extend the major features,
        requirements and quality attributes of a stage 2 VCD simple package.
        The major features of the VCD in stage 3 are:

##### 2.4.3.1 Context specific data

A major feature of a stage 3 VCD advanced package is the introduction of context specific data. These
          data fields are specified in an agreed upon data schema and describe the content of an evidence or
          parts of its content under a predefined selection schema. The benefit of using context specific data is
          to avoid the necessity to read through the original version or a translated version of an evidence in
          order to obtain the information which is necessary to decide, whether a criterion is satisfied or not and
          thereby having a structured overview of the important key data or information of the evidences
          contained in a VCD. This overview – the data representation – can be implemented either language
          independent or in multiple languages, so there is no need to translate the evidence any more if it is
          sufficiently described through context specific data. The enhanced and automated documents’
          readability that comes from the context specific data must be compared to the local legal provisions
          and document checking practice adopted by contracting authorities. Whether to use context specific
          data as substitute of a certified translation of an evidences or as decision support belongs to the
          contracting authority’s decision.
          Requirements: context specific data

##### 2.4.3.2 Advanced VCD creation service

The VCD creation service of stage 2 VCD simple package has to be improved in order to include the
          functionalities for considering context specific data and VCD merging.
          Requirements: Advanced VCD creation service

##### 2.4.3.3 VCD re-compilation service

In stage 3, the functionality of the VCD system has to be extended in order to provide a VCD recompilation
          functionality. Re-compiling a VCD package means using evidence data from an existing
          VCD package, validating which of the evidences are outdated, retrieving actual versions of the outdated
          evidences an creating a new VCD package which contains the not-outdated evidences from the
          original VCD package and the newly obtained evidences. The re-compilation process considers only
          those evidences which are necessary in be compliant to the criteria which have to be addressed in the
          new VCD package. The re-compilation can be invoked to re-compile a VCD package for a different
          Tender.
          Requirements: VCD re-compilation service

#### 2.4.4 Expected Benefits for stakeholders


Stage 3 will include the features depicted in chapter 2.4.3. Providing context specific data leads to an
        additional support for the economic operator and for the contracting authority addressing the need to
        evaluate the contents of evidences across borders. An economic operator is able to verify the
        correctness of the provided context specific data. The contracting authority in turn can check the
        suitability of an Economic Operator by having a sufficient summary of the contents of a VCD in the
        required language. The provision of context specific data avoids the need for translating certain
        evidences that are available in electronic format and allow the description of its contents using the
        common standard schema of context specific data. This approach follows again the idea to ensure the
        completeness of the VCD on the one hand and the level of support on the other hand by stepwise
        including more electronic evidences to the VCD.
        An important point to ensure the acceptance of this approach is to establish or expand the trust in
        national VCD services cross borders:

### 2.5 VCD network package (Stage 4)

#### 2.5.1 Vision statement

Stage 4 introduces a set of ideas and possibilities how further value can be added to a Virtual
        Company Dossier. The key idea of Stage 4 is to create a network for the VCD that allows retrieving
        attestations in a more flexible way. Potentially a direct exchange from trusted attestation services to
        contracting authorities could therefore be implemented. The Virtual Company Dossier than consists of
        some references to attestation services which mandate a contracting authority to obtain information
        directly.
        A direct exchange between trusted attestation services and a contracting authority would provide
        many opportunities with regard to an increase of the actuality of evidence, to lower the transaction
        costs of the parties involved and to reduce the time to create a VCD. Nevertheless such direct
        exchange is very difficult to implement technically because a lot of entities and attestation services
        have to be federated. This raises costs and other technical questions such as access policies to
        trusted attestation services and therewith also legal uncertainties such as data privacy, data security
        and data protection. Also from a political point of view there might be several objections to give a direct
        access to source registers and issuing bodies. Finally a semantic pre-condition would be that evidence
        is provided in a common electronic format that allows an automated transformation into the requestor’s
        target language. Such a solution would then be also depended on mutually recognized, contextspecific
        data formats provided by some specific networks such as BRITE or ECRIS
        (Siemens_and_Time.lex 2008).
        In order to avoid some of the above mentioned complexity we propose some first steps that might help
        to combine the ideas of a VCD and a federated network in medium term allowing further
        improvements of a VCD. To avoid political and technical questions with regard to federated networks,
        the access to attestations services should be done indirectly through the national VCD service
        provider. We suggest that a national VCD service provider uses a temporary storage to hold the
        attestations instead of compiling them directly into a VCD. The VCD then only consists of a number of
        flags that denote an evidence as well as structural data of evidence and context specific data plus a
        reference to retrieve the attestation on demand at the time of awarding. Therefore it would be
        important that the evidence requested is valid at the time of awarding or when the call for tender is
        closed. Also mechanism for maintenance of evidence could potentially be implemented in order to
        keep the information up to date. Such model of indirect exchange would also make it easier for a
        national VCD service to establish an official list of approved economic operators in accordance with
        Article 52 (1) of Directive 2004/18/EC. The national VCD service provider could use the information
        within its storage to maintain such lists. Evidence that is sufficiently described through context specific
        data could then for example be automatically validated by a national VCD service provider by putting
        validation values into a VCD.
        Stage 4 therewith improves the level of support for the economic operator since the need and burden
        to present specific attestations to the contracting authority will be eliminated. Stage 4 therewith fulfils
        the paradigm shift where a contracting authority only asks for the fulfilment of certain criteria and not
        for the delivery of specific evidence. It changes the general approach of providing attestations at the
        time of the bid but consequently performs all the related functionality of stages 2 and 3 (e.g. provision
        of structural data of evidence and context specific data). Stage 4 introduces the "on-demand" idea
        which allows retrieving evidence directly from the national VCD service provider on individual basis. In
        order to ensure the level of completeness, the VCD network package needs to be extended stepwise
        by including evidences which are sufficiently described through agreed and standardised contextspecific
        data and structural data of evidence (and which can easily be validated by the national VCD
        service provider when he accredits economic operators according to Article 52). We propose the
        following major building blocks to establish a VCD networked package:


#### 2.5.2 Use Case description

Stage 4 does not contain a modelled use case diagram that clarifies the system interaction and a
      detailed description of requirements because it mainly relies on the functions introduced in the
      previous stages and there are no pilots yet for this stage. Nevertheless the use case description
      provides a short textual explanation and major requirements of this stage are mentioned. Functions in
      round brackets ( ) are new to this use case:
      The economic operator requests a VCD on the basis of stages 1, 2 and 3 at the National Service
      Provider. The National Service Provider starts the VCD creation process by requesting attestations
      from Trusted Attestation Services that are connected to context specific networks. Trusted Attestation
      Services provide requested attestations to a local database or repository that is owned by the National
      VCD Service Provider (store attestation). The VCD system enables the economic operator to mandate
      the contracting authority to access his attestations within the VCD system if the attestations are
      sufficiently described through context specific data (mandate to request attestation through VCD
      specific reference) and the VCD system creates a specific reference into the VCD itself (set reference
      to attestation to VCD).
      When all attestations are compiled by the VCD system the economic operator can submit its VCD to
      the contracting authority. The contracting authority can now request attestations through the reference
      that is specified in the VCD (request attestation on individual basis). The VCD System checks whether
      the contracting authority has sufficient access rights and has been mandated by the economic
      operator to retrieve that attestation (check access rights). Afterwards the VCD system delivers the
      attestation to the contracting authority (retrieve attestation) or informs the economic about a request
      that cannot be handled adequately (conflict resolution). The economic operator than may have to
      provide an additional translation to the contracting authority within a certain period of time.

This chapter contains the major feature, requirements and quality attributes which are derived from the
       vision statement and the use-case description of stage 4 and which extend the features, requirements
       and quality attributes of the previous stages.
       Feature: Mandate contracting authority

#### 2.5.4 Expected Benefits for stakeholders


#### 2.5.5 Scope, Limitations, Assumptions and Dependencies

Stage 4 relies on several functionalities or concepts that have been already addressed and described
      in previous stages. Basically the VCD network package relies on most of the features and
      functionalities already described in the previous stages. Nevertheless some of them take a particular
      role for implementing stage 4:


## 3 Legal, organisational and semantic framework and requirements

Interoperability is a major topic being discussed in eGovernment for a while now. Already in 2003, the
    EC has published a working document, the European Interoperability Framework (EIF), where the
    authors defined IOP as “the means by which the interlinking of systems, information and ways of
    working, whether within or between administrations, nationally or across Europe, or with the enterprise
    sector, occurs” ((IDABC 2004), pp. 6). The document recalls IOP needs on technical, semantic and
    organizational layer with a rather wide understanding of IOP (IDABC 2004). In late 2008 a draft for a
    revised European Interoperability Framework was published by IDABC extending the requirement for
    IOP to five levels12:
    The aim of this chapter is to draw a picture about the current situation applied in the countries with
    regard to potentially placement of a VCD in the MS according to the European Interoperability
    Framework version 2 (EIF2):


### 3.1 Organisational Framework

#### 3.1.1 Overview about organisational framework

The organisational framework for the VCD has several dimensions. The use cases of the stages
        above show the actors that are involved and have to be addressed through the organisational
        framework e.g. economic operators, contracting authorities, issuing bodies, national service providers
        etc. Within the project it will be necessary to manage these different kinds of stakeholders by
        adequately integrating them into the project. Thereby it will be of importance to define their specific
        role and their importance for our work package within the lifetime of the project. Networks of gathering
        evidences are complex to handle because there are several stakeholders to consider. To avoid
        problems of involvement a clear approach of stakeholder analysis is needed. WP2 can only provide
        guidance to this since it will be a national responsibility. Austria for example has set up a physical
        stakeholder forum that informs key stakeholder in regular time intervals about the results of PEPPOL.
        Next to this the WP2 team of Austria is building up a participation platform13 where latest results are
        presented and can be further discussed within forums and mini surveys. Each member state has to
        define its own strategy to involve stakeholders during the lifetime of the project. WP2 has developed a
        template for stakeholder management that may provide guidance for this. It can be found in ANNEX
        IV: Template for stakeholder analysis.
        To ensure a wide acceptance of the solutions provided by WP2 among stakeholders we have to
        prevent changes in national procedures and infrastructures but to utilize them as much as possible. In
        stages 2, 3 and 4 it will be necessary to establish a national service provider who will take care about
        critical VCD processes and therewith ensure legitimacy, trust and appropriate change management.
        Any VCD solution should provide universal support for economic operators of any size. Testing of a
        VCD solution will be very important and should be done by reprocessing historical tenders in order to
        avoid problems of disqualification due to errors of applications.
        Another important part of the stakeholder analysis is the identification of recognized public and private
        issuing bodies. This may be done through the support of DG Markt’s study (Siemens_and_Time.lex
        2007) report on national country profiles14 and additional national analysis. These entities then need to
        be included into a list of recognized private and public issuing bodies which will be an important part
        when defining structural data of evidence (e.g. issuer, availability, delivery time etc). A national VCD
        application may list several different issuing bodies that provide the same attestation. These may have
        different characteristics as for example price, availability or delivery time. However the choice which
        attestation is most appropriate should be left to the economic operator but this decision may be
        supported through displaying these different characteristics. If an economic operator for example
        decides to rely on a manual issuing service that cannot be directly invoked by a national service
        provider it is the responsibility of the economic operator to provide this attestation and act as issuing
        body by uploading it to the system of the national service provider in order to create a VCD package.
        Each national service provider provides a national VCD solution in accordance to the key principles
        mentioned in the use cases. National solutions therefore may vary due to freedom of implementing
        national solutions but conformance to key issues should ensure their interoperability. A key issue for
        example is the pre-VCD mapping tool and it should be integrated into any national solutions either as
        a module or as interface to query results for the mapping of evidences among member states. To
        enable automated information processing on the basis of the pre-VCD mapping tool within national
        solutions additional structured information has to be defined within the Call for Tender that enables the
        retrieval of qualification and selection criteria from contracting authorities. A contracting authority
        therefore has to specify a relevant criteria subset within a Call for Tender which can then for example
        be referred to by an economic operator by providing the ID of a Call for Tender to the national solution.
        Two phased tendering is not explicitly foreseen by the VCD even if it might be used for this purpose. In
        most cases we do not see great efforts for economic operators in two-phased since many countries
        only required the submission of self-declarations.
        None of the above mentioned solutions explicitly requires implementing Article 52 of directive
        2004/18/EC. Thus the VCD itself provides support for the proofing of conformance but it does not
        provide any information whether an economic operator is conform. In stages 3 and 4 a higher “level of
        decision making” is promoted and we see especially the provision of context specific data (stage 3)
        and the on demand approach (stage 4) as a pre-conditions that ease the establishment of lists of
        approved economic operators across borders. However if there is a country that wishes to enable
        such a proof in the VCD it can be done before but will require several manual efforts. Although such
        proof of conformance should rely on Articles 45 and 46 of directive 2004/18/EC first.

#### 3.1.2 Organisational requirements

The requirements listed in the subsequent section have been identified and are essential for any WP2
        solution. They are independent of a particular stage or show interrelations between them thus they are
        called high-level organisational requirements. The requirements have to be fulfilled or further analysed
        and specified in the project lifetime in order to further draft the organisational framework for a VCD to a
        greater extend.

##### 3.1.2.1 List of recognized public attestation bodies

Description
          Article 52 describes that Member States may introduce either official lists of approved contractors,
          suppliers or service providers or certification by certification bodies established in public or private law.
          Requirement
          A list of recognized public authorities that are able to issue certain attestations in a particular Member
          State MUST be established.
          Measurement
          List of recognized public attestation bodies in VCD index

##### 3.1.2.2 List of recognized private attestation bodies

Description
          Article 52 describes that Member States may introduce either official lists of approved contractors,
          suppliers or service providers or certification by certification bodies established in public or private law.
          Requirement
          A list of recognized private entities that are able to issue certain attestations in a particular Member
          State SHOULD be established.
          Measurement
          List of recognized public attestation bodies in VCD index

##### 3.1.2.3 Utilization of existing national procedures and infrastructures

Description
          Widely accepted national procedures and infrastructures in requesting, issuing, exchanging, collecting,
          assembling, proving and submitting evidence should be utilized wherever possible in order to improve
          acceptance of a solution and in order to lower the complexity of the domain.
          Requirement
          Widely accepted national procedures and infrastructures SHOULD be utilized wherever possible.
          Measurement
          Acceptance of the solution among stakeholders

##### 3.1.2.4 Increasing trust through national authority

Description
          A national authority (e.g. national service provider) should ensure legitimacy in critical VCD processes
          of requesting, issuing, exchanging, collecting, assembling, proving and submitting evidence in order to
          increase the trust between the entities involved.
          Requirement
          A national authority MUST support critical processes in order to increase the trust between the entities
          involved.
          Measurement
          Establishment of legally regulated national service provider for the VCD

##### 3.1.2.5 Conformance of national solution with pre-VCD mapping tool defined in stage 1

Description
          The common ground for WP2 is the establishment of national pilot solutions that ensure
          interoperability of attestations across Member States. Therefore WP 2 has defined a pre-VCD
          mapping tool described in stage 1. Any national pilot solution that will be developed using resources of
          PEPPOL must use the pre-VCD mapping tool in order to achieve the desired objectives.
          Requirement
          Any national pilot solution that will be developed in the context of PEPPOL WP2 has to follow the pre-
          VCD mapping defined in stage 1.
          Conformance between the processing of different national VCD services has to be ensured, monitored
          and surveyed by a European VCD service provider that needs to be set up with defined
          responsibilities and procedures. The European VCD service provider will maintain the common
          descriptions and monitor the development of the national solutions and assess their conformance to a
          common European interface (i.e. the pre-VCD mapping tool).
          Measurement
          VCD packages need to provide mapping functionality with the pre-VCD mapping tool

##### 3.1.2.6 National Freedom of implementing pilot solutions

Description
          The implementation of a national VCD solution in stages 2, 3 and 4 requires a wide degree of freedom
          in implementing this solution according to national conditions and requirements. Specific national
          functionalities of pilot solutions therefore are not subject to discussions and agreements between
          different WP partners as long as they follow the common interoperability guidelines of the
          specification.
          Requirement
          National implementations of VCD systems and their functions are no subject to discussions and
          agreements between WP partners as long as they follow common interoperability guidelines that will
          be monitored by the European VCD Service Provider.
          Measurement
          Conformance with common interoperability guidelines that will be monitored by the European VCD
          Service Provider.

##### 3.1.2.7 Scope with regard to Article 52

Description
          Article 5215 describes that EU Member States may introduce either official lists of approved
          contractors, suppliers or service providers or certification by certification bodies established in public or
          private law.
          Pilots implemented in stages 1, 2, 3 and 4 produce VCD artefacts that enable matching between
          attestations and certain criteria across borders and the implementation of the VCD package. This does
          not include that any check or proof of conformance is performed by any national service provider who
          provides a VCD package with regard to the contents of the package and its attestation as for example
          describe in Article 52 of the directive (“official lists of approved contractors, suppliers or service
          providers”). In stages 1, 2, 3 and potentially also in stage 4 the check and proof of conformance
          belongs to the economic operator himself. Nevertheless any stage may be implemented according to
          Article 52 if there is adequate legal basis within a country and if there is political commitment for doing
          so. Stage 4 is providing a good opportunity to implement Article 52.
          Requirement
          A national pilot solution may implement attestation validation feature but proof of conformance and
          checking is not a mandatory feature that has to be fulfilled by a national service provider.
          Measurement
          National Service Provider does not have to approve the documents submitted by economic operators
          Requirement
          Any of the proposed stages SHOULD be applicable within a Member State who wishes to apply Article
          52 and EFTA EEA Committee decision 68/2006.
          Requirement
          A Member State MUST formally define an authority that is able to provide a proof of conformance to
          certain criteria if the Member State wishes to implement Article 52 or if Article 52 is already
          implemented.
          Measurement
          Authority that takes the role of validation point and Article 52 implemented.

##### 3.1.2.8 Specification of subset of evidences and related criteria by the contracting authority

Description
          A contracting authority sends a notification on a Call for Tender to a Publication body that publishes
          the call. The Call for Tender contains the definition of relevant evidences and specifies the relevant
          criteria on qualitative selection and exclusion. If an economic operator decides to participate in a
          particular Call for Tender he can directly retrieve the relevant criteria and evidences by using the
          information published in the Call for Tender. In cases below threshold the economic operator might
          send a direct request to the contracting authority in order to retrieve the required information. Having
          the relevant criteria in place the economic operator will be enabled to get a mapping to the national
          attestations that refer to those criteria via the pre-VCD mapping tool.
          Requirement
          The contracting authority has to specify a subset of the superset of criteria that is relevant to a specific
          Call for Tender so that any VCD application can perform the mapping later on
          Measurement
          Development of standard template for specifying criteria as part of tender-specific data

##### 3.1.2.9 Provision of subset of evidences and criteria by the Economic Operator

Description
          If an economic operator decides to participate in a particular Call for Tender he can directly retrieve
          information about relevant evidences and related criteria by using the information published in the Call
          for Tender. In cases below threshold the economic operator might send a direct request to the
          contracting authority in order to retrieve the required information. Having the relevant evidences and
          criteria in place the economic operator will be enabled to get a mapping to the national attestations
          that refer to those criteria via the pre-VCD mapping tool. The economic operator therefore has to
          provide a subset of the superset of evidences that is relevant to a specific Call for Tender to its
          National Service Provider or VCD system.
          Requirement
          Any VCD system must have an interface to provide tender-specific data and (in particular the relevant
          criteria subset) in order to perform the mapping.
          Measurement
          Interface for providing tender specific data and in particular the relevant criteria subset.

##### 3.1.2.10 Scope of VCD application with regard to two-phased tendering

Description
          The VCD is subject to the main submission of attestations and not to any pre-submission typically
          required in two-phased tendering. A national pilot VCD solution may support the pre-submission of
          evidence as well.
          Requirement
          The main subject of the VCD is the final submission of evidence to the contracting authority
          Measurement
          VCD package supports final submission of evidence

##### 3.1.2.11 Principle for selecting issuing body

Description
          There are often multiple issuing bodies available which provide evidence of the same kind but with
          different characteristics such as cheap issuing services and fast issuing services. The requestor has to
          decide by himself which issuing service is most appropriate to satisfy his needs. A pre-selection of
          issuing services could be provided by the VCD system.
          Requirement
          If there are multiple ways to provide evidence the choice of selecting a specific issuing service is left to
          the requester.
          Measurement
          Functionality and interface to select issuing services

##### 3.1.2.12 Economic Operators that act as Issuing Bodies

Description
          Any VCD system relies on issuing services that cannot directly invoked electronically. Often the VCD
          system will have the possibility to specify the issuing services that are needed to evidence certain
          criteria e.g. candidate statements or attestations from third parties that are not available in electronic
          format. An Economic Operators must take care of collecting and preparing these evidences and to
          submit them to the VCD system.
          Requirement
          An economic operator MUST be able to act as an issuing body for candidate statements or other
          evidence that cannot be directly or electronically retrieved by the VCD system.
          Measurement
          Functionality and interface that enable economic operator to upload any kind of evidence to the VCD

##### 3.1.2.13 Universal support

Description
          “E-business is relevant to organizations of any size. Traditionally only larger organizations have been
          able to take advantage of e-business primarily due to the cost barrier. The evolution on the Internet
          has shown that as soon as the barrier for entry is lowered enough – even the smallest organizations
          will take advantage of the new technology. It is therefore important that when new technology is
          established that the barrier for taking up the technology is sufficiently low.” (Bausa O. and Boujraf A.
          2009)
          Requirement
          The electronic procurement framework MUST support organizations of any size and industry.

##### 3.1.2.14 Testing of VCD solution

Description
          WP2 concentrates on pre-awarding issues where requirements and procedures are often strict due to
          principles like equal treatment, non-discrimination, transparency, competition etc. Although a VCD
          does not include the offer itself it provides several documents that are of great importance for the
          award of contracts and therewith critical for the success of an economic operator for example in cases
          of disqualification because of late delivery of a VCD. To avoid those problems testing of VCD should
          be done by reprocessing historical tenders.
          Requirement
          The VCD solutions MUST be tested in specific cases by re-processing historical tenders. The testing
          SHOULD be repeated regularly and especially after up-dating of software. A national solution will only
          be authorized to operate cross-border when all tests are passed; the testing has to be maintained and
          monitored by the European VCD Service Provider.
          Stakeholder MUST be found in order to re-process historical tenders.
          Measurement
          Test results.

### 3.2 Semantic framework

#### 3.2.1 Overview of semantic framework

Today’s work in public administration is still strongly based on the work with documents and files. With
        the consideration of data object and document flow, a disambiguation of the terms used is reasonable
        to clarify the concepts.
        Electronic documents can be text, tables, images or a combination of these and are available in digital
        form. Generally, this comprises each potentially permanent recording of data on a data carrier. Many
        European states allow the use of electronic documents as a replacement for documents in written
        form. Such documents find also application in tendering procedures and shall be part of VCD. Thus
        the electronic document is the central means for Public eProcurement and for the usage of a VCD on
        pan-European level.
        The characteristics of a document are combined from physical shape (paper or electronic file), formal
        properties (e.g. structure and style), organisational properties (functional relation, version, indexing in
        a filing plan), content, document type (storage obligations, legal character, editability), time stamping
        (creation, expiry, last access), editors (sender, creator, author) and users (receiver, (last) editor,
        reader).
        Official documents need to fulfil specific requirements like completeness, integrity and transparency.
        Apart from this, they also need to conform to the legality principle of administrative actions and to audit
        trails. A file (record) is a factual and task-related arrangement and collection of documents which
        belong together. The goal is to keep the content available and traceable at any time. Files are
        recorded with a unique identification.
        This chapter describes the semantic framework of work package 2 that comprise solutions for the VCD
        from the data perspective. Section 3.2.2 therefore provides a brief overview about general patterns for
        data representation and utilisation. Thereby different data perspectives have to be separated that
        comprise a VCD:

#### 3.2.2 Patterns for Data Representation and Utilisation

The Vision of the VCD comprises several different concepts such as visualization of data (e.g. stage2:
        visualisation of a VCD), sending / receiving data elements (e.g. stage 2: collecting evidence or stage
        4: requesting attestation on demand), transferring data (e.g. stage 2: submission of a VCD) and
        routing of data (stage 4: exchange of validation values). To further clarify their interrelation we take the
        research by (Russel N., Hofsteded A.H.M. et al. 2005) of data occurrences in systems into account
        that characterize following categories:



#### 3.2.3 Relevant standards, methodologies and initiatives for the VCD package

The following subsections contain major standards and methodologies that shall be used for creating
        a VCD package. The mentioned metadata standards and the standards for record management are
        currently investigated for the purpose of our work package. Beside this CEN BII16 develops a VCD
        profile that can be interpreted and used by systems based on both UN/CEFACT and UBL.

##### 3.2.3.1 Records Management

A selection of such documents will be included in any VCD; they will be produced by national units
          according to national legislation. This means that their content of data and information will vary. Both
          manual and automated cross border evaluation processes will require information about the legal
          validity of the documents, record by record.
          This means that the records of these documents need to be tagged for the processing. The label can
          give access to contextual information, like a country’s legislation and constraints valid for the very
          document.
          Methods are specified in ISO 15489-117 “Records Management”, and European requirements are
          detailed in MOREQ II18. Application of the standard will ease manual processing of such documents
          across borders and it will prepare for the use of automation.

##### 3.2.3.2 Metadata standards

Tagged records, information and data can be processed by independent systems and applications
          only if the constraining tags or metadata are recognized by the different processing parties. ISO
          1117919 offers such a methodology that is widely accepted.
          The purpose of ISO/IEC 11179 is to give concrete guidance on the formulation and maintenance of
          discrete data element descriptions and semantic content (metadata) that shall be used to formulate
          data elements in a consistent, standardized manner.

##### 3.2.3.3 CEN BII

CEN BII is addressing the convergence between UN/CEFACT and UBL by working out neutral
          descriptions called profiles that are describing business operational units of business functionality, like
          the VCD. The CEN BII VCD profile will be a document that can be interpreted and used by systems
          based on both UN/CEFACT and on UBL. The process of a cross-border submission of the VCD will be
          done co-jointly with the CEN BII workshop. Hence, the use of ISO 15489 and ISO 11179 leads to
          standardised records and information management that can be automated in existing structures.

##### 3.2.3.4 Methodical Framework

PEPPOL WP2 is investigating how to apply ISO 15489 to describe the structure and content of:

#### 3.2.4 Semantic Requirements

The requirements listed in the subsequent section have been identified and are essential for any WP2
        solution. They are independent of a particular stage or show interrelations between them thus they are
        called high-level semantic requirements. The requirements have to be fulfilled or further analysed and
        specified in the project lifetime in order to further draft the semantic framework for a VCD to a greater
        extend.

##### 3.2.4.1 Semantic interoperability

Description
          Semantic interoperability refers to the exchange of information in an understandable way within and
          across organizational borders.
          “To run real electronic business transactions without human intervention, semantic interoperability
          must be achieved. Deliverables from CEN BII are addressing semantic interoperability for some
          business documents relevant in electronic procurement. Outcomes from CEN BII are syntax neutral,
          which means that different syntaxes can be bound to the semantic requirements for the documents to
          be exchanged meaningfully despite their syntax.
          Even if syntax interoperability is not achieved in a pan-European framework, it has to be possible to
          transform from a syntax vocabulary to another one without loosing.
          Semantic interoperability should apply to all documents related with electronic procurement. It is
          required to work on the semantic interoperability for electronic attestations and certificates that
          requires not only semantic alignment but legal alignment in Europe.”(Bausa O. and Boujraf A. 2009)
          Requirement
          Evidential documents exchanged between parties MUST be semantically harmonized in order
          to be processed electronically.

##### 3.2.4.2 Correspondence between national and European criteria

Description
          National criteria for qualitative selection and exclusion should be formulated in a way that they can be
          mapped to European criteria for qualitative selection and exclusion mentioned by the Articles 45-50.
          Requirement
          National criteria for qualitative selection and exclusion MUST correspond to European criteria which
          are derived from Article 45-50 and which are partially described in the Eligibility of Tenders.
          Measurement
          Specialization Relationship
          Requirement
          National criteria SHOULD be consistent among themselves and with European criteria.
          Measurement
          Qualitative Evaluation and mapping

##### 3.2.4.3 VCD specific characteristics

Description
          Any instance of a VCD requires to be defined for a particular economic operator. Next to this it is the
          aim of the work package to make each VCD specific to a particular Call for Tender. The pre-VCD
          mapping tool therefore will provide sufficient support and has to be integrated into a VCD system.
          Requirement
          Any VCD instance MUST be specific with regards to a certain economic operator.
          Any VCD instance SHOULD be specific with regards to a certain tender.
          A unique VCD identifier needs to be established.
          Measurement
          VCD can be applied to a specific tender and economic operator.

##### 3.2.4.4 Method for ensuring “Level of completeness”

Description
          A VCD package will show its full potential only when all requested evidences (all that are necessary to
          prove all the requested criteria) are contained within it. The range of attestations varies from selfdeclarations
          to official attestations/certificates issued by public authorities. From a very pragmatic point
          of view it seems reasonable to focus on a subset of attestations in a first step and to complete the
          VCD Package later on. It is also reasonably to define, where and when permitted, a default packaging
          list of tender independent criteria to be served without the burden of reading or interpreting the “Call
          for Tender”. Several requirements can be derived.
          Requirement
          When implementing any tool, system or service WP2 MUST focus on mandatory requirements and
          evidences mentioned in Articles 45 and 46 first since theses Articles are not tender-specific and
          therewith relevant for nearly all tenders.
          Measurement
          Any definition, specification, modelling or implementation will first focus on Article 45 to 46
          Requirement
          The mapping between evidences via requirements MUST have set a primary focus on the mandatory
          requirements and evidences of a VCD.
          Measurement
          The definition, specification, modelling or implementation of the pre-VCD mapping tool will focus on
          Articles 45 to 46
          Requirement
          Articles 47 to 50 open a wide range of different criteria which are tender- and country-specific thus
          they MUST be added stepwise to the pre-VCD mapping tool (which may require a higher-level
          mapping).
          Measurement
          Any definition, specification, modelling or implementation of Articles 47 to 50 will be done on a higher
          level.
          Requirement
          Any VCD system SHOULD provide the opportunity to the economic operator to produce a complete
          VCD even if there are several issuing services that are not under control of a national service provider,
          do not have specific mapping to other documents defined in the pre-VCD mapping tool and have to be
          provided by the economic operator manually.
          Measurement
          The VCD solution includes a concept of placeholders.

##### 3.2.4.5 Placeholders in VCD packages

Description
          Since the completeness of a VCD package should be ensured but a complete mapping of evidence
          may not be provided as especially the criteria of Articles 49 to 50 of the directive are unstructured and
          much dependent on tender-specific requirements it has to be possible to define placeholders where a
          contracting authority may complete the mapping on individual basis through uploading evidence to
          these placeholders.
          Requirement
          Any VCD system provides the functionality to add additional documents through placeholders.
          Measurement
          Conceptual definition of placeholders with the VCD system and mapping

##### 3.2.4.6 Semantics of evidence

Description
          The VCD system should provide a functionality that allows issuing bodies to submit evidence to it.
          Therefore interfaces to submit evidence to the VCD system have to be defined. Those interfaces
          should also provide the possibility to describe structural data, context specific data and where
          applicable validation values of the evidence along with common semantics. Thereby manual, semiautomated
          and automated interfaces have to be separated
          Requirement
          Interfaces to submit evidence to the VCD system have to be defined along with common semantics in
          order to allow issuing bodies to further specify evidence with regard to structural data, context specific
          data and validation values.
          Measurement
          Interface to upload evidence or to retrieve evidence contains possibility to specify structural data
          manually or automatically

##### 3.2.4.7 Visualization of the VCD package

Description
          Any VCD package that is created by a VCD system should be an artefact that can be interpreted
          without using specific technology. Thereby the VCD requires a sufficient format in order to be
          presented and displayed to other systems and users.
          Requirement
          Develop a format that allows the presentation and displaying of the contents of a VCD package.
          Measurement
          Visualization of the VCD package

##### 3.2.4.8 Implementation approach with regard to stages of maturity

Description
          The implementation of different stages of maturity requires a general approach that defines which
          parts are mandatory and ensure semantic interoperability of VCD packages. The below mentioned
          requirements provide guidance for and further explain where mandatory and optional requirements
          can be found.
          Requirement
          The pre-VCD mapping tool (Stage 1) MUST be filled with instances (defined) by every Member State
          since Stage 1 is a precondition for any other stage.
          Measurement
          Pre-VCD mapping tool filled with national instances
          Requirement
          The VCD simple package (Stage 2) lays the basic ground for the creation of VCDs and the
          implementation of other services mentioned in stages 3 and 4 so the key concepts of Stage 2 MUST
          be implemented in each Member States.
          Measurement
          Key concepts such as structural data of evidence applied to VCD package
          Requirement
          Stage 3 (VCD advanced package) and stage 4 (VCD networked package) introduce a set of optional
          functions that SHOULD be considered by each Member State when implementing a VCD.
          Requirement
          The stages are logically built upon each other but it MUST be possible to implement certain features of
          stage 4 if the necessary requirements for this are fulfilled in the lower stages even if maybe not all
          requirements are fulfilled in stage 3.

##### 3.2.4.9 Principle for including attestations in stage 3 and 4

Description
          Stage 4 implies the exchange of certified validation values (e.g. certified “Yes/No” statements) instead
          of delivering an attestation. The attestations can be requested by the contracting authority on
          individual basis at the time of awarding and selection of candidates.
          Validation values (e.g. certified “Yes/No” statements) should only be applied to networks where
          sufficient context specific data is available in order to approve this value. The validation value should
          be able to prove conformance to criteria of qualitative exclusion and selection unambiguously. This
          principle should be applied wherever possible for example:
          • The economic operator has to prove that he paid fiscal taxes according to national regulations – in
          this case a “Yes/No statement” will be sufficient.
          • The economic operator has to provide balance sheet or extracts from it in order to proof its
          economic or financial standing – in this case the whole attestation (balance sheet or extracts of it)
          has to be delivered.
          - If sufficient context specific data format for representing those information unambiguously is
          available it may be applied for stage 4.
          Requirement
          PEPPOL WP2 is not focussing on the creation of context-specific data of attestations or candidate
          statements in multilingual versions. If context-specific data is provided in multilingual versions (e.g.
          XBRL, ECRIS etc.) this has a high priority to be included into stage 3 and stage 4.
          Requirement
          If attestations are described sufficiently in multiple lingual versions they SHOULD be included first to
          stages 3 and 4.
          Requirement
          If the prove concentrates on qualitative aspects (e.g. provide balance sheet or extracts from it in order
          to proof its economic or financial standing) then the validation value cannot be applied. Instead such
          an attestation can be included into VCD stages 3 and 4 if it is sufficiently described through context
          specific data in multilingual versions (e.g. XBRL, ECRIS etc.).
          Measurement
          Evaluation of context-specific specific standard representations for evidences

##### 3.2.4.10 Classification schemes awareness

Description
          “A classification scheme is the descriptive information for an arrangement or division of objects into
          groups based on characteristics that the objects have in common”20.
          “Classification schemes and code lists conveys semantics to the objects so they are a key factor to
          achieve semantic interoperability.
          Different industries provide specific classification schemes for their products or services. As it is quite
          complex to establish a common and unique classification scheme cross-border and cross-sector,
          business document instances should be carry metadata about classification schemes they use.”
          (Bausa O. and Boujraf A. 2009)
          Requirement
          Classification schemes for goods, services and code lists SHOULD be publicly available and identified
          in the document objects.

### 3.3 Legal framework

#### 3.3.1 Overview of legal framework

Public procurement requires strict compliance with the legal frameworks provided by the procurement
        directives. Supporting pan-European procurement and implementing services to enable pan-European
        deployment of evidences is the major goal of PEPPOL WP2. Any WP2 solution therefore needs to
        comply with the legal requirements concerning selection and exclusion criteria in public procurement
        defined by the European procurement directives and in national implementing legislation.
        Compliance with these regulations will ensure acceptance of a solution and will ensure and help to
        establish a "level of trust" between the parties involved. Therefore a comprehensive analysis of the
        relevant legal regulation has to take place. To get an overview on the legal requirements and
        regulations on different levels the following sources have to be analysed:

#### 3.3.2 Legal Requirements

The requirements listed in the subsequent section have been identified as essential for any WP2
        solution. They are independent of a particular stage. The requirements have to be fulfilled or further
        analysed and specified in order to further draft the legal framework for a VCD to a greater extent.

##### 3.3.2.1 Equal treatment of foreign economic operators

Description
          The principle of equal treatment is often mentioned by the directive 2004/18/EC for example in
          connection with contracts that should be awarded on the basis of objective criteria which ensure
          compliance with the principles of transparency, non-discrimination and equal treatment and which
          guarantee that tenders are assessed in conditions of effective competition. The VCD package should
          ensure equal treatment of foreign economic operators by providing a tool to submit evidence from one
          member state to another. Therefore Article 52(5) states that “economic operators from other Member
          States may not be obliged to undergo such registration or certification in order to participate in a public
          contract. The contracting authorities shall recognise equivalent certificates from bodies established in
          other Member States. They shall also accept other equivalent means of proof” [(EC 30.04.2004),p.
          134].
          Requirement
          The VCD SHOULD support that economic operators from foreign member states may not be treated
          harder than own member state’s economic operators.
          Measurement
          Tests and usability checks of historical tenders with contracting authorities and economic operators

##### 3.3.2.2 Minimum period of validity of VCD package

Description
          A VCD package contains information with different validities. It has to be defined whether a VCD
          package can have its own validity or if its validity is only based on the contained information.
          Requirement
          The possibility of a definition of a minimum validity of a VCD package has to be defined
          Measurement
          Data type in Structural VCD package data which specifies validity for the whole package
          3.3.2.3 Equivalence between automated transformation and official translation of attestations

##### 3.3.2.3 Equivalence between automated transformation and official translation of attestations

Description
          The use of context-specific formats that include multi-lingual versions of attestations should ensure
          that an automated transformation from one language version into another language version delivers
          results that have from the viewpoint of official translations, a similar legal status.
          Requirement
          The provision of attestations that are available in context-specific formats including multi-lingual
          versions and their transformation into any target language has to guarantee similar legal status and
          effect is reached compared to official translation.
          Measurement
          The evaluation of relevant legal regulations

##### 3.3.2.4 Legal effect of subset criteria and evidences specified by the contracting autho

Description
          A contracting authority sends a contract notice to a Publication body that publishes the call. The Call
          for Tender should contain the definition of specific criteria on qualitative selection and exclusion that
          are relevant to this particular procurement.
          If an economic operator decides to participate in a particular procurement procedure he can directly
          retrieve the relevant criteria by using the information published in the contract notice. In cases below
          threshold the economic operator might send a direct request to the procurer in order to retrieve the
          required information. The economic operator will be enabled to get a mapping to the relevant national
          attestations via the pre-VCD mapping tool. (cf. subsection 3.1.2.8: “Specification of criteria subset by
          the Procurer”; and subsection 3.1.2.9: “Provision of criteria subset by the Economic Operator”
          Requirement
          The contracting authority SHOULD specify a subset of evidences from the superset evidences that are
          relevant to a specific Call for Tender.
          Measurement
          Definition of the legal basis

##### 3.3.2.5 Scope of mutual recognition

Description
          Description
          Article 52(5) states “that contracting authorities shall recognise equivalent certificates from bodies
          established in other Member States. They shall also accept other equivalent means of proof” (EC
          30.04.2004). This specifically points to the relevant Community rules on mutual recognition of
          diplomas, certificates or other evidence of formal qualifications. The scope of mutual recognition needs
          to be clearly defined by legal experts. This requirement in particular targets the following topics

##### 3.3.2.5.1 Mutual recognition and candidate statements

Description
            Which roles do candidate statements take in general and specifically as replacement for attestations
            that cannot be provided? Which roles take candidate statements with regard to mutual recognition and
            which conditions have to be fulfilled to provide candidate statements instead of attestations within
            public procurement procedures? Is mutual recognition and the use of candidate statements bound to
            those cases where equivalent documents are missing or can mutual recognition of candidate
            statements cover other conditions or conventions as well (e.g. increased usage of candidate
            statements in pan-European public procurement procedures)?
            Requirement
            The scope of mutual recognition needs to be further clarified with regard to the role of candidate
            statements.
            Measurement
            Qualitative legal specification on the scope of mutual recognition

##### 3.3.2.5.2 Equivalence of missing attestations

Description
            Not every Member State provides all attestations that are necessary for an economic operator to prove
            conformance with given criteria specified by another Member State. Thus only the economic operators
            from Member States where such attestations are available can provide these attestations. Other
            economic operators have to provide similar evidence instead (e.g. a candidate statement). The
            working group has to provide a concept of how each possible attestation has to be fulfilled (mapping of
            evidences defined in the directive with national implementation). Thereby the evidences provided by
            economic operator should be considered of equal value as evidences provided by a traditional issuing
            body if equivalence is missing
            Requirement
            It has to be defined which method and concept should be applied if there are missing attestations.
            Measurement
            Qualitative legal specification on the scope of mutual recognition

##### 3.3.2.6 Correct implementation of directives into national procurement law

Description
          Articles 45 to 50 of directive 2004/18/EC are the basis of our mapping strategy and for the
          development of the pre-VCD mapping tool. In order to achieve good mapping results it has to be
          checked whether these articles are sufficiently implemented into national procurement law. This in
          particular covers the semantic requirement: correspondence between national and European criteria
          of qualitative selection and exclusion (cf. ANNEX III: Questionnaire concerning the legal analysis)
          Requirement
          It has to be guaranteed whether the directive is correctly implemented in national procurement law
          with regard to VCD relevant articles 45-52.
          Measurement
          National procurement existing

##### 3.3.2.7 Legal basis for exchanging validation data

Description
          In case a MS decides to exchange validation values (e.g. certified “Yes/No” statements) instead of
          delivering an attestation physically (stage 4 specific) it MUST ensure that this provision is legally
          allowed. Directive 2004/17/EC and Article 52 of Directive 2004/18/EC may provide a legal basis for
          such decision. The legal foundation in the country will provide a basis to accept these statements
          across borders according to the principle of mutual recognition of diplomas, certificates or other
          evidence of formal qualifications. The requirement is strongly related to the organisational
          requirement: “Scope with regard to Article 52”.
          Requirement
          The legal foundation for exchanging validation values SHOULD be given in the home Member States
          in order to support mutual recognition across Member States.
          Measurement
          Related regulations within national procurement law.

##### 3.3.2.8 Legal requirements regarding service providers

##### 3.3.2.8.1 European Service Provider

This section contains requirements concerning a European Service Provider who may host services
            necessary to ensure sustainable interoperability between VCD solutions in long terms. In particular a
            European Service Provider refers to the pre-VCD mapping tool which will provide a basis for all other
            VCD application in the subsequent stages. Especially responsibilities and services like hosting,
            maintaining and governing pan-European processes will be important. Several formal legal
            requirements have to be answered previously in order to define the scope of such European Service
            Provider
            Requirement
            The legal status and legitimacy of the European Service Provider MUST be defined.
            Measurement
            Formal establishment of the European Service Provider
            Requirements
            The responsibility of the European Service Provider MUST be defined (e.g. definitions, rule-set).
            The liability of the European Service Provider MUST be defined.
            Measurement
            Definition of the legal basis for the establishment of such a Service Provider
            Requirements
            The legal regulation applicable for the European Service Provider MUST be defined.
            Measurement
            Definition of the legal basis for the establishment of such Service Provider
            Requirements
            A suitable way to establish the relevant regulation for the European Service Provider MUST be
            defined.
            Measurement
            Necessity for amendments of existing regulations has to be proofed

##### 3.3.2.8.1 National Service Providers

Description
            This section contains requirements concerning a National Service Provider who may host services
            necessary to ensure sustainable interoperability of a national VCD solution in long term. In particular a
            National Service Provider refers to any VCD system and VCD package that is developed within a
            Member State. Especially responsibilities and services like hosting, maintaining and governing the
            national processes with regard to a VCD solution will be important. Several formal legal requirements
            have to be answered previously in order to define the scope of such a National Service Provider
            Requirement
            The legal status and legitimacy of the National Service Provider MUST be defined.
            Measurement
            Formal establishment of the National Service Provider
            Requirements
            The responsibility and the related processes of the National Service Provider MUST be defined (e.g.
            mapping activity, compilation of VCD package).
            The liability of the National Service Provider (depending on its legal status) MUST be defined.
            Measurement
            Definition of the legal basis for the establishment of such Service Provider
            Requirements
            The legal regulation applicable for the National Service Provider MUST be defined.
            Measurement
            Definition of the legal basis for the establishment of such a Service Provider
            Requirement
            A suitable way to establish the relevant regulations for the National Service Provider MUST be defined
            (e.g. special legal regulations concerning VCD service provision).
            Measurement
            Necessity for amendments of existing regulations has to be proofed.
            Requirement
            Regulations concerning monetary aspects of the VCD service provision MUST be defined, therefore
            related legal regulations (e.g. competition protection act) MUST be considered.
            Measurement
            Definition of the legal basis for the establishment of such Service Provider.

##### 3.3.2.9 Legal requirements regarding the collection of evidences

Description
          In many countries there are certain regulations with regard to evidences that have to be considered.
          For example in some countries it is not allowed to directly issue an extract from the register of
          conviction to the economic operator but to directly deliver these evidence to the requesting authority.
          Requirement
          Special legal regulations for evidences MUST be considered (e.g. for extract from the register of
          conviction).
          Measurement
          Results of analysis of legal basis.
          Requirement
          Regulations for handling the non-existence of selected evidence requested in a MS MUST be defined
          and made operational.
          Measurement
          Results of analysis of legal basis.

##### 3.3.2.10 Legal requirements regarding data protection

Description
          Data protection defines a legal basis for the handling of information relating to people or entities. Data
          protection is the main piece of legislation that governs the protection of personal or entity related data
          in a way in which individuals or entities can enforce the control of information about themselves.
          Although data protection does not directly refer to principles like data privacy, data confidentiality, data
          availability, non-repudiation of data, data integrity and data security these principles are strongly
          connected to data protection. Thus data protection plays an important role for a VCD.
          Requirement
          Relevant regulations of national data protection acts MUST be analysed and considered.
          Additional requirements for cross-border data exchange MUST be analysed and considered.
          Measurement
          Results of analysis of legal basis.

##### 3.3.2.11 Separation of VCD package and tender

Description
          The VCD package is just one part of a bid that an economic operator may submit to a contracting
          authority. Therefore the rules and regulations in each Member State have to be analysed with regard
          to the prospects of separating these two parts from each other. This may also include for example to
          submit a VCD package via the PEPPOL infrastructure while submitting other parts or the bid itself via
          secondary channels or whether tendering platforms enable such separation.
          Requirement
          It MUST be clarified which prospects and limitations exists within a Member State to separate a VCD
          package from the tender itself.
          Measurement
          Results of analysis of legal basis.

##### 3.3.2.12 Trust model between the entities involved

Description
          There are several actors that are involved in the processes related to WP2 and these processes have
          to be defined with regard to trust between the entities involved (e.g. European service provider,
          national service providers, issuing bodies, economic operators, contracting authorities).
          Trust models have to be defined for each process in order to clarify roles and responsibilities during
          transactions. This may include on a national level the definition of trust with regard to roles and
          responsibilities between national service providers and issuing bodies (public/private). On the
          European level it may include the “scope of mutual recognition” for example the trust between the
          national service provider who provides a VCD simple package and the European service provider who
          provides a particular mapping facility.
          Requirement
          A trust model and trust system MUST be defined from a legal point of view for every process which
          includes the roles and responsibilities of the entities involved.
          Measurement
          Ensuring trust through suitable legal regulations about roles, responsibilities and processes.

##### 3.3.2.13 Legal Validity

Description
          “Some documents exchanged during the electronic procurement process have to be legally valid
          following EU Directives.
          Directive 2004/18 states that the public procurement procedures and the rules applicable to service
          contests require a level of security and confidentiality higher than that required by Directives.
          Accordingly, the devices for the electronic receipt of offers, requests to participate and plans and
          projects should comply with specific additional requirements. To this end, use of electronic signatures,
          in particular advanced electronic signatures, should, as far as possible, be encouraged. Moreover, the
          existence of voluntary accreditation schemes could constitute a favourable framework for enhancing
          the level of certification service provision for these devices.” (Bausa O. and Boujraf A. 2009)
          Requirement
          Electronic signature, with the same legal meaning of handwritten signature, SHOULD be encouraged
          in cross-border scenario.
          Requirement
          The regulations concerning the use of electronic documents, the exchange or download of electronic
          documents (e.g. mandatory usage of an e-signature) MUST be considered (especially regulations
          from national procurement act and directive 2004/18/EC).
          Measurement
          Results of analysis of legal basis for exchanging evidences and data.
          Requirement
          A process for document handling compliant with the relevant legal regulations MUST be defined
          (especially with respect to the data protection acts).
          Measurement
          Agreed process definition for document handling compliant with the relevant legal regulations.

### 3.4 Technical Framework (Infrastructure specific)

#### 3.4.1 Overview of technical framework

This chapter shall include technical requirements that are essential for submitting a VCD via the
        PEPPOL infrastructures. In particular this refers to the proposed infrastructure of WP8 and the
        interrelation with our work package. The PEPPOL infrastructure of WP8 is dedicated in particular to
        the exchange of electronic business documents in a secure and reliable manner. Thereby it connects
        to existing e-business frameworks and value added networks and is being built on existing
        technologies and standards that have been tested and which have proven to be reliable and secure
        for enterprise use. WP2 takes a specific role within the project by concentrating on pre-awarding
        issues where requirements and procedures are often stricter due to principle like equal treatment, nondiscrimination,
        transparency, competition etc. Although a VCD does not include the offer itself it
        provides several documents that are of great importance for the award of contracts and therewith
        critical for the success of an economic operator for example in cases of disqualification because of late
        delivery of a VCD.
        An overall pre-condition for using the infrastructure and WP2 solutions in long term is that they are
        governed even after the project lifetime by maintaining and sustaining its functions. Therefore the
        governing models of WP8 and WP2 should be aligned.
        Authentication is an essential feature of WP2 as a Virtual Company Dossier contains several
        documents that contain sensitive data about an economic operator. Hence, it has to be ensured that
        only those persons that have sufficient rights are able to access and retrieve these data.
        Authentication of origin is also an important feature with regard to non-repudiation, for example when
        submitting a VCD to a contracting authority.
        Authentication is a verification of evidence of identity; for individuals and companies identifiers are
        used to process authentication. Such identifiers are national and in many countries specific and
        maintained within sectors, like tax, health, health insurance, employment, registration authorities, etc.
        PEPPOL will need to design an authentication system that serves its purposes. Hence, collaboration
        with WP 1 will be strengthened in the second phase of WP 2.
        Time-stamping shall ensure that the submission of a VCD is adequately documented for example to
        verify that it has been sent or received previously to the closure of a call for tender. In order to obtain
        trust, the VCD services should use certified time stamps.
        Moreover there are several actors involved in the WP2 scenarios which need to be connected to the
        PEPPOL infrastructure thus a sufficient allocation of identifiers, in connection with the identity an actor
        claims to have, has to be ensured. This shall ensure that unauthorized usage of an individuals’ identity
        is avoided. Overall we see a need for commonly monitored identity and access management in
        particular for all national VCD solutions and for the PEPPOL infrastructure thus both approaches
        should be aligned and should make use of the same mechanisms through for example single-sign-on
        functionality.
        Apart from functionalities like addressability and discovery, the infrastructure should provide access
        points to support the actors or services to connect to the infrastructure. The PEPPOL infrastructure will
        make it possible to exchange electronic business documents in a secure and reliable manner. Thus
        also the VCD should be able to be submitted through the PEPPOL infrastructure. We also assume
        that a VCD in stages 2 and 3 can be potentially submitted through other means but this is up to the
        choice of an economic operator and should not be promoted because bypassing the infrastructure is
        critical from the viewpoint of using validation services to ensure confidentiality of a VCD and its
        contained documents (WP1) and secure and reliable transport ensured through the PEPPOL
        infrastructure (WP8). During transportation the integrity of a VCD has to be ensured when for example
        validating it.
        Usage of the Infrastructure will require that national access points to the infrastructure (e.g. national
        service providers, contracting authorities) will be implemented but also direct access points that
        support SMEs in connecting to it. We also see a potential need to access web services via the
        infrastructure that enable client-side code generation in SOAP frameworks for example for the retrieval
        of attestations on demand, connecting to tendering platforms or viewing the VCD on some platform at
        the national service provider.

#### 3.4.2 Technical Requirements

The requirements listed in the subsequent section have been identified and are essential for any WP2
        solution. They are independent of a particular stage or show interrelations between them thus they are
        called high-level technical requirements. The requirements have to be fulfilled or further analysed and
        specified with in conjunction with WP1 and WP8 in order to further draft the technical framework with
        regard to the VCD.

##### 3.4.2.1 Interrelation of governance models of WP2 and WP8

A governing model has to be defined in order to deploy the WP2 systems and tools and to maintain
          their states and sustainability over time. In this respect the composition, structure and scope of the
          governing model has to be formally defined to ensure fulfilment of functions like liability, sustainability
          and maintainability (e.g. especially to maintain and sustain a pre-VCD mapping tool in long term and
          therewith to ensure (re-)liable functions) The dedicated governing model should have the necessary
          status and power to govern its assigned functions.
          Requirement
          It MUST be clarified how the governance model of WP2 fits into the overall governance model of WP8.
          Measurement
          Governing model of WP2.

##### 3.4.2.2 Authentication of PEPPOL Actors

Description
          The identity and access management of systems for company evidential documents is regulated by
          local procedures and could become part of the WP2 proposed systems (cf. stage 2 description).
          Economic operators have to apply for a VCD account in order to become authenticated. An officer has
          to verify whether the data that is necessary to apply for an account belongs to the economic operator
          and has to assure its correctness. An economic operator can authenticate to the VCD system only
          when the economic operator has sufficient user rights provided by identity and access management.
          Thereby WP2 has to take into account which natural person has the power to act as authorized
          representative of the economic operator.
          Requirement
          WP2 stakeholders MUST be authenticated to the VCD system and for the PEPPOL infrastructure.
          Measurement
          Formal authentication mechanism.
          Requirement
          The identity and access management procedures for creating a VCD account SHOULD be
          harmonized with the registration procedure of the overall infrastructure provided by WP 8.
          Measurement
          Single-Sign-On functionality.
          Requirement
          A single-sign-on SHOULD be implemented in order to allow identity and access management across
          different systems.
          Measurement
          Single-Sign-On functionality.

##### 3.4.2.3 Allocation of identifiers

Description
          Work package 2 will use the PEPPOL infrastructure for discovering addressing information which is
          typically stored in a registry. Therefore we need to find a method how addresses can be allocated and
          being provided to the WP 2 stakeholders so that they can use the PEPPOL infrastructure for
          exchanging VCDs and access related services.
          Requirement
          A method MUST be found how to allocate identifiers to the participants that use the infrastructure for
          transportation of VCDs and related services.
          Measurement
          Joined strategy and method with WP8 how to allocate identifiers among stakeholders and WP2 related
          services.

##### 3.4.2.4 Identity

Description
          “Member States are building electronic identity management systems as a key element in their
          national strategy to deploy electronic services. Those national based systems are evolving without
          taking into account the requirement for interoperability that is needed in a cross-border scenario,
          resulting in a fragmented service that prevents the deployment of pan-European electronic services.
          In the public procurement business process, as in other electronic business processes, electronic
          identity is a key element for two main purposes:
          Avoiding unauthorized use of individuals identity
          Assuring to administrations that individuals are the persons they claim to be and have the mandate
          they claim to have” (Bausa O. and Boujraf A. 2009)
          Requirement
          Every party participating MUST be uniquely identifiable

##### 3.4.2.5 Addressability

Description
          “As per the wide deployment of the Internet and the web, most electronic Government services have
          been focused on the provision of services through websites. However, using websites is not a good
          approach when dealing with services that affect business processes in both ends of a collaboration.
          Those business processes, such as the public procurement processes, can be run between
          applications, so no human intervention should be enforced to those organizations with automated
          procurement systems.
          In such cases, every partner in the collaboration needs to be addressable so electronic documents
          can be exchanged from end to end through the underlying transport infrastructure.” (Bausa O. and
          Boujraf A. 2009)
          Requirement
          Every party participating SHOULD have a secure and verifiable electronic address.

##### 3.4.2.6 Discovery

Description
        “To exchange electronic documents between parties in a cross-border environment, a major challenge
        is to find out the other party’s address and to understand what are his systems’ capabilities and
        requirements.
        Different levels of maturity and implementation of electronic business interfaces on public
        administrations and economic operators across Europe obliges to create mechanisms for discovering
        the supported standards, documents and endpoints for trader partners.” (Bausa O. and Boujraf A.
        2009)
        Requirement
        In stage 4 it MUST be possible to discover the verified electronic address for an identified party.

##### 3.4.2.7 Access Points to the PEPPOL infrastructure

The PEPPOL infrastructure will make it possible to exchange electronic business documents in a
          secure and reliable manner. It connects existing frameworks and networks, but also allows small
          businesses to participate in the electronic business processes if they have Internet access and can be
          securely identified. The PEPPOL infrastructure is being built on existing technologies and standards
          that have been tested and which have proven to be reliable and secure to use. For WP2 it will
          important to access the infrastructure from different perspectives. An economic operator for example
          has to submit a VCD via the PEPPOL infrastructure. A contracting authority may require access to a
          database hosted by a national service provider to receive an attestation by using a direct reference to
          it. Some web services may be connected to the infrastructure to add additional functionalities to a VCD
          or for example to receive mapping information from the pre-VCD mapping tool. Therefore different
          access points to the PEPPOL infrastructure may be necessary in particular:

##### 3.4.2.8 Use of PEPPOL infrastructure to submit a VCD (next to a bid)

Description
          The VCD is just one part of bid that an economic operator may submit to a contracting authority.
          Therefore the systems in each Member State have to be analysed with regard to the prospects of
          separating both parts from each other. This may include for example to submit a VCD via the PEPPOL
          infrastructure while submitting other parts or the bid itself via secondary channels or whether tendering
          platforms enable such separation.
          Requirement
          It MUST be clarified whether tendering platforms enable a separated submission of a VCD and the bid
          itself.
          Measurement
          Result of national system analysis.
          Requirement
          The PEPPOL infrastructure MUST have the capability to submit a VCD to a contracting authority or
          tendering platform.
          Measurement
          Functionality for submitting VCD to a contracting authority or tendering platform.
          Requirement
          The PEPPOL infrastructure SHOULD have the capability to submit a bid which contains a VCD.
          Measurement
          Discussion with WP8 about the prospects to have a functionality for submitting a bid to a contracting
          authority or tendering platform that includes a VCD.

##### 3.4.2.9 Confidentiality

Description
          “Ensuring that information is accessible only to those authorized to have access and in a predefined
          date is mandatory by the European Directive in some public procurement processes. Specifically,
          contracting authorities must provide a way to receive electronic tenders and ensure those electronic
          tenders are not accessed until the prescribed time for opening them. Annex X of the Directive
          2004/18/EC lists the requirements relating to devices for the electronic receipt of tenders, requests for
          participation and plans and projects in contests.” (Bausa O. and Boujraf A. 2009)
          Requirement
          It MUST be possible to guarantee confidentiality for specific documents.

##### 3.4.2.10 Usage of validation service provided by WP1

Description
          WP1 assumes that all actors can sign inside their corporate infrastructure. The e-tendering platform
          must offer download functionality for forms and other material to be filled in, signed, and returned by
          an economic operator. A validation service may be a technical service or a Validation Authority (VA)
          that takes on liability and acts as a trust anchor of its own. Validation services may be chained in
          order to serve requests that cannot be handled by the “local” validation service. The VCD essentially
          relies on such validation service in order to guarantee data integrity and confidentially of a VCD (cf.
          PEPPOL WP1-D1.1).
          Requirement
          It MUST be possible to apply the validation service provided by WP1 to a VCD in order to enable
          economic operators to guarantee data integrity and confidentiality of a VCD.
          Measurement
          Testing of validation service with VCD within the PEPPOL infrastructure.
          Requirement
          It MUST be clarified whether the VCD can use the validation service of WP1 if the transportation
          infrastructure is not used by an economic operator.
          Measurement
          Discussion with WP1.

##### 3.4.2.11 Reliability

Description
          “The purpose of an e-business transport infrastructure is to transport business documents between
          business partners. The transactions must be performed with high level of security and reliability. E.g. it
          must be ensured that business documents are actually delivered to the recipient party.” (Bausa O. and
          Boujraf A. 2009)
          Requirement
          Transport mechanisms between party’s addresses MUST be reliable.

##### 3.4.2.12 Security

Description
          “The e-business transport infrastructure is to transport business documents between business
          partners. The transactions must be performed with high level of security. E.g. it must be ensured that
          third parties cannot intercept and read or modify the business documents.” (Bausa O. and Boujraf A.
          2009).
          Requirement
          Transport mechanisms between party’s addresses MUST be secure.

##### 3.4.2.13 Data Integrity

Description
          “Data integrity ensures data has not been altered or modified during any operation such as transport
          or storage. Integrity can be compromised both by malicious intervention from a third party or by errors
          in the transport or storage mechanisms. Despite legal issues about the integrity of certain documents
          such as the electronic invoices, it should be a general rule to assure the integrity of all documents
          exchanged between partners.” (Bausa O. and Boujraf A. 2009).
          Requirement
          It MUST be assured that business document instances are consistent and correct during
          transportation, validation or transformation operations.

##### 3.4.2.14 Non-repudiation of origin

Description
          “In electronic procurement, some processes require to ensure that the sender of an electronic
          document cannot repudiate its validity“ (Bausa O. and Boujraf A. 2009).
          Requirement
          Authentication of origin for business document instances MUST be supported.

##### 3.4.2.15 Time stamping

Description
          “In electronic procurement, some processes require to ensure that the documentation (attestations,
          tenders, etc.) is delivered before a time limit set.” (Bausa O. and Boujraf A. 2009).
          Requirement
          Time stamping SHOULD be applied in some processes to certify relevant date and time.

##### 3.4.2.16 Time stamping

Description
          “In electronic procurement it is fundamental to create a trust “environment” for the economic operator.
          A trust “environment” is needed in several phases of the eProcurement process (e.g. awarding a
          contract notice). It could be also a good deterrent against insider.” (Bausa O. and Boujraf A. 2009).
          Requirement
          The electronic procurement process MUST have an audit trailing to ensure transparency for both
          parties.

## 4 High-level concepts for pilot implementations

### 4.1 Pre-VCD mapping tool

#### 4.1.1 Preliminary study on the electronic provision of certificates and attestations usually required in public procurement procedures

The first interim report – national country profiles – of the preliminary study of DG Markt comprises a
        list of qualification documents typically used in tendering procedures in the Member States. The report
        documents various attestations of the Member States which are arranged according to the Articles 45
        to 50 of Directive 2004/18/EC (Siemens_and_Time.lex 2007):

#### 4.1.2 Certificates issued on the eligibility of tenderers and official lists of economic operators

Furthermore the Commission Service designed a questionnaire “Eligibility of tenderers”21 in order to
        facilitate access to information related to some of the above mentioned evidences. The questionnaire
        contains a set of European criteria and requirements derived from directive 2004/18/EC and
        connected to specific evidences in order to make them comparable among Member States. Besides
        that, results from the ”Study on the proposal for a tool for a mutual information mechanism on the
        electronic provision of certificates and attestations usually required in public procurement procedures”
        and the country profile templates developed by Siemens Time.lex commissioned by DG MARKT have
        been Stage 1, the pre-VCD mapping tool, will be built upon this information by providing automated
        mappings and comparisons between the defined documents via the mentioned exclusion criteria (cf.
        Table 10).
        Combining structural information about evidence and the criteria mentioned in the “Eligibility of
        Tenderes” they are referring to, it will be firstly possible to set up a database with common definitions
        that referring to evidences and secondly to define precise mapping between those evidences via the
        templates. Every partner of this work package should therefore fill the pre-VCD mapping tool with
        national instances and define the mapping to European criteria. This will also enable VCDs of the
        piloting country to work on a wider scope. Even if a country hasn’t defined a pilot implementation for a
        VCD it can receive and interpret a VCD according to the information provided by the pre-VCD
        mapping tool.
        The next section provides an overview of relevant technologies that may enable such a mapping of
        evidence.


#### 4.1.3 Relevant technologies and standards for pre-VCD mapping tool

This section provides an overview about relevant technologies that can be applied for a pre-VCD
          mapping tool. The pre-VCD mapping tool is depending upon formal semantics that describe how
          evidences related to each other. Therefore WP 2 proposes to derive criteria from the European
          directive 2004/18/EC as shown for instance within the “Eligibility of Tenderers”. Using formal
          semantics with the proposed technologies as presented in section 4.1.3 below enables several
          advantages (Fensel, Lausen et al. 2007):

Implementing the VCD concept as introduced in this report has cross-border as well as national and/or
      regional dimensions. Figure 21 depicts the overall concept of the VCD system implementations. As
      shown in the figure and introduced before, the key technical elements of the VCD implementation are:


### 4.3 Austrian implementation and piloting proposal

#### 4.3.1 Implementation approach

Austria will implement and pilot a VCD service based on the VCD concept introduced in this report.
        The intention is to create a system, which can handle all functions of a stage 3 VCD advanced
        package solution, and thereby achieve:



#### 4.3.1 Piloting approach

The piloting phase of the Austrian VCD implementation will include several selected stakeholders,
        which take up key positions in the Austrian procurement landscape. The following stakeholder groups
        will be represented in the Austrian pilot:

### 4.4 Italian implementation and piloting proposal

#### 4.4.1 Implementation approach

Italy plans to adapt its current company’s dossier builder to the design and implementation principles
        set by PEPPOL WP2. This requires a set of actions in order to conform to the adopted standards and
        interoperability agreements of PEPPOL WP2. The interoperability dimension represents the challenge
        at the moment as very few transactions take place across borders and when they are performed they
        represent a heavy burden for those attending their execution.
        Italy is pressing on this by adopting different measures, i.e., by improving the organizational
        infrastructure, by offering better visibility of the involved organizations, by designing and developing
        policies that increase the trust among national and European organizations, by improving the
        information processing environment in order to reach the requirements set by the PEPPOL
        community.
        The conformance to PEPPOL’s WP2 interoperability standards will be approached by following the
        project agreed roadmap that includes the design and management of a dynamic knowledge base,
        known as the pre-VCD mapping tool and by implementing VCD services that conform to a multi-stage
        approach. For PEPPOL’s project runtime, Italy is planning to reach Stage 2 as ultimate stage in its
        system and services evolution along with solid contributions for the analysis and design of the upper
        level stages.
        The Italian implementation approach includes a long preparation activity that focuses more on legal
        investigation rather than technical engineering. Currently, the major challenge on interoperability
        across Europe comes from the persistent non homogeneous legal background and the reluctant
        attitude towards digital objects, mostly on electronic documents, digital identities and public registries.
        We see the two aspects, i.e. the legal and technical closely related, and aim at treating them with
        equal priority.
        Effort will be spent on refining and consolidating the document’s acquisition infrastructure that
        represents a multi-site networking system to reach the different certification authorities that are the
        authoritative suppliers of documents essential to the VCD package construction. A specific set of tasks
        will also address the transformation of evidences from the conventional form into an electronic form for
        computer assisted handling and management.
        As part of the interoperability dimension, there will be a supporting action for digging into existing
        certificates and dragging out of them the most valuable information.

#### 4.4.2 Piloting approach

The piloting phase of the Italian VCD service will include the technical actions identified by the
        implementation plan and some interfacing events to reach selected stakeholders and define through
        their input the driving conditions for the VCD setup. This interfacing activity will precede the final
        design and the real pilot implementation. The VCD service provider for the piloting phase will be the
        Italian Business Registers System.

## 5 Synthesis: Major interoperability requirements, SWOT and next steps

### 5.1 Major requirements for VCD interoperability

This section provides an overview about the deliverable and in particular about major requirements for
    VCD interoperability.
    The requirements and contents contained in chapters 2, 3 and 4 can be aggregated according to the
    following aspects:
    Level of support: The different levels of support address the maturity of the service and the maturity
    of the VCD package, where the former correspond to the functionalities (e.g. compilation support vs.
    recompilation support) provided and the latter corresponds to the semantic richness of the provided
    information (e.g. information support vs. decision support).
    Level of completeness: A VCD Package will show its full potential when all the requested
    attestations (all that are necessary to prove all requested criteria) are contained in it. The VCD
    promotes a step wise approach in order to reach a sufficient level of completeness by concentrating
    first on evidences with regard to Articles 45 – 46 and afterwards on evidences with regard to Articles
    47 – 50.
    Paradigm shift: The paradigm shift refers to the handling of documents to handling of information and
    electronic exchange of information in order to establish interoperability on the basis of mutual
    recognition. The VCD should encompass this change.
    Criteria for qualification and selection and non-exclusion: The criteria for qualitative selection and
    non-exclusion as defined in Article 45 to 50 of Directive 2004/18/EC are the common ground for
    building a cross border VCD service. Evidences will be connected to these criteria by further defining
    and grouping them into sub criteria and atomic criteria.
    Pre-VCD mapping tool: Provides a widely available tool which contains the up-to-date mappings of
    European criteria and evidences. The tool is build upon a basic semantic interoperability model
    consisting of relationships between evidences available in the Member States and European criteria of
    qualitative selection and exclusion (Superset). Tender specific requirements then have to be stated by
    contracting authorities according to the European criteria during notification phase in order to derive
    tender specific mapping results on evidences required to submit at tendering (Subset).
    VCD simple package: Establishment of a VCD system which consist of VCD services, hosted by a
    VCD service provider. VCD services are capable to collect evidences from different sources and
    compiling VCD packages from it. VCD simple package defines the structure of a package with regard
    to types of data.
    Types of data contained in a VCD: Provide the basis for a common structure of a VCD. Includes
    several data types (cf. ANNEX I – Glossary) to build the VCD from different sources and formats (e.g.
    tender specific data that refer to a particular Call for Tender, the evidences itself as electronic file or
    scanned copy and structural data of evidence that describe the evidences according to generic
    aspects).
    VCD advanced package: Introduces several additional VCD services that increase the level of
    support for the entities involved. Economic operators are for example enabled to maintain their data
    through re-compilation of a VCD or to merge their VCD with VCDs’ from other economic operators in
    order to create groups of economic operators for bidding consortia. VCD advanced package also
    introduces context specific data as additional type of data that describe the content of an attestation in
    a machine interpretable format.
    VCD networked package: Introduces “on-demand” retrieval of attestations that are sufficiently
    described through context specific data. The VCD networked package offers a good opportunity for a
    national service provider to establish official list of approved economic operators as foreseen in Article
    52 (1) of Directive 2004/18/EC. Therefore national service providers have to store attestations and
    referencing to it within the VCD. Contracting authorities are mandated to request attestations in
    individual cases (“on demand”) if they do not trust on the list of approved economic operators. The
    VCD networked package needs conflict resolution in cases of failure or system errors during “on
    demand” requests.
    Organisational Framework: Lists the requirements forming the organisational basis for implementing
    any of the VCD stages. They are independent of a particular implementation or stage thus they are
    called organisational requirements for a VCD.
    Legal Framework: Lists the requirements forming legal basis for any VCD stage. They are
    independent of a particular VCD implementation or stage thus they are called legal requirements for a
    VCD.
    Semantic Framework: Lists the requirements which form the semantic basis for any of the VCD
    stages. They are independent of a particular implementation or stage thus they are called semantic
    requirements for a VCD.
    Technical Framework: Referring to the PEPPOL infrastructure. The technical framework lists several
    requirements that are essential to specify the technical (transportation and validation) basis in order to
    submit any WP2 solution across borders. They are independent of a particular implementation or
    stage thus they are called technical requirements for a VCD.
    In a next step these results will be transformed into a SWOT Analysis identifying the Strengths and
    Weaknesses of the proposed concept and its market opportunities.

### 5.2 VCD concept and its Strengths, Weaknesses, Opportunities and Threats

SWOT Analysis is a strategic planning method used to evaluate the Strengths, Weaknesses,
      Opportunities, and Threats of a project or intention. A SWOT analysis usually starts by defining an end
      state or objective which has been done for WP2 in chapter 2 and subsequent chapters. The aim of
      any SWOT analysis is to identify the key internal and external factors that influence the achievements
      of this objective. SWOT analysis thereby groups key pieces of information into categories:

#### 5.2.1 Strength of the VCD concepts

The major objective of this deliverable is to develop a concept for a VCD and to define major
        requirements that shape this VCD concept. Therefore we have defined different scenarios and a vision
        that contains several different levels of maturity. With the staged maturity model we intend to reach a
        wide flexibility and openness of such a solution encompassing all Member States to implement their
        individual preferences. Nevertheless the concept provides common grounds such as the pre-VCD
        mapping and structural data of evidences which ensures interoperability of evidences and their
        perception across borders. Beside we defined a set of requirements on organisational, semantic,
        technical and legal level that clarify general aspect of VCD development and deployment.
        To support the mutual recognition of evidences across border the VCD requires an underlying
        semantic model that enables a standardized classification and mapping between them (pre-VCD
        mapping tool). If the contracting authority specifies the relevant evidences which are related to criteria,
        the data can be processed automatically in order to look-up the evidences required within another
        Member State. The standard structure of the VCD, with the semantic enrichment of its structure then
        provides a European-wide understanding and format of company formal evidence.
        The different levels of maturity can be applied in dependence on the willingness and readiness of
        every Member State. The aim is to support basic interoperability and exchange of documents on the
        lower maturity levels and leading towards direct electronic exchange of evidence in the higher maturity
        levels. Thereby each maturity level is built upon the lower ones thus allowing integration and stepwise
        advancement.
        The VCD shall ensure that a significant part of the public procurement processes can be made
        through electronic cross-border transactions. Therefore the national focus of a VCD needs to be
        enhanced through a cross border perspective. The VCD will provide the possibility to utilize evidences
        used in one Member State and to submit them across borders to any European contracting authority.
        A VCD provides a single point of contact for an economic operator that enables him to invoke and
        manage different services to create a VCD. A service (re-)compiles the VCD package for the
        economic operator or even a group of economic operators. The VCD services merge data from
        several sources into a single container and make this data available and understandable to the actors
        involved. Economic operators will be enabled to perform checks with regard to the existence and
        validity of the requested evidences in the VCD package. Structural data of evidence will provide
        guidance for foreign contracting authorities to understand the evidences contained within a VCD and
        they can trust that general information since it is provided by national VCD service providers that take
        the role of trusted parties. Context specific data will be provided on the higher levels to increase
        decision support.

#### 5.2.2 Weaknesses of a VCD

There are also some weaknesses that can be identified for the overall concept. These weaknesses
        are mostly derived from the complexity of the domain and how the VCD solution reacts on this domain.
        One of the biggest weaknesses is probably the development of context specific data for the evidences
        within a VCD. The development of context specific data shall ensure the automatic processing of
        electronic attestations without regard to linguistic barriers. The development of standards and context
        specific vocabularies is time consuming and requires long term involvement of user groups that will
        make use of these standards. The VCD contains several different kinds of evidences and to develop
        common standards for each one cannot be a major task and focus of this work package and should be
        done by initiative such as CEN BII, BRITE, XBRL or ECRIS. Since CEN BII workshop is close to an
        end it will probably not work out to do this development within its scope. Nevertheless we will start to
        develop comm of contents and marginal variances in their contents. Furthermore we rely on structural
        data of evidences that describe and characterize evidence from a more generic point of view.
        The possibility to replace the full document translation with a “selective translation” through context
        specific data (keywords and major contents) bares certain risks. The “selective translation” could be
        arranged in multiple languages in particular when context specific data belongs to a common agreed
        dictionary of expressions. Nevertheless the acceptance of those selective translations instead of
        certified translations may be questionable for contracting authorities. Thus the resolution of language
        barriers and linguistic issues cannot be completely managed by a VCD in short term and may require
        adding official translations beside selective translations.
        Provision of context specific data is a precondition to establish direct information exchange between
        attestation providers and contracting authorities. This direct information exchange would provide many
        opportunities with regard to increase the actuality of evidence, to lower the transaction costs of the
        parties involved and to reduce the time to create a VCD. Nevertheless such direct exchange is very
        difficult to establish because a lot of entities and attestation services have to be federated, access
        policies have to be developed, legal uncertainties have to be resolved and political guidelines have to
        be considered. To circumvent these problems the VCD provides in particular in stage 4 a guideline on
        how to move forward in order to reach this ambitious aim but it will not be a major focus of a VCD as
        such.
        The VCD will be dependent on a number of services that rely on manual and semi-automated input.
        Thus the VCD system will be primary a tool for the economic operator to arrange a VCD package
        instance which is conform according to the requirements stated in particular call for tender which he
        can fill through additional inputs. A direct access to attestation via the national VCD service provider
        can only be provided for those public attestations that are already available in electronic format. The
        VCD will not enforce any development of electronic attestation on a national level as this is a clear
        national duty and is depended upon the development of context specific data. Nevertheless existing
        attestations may be extended through additional annotations that describe these documents
        generically (structural data of evidences).
        Unclear yet is the role of Member States that have already implemented Article 5224. The scope of
        mutual recognition needs to be further clarified with regard to acceptance of these procedures across
        borders and the liability of those trusted third parties across borders. It needs to be further defined how
        a VCD can support countries that have implemented Article 52 but since there are currently no pilots in
        our work package that have such procedures already implemented we have left this out of scope.
        Neverton representations (context specific data) for evidences that have an, easy structure,
        low quantityheless we see a great opportunity to combine both ideas as shown in stage 4.

#### 5.2.3 Opportunities for a VCD in public procurement

A major point of discussion in the domain is a sustainable and reliable long-term vision for exchanging
        attestations among Member States. In the long-run the VCD should be able to adequately fulfil the
        contracting authorities’ need to proof conformance to certain criteria for qualitative selection and
        exclusion while reducing the burden of proof for the Economic Operator. The costs of transaction of
        economic operators can be reduced through a single point of contact and through automatic
        arrangement of a VCD package instance according to the given criteria. Therewith manual comparison
        of tender specific requirements is being omitted. The same burden lays on contracting authorities who
        have to check for each evidence whether the issuer has appropriate rights within that country to
        provide evidence. Furthermore the possibility to re-use evidences that are still valid (time) and the
        maintenance of a VCD will again provide possibilities for cost reductions at the side of the economic
        operator.
        A paradigm shift towards electronic exchange of evidence and a next generation of attestations and
        certificates that are currently barely available in electronic form may be promoted by a VCD. At least
        the structural representation of attestation will provide benefit for the entities involved by providing
        transparency about the tendering requirements and the evidences that have to be submitted in cross
        border procedures. The pre-VCD mapping tool in particular will ensure transparency on cross border
        tendering requirements and will give indications about mutual recognition of evidences across borders.
        In contrast a VCD package contains the data necessary to prove the suitability of an economic
        operator according to these requirements. Therewith the VCD ease the overall procedure, may raise
        the number of cases of cross border procurements and may raise possibilities for greater competition
        across borders.

#### 5.2.4 Threats for a VCD in public procurement

Challenges to be dissolved when facing in particular the European perspectives of a VCD are
        mentioned by (Siemens_and_Time.lex 2008):

### 5.3 Next steps in specification

The requirements specification at hand lays the ground for further development towards a VCD. The
      report lists requirements that scope a potential solution according to the different levels of maturity and
      generic requirements. These requirements now have to be taken further into account in order to
      specify the VCD and implement the various stages. To facilitate management of the requirements,
      they will be transformed into a spreadsheet with information as shown in Table 11. A distinction will be
      made among functional requirements, non-functional requirements and requirements that specifically
      refer to the development process.
      The spreadsheet will be used in the project in order to maintain, adapt and perform change
      management to the requirements over the project lifetime. Maintaining them over the project lifetime
      will ensure that the requirements are complete, explicitly defined, clearly described, numbered and
      referenced. Further characteristics to evaluate the quality of requirements will be considered such as
      their determinability (atomic character), verifiability (well defined measurement towards the fulfilment of
      a requirement), traceability (tracking of complete fulfilment as well as of where a requirement emerged
      from) and consistency (conflicts between requirements such as contrary features or quality aspects).
      The requirements will be the basis for further development and will provide guidance and reference to
      subsequent activities. Taking the PEPPOL development infrastructure guidelines, SCRUM25 or the
      waterfall model (McDermind_and_Rook, 1991) as reference models, the next phase focuses now on
      the detailed design of the VCD concept as presented above. This phase will further detail the
      requirements through explicit models and artefacts that describe relevant process flows, data
      characteristics and software.
      Drafting agreed models requires interdisciplinary work between participants with different skills.
      Software engineers thereby may design a software model for the mapping of evidences together with
      legal experts that ensure the legitimacy of such a model. Furthermore we intend to work closely
      together CEN BII workshop and DG Markt (including Siemens and Time.lex) when drafting these models
      in order to ensure long term sustainability of the solution envisaged. The shared artefacts then can
      provide the basis for the implementation stage. They will also be fed back to the requirements and
      may enforce change to them.


## 6 Conclusions

The report at hand aimed at documenting the functional and non-functional requirements for a Virtual
    Company Dossier. Departing from a description of the current procedure when economic operators
    collect the necessary evidences as proofs of selection and exclusion criteria in public tenders, the
    team of work package 2 has elaborated a four-stage vision for the VCD. This four-stage concept takes
    into consideration different strategies and levels of development in the provision of evidences within
    Member States. With the implementation of stage 1, the pre-VCD mapping, a first level of
    interoperability and facilitation to collect the necessary evidences for a public tender in another
    Member State is supported. The VCD concept, however, fosters higher maturity degrees, i.e.
    interoperability and facilitation for both, economic operators and procuring agencies through machinereadable
    and computable VCD packages containing the individual evidences.
    Throughout the analysis, elaboration and definition of the VCD concept plus the necessary research
    affiliated with this activity, fruitful insights could be collected about dependencies and
    interrelationships, which make this domain rather complex.
    The project team is aware of the fact that the VCD concept conceptualised in this report is rather
    generous – especially if we attempt to implement stage 4 of the VCD vision. A big step towards
    interoperability and cross-border facilitation in the collection of company information of economic
    operators can already be made when implementing the pre-VCD mapping tool.
    Consequently, a recommendation is given to focus implementation on the pre-VCD mapping tool for
    widespread application of a VCD at first hand. This very first level of interoperability and semantic
    mapping is the basis for the subsequent stages. Nonetheless, the big potentials of interoperability, of
    facilitation, of cost savings and of reduction of administrative burden lay in the implementation of
    stages 3 and 4. The two pilots scheduled within WP 2 will concentrate their efforts on these latter
    stages, and hence will evidence the potentials of these stages. They form the test cases for a wider
    rollout of the VCD concept as developed throughout phase 1 of work package 2 within PEPPOL.

## 7 References

Bausa O. and Boujraf A. (2009). Draft delivarable of CEN/ISSS WS/BII - WG3: High
    Level Requirements for Electronic Procurement. Business Domain: Electronic
    Procurement, European Committee for Standardization (CEN).
    Berners-Lee, T. (2000) "Semantic Web - XML2000." W3C Talks Volume, DOI:
    Commission_of_the_European_Communitites (2004). Action plan for the implementation
    of the legal framework for electronic public procurement. Brussels, European
    Commission.
    Commission_Staff_Working_Document (08.07.2005) "Requirements for conducting public
    procurement using electronic means under the new public procurement Directives
    2004/18/EC and 2004/17/EC." Volume, DOI:
    EC (30.04.2004). "Directive 2004/18/EC of the European Parliament and of the Council of
    31 March 2004 on the coordination of procedures for the award of public works
    contracts, public supply contracts and public service contracts." Official Journal of
    the European Union.
    EC (2005). Integrated Guidelines For Growth And Jobs. COM (2005) 141 final. Brussels.
    141 final.
    European_Dynamics_S_A (2004). State of the Art Report Volume 1: Case Studies on
    European Electronic Public Procurement Projects in Public eProcurement.
    Brussels, European Commission.
    Fensel, D. (2001). Ontologies: A Silver Bullet for Knowledge Management and Electronic
    Commerce. Heidelberg, Springer Verlag.
    Fensel, D., H. Lausen, et al. (2007). Enabling Semantic Web Services: The Web Service
    Modeling Ontology. Berlin, Heidelberg, New York, Springer-Verlag.
    IDABC (2004). EIF: European Interoperability Framework for Pan-European EGovernment
    Services. European Communities.
    Ministerial_Declaration (2005). Transforming Public Services. Manchester, Ministers of
    the European Union.
    Passin, T. B. (2004). Explorer's Guide to the Semantic Web, Manning Publications Co.
    Russel N., Hofsteded A.H.M., et al. (2005). "Workflow Data Patterns: Identification,
    Representation and Tool Support." Conceptual Modeling ER 2005 pp. 353-368.
    Shadbolt, N., W. Hall, et al. (2006). "The Semantic Web Revisited." IEEE Computer
    Society 21(3): 96-101.
    Siemens_and_Time.lex (2007) "Preliminary Study on the electronic provision of
    certificates and attestations usually required in public procurement procedures:
    First interim report - National Country Profiles." prepared on behalf of the
    European Commission, Directorate-General Internal Market and Services Volume,
    DOI:
    Siemens_and_Time.lex (2008). Preliminary Study on the electronic provision of certificates
    and attestations usually required in public procurement procedures: Final report -
    Strategy and implementation roadmaps. prepared on behalf of the European
    Commission Directorate-General Internal Market and Services. Brussels.
    Siemens_and_Time.lex (2008). Preliminary Study on the electronic provision of certificates
    and attestations usually required in public procurement procedures: Third interim
    report - Scenario building, assessment and benchmarking. prepared on behalf of the
    European Commission Directorate-General Internal Market and Services. Brussels.
