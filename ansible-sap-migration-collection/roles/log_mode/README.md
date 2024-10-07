# log_mode
This role is used to check whether logmode is set to normal or not, the role also helps in setting the mode to normal if the mode is overwrite.

## Role variables
The variables to be used within this role are all defined at all.yml level

### group variables (common)
|variable|info|required?|
|---|---|---|
|sid|sid of source or target database|yes|
|hdbuserstore_key.key_name|userstorekey of database|no|

## Example Playbook
```yaml
---
- hosts: sourec_db/target_db
  roles:
      - log_mode
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/playbooks/05_1_hsr_migration_source.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/inventory)

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|27th feb 2023|Pavithra Sathyanarayanan|
|minor|changes made to check log mode with hdbuserstorekey or user and password|13th march 2023|Pavithra Sathyanarayanan|
|minor|modified script for HA scenario|25th april 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]