# enable_site
This role helps in enabling the primary site.

## Role Variables
The variables to be used within this role are all defined at all.yml,group_vars and host_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|sid|sid of source or target database|yes|
|rep_source_db|primary db physical or virtual hostname|yes|
|primary_host| primary database host name|yes|

## Example Playbook
```yaml
---
- hosts: target_db
  roles:
      - enable_site
```

## checks
On primary database you can validate by running the below command
```
sudo su - sidadm
hdbnsutil -sr_state
```
## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/playbooks/05_2_hsr_migration_target.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/inventory/ansible/inventory)

## Code Update
|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|1st march 2023|Pavithra Sathyanarayanan|
|minor|included new to take enable site hostname|9th march 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]
