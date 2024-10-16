# exp_imp_prechecks
This role is used to perform checks on source and target before export import method of migration

The profile is selected by setting the `mode` variable.  Valid profiles are:
* `source` - used for pre-migration checks 
* `target` - used for ramp-down checks
* `compare` - used for ramp-down activities

## Overview

The steps involves:
* executing commands in source
* executing commands in target 
* comparing results of source and target and creating a report in md, json and excel format.

## Role Variables

The variables to be used within this role are all defined at all.yml,group_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of database|yes|
|instance_number|instance number of database|yes|

### group variables (common)
|variable|info|required?|
|---|---|---|
||app_sid|ascs or pas SID|yes|

### group variables (all)
|variable|info|required?|
|---|---|---|
|exp_imp_prechecks.prechecks_output_path|outputh path|yes|
|exp_imp_prechecks.source_file_path|path to store outputs generated from executing commands in source|yes|
|exp_imp_prechecks.target_file_path|path to store outputs generated from executing commands in target|yes|
|exp_imp_prechecks.output_format|output file format|yes|
|exp_imp_prechecks.expdir|export directory|yes|
|exp_imp_prechecks.impdir|import directory|yes|
|exp_imp_prechecks.export_dir_size_src|export directory size|yes|
|exp_imp_prechecks.data_transfer_type|data transfer protocol between source and target db|yes|
|exp_imp_prechecks.oracle_lister_port_source|oracle lister port in source system|no|

## Example Playbook
```yaml
---
- hosts: source_db
  roles:
      - exp_imp_prechecks
```

## Checks
Check if the output file is generated in the below path(output format json or excel)
```bash
# path- /cm_sap_migration/examples-sap-migration/sc01-abap-migration_{{ source.sap.sid }}_{{ target.sap.sid }}/ansible/outputs/exp_imp_prechecks"
cd <path>
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding role exp_imp prechecks|7th aug 2023|Susmita Karar|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## References
[Cloud Migrate Developer Team design]
