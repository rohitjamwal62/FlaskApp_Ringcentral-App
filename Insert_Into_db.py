import psycopg2,configparser,time
from Call_Api import call,Active_Call,Get_Call_History
config = configparser.ConfigParser()

config.read('database.ini')
host = config.get('postgresql', 'host')
database = config.get('postgresql', 'database')
user = config.get('postgresql', 'user')
port = config.get('postgresql', 'port')
password = "%dtJkejudi#$3WcVUHK5"

try:
    conn_params = {"host": host,"port": port, "database": database,"user": user,"password":password}
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    call()
    time.sleep(15)
    Get_Call_Records = Active_Call()
    Get_Rc_Call_History = Get_Call_History()
    for calls in Get_Call_Records:
        # Insert into rc_call_history Table
        insert_query = 'INSERT INTO db.rc_call_history ("sessionId","calledExtension","callDirection","callerFrom",cname,"callerTo","callingStatus","recentStatus","callStartTimeUTC","ringingTime","callDuration","customerID","callRecordingUrl","callRecordingId","callStartTimeLocal","dateUpdated") VALUES (%(sessionId)s, %(calledExtension)s, %(callDirection)s,%(callerFrom)s,%(cname)s,%(callerTo)s,%(callingStatus)s,%(recentStatus)s,%(callStartTimeUTC)s,%(ringingTime)s,%(callDuration)s,%(callRecordingUrl)s,%(callRecordingId)s,%(customerID)s,%(callStartTimeLocal)s,%(dateUpdated)s)'
        cur.execute(insert_query,calls[0])
        time.sleep(3)
        # Insert into rc_currentCaller Table
        rc_currentCaller_query = 'INSERT INTO db."rc_currentCaller" ("externalExtension","extensionNumber","callDirection","callerId","calledTo","telephonyStatus","presenceStatus","customerID",cname,"dndStatus") VALUES(%(externalExtension)s,%(extensionNumber)s,%(callDirection)s,%(callerId)s,%(calledTo)s,%(telephonyStatus)s,%(presenceStatus)s,%(customerID)s,%(cname)s,%(dndStatus)s)'
        cur.execute(rc_currentCaller_query,calls[1])
        conn.commit()
        print("Record inserted successfully into re_call_history table")
        
    # Only Call history
    for call_history in Get_Rc_Call_History:
        Call_History_insert_query = 'INSERT INTO db.rc_call_history ("sessionId","calledExtension","callDirection","callerFrom",cname,"callerTo","callingStatus","recentStatus","callStartTimeUTC","ringingTime","callDuration","customerID","callStartTimeLocal","dateUpdated") VALUES (%(sessionId)s, %(calledExtension)s, %(callDirection)s,%(callerFrom)s,%(cname)s,%(callerTo)s,%(callingStatus)s,%(recentStatus)s,%(callStartTimeUTC)s,%(ringingTime)s,%(callDuration)s,%(customerID)s,%(callStartTimeLocal)s,%(dateUpdated)s)'
        cur.execute(Call_History_insert_query,call_history)
        conn.commit()
        print("Record inserted successfully into re_call_history table")
  
    
except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into re_call_history table", error)

finally:
    # closing database connection.
    if conn:
        cur.close()
        conn.close()
        print("PostgreSQL connection is closed")
