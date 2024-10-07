# sap_db_start_stop
The role is used to start and stop db. It also checks the status after start and stop.

The profile is selected by setting the `action` variable.  Valid profiles are:
* `start` - used for starting the database 
* `stop` - used for stopping the database
* `status` - Helps to check the status

## Role Variables

The variables to be used within this role are all defined at group_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of source or target database|yes|
|instance_no|instance number of database|yes|

## Example Playbook
```yaml
---
- hosts: localhost
  roles:
    - { role: sap_db_start_stop, action: stop }
    - { role: sap_db_start_stop, action: start }
    - { role: sap_db_start_stop, action: status }
```
## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/playbooks/05_2_hsr_migration_target.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/inventory/)

## Checks
Check if the instance status is green and running
```
sudo su - sidadm
sapcontrol -nr <instance_number> -function GetProcessList
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|1st march 2023|Pavithra Sathyanarayanan|
|minor|changes made to start,stop and status files|9th march 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

