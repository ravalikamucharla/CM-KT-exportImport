#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# this is a windows documentation stub, actual code lives in the .ps1
# file of the same name

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'cloud builder'}

DOCUMENTATION = r'''
---
module: win_sap_install
version_added: '2.9'
short_description: Runs SAP install on Windows
description:
- Allows you to install SAP via sapinst.exe.
options:
  arguments:
    description:
    - Arguments to be passed to sapinst.exe.
    type: str
    required: yes
  checks:
    description:
    - Checks that should be carried during installation
    - Actions that should be performed based on the result of a check
    type: list
    elements: dict
    required: no
    options:
      action:
        description:
        - Action to perform
        type: str
        choices:
          - stop_sapinst
        required: yes
      path:
        description:
        - Path to a file to search for a pattern.
        - If no file path given it will look in the SAPINST_CWD path.
        - required for C(type=file)
        type: str
        required: no
      regex:
        description:
        - Regular expression to search for in the file
        - required for C(type=file)
        type: str
        required: no
      state:
        description:
        - State of the SAP deployment.
        type: str
        choices:
          - present
        default: present
      type:
        description:
        - Type of check to perform.
        type: str
        choices:
          - file
        required: yes
  delay:
    description:
    - Initial delay after starting sapinst.exe process.
    type: int
    required: no
    default: 30
  path:
    description:
    - Path to the SAP sapinst.exe installation executable.
    type: str
    required: yes
  sleep:
    description:
    - Number of seconds to sleep between checks.
    type: int
    default: 30
  timeout:
    description:
    - The maximum number of seconds to wait for.
    type: int
    default: 3600

notes:
- This module uses is a wrapper to the sapinst.exe SAP installation tool
author:
- Tony Skidmore (anthony.skidmore@accenture.com)
'''

EXAMPLES = r'''
- name: Perform a SAP installation
  win_sap_install:
    path: F:\SilentInstall\SWPM10SP24\sapinst.exe
    arguments: >-
      SAPINST_INPUT_PARAMETERS_URL=F:\SilentInstall\DBInifile.params
      SAPINST_CWD=F:\SilentInstall\DBLogs
      SAPINST_EXECUTE_PRODUCT_ID=NW_ABAP_ASCS:NW750.MSS.CP
      SAPINST_SKIP_DIALOGS=true
      SAPINST_START_GUI=false
      SAPINST_START_GUISERVER=false

- name: Perform a SAP installation with checks
  win_sap_install:
    path: F:\SilentInstall\SWPM10SP24\sapinst.exe
    arguments: >-
      SAPINST_INPUT_PARAMETERS_URL=F:\SilentInstall\DBInifile.params
      SAPINST_CWD=F:\SilentInstall\DBLogs
      SAPINST_EXECUTE_PRODUCT_ID=NW_ABAP_ASCS:NW750.MSS.CP
      SAPINST_SKIP_DIALOGS=true
      SAPINST_START_GUI=false
      SAPINST_START_GUISERVER=false
    checks:
      - type: file
        path: sapinst.log
        regex: "AddPrivileges was executed with status ERROR"
        action: stop_sapinst

'''

RETURN = r'''
arguments:
  description: The command line arguments passed to sapinst.exe
  type: string
  sample: "SAPINST_INPUT_PARAMETERS_URL=F:\\SilentInstall\\ASCSInifile.params SAPINST_CWD=F:\\SilentInstall\\ASCSLogs"
checks:
  description: The list of dicts passed as checks to perform
  type: list
  sample: [
            {
                "action": "stop_sapinst",
                "path": "sapinst.log",
                "regex": "AddPrivileges was executed with status ERROR",
                "type": "file"
            }
          ]
cwd:
  description: The value derived from the SAPINST_CWD parameter passed in arguments
  type: string
  sample: "F:\\SilentInstall\\ASCSLogs"
elapsed:
  description: The length in seconds of the module execution time 
  type: int
  sample: 534
path:
  description: The path of the sapinst.exe installation executable passed in the path argument
  type: string
  sample: "F:\\SilentInstall\\SWPM10SP24\\sapinst.exe"
result:
  description: Result for the operation
  type: str
  sample: "SAP installation suceeded"

'''