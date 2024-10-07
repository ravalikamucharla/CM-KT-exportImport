# sc03_hsr_ha_migration_sourcesid_targetsid
This scenario is used for HSR method of migration on High availability System.

# Product details
|Specifications|Details|
|---|---|
|Description|HSR migration on HA system|
|Tier|3 tier|
|Database|hana|
|os|linux|
|PYRFC SDK Media file|Local (Media to be copied from BLOB to local disks)|
|Platform|Azure|
|Login Mechanism|sudo| 
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
* 05_1_hsr_migration_source.yml: HSR on source system
* 05_2_hsr_migration_target.yml: HSR on target system
* 05_3_hsr_replication_status.yml: Check the replication status 
* 05_4_hsr_disable_replication.yml: disable replication between source and target
* 05_5_hsr_migration_target_primary.yml: HSR between target primary and target secondary
* 05_6_hsr_replication_status_target.yml: check the replication status on target
* 05_7_hsr_reset_maintenance_mode.yml: set maintainance mode to false on target
* 05_4_scheduling_cut_over.yml: scheduling the cut over at a particular date and time
* 05_5_hsr_disable_replication.yml: desable replication between source and target
* 05_db_hsr_migration.yml: Hana system replication end-to-end execution.
* 06_target_post_migration_basisconfig_export.yml: Selective target export to be executed which will be used by the update scripts(07 playbook)
* 07_a_target_post_migration_basisconfig_validate_update.yml: Update scripts execution
* 07_b_environmental_variable_update.yml: updates enviromental varaibles in target system
* 08_target_post_migration_basisconfig_export_final: Compare scripts execution
* single_script_execution.yml: This playbook is used for execution of single abap script.

Ansible command:
```bash
cd <ansible directory>
ansible-playbook playbooks/05_db_hsr_migration.yml
```

## Code Update
|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|feature|added a scenario|25th april 2023|Pavithra Sathyanarayanan|
|minor|changes in hsr playbooks|27th april 2023|Pavithra Sathyanarayanan|


## License
Accenture use only

## Author Information
[Cloud Migrate Team](https://alm.accenture.com/wiki/display/IACHSTBU/SAP+Cloud+Migrate)

# Design
[Cloud Migrate Developer Team design]