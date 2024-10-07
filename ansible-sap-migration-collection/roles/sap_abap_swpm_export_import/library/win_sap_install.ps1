#!powershell

#AnsibleRequires -CSharpUtil Ansible.Basic

Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'

$spec = @{
    options = @{
        arguments = @{ type = "str"; required = $true }
        checks = @{
            type = "list"
            elements = "dict"
            options = @{
                action = @{ type = "str"; required = $true; choices = @("stop_sapinst") }
                type = @{ type = "str"; required = $true; choices = @("file") }
                path = @{ type = "str" }
                regex = @{ type = "str" }
            }
            required_if = @(,@( "type", "file", @("path", "regex")))
        }
        delay = @{ type = "int" ; default = 30 }
        path = @{ type = "str"; required = $true }
        sleep = @{ type = "int"; default = 30  }
        state = @{ type = "str"; choices = @("present"); default = "present" }
        timeout = @{ type = "int"; default = 3600  }
    }
    supports_check_mode = $false
}

$module = [Ansible.Basic.AnsibleModule]::Create($args, $spec)

$arguments = $module.Params.arguments
$checks = $module.Params.checks
$delay = $module.Params.delay
$path = $module.Params.path
$sleep = $module.Params.sleep
$timeout = $module.Params.timeout

$module.Result.changed = $false
$module.Result.path = $path

if(Get-Variable -Name checks -ErrorAction Ignore) { $module.Result.checks = $checks }


function Start-SapInst($path, $arguments) {

    # check that the sapinst.exe is in the supplied location
    if(-not(Test-Path -Path $path)) {
        $module.FailJson("win_sap_install: Could not find sapinst.exe at this location $path")
    }

    # start the sapinst.exe installation program
    # this will just initiate the process and it will continue to run asynchronously
    try {
        Start-Process $Path -ArgumentList $Arguments -ErrorAction Stop
        $module.Result.changed = $true
    } catch {
        $module.FailJson("win_sap_install: sapinst.exe execution error: $($_.Exception.Message)")
    }

}

# split out input arguments into a hashtable for ease of reference
function Get-SapArguments() {
    # split on any whitespace
    # stray spaces in the arguments definition could cause issues
    # if trying to split on single space
    $args = $arguments -split '\s+'
    $ht = @{}
    foreach ($arg in $args) {
        $key, $value = $($arg.split('='))[0..1]
        $ht[$key] = $value
    }

    $ht
}

# function to join hashtable back to a space separated string
# sapinst is sensitive to multiple spaces so ensure we handle
# that by splitting out the hashtable into a single spaced string
function Join-SapArguments() {
    Param(
        [hashtable]
        $InputObject
    )

    $stringArray = $InputObject.GetEnumerator() | ForEach-Object { "$($_.Name)=$($_.Value)" }
    $stringArray -join ' '

}

# currently only supports the 'stop_sapinst' action but could be extended if needed
function Set-FileType {
    Param(
        $Check
    )

    if(Test-FileType -Check $Check) {

        switch -regex ($check.action) {

            'stop_sapinst' { Stop-SAPProcess }
        }
    }

}

function Test-FileType {
    Param (
        $Check
    )

    # default to log path if not fully qualified
    if(-not([System.IO.Path]::IsPathRooted($Check.path))) {
        $filePath = Join-Path -Path $sapLogPath -ChildPath $Check.path
    } else {
        $filePath = $Check.path
    }

    # do not fail if file is not present yet
    # if(-not (Test-Path -Path $filePath)) {
    #     $module.FailJson("Cannot find file $($filePath)")
    # }

    try {
        if(Test-Path -Path $filePath) {
            $search = Select-String -Path $filePath -Pattern $Check.regex -AllMatches -ErrorAction Stop
        }
    }
    catch {
        if( $_.Exception.message -notlike "Cannot find path*") {
            $module.FailJson("Failed to test for $($Check.regex) in $($filePath):  $($_.Exception.Message)")
        }
    }

    if(Test-Path -Path $filePath) {
        if($null -eq $search) {
            $false
        } else {
            $true
        }
    } else {
        $false
    }

}

function Stop-SAPProcess {

    try {
        Stop-Process -Name sapinst -Force -Confirm:$false -ErrorAction Ignore
    }
    catch {
        if( $_.Exception.message -notlike "Cannot find a process with the name*") {
            $module.FailJson("Failed to stop sapinst process:  $($_.Exception.Message)")
        }
    }

    $module.FailJson('The sapinst process was forcibly stopped')

}

# currently only supports the 'file' type but could be extended if needed
function Start-Check {
    foreach($check in $checks) {

        switch -regex ($check.type) {
            'file' { Set-FileType -Check $check }
        }

    }
}

# capture module initialization datetime
$module_start = Get-Date

$sapArgs = Get-SapArguments
if($sapArgs['SAPINST_CWD']) {
    $sapLogPath = $sapArgs['SAPINST_CWD']
} else {
    $module.FailJson("Failed to detect SAPINST_CWD install parameter")
}

# it seems that the sapinst program is sensitive to multiple spaces
# so if someone inadventently introduces a ouble space anywhere installation
# will not work correctly, so parse $sapArgs to reconstruct single spaced arguments
$argsParsed = Join-SapArguments -InputObject $sapArgs
$module.Result.arguments = $argsParsed

# create the log path from the SAPINST_CWD if it does not already exist
if(-not(Test-Path $sapLogPath)) {
    try {
        [void](New-Item -Path $sapLogPath -ItemType Directory -ErrorAction Stop)
    }
    catch {
        $module.FailJson("Failed to create $($sapLogPath):  $($_.Exception.Message)")
    }
}

# start the sapinst process with the supplied arguments
Start-SapInst -path $path -arguments $argsParsed

# trigger an initial delay for the sapint process to initialize
Start-Sleep -Seconds $delay

# initialize variable for setting whether the sapinst process has been completed
$complete = $false

# loop until expected condition or timeout is reached
while (((Get-Date) - $module_start).TotalSeconds -lt $timeout) {

    if(Get-Variable -Name checks -ErrorAction Ignore) {
        Start-Check
    }

    if((-not (Get-Process -Name sapinst -ErrorAction SilentlyContinue)) -and
      ((Test-Path -Path "$sapLogPath\INSTANA.XML"))) {
        $complete = $true
        break
    }

    Start-Sleep -Seconds $sleep
}

if($complete -eq $false) {
    $module.FailJson("Failed to complete within the timeout")
}

if(Test-Path -Path "$sapLogPath\installationSuccesfullyFinished.dat") {
    $module.Result.result = "SAP installation succeeded"
}
else {
    $module.FailJson("SAP installation failed")
}

# add elapsed time to the result
$module.Result.elasped = [math]::Round(((Get-Date) - $module_start).TotalSeconds)
# add the detected SAP_CWD to the result
$module.Result.cwd = $sapLogPath

$module.ExitJson()
