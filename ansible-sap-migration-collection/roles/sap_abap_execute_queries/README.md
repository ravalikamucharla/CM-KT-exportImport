# sap_abap_execute_queries

This role establish connection to an SAP system using ansible custom module(sap_pyrfc).
To perform the basis tasks for system migration using ABAP scripts.
it includes taking backup of system configurations and existing data for verification post migration

The pre and post migrate abap profile is selected by setting the `playbook_no` variable.  Valid profiles are:
* `premigration` - used for pre-migration checks 
* `rampdownchecks` - used for ramp-down checks
* `rampdownactivities` - used for ramp-down activities
* `postmigrate_export` - used for target-export checks
* `postmigration_compare` - used for post-migration checks

## Overview

The installation and configuration of sap_abap_execute_queries involves a number of steps (at a high level):
* Establish connection and getting output from SAP system
* Storing outputs in a JSON format 
* Custom module python scripts and ABAP scripts are included in role.
* Custom python module used - sap_pyrfc

## Requirements:

 The Pre-requisites for this role are:

* For ASCS instance port 36xx must be open
* For PAS instance port 33xx must be open
* For DB port 3xx13 or 3xx15 must be open

## Role Variables

The variables to be used within this role are all defined at all.yml,group_vars and host_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|user|sap logon user|yes|
|password|sap logon password|yes|
|client|Client number of r3user|yes|
|abap_scripts_path|path of scripts folder|yes|
|abap_export_path|path where abap scripts outputs should be stored|yes|

### group variables (host_vars)
|variable|info|required?|
|---|---|---|
|instance_number|instance number of ascs or pas|yes|

### group variables (all)
|variable|info|required?|
|---|---|---|
|group|group of ascs or pas|yes|
|outputs_path|path of output folder|yes|
|source.sap.sid|sap sid of source|yes|
|target.sap.sid|sap sid of target|yes|
|cloudmigrate_server_sudo_user|owner name of the folder|yes|
|cloudmigrate_server_sudo_user_group|group name of the folder|yes|
|rampdown_activities.smigr.target_db_type|db type of target database|yes|
|rampdown_activities.smigr.db_version|db version of the database|yes|
|rampdown_activities.smigr.installation_directory|path or directory where smigr output to be installed|yes|

## Dependencies

Ansible custom module(sap_pyrfc) will work only when "PyRFC - The Python RFC Connector" Python package installed in Ansible controller  machine.

[PyRFC Installation Guide](https://sap.github.io/PyRFC/install.html)

## Example Playbook
```yaml
---
- hosts: localhost
  roles:
      - sap_abap_execute_queries
```

## Checks
Check if json files are created in the respective path
```bash
# path- /cm_sap_migration/examples-sap-migration/sc01-abap-migration_{{ source.sap.sid }}_{{ target.sap.sid }}/ansible/outputs/Migrate_{{ source.sap.sid }}_{{ target.sap.sid }}/source/abap_export/"
cd <path>
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|
|minor|changes in smigr input|28th dec 2022|Pavithra Sathyanarayanan|
|minor|abap script changes for 731 version|18th jan 2023|Yasaswini kandukuri|
|bug fix|removed duplicates scripts in defaults(SECSTORE,SM13,SM21,SMICM) and changes in input for top tables|14th feb 2023|Pavithra sathyanarayanan|
|minor|abap script changes based on version specific(STRUST,OAC0)|Ashwini|
|minor|abap script changes for OAC0,SMLG,RZ10 Tcode|27th feb 2023|Ashwini Patil|
|minor|abap script changes for SMQR and SMQS tcode|1st march 2023|Ashwini Patil| 
|minor|abap script changes for RZ12,STRUST,OAC0 tcode|10th April 2023|Yasaswini kandukuri, Ashwini Patil| 
|minor|snc_parameter added for sap_pyrfc module task|10th April 2023|Anuja Gangeswari,Pavithra Sathyanarayanan|
|minor|sp12 tcode added in pre-checks|27th april 2023|Pavithra Sathyanarayanan|
|minor|abap script changes for SM58 tcode and new abap script added ZCM_HDB_SQL_QUERIES_EXECUTE|13th june 2023|Ashwini Patil,Yasaswini Kandukuri|
|minor|removed ZCM_SPNEGO_CONFIG_DETAILS script and added ZCM_DB02_EXP_HOSTS_SERVICES script to hana specific section|19th june 2023|Yasaswini Kandukuri|
|minor|changes in nwbc,sm52 and trexadmin scripts and added title_json file for default message for version scripts|27th june 2023|Ashwini Patil|
|minor|added script and templates to for default message in db scpefic scripts|27th june 2023|Pavithra sathyanarayanan|
|minor|added template for hana sql queries script|28th jsune 2023|Pavithra sathyanarayanan|
|minor|changes in pre and postmigration yml file (db_type to database_type)|14th july 2023|Pavithra sathyanarayanan|
|minor|changes in title_json,RFC check,sm21,sm51,sm52,St03N,strurst,DB02 scripts for 702 version and added rz12 script,coloumn_mapping json file for 702 version|14th july 2023|Ashwini Patil,Yasaswini Kandukuri,Anuja Gangeshwari|


## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## References
[Cloud Migrate Developer Team design]

1. Ticket reference: https://alm.accenture.com/jira/browse/ACNCSSPR-68

