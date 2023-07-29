from flask import Flask, render_template,request,jsonify,redirect, url_for
from datetime import datetime, timedelta
from dateutil import tz
import requests,json,os,time,boto3
from Get_Token import get_access_token
from postredb import create_connection
from Existing_Check import check_file_exists
token = get_access_token()
print(token,"======================================")
headers = {'Authorization': f'Bearer {token}','Content-Type': 'application/json'}
headers_Rec = {'Authorization': f'Bearer {token}','Content-Type': 'audio/x-wav'}
Endpoint = "https://platform.ringcentral.com/restapi/v1.0/account/~/"

app = Flask(__name__)
# It's showing 
@app.route("/")
def home():
    Active_url = f"{Endpoint}active-calls/"
    Actice_response = json.loads(requests.request("GET", Active_url, headers=headers).text)
    Get_Recods = Actice_response.get('records')
    Count_liveCalls = 0
    Active_Call_Count = 0
    queued_callers = 0
    if Get_Recods:
        for i in Get_Recods:
            if i != None:
                # Active Call Count
                Active_Call_Count += 1
                # Live Call Count
                if i.get('result') in ["Call connected"]:
                    Count_liveCalls+=1
                # Queued CAll Count          
                if i["result"] in ["Ringing", "CallConnected"]:
                    queued_callers += 1
    # Count All Recordings
    url = "https://platform.ringcentral.com/restapi/v1.0/account/~/call-log?withRecording=true"
    print(headers_Rec)
    data_got = json.loads(requests.request("GET", url, headers=headers_Rec).text).get('records')
    print(data_got)
    Get_all_Recording_id = [rec for rec in data_got]
    
    Count_Recordings = 0
    for Id in Get_all_Recording_id:
        Count_Recordings +=1
    # Show Call History
    conn = create_connection()
    cur = conn.cursor()
    query = "SELECT * FROM db.rc_call_history"
    cur.execute(query)
    records = cur.fetchall()
    return render_template("index.html",Active_Call_Count=Active_Call_Count,Count_liveCalls=Count_liveCalls,queued_callers=queued_callers,Count_Recordings=Count_Recordings,records=records)
    
@app.route('/calling', methods=['POST','GET'])
def Calling():
    return render_template("calling.html")

@app.route('/admin', methods=['POST','GET'])
def admin():
    return render_template("admin_portal.html")



@app.route('/calling', methods=['POST','GET'])
def Get_Call():
    Call_To = request.form.get('CallFrom')
    url = f"{Endpoint}extension/~/ring-out"
    payload = json.dumps({
        
                    "from": {
                        "phoneNumber": "+13122240518"
                    },
                    "to": {
                        "phoneNumber": f"+1{Call_To}"
                    },
                    "playPrompt": True
                })

    response = json.loads(requests.request("POST", url, headers=headers, data=payload).text)
    Id = response.get('id')
    callerStatus = response.get('status').get('callerStatus')
    return {"Telephony Id":Id,"Caller Status":callerStatus}


