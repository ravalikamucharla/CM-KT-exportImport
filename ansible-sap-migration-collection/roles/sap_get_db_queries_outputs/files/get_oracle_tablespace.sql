set lines 200;
SELECT a.tablespace_name "Tablespace" ,
ROUND (a.bytes_alloc / 1024 / 1024, 2) "Allocated Mb" ,
ROUND (NVL (b.bytes_free, 0) / 1024 / 1024, 2) "Free Mb" ,
ROUND ( (a.bytes_alloc - NVL (b.bytes_free, 0)) / 1024 / 1024, 2) "Used Mb" ,
ROUND ( (NVL (b.bytes_free, 0) / a.bytes_alloc) * 100, 2) "Free %" ,
ROUND (100 - ( (NVL (b.bytes_free, 0) / a.bytes_alloc) * 100), 2) "Used %" ,
ROUND ( (maxbytes / 1048576), 2) "Max Mb",
ROUND (
100
- (NVL (b.bytes_free + (maxbytes - a.bytes_alloc), 0)
/ NVL (maxbytes, 1))
* 100,
2) "Max Used %"
--(SELECT contents FROM dba_tablespaces h WHERE h.tablespace_name = a.tablespace_name) "Contents",
--(SELECT extent_management FROM dba_tablespaces h WHERE h.tablespace_name = a.tablespace_name) "Extent Management",
--(SELECT segment_space_management FROM dba_tablespaces h WHERE h.tablespace_name = a.tablespace_name) "Seg Extent Management"
FROM ( SELECT f.tablespace_name,
SUM (f.BYTES) bytes_alloc,
SUM (
DECODE (f.autoextensible,
'YES', f.maxbytes,
'NO', f.BYTES))
maxbytes
FROM dba_data_files f
GROUP BY tablespace_name) a,
( SELECT f.tablespace_name, SUM (f.BYTES) bytes_free
FROM dba_free_space f
GROUP BY tablespace_name) b
WHERE a.tablespace_name = b.tablespace_name(+)
UNION ALL
SELECT h.tablespace_name,
ROUND (SUM (h.bytes_free + h.bytes_used) / 1048576) megs_alloc,
ROUND (
SUM ( (h.bytes_free + h.bytes_used) - NVL (p.bytes_used, 0))
/ 1048576)
megs_free,
ROUND (SUM (NVL (p.bytes_used, 0)) / 1048576) megs_used,
ROUND (
(SUM ( (h.bytes_free + h.bytes_used) - NVL (p.bytes_used, 0))
/ SUM (h.bytes_used + h.bytes_free))
* 100)
pct_free,
100
- ROUND (
(SUM ( (h.bytes_free + h.bytes_used) - NVL (p.bytes_used, 0))
/ SUM (h.bytes_used + h.bytes_free))
* 100)
pct_used,
ROUND (SUM (f.maxbytes) / 1048576) MAX, NULL
--i.contents "Contents",
--i.extent_management "Extent Management",
--i.segment_space_management "Seg Extent Management"
FROM SYS.v_$temp_space_header h,
SYS.v_$temp_extent_pool p,
dba_temp_files f,
dba_tablespaces i
WHERE p.file_id(+) = h.file_id
AND p.tablespace_name(+) = h.tablespace_name
AND h.tablespace_name = i.tablespace_name
AND f.file_id = h.file_id
AND f.tablespace_name = h.tablespace_name
GROUP BY h.tablespace_name
--i.contents,
--i.extent_management,
--i.segment_space_management
ORDER BY 1 ASC;
EXIT;