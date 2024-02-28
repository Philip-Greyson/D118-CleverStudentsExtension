"""Script for exporting some info into custom fields in Clever.

https://github.com/Philip-Greyson/D118-CleverStudentsExtension

Does query for students, gets their EL transitioned status and LEP status and outputs it as Y/N
Takes output file and uploads it to Clever via SFTP.

needs oracledb: pip install oracledb --upgrade
needs pysftp: pip install pysftp --upgrade
"""

# importing module
import datetime  # used to get current date for course info
import os  # needed to get environement variables
from datetime import *

import oracledb  # used to connect to PowerSchool database
import pysftp  # used to connect to the Clever sftp server and upload the file

DB_UN = os.environ.get('POWERSCHOOL_READ_USER')  # username for read-only database user
DB_PW = os.environ.get('POWERSCHOOL_DB_PASSWORD')  # the password for the database account
DB_CS = os.environ.get('POWERSCHOOL_PROD_DB')  # the IP address, port, and database name to connect to

#set up sftp login info, stored as environment variables on system
SFTP_UN = os.environ.get('CLEVER_SFTP_USERNAME')
SFTP_PW = os.environ.get('CLEVER_SFTP_PASSWORD')
SFTP_HOST = os.environ.get('CLEVER_SFTP_ADDRESS')
CNOPTS = pysftp.CnOpts(knownhosts='known_hosts')  # connection options to use the known_hosts file for key validation

OUTPUT_FILE_NAME = 'students_ext.csv'  # name of the file used for output
OUTPUT_FILE_DIRECTORY = './extensionfields'  # directory where the file will land on the SFTP server

print(f"Database Username: {DB_UN} |Password: {DB_PW} |Server: {DB_CS}")  # debug so we can see where oracle is trying to connect to/with
print(f'SFTP Username: {SFTP_UN} | SFTP Password: {SFTP_PW} | SFTP Server: {SFTP_HOST}')  # debug so we can see what info sftp connection is using
badnames = ['use','test','teststudent','test student','testtt','testt','testtest']


if __name__ == '__main__':  # main file execution
    with open('custom_log.txt', 'w') as log:  # open the logging file
        startTime = datetime.now()
        startTime = startTime.strftime('%H:%M:%S')
        print(f'INFO: Execution started at {startTime}')
        print(f'INFO: Execution started at {startTime}', file=log)
        with open(OUTPUT_FILE_NAME, 'w') as output:  # open the output file
            print('sis_id,ext.el,ext.flyerconnect', file=output)  # print header line in output file
            try:
                with oracledb.connect(user=DB_UN, password=DB_PW, dsn=DB_CS) as con:  # create the connecton to the database
                    with con.cursor() as cur:  # start an entry cursor
                        print(f'INFO: Connection established to PS database on version: {con.version}')
                        print(f'INFO: Connection established to PS database on version: {con.version}', file=log)
                        # get the student info for students that are currently active and not pre-registered, really just student id number and dcid to pass to other queries
                        cur.execute('SELECT stu.student_number, stu.dcid, stu.first_name, stu.last_name, stu.id, ext.el_transitioned, il.lep FROM students stu\
                        LEFT JOIN u_def_ext_students0 ext ON stu.dcid = ext.studentsdcid\
                        LEFT JOIN s_il_stu_x il ON stu.dcid = il.studentsdcid\
                        WHERE stu.enroll_status = 0 ORDER BY stu.dcid DESC')
                        students = cur.fetchall()  # fetchall() is used to fetch all records from result set and store the data from the query into the rows variable
                        # go through each entry (which is a tuple) in rows. Each entrytuple is a single student's data
                        for student in students:
                            try:
                                if not str(student[2]).lower() in badnames and not str(student[3]).lower() in badnames:  # check first and last name against array of bad names, only print if both come back not in it
                                    print(f'DBUG: Starting student {student[0]} with transitioned: {student[5]} and lep: {student[6]}')
                                    print(f'DBUG: Starting student {student[0]} with transitioned: {student[5]} and lep: {student[6]}', file=log)
                                    idNum = int(student[0])  # what we would refer to as their "ID Number" aka 6 digit number starting with 22xxxx or 21xxxx
                                    stuDCID = str(student[1])
                                    stuID = str(student[4])
                                    transitioned = "Y" if str(student[5]) == "Transitioned" else "N"  # set the output to Y if it has the string of "Transitioned" otherwise N
                                    lep = "Y" if student[6] == 1 else "N"  # convert 0/1/Null to Y/N

                                    # print final values out to output file for each student
                                    print(f'{stuID},{transitioned},{lep}', file=output)
                            except Exception as er:
                                print(f'ERROR while processing student {student[0]}: {er}')
                                print(f'ERROR while processing student {student[0]}: {er}', file=log)
            except Exception as er:
                print(f'ERROR while connecting to PowerSchool or doing query: {er}')
                print(f'ERROR while connecting to PowerSchool or doing query: {er}', file=log)

        try:
            # connect to the Clever SFTP server using the login details stored as environement variables
            with pysftp.Connection(SFTP_HOST, username=SFTP_UN, password=SFTP_PW, cnopts=CNOPTS) as sftp:
                print(f'INFO: SFTP connection to Clever at {SFTP_HOST} successfully established')
                print(f'INFO: SFTP connection to Clever at {SFTP_HOST} successfully established', file=log)
                # print(sftp.pwd) # debug, show what folder we connected to
                # print(sftp.listdir())  # debug, show what other files/folders are in the current directory
                sftp.chdir(OUTPUT_FILE_DIRECTORY)  # change to the extensionfields folder
                # print(sftp.pwd) # debug, make sure out changedir worked
                # print(sftp.listdir())
                # sftp.put(OUTPUT_FILE_NAME)  # upload the file onto the sftp server
                print("INFO: Custom field file placed on remote server")
                print("INFO: Custom field file placed on remote server", file=log)
        except Exception as er:
            print(f'ERROR while connecting or uploading to Clever SFTP server: {er}')
            print(f'ERROR while connecting or uploading to Clever SFTP server: {er}', file=log)

        endTime = datetime.now()
        endTime = endTime.strftime('%H:%M:%S')
        print(f'INFO: Execution ended at {endTime}')
        print(f'INFO: Execution ended at {endTime}', file=log)

