# set_network_params
This role is used to set the network parameters on source and target based on user requirement.

The network parameters is set on respective hosts by setting the `set_params_on` variable.  Valid profiles are:
* `source_network_params` - this profile sets the parameters on source
* `target_network_params` - this profile sets the parameters on target

## overview
The setting of network parameters involves a number of steps (at a high level):
* Taking backup of ipv4, ipv6 and core network files
* Set the network values for ipv4, ipv6 and core.

## Requirements 
By default all the network params mentioned in all.yml will be set. Make sure all those values are required else comment.

## Role Variables

The variables to be used within this role are all defined at group_vars level

### group variables (all)
|variable|info|required?|
|---|---|---|
|source_network_params.ipv4_values|network values that needs to be set on ipv4|yes|
|source_network_params.core_values|network values that needs to be set on care|yes|
|source_network_params.ipv6_values|network values that needs to be set on ipv6|yes|
|item.file_name|file name of ipv4/ipv6/core network for which the value has to be changed|yes|
|item.value|value of the network|yes|

## Example Playbook
```yaml
---
- hosts: source_db
  roles:
      - { role: set_network_params, set_params_on: source, when: source_network_params.required == "yes" }
```

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/playbooks/05_1_hsr_migration_source.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc02_standard_hsr_migration_sourcesid_targetsid/ansible/inventory)

## Checks
Check if network parameter value is set correctly for the respective network files
```bash
# path- /proc/sys/net/ipv4/file_name, /proc/sys/net/core/file_name
cd <path>
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major),feature or minor,bugfix or patch|Reason for code update|Date|Author|
|---|---|---|---|
|feature|adding a role|27th feb 2023|Pavithra Sathyanarayanan|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)
