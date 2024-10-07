# backups
This role is used to take backups for hana system.

The backup type is selected by setting the `backup_type` variable.  Valid profiles are:
* `file_backup` - takes file/log backup in the defined path 
* `on_demand_backup` - backup is taken in Azure portal(Azure recovery vault)
* `third_party_backup` - used to take backup with the help of third party tools.

## Requirements:

 The Pre-requisites for this role are:

* Backup directory must be present in source system before taking backup.
* The directory must contain read, write and execute permissions.

## Role Variables

The variables to be used within this role are all defined at group_vars level

### group variables (common)
|variable|info|required?|
|---|---|---|
|instance_number|instance number of database|yes|
|sid|sap sid of source or target|yes|
|db_password|password for SYSTEM DB|yes|
|tenant_db|tenant database of the DB system|yes|
|hana_hsr_path|path where system backup has to be taken|yes|
|hana_hsr_path_tent|path where tenant backup has to be taken|yes|
|vault_name|vault name where system and tenant db is registered for source or target|yes|
|resource_group|resource group name of database system|yes|
|retain_backup|number of days until when the backup has to be retained|yes|
|backup_start_date|date when the backup was executed|yes|

## Dependencies
Taking backup of third party tools will work only when the tool is properly configured.

## Example Playbook
```yaml
---
- hosts: source_db
  roles:
      - backups
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/playbooks/05_1_hsr_migration_source.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/inventory)

## Checks
Check if backup files are created in the respective path
```bash
# path- /hana/backup/data/SYSTEMDB, /hana/backup/data/DB_SID
cd <path>
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|27th feb 2023|Pavithra Sathyanarayanan|


## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)
