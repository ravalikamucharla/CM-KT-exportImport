# port_status_check
This role is being used to check whether the port is open or not.

## Role variables
The variables to be used within this role are all defined at all.yml level

### group variables (common)
|variable|info|required?|
|---|---|---|
|hostip|ip of database|yes|
|db_port|port of database|yes|

## Example Playbook
```yaml
---
- hosts: sourec_db/target_db
  roles:
      - port_status_check
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/playbooks/05_1_hsr_migration_source.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/inventory)

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|27th feb 2023|Pavithra Sathyanarayanan|
|minor|included curl command to check the port status|9th march 2023|Pavithra Sathyanarayanan|
|minor|removed netcat installation steps|26th april 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]