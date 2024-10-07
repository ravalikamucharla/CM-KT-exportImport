# sap_abap_postmigration

This role to perform the basis tasks for post system migration using ABAP scripts. ans establishes connection to SAP system using ansible custom module(sap_pyrfc).
This role also validate the source and target system configurations using ansible custom modules

## Overview

* Establish connection and getting output from SAP system
* Storing outputs in a JSON format 
* Custom module python scripts and ABAP scripts are included in role.
* Custom python module used
  - sap_align_configuration
  - sap_httpurlloc
  - sap_rz21_segment
  - sap_logon_group_smlg
  - sap_rfc_groups

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
|smlg__rz12_source|hostname, instance no and sid of source system|yes|
|smlg_rz12_target|hostname, instance no and sid of source system|yes|
|multiple_instance_smlg|condition for multiple aas instances|yes|
|multiple_instance_rz12|condition for multiple aas instances|yes|

## Dependencies

Ansible custom module(sap_pyrfc) will work only when "PyRFC - The Python RFC Connector" Python package installed in Ansible controller  machine.

[PyRFC Installation Guide](https://sap.github.io/PyRFC/install.html)

## Example Playbook

```yaml
---
- hosts: local host
  roles:
      - sap_abap_postmigration
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/playbooks/07_target_post_migration_basisconfig_validate_update)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/inventory)

## Checks
We can validate by checking if the scripts and outputs folder are created:
```bash
cd <path>
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|minor|changes in smlg and rz12 update script for pas and multiple app servers|03 Jan 2023|Pavithra Sathyanarayanan, Jahanavi Golla|
|minor|added smqr_smqs update script|7th feb|Soumya Shubhra Ray, Pavithra Sathyanarayanan| 
|minor|added profile parameter update script|14th feb|Soumya Shubhra Ray, Jahanavi Golla|
|minor|spad update script changes| 27th feb 2023|Pavithra Sathyanarayanan|
|minor|SMLG,STRUST,RFC_GROUPS,SPAD update script changes|10th April 2023|Anuja Gangeswari,Jahanavi Golla|
|minor|snc_parameter added for sap_pyrfc module task|10th April 2023|Anuja Gangeswari,Pavithra Sathyanarayanan |
|minor|changes in ZCM_SPAD_LOCK_UNLOCK_PRINTERS script-sast scan and changes in rz21 script for multiple aas instance|19th june 2023|Yasaswini kandukuri|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]
1. Ticket reference: https://alm.accenture.com/jira/browse/ACNCSSPR-825

