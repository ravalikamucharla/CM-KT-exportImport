# environment_variable_update
This role compares the environment variable in source and target and updates the enviroment variable in target.

The  profile is selected by os_type variable.  Valid profiles are:
* `lin_env_update` - updates environment variable in linux systems  
* `win_env_update` - updates environment variable in windows systems
* `windows_registry` - updates environment variable in windows systems

## Role Variables

The variables to be used within this role are all defined at all.yml,group_vars and host_vars level

### group variables (all)
|variable|info|required?|
|---|---|---|
|python_interpreter|path of python interpreter of target server|yes|
|source.sap.sid|sid of source system|yes|
|source_hostip|ip of source system|yes|
|env_var_update.env_user.source|username for source system|yes|
|passwords.env_update.source|password of source system|yes|
|target.sap.sid|sid of target system|yes|
|target_hostip|ip of target system|yes|
|env_var_update.env_user.target|username for target system|yes|
|passwords.env_update.target|password of target system|yes|
|env_pem_file_path|path of pem file if it is pemfile authentication|yes|

## Example Playbook
```yaml
---
- hosts: localhost
  roles:
      - environment_variable_update
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/playbooks/07_b_environmental_variable_update)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/inventory)

## Code Update
|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)
