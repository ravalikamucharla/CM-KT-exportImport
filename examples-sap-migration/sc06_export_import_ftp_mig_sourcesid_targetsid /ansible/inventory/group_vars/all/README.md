# Note
The example vault.yml is encrypted with the password "Accenture01" - please use something more secure for actual customer client secrets 

# Key commands
Create a vault file
```bash
ansible-vault create vault.yml
```

Edit a vault file
```bash
ansible-vault edit vault.yml
```

Encrypt and existing file
```bash
ansible-vault encrypt vault.yml
```

Running ansible commands which need to access the secrets, just add
```bash
--ask-vault-pass
```

Read more: https://docs.ansible.com/ansible/latest/user_guide/vault.html

# SMIGR

| DB system | DB version |
|-----------|-----------|
| mssql | sql server 2008 (R2) (max, 1000 partions) |
| mssql | sql server 2008 (R2) (unlimited partions) |
| mssql | sql server 2012 |
| mssql | sql server 2012 (all row-store) |
| mssql | sql server 2012 (all cloumn-store) |
| mssql | sql server 2014 |
| mssql | sql server 2014 (all cloumn-store) |
| mssql | sql server 2016 |
| mssql | sql server 2016 (all cloumn-store) |
| mssql | sql server 2016 (all cloumn-store,unlimited partions) | 
| oracle | special option: Generate DDL's with COMPRESSION |
| oracle | special option: Generate DDL's for tables | 
| oracle | special option: Gen. Indexes without COMPRESSION |
| oracle | special option: Generate DDL's without HCC | 
| oracle | oracle In-memory option disabled |
| oracle | oracle In-memory option enabled |
| syb | Default: no special option |
| syb | special oprion: use parallel index creation |
| DB2-z/os | DB2 settings |
| DB2-z/os | BI settings |
| DB2-z/os | version 8 |
| DB2-z/os | version 9 |
| DB2-z/os | version 10 or higher |
| DB2-z/os | version 8, BI settings |
| DB2-z/os | version 9, BI settings |
| DB2-z/os | version 10 or higher, BI settings |
| DB400 | DB version with Partioning |
| DB400 | DB version without Partioning |
| DB6 | Use Multidimentional Clustering (MDC) for BW |
| DB6 | Use BLU Accelaration for BW (< Db2 11.01.0303) |
| DB6 | Use BLU Accelaration for BW (>= Db2 11.01.0303) |
| DB6 | Use BW basic Table Layout |
| DB6 | Use BLU for BW infocubes |
| DB6 | Use BLU for BW infocubes incl.infoobjecta |
| DB6 | Use BLU for all eligible BW objects |
| DB6 | Compress all tables, Use MDC for BW |
| DB6 | Compress all tables, Do not use MDC for BW |
| DB6 | Compress BW facts/DSO/PSA tables, Use MDC |
| DB6 | Compress BW facts/DSO/PSA tables, Do not use MDC |
| DB6 | DO not compress But use MDC for BW |
| DB6 | DO not compress and do not use MDC for BW |
