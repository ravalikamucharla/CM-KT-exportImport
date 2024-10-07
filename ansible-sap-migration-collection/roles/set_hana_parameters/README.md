# set_hana_parameters
This role is used to set the Hana parameters on source and target based on user requirement.

The network parameters is set on respective hosts by setting the `set_params_on` variable.  Valid profiles are:
* `source` - this profile sets the hana parameters on source
* `target` - this profile sets the hana parameters on target
* `target_primary` - this profile sets the hana parameters on target primary
* `target_secondary` - this profile sets the hana parameters on target secondary

## overview
The setting of network parameters involves a number of steps (at a high level):
* Taking backup of global and indexserver files
* Set the hana values on the respective system.

## Role Variables
The variables to be used within this role are all defined at all.yml level

### group variables (all)
|variable|info|required?|
|---|---|---|
|source_primary.hana_params_change_source.params|hana paramterters like service,mode, parameter and value that needs to be set on source|yes|
|source_primary.hana_params_change_target.params|hana paramterters like service,mode, parameter and value that needs to be set on target|yes|
|target_primary_params.hana_params_change_source.params|hana paramterters like service,mode, parameter and value that needs to be set on target primary|yes|
|target_primary_params.hana_params_change_target.params|hana paramterters like service,mode, parameter and value that needs to be set on target secondary|yes|
|primary_host|hostname of source system|yes|

## Example Playbook
```yaml
---
- hosts: source_db
  roles:
      - { role: set_hana_parameters, set_params_on: source, when: source_primary.hana_params_change_source.required == 'yes' }
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/playbooks/05_2_hsr_migration_target.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/inventory)

## Checks
Check if hana parameter value is set correctly in global or indexserver ini
```bash
# path- /usr/sap/sid/SYS/global/hdb/custom/config/global.ini
# path- /usr/sap/sid/SYS/global/hdb/custom/config/indexserver.ini
cd <path>
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|3rd march 2023|Pavithra Sathyanarayanan|
|minor|changes made in source and target to execute sql query with hdbuserstorekey or user and password|9th march 2023|Pavithra Sathyanarayanan|
|minor|modified script according to HA scenario|27th april 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)