@app.route('/Active_Call', methods=['GET'])
def Capture_Active_Calls():
    url = f"{Endpoint}active-calls/"
    response = json.loads(requests.request("GET", url, headers=headers).text)
    Get_Recods = response.get('records')
    # Get Recent Status________
    Recent_url = f"{Endpoint}extension/~/"
    response_presence = json.loads(requests.request("GET", f"{Recent_url}presence", headers=headers).text)
    Recent_Status = response_presence.get('telephonyStatus')
    presenceStatus = response_presence.get('presenceStatus')
    dndStatus = response_presence.get('dndStatus')
    # End___________
    for Active_records in Get_Recods:
        if Active_records:
            try:
                # Convert the given time string into a datetime object
                time_utc = datetime.fromisoformat(str(Active_records.get('startTime')).replace("Z", "+00:00"))
                # Get the local time zone
                local_tz = tz.gettz()
                # # Convert the UTC time to local time
                Call_Start_Time_Local = time_utc.astimezone(local_tz)

                Call_Start_Time_store = list()
                if Active_records.get('duration'):
                    if Active_records.get('duration') >=1:
                        Call_Start_Time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  
                        Call_Start_Time_store.append(Call_Start_Time)
                try:
                    StartTime = Call_Start_Time_store[0]
                except:
                    StartTime = Call_Start_Time_store
                try:
                    Recording_Url = Active_records.get('recording').get('uri')
                    Recording_Id = Active_records.get('recording').get('id')
                except:
                    Recording_Url = "None"
                    Recording_Id = "None"
                try:
                    duration = Active_records.get('duration')
                except:
                    duration = 0
                try:
                    Caller_To = Active_records.get('to').get('phoneNumber')
                except:
                    Caller_To = 0
                try:
                    extension_id = Active_records.get('extension').get('id')
                except:
                    extension_id = 0
                try:
                    Caller_From = Active_records.get('from').get('phoneNumber')
                except:
                    Caller_From = 0

                # Insert Into DB
                Active_Call_Data = {
                        "sessionId": Active_records.get('sessionId'),
                        "calledExtension": extension_id,
                        "callDirection":Active_records.get('duration'),
                        "callerFrom": Caller_From,
                        "cname": Active_records.get('name'),
                        "callerTo": Caller_To,
                        "callingStatus":Active_records.get('result'),
                        "recentStatus":Recent_Status,
                        "callStartTimeUTC": StartTime,
                        "ringingTime":Active_records.get('startTime'),
                        "callDuration": duration,
                        "callStartTimeLocal": Call_Start_Time_Local,
                        "dateUpdated":str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')),
                        "callRecordingUrl" : Recording_Url,
                        "callRecordingId":Recording_Id,  
                    }
                
                # Insert Records into Call History
                conn = create_connection()
                cur = conn.cursor()
                insert_query = 'INSERT INTO db.rc_call_history ("sessionId","calledExtension","callDirection","callerFrom",cname,"callerTo","callingStatus","recentStatus","callStartTimeUTC","ringingTime","callDuration","callRecordingUrl","callRecordingId","callStartTimeLocal","dateUpdated") VALUES (%(sessionId)s, %(calledExtension)s, %(callDirection)s,%(callerFrom)s,%(cname)s,%(callerTo)s,%(callingStatus)s,%(recentStatus)s,%(callStartTimeUTC)s,%(ringingTime)s,%(callDuration)s,%(callRecordingUrl)s,%(callRecordingId)s,%(callStartTimeLocal)s,%(dateUpdated)s)'
                cur.execute(insert_query,Active_Call_Data)
                conn.commit()
                print("Record inserted successfully into re_call_history table")
     
            except:
                print("error")
                pass
    
    # return jsonify(res)0
    return render_template("Active.html",Get_Recods=Get_Recods)


@app.route('/DND_Call', methods=['GET'])
def Capture_Dnd_Calls():
    response_presence = json.loads(requests.request("GET", f"{Endpoint}extension/~/presence", headers=headers).text)
    # Recent_Status = response_presence.get('telephonyStatus')
    # presenceStatus = response_presence.get('presenceStatus')
    dndStatus = response_presence.get('dndStatus')
    # return jsonify(dndStatus)
    return render_template("dnd.html",dndStatus=dndStatus)

@app.route('/Busy_Call', methods=['GET'])
def Capture_Busy_Calls():
    Busy_response = requests.request("GET", f"{Endpoint}extension/~/presence", headers=headers)
    store_Busy_Call = list()
    if Busy_response.status_code == 200:
        presence_data = Busy_response.json()
        Presence_Status = presence_data.get('presenceStatus')
        # Busy Status Check
        if Presence_Status == "Busy":
            Id = presence_data.get('extension').get('id')
            Telephony_Status = presence_data.get('telephonyStatus')
            Presence_Status = Presence_Status
            Active_url = f"{Endpoint}active-calls/"
            Actice_response = json.loads(requests.request("GET", Active_url, headers=headers).text)
            Get_Recods = Actice_response.get('records')
            if Get_Recods:
                for rec in Get_Recods:
                    if rec.get('result') != "Call connected" and Telephony_Status == "CallConnected":
                        store_Busy_Call.append(rec)
    else:
        print(f"Error {Busy_response.status_code}: {Busy_response.text}")
    return render_template("busy.html",call_status_store=store_Busy_Call)


