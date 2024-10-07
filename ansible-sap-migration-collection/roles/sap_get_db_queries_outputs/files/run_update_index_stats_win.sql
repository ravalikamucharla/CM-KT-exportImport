use @@servername
go

set nocount on
go

declare c_systabs cursor for select so.name from sysobjects so
where so.type='S' and so.name not in ('syslogs','sysgams','sysdams','sysencryptkeys','sysroles')
go

declare @systablename longsysname, @cmd varchar(511)
open c_systabs
fetch c_systabs into @systablename

while (@@sqlstatus = 0)
begin
  set @cmd = "update index statistics [" || @systablename || "]"
  print "Executing '%1!'", @cmd
  exec (@cmd)
  fetch c_systabs into @systablename
end

close c_systabs
go
deallocate cursor c_systabs
go


declare c_tablename cursor for select so.name, user_name(so.uid) from sysobjects so
where so.type ='U' and
so.name not in ('VBDATA','VBHDR','VBMOD','ARFCRSTATE','ARFCSDATA',
'ARFCSSTATE','QREFTID','TRFCQDATA','TRFCQIN','TRFCQINS','TRFCQSTATE')
go

declare @tablename longsysname, @owner sysname, @cmd varchar(511)
open c_tablename
fetch c_tablename into @tablename, @owner

while (@@sqlstatus = 0)
begin
  set @cmd = "update index statistics " || @owner || ".[" || @tablename || "]"
  print "Executing '%1!'", @cmd
  exec (@cmd)
  fetch c_tablename into @tablename,@owner
end

close c_tablename
go
deallocate cursor c_tablename
go
