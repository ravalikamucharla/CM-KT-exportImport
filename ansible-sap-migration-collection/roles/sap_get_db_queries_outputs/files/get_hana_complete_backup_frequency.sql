select TOP 1 FREQUENCY_OF_BACKUP_IN_DAYS,count(FREQUENCY_OF_BACKUP_IN_DAYS) as OCCURENCES,'success' as STATUS from
	(select ENTRY_TYPE_NAME,SYS_START_TIME,lag(sys_start_time) over(order by sys_start_time) as PREVIOUS_START_TIME,
	SECONDS_BETWEEN(SYS_START_TIME,SYS_END_TIME) as BACKUP_DURATION_IN_SEC,
	SECONDS_BETWEEN(SYS_START_TIME,SYS_END_TIME)/60 as BACKUP_DURATION_IN_MIN,
	days_between(lag(sys_start_time)over(order by sys_start_time),sys_start_time) as FREQUENCY_OF_BACKUP_IN_DAYS
	FROM M_BACKUP_catalog where ENTRY_TYPE_NAME in('complete data backup')  
	ORDER BY  sys_start_time desc) group by frequency_of_backup_in_days order by OCCURENCES desc;
