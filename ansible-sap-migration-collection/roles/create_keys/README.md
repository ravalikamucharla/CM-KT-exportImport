# copy_files
This role helps in creating hdbuserstorekey in the database system.

## Role Variables
The variables to be used within this role are all defined at all.yml,group_vars and host_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of source or target database|yes|
|node1|physical hostname of database |yes|
|instance_number|instance number of database|yes|
|db_password|password of SYSTEM DB|yes|

## Example Playbook

```yaml
---
- hosts: source_db/target_db
  roles:
      - create_keys
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/playbooks/05_2_hsr_migration_target.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/inventory/ansible/inventory)

## Checks
1.We can validate by checking:
```bash
sudo su - sidadm
hdbuserstore list
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|27th feb 2023|Pavithra Sathyanarayanan|
|minor|included script to take keys individually for source and target|9th march 2023|Pavithra Sathyanarayanan|
|minor|included script for HA scenario|25th april 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]
