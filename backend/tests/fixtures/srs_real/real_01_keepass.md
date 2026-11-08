# KeePass Password Safe 1.10 Software Requirements Specification

> **Dataset:** PURE Dataset (Zenodo 7118517 / IEEE RE 2017)
> **Original Document Title:** Software Requirements Specification for KeePass Password Safe
> **Domain:** Desktop Security
> **License:** GPL-2.0
> **Source/Project:** https://keepass.info
> **Version:** 1.10
> **Issue Date:** 2008-02-17

---

## 1 Introduction

### 1.1 Purpose

This document includes software requirements for KeePass Password Safe, release number 1.10. KeePass Password Safe is an OSI Certified Open Source Software distributed under the terms of the GNU General Public License Version 2 or under. The system gives resolution to memorizing passwords problem. Its purpose is to keep all of the user’s passwords, data, email accounts, usernames and URLs stored in a very
secure, encrypted database, protected by a Master Password. The system is very small so it can be easily transferred from one computer to another. It provides several functionalities on the already encrypted data and the new ones to be inserted. The database produced, is protected by a Master Password only known by
its inventor with no backup if lost.

### 1.2 Document Conventions

· When writing this document it was inherited that all requirements have the same priority.
· First there is presented an overall view about KeePass and then all features and functions are
analyzed in detail.

### 1.3 Intended Audience and Reading Suggestions

This requirement document contains general information about KeePass, main classes and use cases, functions, features and special technologies. It describes in detail all that KeePass needs to work properly and with safety.
The rest of the document is divided into chapters for better understanding.

### 1.4 Project Scope

KeePass Password Safe is a small system that can be easily transferred from computer to computer by a simple USB stick. Its purpose is to solve a problem that really bothers many people today when they have to choose from memorizing a lot of passwords to be secure or to use every time the same one so they won’t forget it but risk be found out by others. So it provides you a very secure, encrypted database where you can keep inside all your passwords, usernames, email accounts, URLs, notes without any risk for others to find them. That is because KeePass Password Safe can lock every database with only one Master Password and/or key file. There are no duplicates, anywhere in your computer, of this Master Password and/or key file so in case of lost database cannot be opened by anyone. Not even by you and that is because there is no recovery password or back door.
KeePass Password Safe beside security also provides you with several functionalities in order to keep your database organized and up to date. Those are analyzed in the following pages.
More about KeePass you can find out at http://keepass.info/

### 1.5 References

More about KeePass can be found at

### 2.1 Product Perspective

KeePass consists of a database which contains data for one or more users. Each user’s data are divided into groups and subgroups so that they are organized in a form that serves right the user. Every user has a unique Master Key which can be simple or composite and its combination opens uniquely the database. If lost there
is no recovery. Groups and subgroups contain entries with usernames, passwords URLs etc that can be sent or copied to websites, application and accounts. There is also the ability for a onetime key creation to be used once in a transaction without the risk of reused by others for any reason.
In the diagram below there are the main components of the system, subsystem interconnections and external interfaces to help you understand the main idea of KeePass. All of them are analyzed with more details in this document.


### 2.2 Product Features

KeePass Password Safe provides the user with the following functions:

### 2.3 User Classes and Characteristics

### 2.4 Operating Environment

KeePass should run on Operating Systems: WINE, 32-bit MS Windows (95/98), 32-bit MS Windows (NT/2000/XP), All 32-bit MS Windows (95/98/NT/2000/XP),Win2K, WinXP, Microsoft Windows Server 2003.
The user interfaces used are: NET/Mono, Win32 (MS Windows)
All new releases contain Filename Architecture Type
KeePass-1.x-Setup.exe i386 .exe (32-bit Windows)
KeePass-1.x-Src.zip Platform-Independent Source .zip
KeePass-1.x.zip i386 .zip
and release notes witch describe what has changed and what has been added.
Nothing more than these is required for a fully functional KeePass.
KeePass should run perfectly on older releases without any features limitations or data loss.

### 2.5 Design and Implementation Constraints

