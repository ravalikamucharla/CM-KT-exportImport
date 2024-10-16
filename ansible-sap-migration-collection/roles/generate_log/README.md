# log_mode
This role is used to take backup of ansible.log file.

## Role variables
The variables to be used within this role are all defined at playbook level

### group variables (common)
|variable|info|required?|
|---|---|---|
|playbook_name|sid of source or target database|yes|
|tags|userstorekey of database|no|
|create_zip|userstorekey of database|no|
|send_email|userstorekey of database|no|

## Example Playbook
```yaml
---
- hosts: sourec_db/source_pas/source_ascs/target_db/target_ascs/target_pas/localhost
  roles:
      - generate_log
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/playbooks/01_source_pre_migration_basisconfig_export.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/inventory)

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|27th feb 2023|Susmita Karar|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]