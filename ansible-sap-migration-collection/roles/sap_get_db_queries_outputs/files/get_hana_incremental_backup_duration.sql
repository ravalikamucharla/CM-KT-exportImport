SELECT TOP 1 ENTRY_TYPE_NAME,SYS_START_TIME,SYS_END_TIME,
	SECONDS_BETWEEN(SYS_START_TIME,SYS_END_TIME) as BACKUP_DURATION_IN_SEC,
	SECONDS_BETWEEN(SYS_START_TIME,SYS_END_TIME)/60 AS BACKUP_DURATION_IN_MIN,
	'success' AS STATUS
	FROM M_BACKUP_CATALOG  where ENTRY_TYPE_NAME in('incremental data backup') 
	ORDER BY SYS_START_TIME DESC;