Timing requirements in KeePass Password Safe:
When a password is copied for any reason, (e.g. copy to an application, account, and website) it remains in the memory for only 10 seconds. After 10 seconds pass there is nothing to paste and you have to recopy again. That provides security in a case a password is copied and not pasted anywhere so no one can find it out by pasting later.
Language Requirements in KeePass Password Safe:
Not in all translations translated help files and tutorials are available.
Specific Technologies used in KeePass Password Safe:

### 2.6 User Documentation

By downloading KeePass Password Safe, the user also gets:

## 3 System Features

System features are organized by use cases and functional hierarchy so that the main functions of the system will be understandable.

### 3.1 New Database

This feature provides the ability to create a new database

#### 3.1.1 Description

It is the first thing a user must do to begin using KeePass. Its main function is the determination of the master password that will unlock the database from now on

#### 3.1.2 Stimulus/Response Sequences

Data Flow

##### 3.1.2.1 Basic Data Flow

##### 3.1.2.2 Alternative Data Flows

##### 3.1.2.2.1 Alternative Data Flow 1

##### 3.1.2.2.2 Alternative Data Flow 2

##### 3.1.2.2.3 Alternative Data Flow 3

#### 3.1.3 Functional Requirements

### 3.2 Open Database

This feature allows the user to open an existing database.

#### 3.2.1 Description

When choosing to open a database a user is transferred to his documents where he navigates to find the database he wants. When the database is found, the master password is wanted so that the database will be unlocked. Once this is done the user is free to access his data.

#### 3.2.2 Stimulus/Response Sequences

Data Flow

##### 3.2.2.1 Basic Data Flow

##### 3.2.2.2 Alternative Data Flows

##### 3.2.2.2.1 Alternative Data Flow 1

##### 3.2.2.2.2 Alternative Data Flow 2

##### 3.2.2.2.3 Alternative Data Flow 3

#### 3.2.3 Functional Requirements

### 3.3 Save Database

This feature allows the user to save any changes or updates he has performed to his database.

#### 3.3.1 Description

When a database is opened, the user can access his passwords, organize them into new
groups and subgroups, delete and add entries and so much more. But when it is time for the database to close or during his working on the database, he can save the changes made.

#### 3.3.2 Stimulus/Response Sequences

Data Flow

##### 3.3.2.1 Basic Data Flow

##### 3.3.2.2 Alternative Data Flows

##### 3.3.2.2.1 Alternative Data Flow 1

##### 3.3.2.2.2 Alternative Data Flow 2

##### 3.3.2.2.3 Alternative Data Flow 3

##### 3.3.2.2.4 Alternative Data Flow 4

#### 3.3.3 Functional Requirements

### 3.4 Print Database

This feature allows user to print a selection of data that are stored in the database.

#### 3.4.1 Description

While working on the database, the user has the option to print data from his database. This can be done by selecting print. When this happens, a list of data types that can be printed are shown and the user can select the data to be printed. More specifically fields that can be selected for printing are: Backup entries, which contain entries in the back up group, password groups, group tree, title, username, password, URL, notes, creation time, last access, last modification, expires, icon, UUID and attachment.

#### 3.4.2 Stimulus/Response Sequences

Data Flow

##### 3.4.2.1 Basic Data Flow

##### 3.4.2.2 Alternative Data Flows

##### 3.4.2.2.1 Alternative Data Flow 1

3a. User selects some more fields and/or unselects some others.

##### 3.4.2.2.2 Alternative Data Flow 2

##### 3.4.2.2.3 Alternative Data Flow 3

#### 3.4.3 Functional Requirements

### 3.5 Search Database

This feature allows user to search for keywords in his database.

#### 3.5.1 Description

There is the ability to search in the database for usernames, groups, passwords, URLs, notes and titles. This is very useful when the user needs to find out very quickly which password is required in one account or what username he has put on another account. It is not necessary to write in the search field all characters. By writing just one character the database will present all data which contains it or are related with it.

#### 3.5.2. Stimulus/Response Sequences

Data Flow

##### 3.5.2.1 Basic Data Flow

