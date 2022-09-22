# Script to export some info into the custom fields in Clever
# Needs to convert the information on whether they have transitioned out of the EL program to Y/N
# As well as convert the LEP 1/0/Null into Y/N
# Then take result and SFTP upload into correct folder on Clever server


# importing module
import oracledb #used to connect to PowerSchool database
import os #needed to get environement variables
import pysftp #used to connect to the Performance Matters sftp site and upload the file

un = 'PSNavigator' #PSNavigator is read only, PS is read/write
pw = os.environ.get('POWERSCHOOL_DB_PASSWORD') #the password for the PSNavigator account
cs = os.environ.get('POWERSCHOOL_PROD_DB') #the IP address, port, and database name to connect to

#set up sftp login info, stored as environment variables on system
sftpUN = os.environ.get('CLEVER_SFTP_USERNAME')
sftpPW = os.environ.get('CLEVER_SFTP_PASSWORD')
sftpHOST = os.environ.get('CLEVER_SFTP_ADDRESS')
cnopts = pysftp.CnOpts(knownhosts='known_hosts') #connection options to use the known_hosts file for key validation

print("Username: " + str(un) + " |Password: " + str(pw) + " |Server: " + str(cs)) #debug so we can see where oracle is trying to connect to/with
print("SFTP Username: " + str(sftpUN) + " |SFTP Password: " + str(sftpPW) + " |SFTP Server: " + str(sftpHOST)) #debug so we can see where oracle is trying to connect to/with
badnames = ['USE','TEST','TESTSTUDENT','TEST STUDENT','TESTTT','TESTT','TESTTEST']

# create the connecton to the database
with oracledb.connect(user=un, password=pw, dsn=cs) as con:
    with con.cursor() as cur:  # start an entry cursor
        with open('students_ext.csv', 'w') as outputfile:  # open the output file
            print("Database connection established: " + con.version)
            print('sis_id,ext.el,ext.flyerconnect', file=outputfile)  # print header line in output file
            # open a second file for the log output
            outputLog = open('custom_log.txt', 'w')
            try:
                print("Connection established: " + con.version, file=outputLog)
                # get the student info for students that are currently active and not pre-registered, really just student id number and dcid to pass to other queries
                cur.execute('SELECT student_number, dcid, first_name, last_name, id FROM students WHERE enroll_status = 0 AND NOT schoolid = 901 ORDER BY dcid DESC')
                rows = cur.fetchall()  # fetchall() is used to fetch all records from result set and store the data from the query into the rows variable
                # go through each entry (which is a tuple) in rows. Each entrytuple is a single student's data
                for entrytuple in rows:
                    try:
                        #print(entrytuple)  # debug
                        print(entrytuple, file=outputLog)  # debug
                        entry = list(entrytuple) #convert the tuple which is immutable to a list which we can edit. Now entry[] is an array/list of the student data
                        if not str(entry[2]) in badnames and not str(entry[3]) in badnames: #check first and last name against array of bad names, only print if both come back not in it
                            idNum = int(entry[0]) #what we would refer to as their "ID Number" aka 6 digit number starting with 22xxxx or 21xxxx
                            stuDCID = str(entry[1])
                            stuID = str(entry[4])
                            #get the custom field saying if they transitioned out of EL
                            cur.execute('SELECT EL_Transitioned FROM U_DEF_EXT_STUDENTS0 WHERE studentsdcid = ' + stuDCID) 
                            transitionResults = cur.fetchall()
                            #get results directly since there should only be one response row for our selection, and one field returned
                            transitioned = "Y" if str(transitionResults[0][0]) == "Transitioned" else "N" #set the output to Y if it has the string of "Transitioned" otherwise N
                            #print(transitioned)  # debug
                            print(transitioned, file=outputLog)  # debug
                            #get the flag of wheteher they are LEP or not
                            cur.execute('SELECT lep FROM S_IL_STU_X WHERE studentsdcid = ' + stuDCID)
                            lepResults = cur.fetchall()
                            # get results directly since there should only be one response row for our selection, and one field returned
                            lep = "Y" if lepResults[0][0] == 1 else "N"
                            #print(lep)  # debug
                            print(lep, file=outputLog)  # debug
                            # print final values out to output file for each student
                            print(stuID + ',' + transitioned + ',' + lep, file=outputfile)
                    except Exception as err:
                        print('Unknown Error on ' + str(entrytuple[0]) + ': ' + str(err))
                        print('Unknown Error on ' + str(entrytuple[0]) + ': ' + str(err), file=outputLog)
            except Exception as er:
                print('High Level Unknown Error: '+str(er))
                print('High Level Unknown Error: '+str(er), file=outputLog)

with pysftp.Connection(sftpHOST, username=sftpUN, password=sftpPW, cnopts=cnopts) as sftp:
    print('SFTP connection established')
    # print(sftp.pwd) # debug, show what folder we connected to
    # print(sftp.listdir())  # debug, show what other files/folders are in the current directory
    sftp.chdir('./extensionfields')  # change to the extensionfields folder
    # print(sftp.pwd) # debug, make sure out changedir worked
    # print(sftp.listdir())
    sftp.put('students_ext.csv') #upload the file onto the sftp server
    print("Custom field file placed on remote server")
    print("Custom field file placed on remote server", file=outputLog)
outputLog.close()