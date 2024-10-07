# cloud_checker_checks
This role is for checking hana mini checks.

## Role variables
The variables to be used within this role are all defined at group_vars level.

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of database|yes|
|hdbuserstore|hdbuserstore key of hana database|yes|
|set_max_table_count|setting max_table_count paratmeter to 0|yes|

## Example playbook
```yaml
---
- hosts: source_db
  roles:
    - hana_mini_checks
```
## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)
