# sc01-abap-migration_sourcesid_targetsid

This scenario is used to execute pre-migration and post migration.

# Product details

Scenario sc01_abap_migration_sourcesid_targetsid is general for all products and Supports:

|Specifications|Details|
|---|---|
|Description|This scenario is used to execute pre-migration and post migration of any SAP product|
|Product|Any SAP|
|Tier|Standard, 2 tier, 3 tier, HA|
|Database|hana,oracle,db2,mssql|
|os|linux,windows,solaris and AIX|
|PYRFC SDK Media file|Local (Media to be copied from BLOB to local disks)|
|Platform|Azure,AWS and GCP|
|Login Mechanism| sudo and dzdo| 
|Virtual Host|Yes|
|sap_type|abap|


# Instructions

* Create a directory cm_sap_migration
* Clone the examples-sap-migration repo
* Copy the main template and rename the sourcesid and targetsid with the respective SID's
* Copy the custom python modules from ansible/plugins/modules to /usr/share/ansible/plugins/modules/
* Fill the details in Inventory
* Run ansible

## Playbooks description:

* 00_abap_prerequisites.yml: Pre-requisites like Pyrfc sdk is installed for abap script execution.
* 01_source_pre_migration_basisconfig_export.yml: ABAP, OS and DB related scripts are executed for pre-migration.
* 02_target_system_build.yml: Target system build(Under development)
* 03_source_pre_migration_rampdown_checks.yml: ABAP scripts will be executed for rampdown checks
* 04_source_pre_migration_rampdown_activities.yml: ABAP scripts will be executed for rampdown activities.
* 05_db_migration.yml: Actual Migration with Export and Import mechanism.
* 06_target_post_migration_basisconfig_export.yml: Selective target export to be executed which will be used by the update scripts(07 playbook)
* 07_a_target_post_migration_basisconfig_validate_update.yml: Update scripts execution
* 07_b_environmental_variable_update.yml: updates enviromental varaibles in target system
* 08_target_post_migration_basisconfig_export_final: Compare scripts execution
* single_script_execution.yml: This playbook is used for execution of single abap script.

Ansible command:
```bash
cd <ansible directory>
ansible-playbook playbooks/01_source_pre_migration_basisconfig_export.yml
```

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|minor|changes to all.yml, group_vars(source_ascs,source_db,target_db), 01_source_pre_migration_basisconfig_export and 08_target_post_migration_basisconfig_export_final| 06 jan 2023|Pavithra Sathyanarayanan|
|minor|added oracle_user, hana_db_name in 01 and 08 playbook and added a new playbook 07_b_environmental_variable_update.yml|2nd feb 2023|Pavithra Sathyanarayanan|
|minor|added sncpartner_name in group_vars and snc_string_name in all.yml|7th April 2023|Jahanavi Golla|
|minor|variabalized ascs instance number to run windows os queries|27th april 2023|Pavithra Sathyanarayanan|


## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

# Design
[Cloud Migrate Developer Team design]