@app.route('/Queued_Calls', methods=['GET'])
def Capture_Queued_Calls():
    response = json.loads(requests.request("GET", f"{Endpoint}active-calls/", headers=headers).text)
    Get_Recods = response.get('records')
    queued_callers = 0
    for i in Get_Recods:
        if i != None:
            # How many Active caller waiting to be answered
            if i["result"] in ["Ringing", "CallConnected"]:
                queued_callers += 1
    print(f"Number of queued callers: {queued_callers}")
    # return jsonify(queued_callers)
    return render_template("queued.html",queued_callers=queued_callers)  

@app.route('/recordings', methods=['GET','POST'])
def Capture_All_Recordings():
    # Capture All Recordings
    url = f"{Endpoint}call-log?withRecording=true"
    Recording_URL = json.loads(requests.request("GET", url, headers=headers_Rec).text).get('records')
    # ______________S3 Bucket Part_______________________
    session = boto3.Session(aws_access_key_id='AKIA2IU7S34G2C6SKYHQ',
                            aws_secret_access_key='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')
    s3 = session.client('s3')
    bucket_name = 'routecallcenter-recordings'
    status = requests.request("GET", url, headers=headers_Rec).status_code #Get Status Code
    if 429 == status:
        print("Reqests limit exceeded")
        time.sleep(180)
    elif 200 == status:
        print("success")
        # Capture All Recordings
        Get_all_Recording_id = [rec.get('recording').get('id') for rec in json.loads(requests.request("GET", url, headers=headers_Rec).text).get('records')]
        for Id in Get_all_Recording_id:
            # Get Recording using Id
            Rec_Url = "https://platform.ringcentral.com/restapi/v1.0/account/~/recording/{Id}/content"
            Store_Rec = requests.request("GET", Rec_Url, headers=headers_Rec)
            folder_path = 'Recording_mp3'
            file_name = Id+'file.mp3'
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, file_name)
            """
            # Write .mp3 file
            with open(file_path, 'wb') as f:
                f.write(Store_Rec.content)
            """
            prefix = 'development/'
            file_exists = check_file_exists(bucket_name, prefix, file_name)

            if file_exists:
                print(f"The file {prefix}{file_name} exists in the {bucket_name} bucket.")
            else:
                # Upload the MP3 file to the specified S3 bucket and key 
                destination_key = f'development/{file_name}'
                upload_bucket = s3.put_object(Body=Store_Rec.content,Bucket= bucket_name,Key=destination_key)
                print(upload_bucket)
                print(f"The file {prefix}{file_name} does not exist in the {bucket_name} bucket.")


    return render_template("rec.html",Recording_URL=Recording_URL)

@app.route('/start-recording', methods=['POST'])
def start_recording():
    url = f"{Endpoint}active-calls/"
    response = json.loads(requests.request("GET", url, headers=headers).text)
    Get_Recods = response.get('records')
    for i in Get_Recods:
        if i != None:
            # _________________Create Recording here_______________________
            Get_TelephonyId = i.get('telephonySessionId')
            Create_Url = f"{Endpoint}telephony/sessions/{Get_TelephonyId}"
            Get_Parties_Id = [parties_id.get('id') for parties_id in json.loads(requests.request("GET", Create_Url, headers=headers).text).get('parties')][0] #Get Party Id
            time.sleep(2)
            response = requests.request("POST", f"{Create_Url}/parties/{Get_Parties_Id}/recordings", headers=headers)
            Get_Recording_Response= json.loads(response.text)
            print("_____________________________",Get_Recording_Response,"________________________")
            if response.status_code == 204:
                return jsonify({"message": "Recording started successfully"})
            else:
                return jsonify({"error": "Failed to start recording"}), 400

