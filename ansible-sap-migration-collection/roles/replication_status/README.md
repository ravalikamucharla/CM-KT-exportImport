# replication_status
This role is used to check the replication status of system replication.

## Requirements:
* Ensure that source and target node is registered/register node role is executed.

## Role Variables
The variables to be used within this role are all defined at group_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of source or target database|yes|


## Example Playbook
```yaml
---
- hosts: source_db
  roles:
      - replication_status
```

## checks
On primary database you can validate by running the below command
```
sudo su - sidadm
cdpy
python systemReplicationStatus.py
```
## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/playbooks/05_3_hsr_replication_status.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/inventory/ansible/inventory)

## Code Update
|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|1st march 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]