##### 3.5.2.2 Alternative Data Flows

##### 3.5.2.2.1 Alternative Data Flow 1

##### 3.5.2.2.2 Alternative Data Flow 2

##### 3.5.2.2.3 Alternative Data Flow 3

##### 3.5.2.2.4 Alternative Data Flow 4

##### 3.5.3 Functional Requirements

### 3.6 Add Group/Subgroup

This feature is used to keep data organized in categories for easier access.

#### 3.6.1 Description

There is the ability to organize data into groups and subgroups. The user can create a new group or subgroups into an existing group. When creating a group/subgroup the user must select a name and then he can add entries into it.

#### 3.6.2 Stimulus/Response Sequences

Data Flow

##### 3.6.2.1 Basic Data Flow

##### 3.6.2.2 Alternative Data Flows

##### 3.6.2.2.1 Alternative Data Flow 1

##### 3.6.2.2.2 Alternative Data Flow 2

#### 3.6.3 Functional Requirements

### 3.7 Modify group/subgroup

This feature allows user to change a name given to a group/subgroup.

#### 3.7.1 Description

When user wants to change a group or subgroup’s name he has the ability to do that by
modifying it.

#### 3.7.2 Stimulus/Response Sequences

Data Flow

##### 3.7.2.1 Basic Data Flow

##### 3.7.2.2 Alternative Data Flows

##### 3.7.2.2.1 Alternative Data Flow 1

##### 3.7.2.2.2 Alternative Data Flow 2

#### 3.7.3 Functional Requirements

### 3.8 Delete Group/Subgroup

This feature allows the user to delete a group/subgroup.

#### 3.8.1 Description

When a user wants to delete an existing group/subgroup he can do this by selecting Delete group/subgroup from the edit menu. In order for that to happen, he must have chosen first a group/subgroup.

#### 3.8.2 Stimulus/Response Sequences

Data Flow

##### 3.8.2.1 Basic Data Flow

##### 3.8.2.2 Alternative Data Flows

##### 3.8.2.2.1 Alternative Data Flow 1

#### 3.8.3 Functional Requirements

Not exists.

### 3.9 Find Group/Subgroup

This feature allows user to find data into a specific group/subgroup.

#### 3.9.1 Description

The user selects a group/subgroup and then he chooses “find in this group” from file menu. Then a window appears which prompts the user to write a sequence of characters (letters and numbers) from one character to 200 (or more). After that a menu of options to choose from appears and the user can select to search for: title, user name, password, URL, notes, group name. Search results appear in the main window.

#### 3.9.2 Stimulus/Response Sequences

Data Flow

##### 3.9.2.1 Basic Data Flow

##### 3.9.2.2 Alternative Data Flows

##### 3.9.2.2.1 Alternative Data Flow 1

##### 3.9.2.2.2 Alternative Data Flow 2

##### 3.9.2.2.3 Alternative Data Flow 3

##### 3.9.2.2.4 Alternative Data Flow 4

#### 3.9.3 Functional Requirements

### 3.10 Add Entry

This feature adds a new entry on the database.

#### 3.10.1 Description

The user can add a new entry on the database by clicking add entry on the main menu. When he does this, a window opens which is actually a form. In this form the user completes the fields he wants. He can fill in fields like: group where the entry will be added, title, user name, password, repeat password, URL, notes, expiration date and attachment file. Not all fields are required for an entry to be created. In fact an entry can be added with no fields at all. By selecting OK the entry is created in the group selected.

#### 3.10.2 Stimulus/Response Sequences

Data Flow

##### 3.10.2.1 Basic Data Flow

##### 3.10.2.2 Alternative Data Flows

##### 3.10.2.2.1 Alternative Data Flow 1

##### 3.10.2.2.2 Alternative Data Flow 2

##### 3.10.2.2.3 Alternative Data Flow 3

##### 3.10.2.2.4 Alternative Data Flow 4

#### 3.10.3 Functional Requirements

### 3.11 View/Edit Entry

This feature allows the user to change or modify an existing entry.

#### 3.11.1 Description