@app.route('/live_Call', methods=['GET'])
def Capture_Live_Call():
    url = f"{Endpoint}active-calls/"
    response = json.loads(requests.request("GET", url, headers=headers).text)
    Get_Recods = response.get('records')
    # Get Recent Status________
    Recent_url = f"{Endpoint}extension/~/"
    response_presence = json.loads(requests.request("GET", f"{Recent_url}presence", headers=headers).text)
    Recent_Status = response_presence.get('telephonyStatus')
    presenceStatus = response_presence.get('presenceStatus')
    dndStatus = response_presence.get('dndStatus')
    # End___________
    for Active_records in Get_Recods:
        if Active_records != None:
            try:
                if Active_records.get('result') in ["Call connected"]:
                    # Convert the given time string into a datetime object
                    time_utc = datetime.fromisoformat(str(Active_records.get('startTime')).replace("Z", "+00:00"))
                    # Get the local time zone
                    local_tz = tz.gettz()
                    # # Convert the UTC time to local time
                    Call_Start_Time_Local = time_utc.astimezone(local_tz)

                    Call_Start_Time_store = list()
                    if Active_records.get('duration'):
                        if Active_records.get('duration') >=1:
                            Call_Start_Time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  
                            Call_Start_Time_store.append(Call_Start_Time)
                    try:
                        StartTime = Call_Start_Time_store[0]
                    except:
                        StartTime = Call_Start_Time_store
                    try:
                        Recording_Url = Active_records.get('recording').get('uri')
                        Recording_Id = Active_records.get('recording').get('id')
                    except:
                        Recording_Url = "None"
                        Recording_Id = "None"
                    try:
                        duration = Active_records.get('duration')
                    except:
                        duration = 0
                    try:
                        Caller_To = Active_records.get('to').get('phoneNumber')
                    except:
                        Caller_To = 0
                    try:
                        extension_id = Active_records.get('extension').get('id')
                    except:
                        extension_id = 0
                    try:
                        Caller_From = Active_records.get('from').get('phoneNumber')
                    except:
                        Caller_From = 0

                    # Insert Into DB
                    Active_Call_Data = {
                            "sessionId": Active_records.get('sessionId'),
                            "calledExtension": extension_id,
                            "callDirection":Active_records.get('duration'),
                            "callerFrom": Caller_From,
                            "cname": Active_records.get('name'),
                            "callerTo": Caller_To,
                            "callingStatus":Active_records.get('result'),
                            "recentStatus":Recent_Status,
                            "callStartTimeUTC": StartTime,
                            "ringingTime":Active_records.get('startTime'),
                            "callDuration": duration,
                            "callStartTimeLocal": Call_Start_Time_Local,
                            "dateUpdated":str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')),
                            "callRecordingUrl" : Recording_Url,
                            "callRecordingId":Recording_Id,  
                        }
                    # Insert Records into Call History
                    conn = create_connection()
                    cur = conn.cursor()
                    insert_query = 'INSERT INTO db.rc_call_history ("sessionId","calledExtension","callDirection","callerFrom",cname,"callerTo","callingStatus","recentStatus","callStartTimeUTC","ringingTime","callDuration","callRecordingUrl","callRecordingId","callStartTimeLocal","dateUpdated") VALUES (%(sessionId)s, %(calledExtension)s, %(callDirection)s,%(callerFrom)s,%(cname)s,%(callerTo)s,%(callingStatus)s,%(recentStatus)s,%(callStartTimeUTC)s,%(ringingTime)s,%(callDuration)s,%(callRecordingUrl)s,%(callRecordingId)s,%(callStartTimeLocal)s,%(dateUpdated)s)'
                    cur.execute(insert_query,Active_Call_Data)
                    conn.commit()
                    print("Record inserted successfully into re_call_history table")
            except:
                print("error")
                pass
            else:
                print("No call Active")
    # return jsonify(res)
    return render_template("live_call.html",live_records=Get_Recods)

@app.route('/Stop_rec', methods=['GET','POST'])
def Stop_Recordings():
    Call_fun = "call()"
    Get_TelephonyId = Call_fun.get('id')
    url = "https://platform.ringcentral.com/restapi/v1.0/account/~/extension/~/telephony/sessions/{Get_TelephonyId}/parties/~/recordings/stop"
    response = json.loads(requests.request("POST", url, headers=headers).text)
    print(response)

if __name__ == "__main__":
    app.run(debug=True)