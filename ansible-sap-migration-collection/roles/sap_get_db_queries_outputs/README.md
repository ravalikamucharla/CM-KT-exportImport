# sap_get_db_queries_outputs
This role executes different database queries like Hana, Sybase, Oracle, SQL and DB2 

TO execute database related queries profile is selected by setting the `db_type` variable.  Valid profiles are:
* `db2.yml` - used to execute queries related to db2 database 
* `hana.ymk` - used to execute queries related to hana database
* `oracle_linux_sudo` - used to execute queries related to oracle linux database
* `oracle_windows` - used to execute queries related to oracle windows database
* `sql` - used to execute queries related to sql database
* `sybase` - used to execute queries related to sybase database

## Overview

The configuration of sap_get_db_queries_outputs involves a number of steps (at a high level):
Based on db_type variable, it will get invoked to required sub-tasks.
 
- Execute db queries
- Storing outputs in a JSON format and text formats.

## Requirements:

 The Pre-requisites for this role are:

* For DB port 3xx13 or 3xx15 must be open
* To connect to linux 22 port must be open

# Role Variables

The variables to be used within this role are all defined at all.yml,group_vars and host_vars level

# group_vars

|varible|info|required?|
|---|---|---|
|db_type|type of db installed|yes|
|sid|sid of db install|yes|
|sap_schema_owner_hana|required schema name for row count|yes|
|default_table_name|required table name for row count|yes|
|sql_db_host|required when db type is sql|yes|
|sql_db_username|required when db type is sql|yes|
|sql_db_password|required when db type is sql|yes|
|sql_db_name|required when db type is sql|yes|
|sql_db_port|required when db type is sql|yes|


## Dependencies

- For Oracle system make sure sql plus component should be there.


## Example Playbook

```yaml
---
- hosts: source_db:target_db
  roles:
      - sap_get_db_queries_outputs
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/playbooks/01_source_pre_migration_basisconfig_export)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/inventory)

## Checks
Check if json and text files are created in the respective path
```bash
# path- /cm_sap_migration/examples-sap-migration/sc01-abap-migration_{{ source.sap.sid }}_{{ target.sap.sid }}/ansible/outputs//Migrate_{{ source.sap.sid }}_{{ target.sap.sid }}/(source/target)/db_export/"
cd <path>
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|minor|changes in sql command in hana and oracle db files|27th jan|Pavithra Sathyanarayanan|
|minor|added format as input for hana queries, new script added for hdb info and hana service|8th feb 2023|Jahanavi golla|
|minor|changes in hana_db_info,log_backup_duration, hana service templates|10th feb 2023|Jahanavi Golla|
|minor|changes in differential_backup_duration template and hana.yml task|10th April 2023|Jahanavi Golla|
|minor|changes in get_hana_differential_backup_duration and get_hana_log_backup_duration templates|27th april 2023|Pavithra Sathyanarayanan|
|minor|removed python module and executing sql commands with ansible(sql.yml) and included sql_commands_output template|19th june 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## References
[Cloud Migrate Developer Team design]
1. Ticket reference: https://alm.accenture.com/jira/browse/ACNCSSPR-842

