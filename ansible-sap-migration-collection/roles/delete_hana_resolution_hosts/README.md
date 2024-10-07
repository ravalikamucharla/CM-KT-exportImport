# db_start_stop_status
This role is used to delete the hana host resolution parameter in globalini file.

## Role Variables
The variables to be used within this role are all defined at all.yml,group_vars and host_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of source or target database|yes|

## Example Playbook

```yaml
---
- hosts: target_db
  roles:
      - delete_hana_resolution_hosts
```
## check
```bash
#path: /usr/sap/SID/SYS/global/hdb/custom/config/global.ini
cd <path>
check whether system_replication_communication, system_replication_hostname_resolution sections are deleted.
```
## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/playbooks/05_4_disable_replication.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/inventory/ansible/inventory)

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|3rd march 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]
