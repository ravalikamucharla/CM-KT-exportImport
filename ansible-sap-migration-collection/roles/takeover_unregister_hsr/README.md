# takeover_unregister_hsr
This role is used to unregister the source from target after replication and also helps to takeover the target site as primary site.

Valid profiles are:
* `take_over` - helps in take over of target system  as primary system
* `unregister` - unregisters the system after the replication between source and target is completed.

## Role Variables

The variables to be used within this role are all defined at group_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of source and target database|yes|
|unregister_db|source database name which has to be unregistered|yes|

## Example Playbook
```yaml
---
- hosts: target_db
  roles:
      - takeover_unregister_hsr
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/playbooks/05_4_hsr_disable_replication.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/inventory/)

## Checks
```
sudo su - sidadm
hdbnsutil -sr_state
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|3rd march 2023|Pavithra Sathyanarayanan|
|minor|changes made to take site id to unregister|9th march 2023|Pavithra Sathyanarayanan|
|minor|changes made to take default db name|27th april 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)