The user can modify the context of an entry he already has added. This can be done by
selecting view/edit entry. In order for that to happen, the user must select an entry first.
When he does this, the form he filled in when he created or last modified the entry open.
Then the user can change the group, title, user name, password, URL, notes, expiration date and attachment file. His changes are saved by clicking OK.

#### 3.11.2 Stimulus/Response Sequences

Data Flow

##### 3.11.2.1 Basic Data Flow

##### 3.11.2.2 Alternative Data Flows

##### 3.11.2.2.1 Alternative Data Flow 1

##### 3.11.2.2.2 Alternative Data Flow 2

##### 3.11.2.2.3 Alternative Data Flow 3

#### 3.11.3 Functional Requirements

### 3.12 Duplicate Entry

This feature creates an exact copy of the selected entry in the same group.

#### 3.12.1 Description

The user can create an exact copy of an entry. This can be done by selecting an entry and clicking duplicate entry. When this is done the new entry is added in the same group were the first was.

#### 3.12.2 Stimulus/Response Sequences

Data Flow

##### 3.12.2.1 Basic Data Flow

##### 3.12.2.2 Alternative Data Flows

Not exist

#### 3.12.3 Functional Requirements

### 3.13 Delete Entry

This feature allows the user to delete an existing entry

#### 3.13.1 Description

The user can delete an existing entry by selecting it and then by clicking delete entry. When this is done a message appears and informs the user that if he deletes the entry he won’t be able to restore it back.

#### 3.13.2 Stimulus/Response Sequences

Data Flow

##### 3.13.2.1 Basic Data Flow

##### 3.13.2.2 Alternative Data Flows

##### 3.13.2.2.1 Alternative Data Flow 1

##### 3.13.2.2.2 Alternative Data Flow 2

#### 3.13.3 Functional Requirements

REQ-17: An entry must be selected to be deleted

### 3.14 Change Language

This feature allows user to choose one of the language translations that are available in KeePass

#### 3.14.1 Description

The user can select between a number of translations that are available at KeePass website.
There are available translations in Arabic, Brazilian, Bulgarian, Catalan, Chinese
(Simplified and Traditional), Czech, Danish, Dutch, English, Estonian, Finnish, French,
Galician, German, Greek, Hebrew, Hungarian, Italian, Japanese, Korean, Lithuanian,
Macedonian, Malay, Norwegian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak,
Spanish, Swedish, Turkish and Ukrainian. All the user has to do is to select change
language from the view menu and then the language he wants. If he already has download languages packets he can choose one of them. If he wants another language pack he can select get more language. Doing this he will be transferred at KeePass website and choose the language he wants for downloading.

#### 3.14.2 Stimulus/Response Sequences

Data Flow

##### 3.14.2.1 Basic Data Flow

1. User opens KeePass and selects to change language from the view menu
2. The user selects a language to load from the list that appears
3. A message appears that informs user that the installation has been done and in order for the changes to take place KeePass must be restarted
4. User selects yes (restart now)
5. KeePass asks to save any changes that may have been made in the database and restarts
6. User unlocks the database using the Master Password
7. The database appears translated in the new language

##### 3.14.2.2 Alternative Data Flows

##### 3.14.2.2.1 Alternative Data Flow 1

##### 3.14.2.2.2 Alternative Data Flow 2

##### 3.14.2.2.3 Alternative Data Flow 3

#### 3.14.3 Functional Requirements

### 3.15 Auto-type

This feature allows user to define a sequence of keypresses which KeePass will automatically perform.

#### 3.15.1 Description

The user defines the sequences which can be sent to any other open window like browsers or login accounts. By default the sent keystroke sequence is {USERNAME}{TAB}{PASSWORD}{ENTER}. There is the ability for the user to define his own auto-type sequence in the notes field of each entry. The sequence must be prefixed with “Auto-Type” and length of one line. If a sequence is more than a line it cannot be used and in case of two sequences in one note’s field only the first one is used. There are 3 methods to invoke auto-type.

#### 3.15.2 Functional Requirements

### 3.16 Command Line Options

