# SNC_configuration
This role is used to configure SNC and test the connection.(/SAPCAR_1200-70007716.EXE file should be present under /cm_sap_migration/cm-role/SNC_config)

## Role Variables

The variables to be used within this role are all defined at playbook level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|system_cert_name|system certificate name|yes|

## Example Playbook
```yaml
---
- hosts: localhost
  roles:
      - SNC_configuration
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/playbooks/05_4_hsr_disable_replication.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc03_hsr_ha_migration_sourcesid_targetsid/ansible/inventory/)


## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor|Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|18th July 2024|Susmita Karar|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)
