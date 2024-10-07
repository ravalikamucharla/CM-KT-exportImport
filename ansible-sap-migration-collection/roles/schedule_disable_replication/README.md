# sap_abap_execute_queries
The role is used to schedule task on user defined date and time.

## Prequisites:
* Make sure to provide the server date and time before excuting this task.

## Role Variables

The variables to be used within this role are all defined at all.yml level

### group variables (all)
|variable|info|required?|
|---|---|---|
|topology|sap logon user|yes|

## Example Playbook
```yaml
---
- hosts: localhost
  roles:
      - schedule_disable_replication
```
## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/playbooks/05_5_sceduling_cut_over.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/inventory)

## Code Update
|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|3rd march 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## References
[Cloud Migrate Developer Team design]

1. Ticket reference: https://alm.accenture.com/jira/browse/ACNCSSPR-68

