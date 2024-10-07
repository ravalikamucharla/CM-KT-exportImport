# sap_get_os_command_outputs

This role establish connection to linux systems for os level commands invocation and there are few OS informations that are extracted from gather facts.

TO execute OS related queries. Valid profiles are:
* `linux_sol_aix.yml` - used to execute os related queries for linux,solaris and AIX 
* `windows.yml` - used to execute os related queries for windows

## Overview

The configuration of get-os-commands-outputs involves a number of steps (at a high level):

  - Following are the tasks fetching os details from gather facts and generating json files through j2 template. 
    1. OS version 
    2. Capture CPU memory
  - Following are the tasks fetching OS details invoking respective in-line commands and generating json files through j2 template. 
     - disk layout, java version etc..
  - Transfer profile and host files from target node to controller node

## Requirements:

 The Pre-requisites for this role are:

* For ASCS instance port 36xx must be open
* For PAS instance port 33xx must be open
* For DB port 3xx13 or 3xx15 must be open
* To execute os commands in linux 22 port must be opened
* To execute os commands in windows 5985/5986 port must be open

## Role Variables

The variables to be used within this role are all defined at all,group_vars and host_vars level

### group variables (group_vars)

|varible|info|required?|
|---|---|---|
|sid|sap sid of source or target system|yes|
|sap_type|type of SAP installed in system|yes|
|os_export_path|path of folder where os command outputs are generated|yes|
|pse_cert_instance_number|instance number for pse and certificate|yes| 

### group variables (host_vars)

|varible|info|required?|
|---|---|---|
|instance_number|instance number of ascs, pas or db|yes|

### group variables (all)
|varible|info|required?|
|---|---|---|
|cloudmigrate_server_sudo_user|owner permission of the folder|yes|
|cloudmigrate_server_sudo_user_group|group permission of the folder|yes|
|os_export_path|path of folder where os command outputs are generated|yes|
|webdisp_sid|sid in which web dispatcher is installed|yes|
|DAA_path|path where DAA is installed|no|
|DAA_instance_number|instance number of DAA|yes|
|pse_cert_path|path where PSE and certificates are present|no|

## Example Playbook
```yaml
---
- hosts: servers
  roles:
      - sap_get_os_command_outputs
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/playbooks/08_source_pre_migration_basisconfig_export)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/inventory)

## Checks
Check if json files are created in the respective path
```bash
# path- /cm_sap_migration/examples-sap-migration/sc01-abap-migration_{{ source.sap.sid }}_{{ target.sap.sid }}/ansible/outputs/Migrate_{{ source.sap.sid }}_{{ target.sap.sid }}/(source/target)/os_export/"
cd <path>
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|minor|added template for java version output|18th jan 2023|Pavithra Sathyanarayanan|
|minor|changes in ulimit command|27th jan|Pavithra Sathyanarayanan|
|minor|changes in capture_memory, ulimit and disklayout templates|10th feb 2023|Pavithra Sathyanarayanan|
|bugfix|ulimit template changes|27th feb 2023|Jahanavi Golla|


## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## References
[Cloud Migrate Developer Team design]
1. Ticket reference: https://alm.accenture.com/jira/browse/ACNCSSPR-345

