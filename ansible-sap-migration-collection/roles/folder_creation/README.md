# folder_creation
This role is being used for creating folders.

## Role variables
The variables to be used within this role are all defined at sap-abap-execute-queries role and at all.yml level

### group variables (common)
|variable|info|required?|
|---|---|---|
|folders|an array of directories to be created|yes|
|folders[loopindex].path|name of the directory path|yes|
|folders[loopindex].owner|name of the owner of the directory|yes| 
|folders[loopindex].group|name of the group of the directory|yes|
|folders[loopindex].mode|permission of the deirectory|no (defaults to associated "755" value)|

## Example Playbook
```yaml
---
- hosts: localhost
  roles:
      - folder_creation
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/playbooks/01_source_pre_migration_basisconfig_export)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/inventory)

## Checks
We can validate by checking if the scripts and outputs folder are created:
```bash
# 1./cm_sap_migration/examples-sap-migration/sc01-abap-migration_{{ source.sap.sid }}_{{ target.sap.sid }}/ansible/scripts/
# 2./cm_sap_migration/examples-sap-migration/sc01-abap-migration_{{ source.sap.sid }}_{{ target.sap.sid }}/ansible/outputs
cd <path>
```

## Code Update
|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|minor|changes made to create folders with root access|9th march 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

# Design
[Cloud Migrate Developer Team design]