# abap_prereqs
This role is being used to install SAP NW RFC SDK.

## Role variables
The variables to be used within this role are all defined at all.yml level

### group variables (common)
|variable|info|required?|
|---|---|---|
|pyrfc.url|url to be used for downloading|yes|
|pyrfc.file_name|file_name to be used for installation|yes|

## Example Playbook
```yaml
---
- hosts: localhost
  roles:
      - abap_prereqs
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/playbooks/01_abap_prerequisites.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc01-abap-migration_sourcesid_targetsid/ansible/inventory)

## Checks
We can validate by checking if the scripts and outputs folder are created:
* check if sap folder is created in /usr/local/
* check if nwrfc750P_6-70002752.zip is present in /usr/local/sap
* check if libraries are installed ldconfig -p | grep sap

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]