# ftp_setup
This role helps in installing and configuring FTP.

## Role Variables
The variables to be used within this role are all defined at all.yml,group_vars and host_vars level

### group variables (group_vars)
|variable|info|required?|
|---|---|---|
|user_file|user file to store the user details|yes|
|ftp_usr_name|ftp user name|yes|
|ftp_dir| ftp directory |yes|

## Example Playbook
```yaml
---
- hosts: target_db
  roles:
      - ftp_setup
```

## checks
In source db to check the connection - Linux
``
ftp <ip>
Name: ftpuser
password: *******
``

## Example playbook
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/sc06_export_import_ftp_mig_sourcesid_targetsid/ansible/playbooks/05_2_hsr_migration_target.yml)

## Example inventory
See: [Examples Repo](https://innersource.accenture.com/projects/IASC/repos/examples-sap-migration/browse/sc06_export_import_ftp_mig_sourcesid_targetsid/ansible/inventory/ansible/inventory)

## Code Update
|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|

## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

## Design
[Cloud Migrate Developer Team design]
