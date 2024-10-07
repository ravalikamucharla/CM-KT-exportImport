# copy_files
This role is used to copy the DAT and KEY file from one server to another with different authentication method.

The method to copy files is selected by setting the `authentication_type` variable.  Valid profiles are:
* `copy_passwordless` - copy files without password
* `copy_with_password` - copy files with password
* `ppk` - copy files with ppk and pem files

## Overview
The role performs multiple tasks like 
* taking backup of the dat and key files before copying
* install pexpect module for password authentication if os is redhat 
* installing puttygen if authencation is ppk
* copying files from source system to the respective target system

## Role Variables
The variables to be used within this role are all defined at all.yml,group_vars and host_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of source or target database|yes|
|rep_source_db|physical or virtual hostname of database from which the files should be copied|yes|
|ppk_source_path|path of ppk file|yes|
|ppk_name|ppk file name|yes|
|primary_host|source hostname of database|yes|

## Example Playbook

```yaml
---
- hosts: source_db/target_db
  roles:
      - copy_files
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/playbooks/05_2_hsr_migration_target.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/inventory/ansible/inventory)

## Checks
1.We can validate by checking if the files are copied to the respective path.
```bash
cd /usr/sap/SID/SYS/global/security/rsecssfs/data/ 
cd /usr/sap/SID/SYS/global/security/rsecssfs/key/
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|1st march 2023|Pavithra Sathyanarayanan|
|minor|changes in copy_with_password( query to take ip or hostname)|9th march 20233|Pavithra Sathyanarayanan|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]
