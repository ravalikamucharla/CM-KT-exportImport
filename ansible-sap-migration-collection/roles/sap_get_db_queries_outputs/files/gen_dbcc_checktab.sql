use @@servername
go
set nocount on
go
select "dbcc checktable (["+user_name(uid)+'.'+name+'])'+ char(10) + 'go' from sysobjects 
where type IN ('U','S') 
and name not in ('syslogs','sysgams','sysencryptkeys','sysroles')
go
