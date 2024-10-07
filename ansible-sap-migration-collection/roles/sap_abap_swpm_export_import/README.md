# sap_abap_swpm_export_import
This role installs sap in both source and target servers of db on different OS.
In source system export gets triggered, and in target system import is triggered.

The sap_abap_swpm_export_import role is performed by selecting the playbooks based on source and target os_type and db_type
* `export-oracle-linux_sudo-hana-linux_sudo` - used for pre-migration checks 
* `export-oracle-linux_sudo-hana-linux_sudo` - used for ramp-down checks
* `export-oracle-linux_sudo-hana-linux_sudo` - used for ramp-down activities

## Overview
This role is one of several required to deliver a working end to end SAP system and is expected to be executed as part of a runbook like the one below.

In addition, prior to execution it is expected that SAP software has been downloaded. And can be shared by different mechanisms like: 
- NFS share
- FTP

Example playbook:
```yaml
---
# This forces a gather facts across all hosts
- hosts: all!vip

# install sap on pas machine
- hosts: source_db
  roles:
    - sap_abap_swpm_export_import

```

## Role variables
The variables to be used within this role are all defined at group level, host level and playbook level .

### group variables (all)
|variable|info|required?|
|---|---|---|
|sap.sid|SID of the sap install|yes|
|sap.db.sid|SID of the HANA install|yes|
|sap.instance_numbers.db|instance number for the HANA instance|yes|
|passwords.admin|password for the standard os admin user|yes|
|passwords.master|master password for HANA install|yes|
|passwords.sapadm|password for the sapadm user|yes|
|passwords.system|password for system user|yes|
|passwords.sidadm|password for sidadm user|yes|
|passwords.systemdb|password for systemdb user|yes|
|users.sapsys.gid|gid for the sapsys group|no (although null is allowed)|
|users.sapadm.uid|uid for the \<sap\>adm|no (although null is allowed)|

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|


## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)