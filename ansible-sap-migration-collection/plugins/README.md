# Collections Plugins Directory

This directory can be used to ship various plugins inside an Ansible collection. Each plugin is placed in a folder that
is named after the type of plugin it is in. It can also include the `module_utils` and `modules` directory that
would contain module utils and modules respectively.

Here is an example directory of the majority of plugins currently supported by Ansible:

```
└── plugins
    ├── action
    ├── become
    ├── cache
    ├── callback
    ├── cliconf
    ├── connection
    ├── filter
    ├── httpapi
    ├── inventory
    ├── lookup
    ├── module_utils
    ├── modules
    ├── netconf
    ├── shell
    ├── strategy
    ├── terminal
    ├── test
    └── vars
```

A full list of plugin types can be found at [Working With Plugins](https://docs.ansible.com/ansible/2.10/plugins/plugins.html).

## Code Update

|Type of release(create a new line for each release) - interface breaking(major), feature or minor |Reason for code update|Date|Author|
|---|---|---|---|
|minor|changes for sap_logon_group_smlg,sap_rfc_groups,sap_pyrfc and get_abap_version for multiple app servers|20th dec 2022|Anuja Gangeswari,Sakshi Kaul|
|minor|changes in sap_pyrfc and sap_spad script| 27th feb 2023|Anuja Gangeswari|
|minor|changes in sap_logon_group_smlg|3rd march 2023|Anuja Gangeswari|
|minor|changes in sap_pyrfc,sap_rfc_groups,sap_logon_group_smlg,sap_certificates_export,sap_align_configuration,sap_spad|10th April 2023|Anuja Gangeswari|
|minor| new module SAP_general_login added|10th April 2023|Anuja Gangeswari|
|minor|changes in SAP_general_login|27th april 2023|Anuja Gangeswari|
|minor|changes in get_abap_version|19th june 2023|Anuja Gangeswari|
|minor|updates in sap_pyrfc for default titles for version related scripts|27th june 2023|Anuja Gangeswari|
|minor|updates in sap_pyrfc for title issue|14th july 2023|Anuja Gangeswari|

## License
Accenture use only

## Design
[Cloud Migrate Developer Team design]