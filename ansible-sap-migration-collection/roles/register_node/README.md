# register_node
This role helps in registering source system and target system and set full sync and time travel parameter after registering the node.

Valid profiles are:
* `full_sync` - used to set full sync parameter when replication mode is sync
* `register_node` - register the source and target node
* `time_travel` - set the time travel hana parameter

## Role Variables

The variables to be used within this role are all defined at all.yml,group_vars and host_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of database|yes|
|rep_source_db|physical or virtual hostname of source database system which has to be registered|yes|
|rep_mode|replication mode while registering|yes|
|oper_mode|operation mode while registering|no|
|rep_target_db|physical or virtual hostname of target database system which has to be registered|yes|

### group variables (host_vars)
|variable|info|required?|
|---|---|---|
|instance_number|instance number of target db|yes|

### group variables (all)
|variable|info|required?|
|---|---|---|
|primary_host|physical hostname of source database|yes|
|time_travel_value|value to to set for timetravel|yes|

## Example Playbook
```yaml
---
- hosts: target_db
  roles:
      - register_node
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/playbooks/05_2_hsr_migration_target.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/inventory/ansible/inventory)

## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|1st march 2023|Pavithra Sathyanarayanan|
|minor|added logic to check the status after db instance is started|27th april 2022|Pavithra Sathyanarayanan|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)
