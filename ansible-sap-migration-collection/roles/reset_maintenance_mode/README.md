# reset_maintenance_mode
This role is used to set the maintenance mode to false.

## Overview
The role performs multiple tasks like 
* restarting the database instance in target cluster system
* setting maintenance mode to false
* cleanup cluster resource

## Requirements:
* The system must be Cluster system.

## Role Variables

The variables to be used within this role are all defined at group_vars level.

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of source or target database|yes|

## Example Playbook

```yaml
---
- hosts: target_slave_db
  roles:
      - reset_maintenance_mode
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/playbooks/05_7_hsr_reset_maintenance_mode.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/inventory/)

## Checks
1.We can validate if maintenance made is set to false by checking if the clusters are in managed state, can run the following command from the any cluster node:
```bash
sudo crm_mon -1
```
2.To validate cleanup, run the following command as sidadm user and check if system replication state online mode is false.
```bash
sudo su - sidadm
hdbnsutil -sr_state
```

## Code Update
|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|25th april 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]