This feature allows user to pass a file patch in the command line so that KeePass will open it immediately after start up.

#### 3.16.1 Description

The database file location is passed as argument in the command line. More about this
feature and examples for using it can be found at help contents in KeePass

#### 3.16.2 Functional Requirements

### 3.17 Composite Master Key

This feature is a composition of master password and key files and all its composites are required so that the database can be unlocked.

#### 3.17.1 Description

The database can be unlocked with a master password, a key file or both of them. But the same composition of them must be used always.
A master key is a password the user creates. Once a master key is created for a database, it is always required. In case the user forgets it, the database can never be opened again by any way.
A key file is a file that locks the database. The database opens when this file is present. If the file is lost and there are no copies of it, all data are gone forever and database never unlocks again.

#### 3.17.2 Functional Requirements

### 3.18 Import/Export

This feature gives the ability to user to import/export files from/to database.

#### 3.18.1 Description

There is the ability to import data from CSV files, code wallet, password safe and password vault. There are available plug-ins which add more import capabilities and formats and those are: File format CSV and File format XML. There isn’t any standard password database format and every password manager uses its own file format. Despite that, almost all support exporting to CSV or XML files.

#### 3.18.2 Functional Requirements

### 3.19 Integration

This feature allows switching back from an application to KeePass.

#### 3.19.1 Description

The global hot key takes the user back from one window to KeePass. In case of multiple
databases running of KeePass the global hot key restores the window which was opened first of all. The global hot key is Ctrl+Alt+K

#### 3.19.2 Functional Requirements

### 3.20 Password Generator

This feature generates random passwords.

#### 3.20.1 Description

The password generator creates random passwords every time an entry is created. This
password may contain letters (big and small) and numbers. The user can keep it or he can put his own in the field. The generation can be based on character sets, patterns or can be created according by rules. This feature can be disabled if user wants it by selecting 0 as password length in the password generator dialog. More about characters sets and patterns can be found at KeePass Help Files including directions and examples.

#### 3.20.2 Functional Requirements

According to restriction rules that are applied every time.

### 3.21 TAN Support

This feature allows creation of Transaction Authentication Numbers.

#### 3.21.1 Description

TANs can be passwords that provide security because they can never be used for more than once time. They can be added to user’s database by using TAN wizard and can contain all letters and numbers. When TAN are created, they appear as typical entries which in the field title contain “TAN” so that KeePass will know it’s a TAN. In TAN entries, user cannot change the title, user name or URL but notes can be added. When a TAN is used, its expiration time is set to that current time and the entry expires automatically.

#### 3.21.2 Functional Requirements

## 4 External Interface Requirements

### 4.1 User Interfaces

User interface includes various forms and windows. The main database window consists of the main menu bar with file, edit, view, tools and help. Under main menu there is a toolbar with shortcuts to most used functions of KeePass. Those are: new, open, save, add entry, edit/view entry, delete entry, copy username to clipboard, copy password to clipboard, find in database and lock workspace. On the main database window are appeared entries from a selected group. Groups and subgroups can be found at a side bar.
When a function is performed like adding, editing or deleting, the active window is the one performing the action. At this time the main database window is inactive and cannot be accessed unless the current active window is closed.
KeePass as referred previously uses NET/Mono and Win32 (MS Windows) interfaces.

### 4.2 Communications Interfaces

## 5. Other Nonfunctional Requirements

### 5.1 Performance Requirements

When a password is copied, it remains on memory for only 10 seconds. If in the meanwhile it is not pasted anywhere, it must be copied again. That happens so that if user copies a password and not paste it anywhere, the password cannot be found by anyone later.

### 5.2 Safety Requirements

When a USB which contains the database is removed from a computer while changes haven’t been completely saved, the database is damaged and cannot be opened. In this case the repair functionality can help by repairing KeePass database file from tools menu.
In case the user forgets or loses the Master Password, the repair functionality won’t help.
In case the header of the database, which is the first few bytes, is corrupted, again the repair functionality won’t help.
To avoid this kind of situations, backups can be done regularly.

### 5,3 Software Quality Attributes
