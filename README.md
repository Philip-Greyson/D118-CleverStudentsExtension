# D118-CleverStudentsExtension

Script to export a few things into custom fields in Clever.

## Overview

This script is a fairly straightforward exporting of just a couple fields from PowerSchool to custom fields in Clever. An SQL query is done for all active students to get their EL transitioned status and LEP (Low English Proficiency) status, the data is translated to the Y/N format that Clever wants. Then each student is output to a file which is then uploaded to the Clever SFTP server.

## Requirements

The following Environment Variables must be set on the machine running the script:

- POWERSCHOOL_READ_USER
- POWERSCHOOL_DB_PASSWORD
- POWERSCHOOL_PROD_DB
- CLEVER_SFTP_USERNAME
- CLEVER_SFTP_PASSWORD
- CLEVER_SFTP_ADDRESS

These are fairly self explanatory, and just relate to the usernames, passwords, and host IP/URLs for PowerSchool and the Clever SFTP server (provided by them). If you wish to directly edit the script and include these credentials or to use other environment variable names, you can.

Additionally, the following Python libraries must be installed on the host machine (links to the installation guide):

- [Python-oracledb](https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html)
- [pysftp](https://pypi.org/project/pysftp/)

**As part of the pysftp connection to the output SFTP server, you must include the server host key in a file** with no extension named "known_hosts" in the same directory as the Python script. You can see [here](https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html#pysftp-cnopts) for details on how it is used, but the easiest way to include this I have found is to create an SSH connection from a linux machine using the login info and then find the key (the newest entry should be on the bottom) in ~/.ssh/known_hosts and copy and paste that into a new file named "known_hosts" in the script directory.

You will need to change where the LEP information comes from and how it is processed if you are not in IL, as we use the IL demographics table which will not exist on other PowerSchool instances.
You will also need to have the EL transitioned status in a custom field, we use u_def_ext_students0.el_transitioned to store it with the string of "transitioned" if they are no longer in the EL program. If you use a different table and field, you will need to edit the SQL query to match.
Finally, you will also need to have the counselor name and email in a custom field, we use u_studentsuserfields.custom_counselor and .custom_counselor_email. If you use a different table and field, you will need to edit the SQL query to match.

## Customization

The script is pretty barebones and only has the 5 custom fields we want in Clever, but it can be used as a framework for other things you might want. Besides the processing of the fields mentioned above in the requirements section, the script should just work.

- If you want to add any other  fields to the output, you will need to add them to the header, change the SQL query to retrieve them, process them, and them add them to the output line in the same field order as the header row.
