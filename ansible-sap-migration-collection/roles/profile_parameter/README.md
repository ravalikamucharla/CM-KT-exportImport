# sap_abap_execute_queries
This role is used to compare the source and target profile files and update the fiels in target system.

The profile is selected by setting the `mode` variable.  Valid profiles are:
* `profile_parameter_source` - used to fetch the profile file from source system 
* `profile_parameter_target` - used to fetch the profile file from target system
* `profile_parameter_update` - used to update the profile files in target system

## Role Variables

The variables to be used within this role are all defined at all.yml,group_vars and host_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|profile_param_output|output path for profile paramater files in source or target|yes|
|sid|sid of source or target system|yes|
|profile_files|path to store profile files of source or target|yes|

### group variables (all)
|variable|info|required?|
|---|---|---|
|cloudmigrate_server_sudo_user|owner name of the folder|yes|
|cloudmigrate_server_sudo_user_group|group name of the folder|yes|

## Example Playbook
```yaml
---
- hosts: target_db
  roles:
      - profile_parameter
```
## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/playbooks/07_a_target_post_migration_basisconfig_validate_update)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/inventory)

## Checks
Check if output files are generated in the respective path
```bash
# path- /cm_sap_migration/examples-sap-migration/sc01-abap-migration_{{ source.sap.sid }}_{{ target.sap.sid }}/ansible/outputs/Migrate_{{ source.sap.sid }}_{{ target.sap.sid }}/source/{{ profile_param_output }}/PFL_Updated//"
cd <path>
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|
|feature|added role prfile_parameter|20th sep 2023|Pavithra Sathyanarayanan|
|bug fix| changed the name of sap_profile_update to sap_profile_update_os|20th oct 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## References
[Cloud Migrate Developer Team design]

