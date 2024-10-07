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



# Hana parmeter changes ( Source primary and Target primary)

|service_ini    | set_mode         |         operation_mode            |  parameter             | Recomended value | replcation_mod |
|---------------|------------------|-----------------------------------|------------------------|------------------|----------------|
|global.ini     |system_replication| logreplay or logreplay_readaccess |  enable_log_retention  |  on | |
|global.ini     |system_replication| logreplay or logreplay_readaccess |logshipping_max_retention_size|204800| - |                        
|global.ini     |system_replication| logreplay or logreplay_readaccess |enable_log_compression  | - | -|
|global.ini     |system_replication| delta_shipping                    |datashipping_snapshot_max_retention_time| 300|=|
|global.ini     |inifile_checker   |                                   | enable                 | true |-|
|global.ini     |inifile_checker   |                                   | replicate              | true |-|
|indexserver.ini|                  | logreplay                         |logshipping_async_buffer_size | 4294967296| async |
|global.ini     |                  | logreplay                         |logshipping_async_wait_on_buffer_full | false| async|
|               |                  |                                   |reconnect_time_interval |300 
| -             | -                |                                   |logshipping_replay_push_persistent_segment_count | 64 |
|               |                  |                                   | logshipping_replay_logbuffer_cache_size | 21474836480 | |
|               |                  |                                   | replay_step_size       | 1073741824 |  |
|               |                  |                                   | propagate_log_retention | on |  |
|               |                  |                                   | register_secondaries_on_takeover|  false |


# hana parameter changes (TARGET)
|service_ini   | set_mode         |         operation_mode       |  parameter            | Recomended value | replcation_mod |
|--------------|------------------|------------------------------|-----------------------|------------------|----------------|
|              |                  |                              |enable_log_retention   |        on        |
|              |                  |                              |enable_log_compression |       true       | 
|              |                  |                              |enable_data_compression|       true       |
|              |                  |                              |propagate_log_retention|       on         |
|              |                  |                              |datashipping_parallel_channels| 8         |
|              |                  |                              |register_secondaries_on_takeover| true    |    



# Network Parameter changes
| Parameter                           |    Current value  |   Recommanded value     |  
| ------------------------------------| ------------------| ----------------------- |
| net.core.somaxconn                  |        4096       |      >=4096             |
| net.core.wmem_max                   |          -        |      20971520           |
| net.core.rmem_max                   |          -        |      20971520           |
| net.ipv4.tcp_max_syn_backlog        |        8192       |       >=8192            |
| net.ipv4.ip_local_port_range        |     40000 65300   |  Check OSS note 2382421 |
| net.ipv4.tcp_slow_start_after_idle  |          0        |          0              |
| net.ipv4.tcp_wmem                   | 4096 16384 262144 |   4096 16384 20971520   |
| net.ipv4.tcp_rmem                   | 4096 87380 6291456|   4096 16384 20971520   |
| net.ipv4.tcp_window_scaling         |          1        |          1              |
| net.ipv4.tcp_timestamps             |          1        |          1              | 
| net.ipv4.tcp_tw_reuse               |          1        |          2              |
| net.ipv4.tcp_syn_retries            |          8        |          5              |