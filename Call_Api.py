import psycopg2,json,requests,time,os
from Get_Token import Token_List
print(Token_List,"++++++++++++++++++++++++")
from datetime import datetime, timedelta
from dateutil import tz
Main_Header = {'Authorization': f'Bearer {Token_List[0]}','Content-Type': 'application/json'}
Endpoint_Url = "https://platform.ringcentral.com/restapi/v1.0/account/~/"

def call():
    # payload = json.dumps({"from": {"phoneNumber": "+14243165330"},"to": {"phoneNumber": "+18474776562"},"playPrompt": False})
    #  payload = json.dumps({"from": {"phoneNumber": "+14243165330"},"to": {"phoneNumber": "+18474776562"},"playPrompt": True})
    payload = json.dumps({"from": {"phoneNumber": "+14243165330"},"to": {"phoneNumber": "+918988071732"},"playPrompt": True})
    response = json.loads(requests.request("POST", f"{Endpoint_Url}extension/~/ring-out", headers=Main_Header, data=payload).text)
    return response

def Active_Call():
    print("yes")

    url = f"{Endpoint_Url}extension/~/active-calls"
  
    response = json.loads(requests.request("GET", url, headers=Main_Header).text)
    url = f"{Endpoint_Url}extension/~/"
    # ===DND Calls===
    response_presence = json.loads(requests.request("GET", f"{url}presence", headers=Main_Header).text) 
    Recent_Status = response_presence.get('telephonyStatus')
    presenceStatus = response_presence.get('presenceStatus')
    dndStatus = response_presence.get('dndStatus')
    # ===End DND Calls===

    # ____Get Busy Call__________
    Busy_response = requests.request("GET", url, headers=Main_Header)
    if Busy_response.status_code == 200:
        presence_data = Busy_response.json()
        call_status = presence_data["telephonyStatus"]
        if call_status == "Busy":
            store_Busy_Call = call_status
            print("The call is busy.")
        else:
            print(f"The call status is {call_status}.")
    else:
        print(f"Error {Busy_response.status_code}: {Busy_response.text}")
    # End ________Busy Call______

    # ===Customer Name===
    response_Account = json.loads(requests.request("GET", url, headers=Main_Header).text)
    Customer_Id = response_Account.get('id')
    Current_customer = response_Account.get('contact').get('firstName') +" "+ response_Account.get('contact').get('lastName')
    # ===End Customer Name===

    # ====Get Active Calls====
    Get_Recods = response.get('records')
#   If you want to run this step so you'll need to create a call
    queued_callers = 0
    for i in Get_Recods:
        if i != None:
            # How many Active caller waiting to be answered
            if i["result"] in ["Ringing", "CallConnected"]:
                queued_callers += 1

            callerId = i.get('id')
            Call_Direction = i.get('direction')
            Action = i.get('action')
            Calling_Status =  i.get('result')
            Caller_To = i.get('to').get('phoneNumber')
            Caller_From =  i.get('from').get('phoneNumber')

            Called_extension = i.get('extension').get('id')

            Call_Duration = i.get('duration')
            extensionNumber = i.get('from').get('extensionNumber')
            extensionId = i.get('from').get('extensionId')
            Call_Start_Time_store = list()
            if Call_Duration:
                if Call_Duration >=1:
                    Call_Start_Time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  
                    Call_Start_Time_store.append(Call_Start_Time)
            try:
                StartTime = Call_Start_Time_store[0]
            except:
                StartTime = Call_Start_Time_store
            sessionId = i.get('sessionId')
            Cname = i.get('from').get('name')
            Call_Start_Time_UTC = i.get('startTime')
            # Convert the given time string into a datetime object
            time_utc = datetime.fromisoformat(str(Call_Start_Time_UTC).replace("Z", "+00:00"))
            # Get the local time zone
            local_tz = tz.gettz()
            # # Convert the UTC time to local time
            Call_Start_Time_Local = time_utc.astimezone(local_tz)
            telephonySessionId = i.get('telephonySessionId')
            Ringing_Time = i.get('startTime')
            dateUpdated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            try:

                Recording_Url = i.get('recording').get('uri')
                Recording_Id = i.get('recording').get('id')
            except:
                Recording_Url = "None"
                Recording_Id = "None"

            data = {
                    "sessionId": sessionId,
                    "calledExtension": Called_extension,
                    "callDirection": Call_Direction,
                    "callerFrom": Caller_From,
                    "cname": Cname,
                    "callerTo": Caller_To,
                    "callingStatus":Calling_Status,
                    "recentStatus":Recent_Status,
                    "callStartTimeUTC": StartTime,
                    "ringingTime":Ringing_Time,
                    "callDuration": Call_Duration,
                    # "currentCustomer":Current_customer,
                    "customerID":str(Customer_Id),
                    "callStartTimeLocal": Call_Start_Time_Local,
                    # "telephonySessionId":telephonySessionId,
                    "dateUpdated" :str(dateUpdated),
                    "callRecordingUrl" : Recording_Url,
                    "callRecordingId":Recording_Id
                }
            
    
            rc_currentCaller_Table = {
                "externalExtension":Called_extension,
                "extensionNumber":extensionNumber,
                "callDirection" : Call_Direction,
                "callerId" : callerId,
                "calledTo" : Caller_To,
                "telephonyStatus":Recent_Status,
                "presenceStatus":presenceStatus,
                # "currentCustomer":
                "customerID":Customer_Id,
                "cname": Cname,
                "dndStatus":dndStatus,
                # "branch_id":

            }
            print(f"Number of queued callers: {queued_callers}")
            yield data,rc_currentCaller_Table
    


def Get_Call_History():
    url = f"{Endpoint_Url}extension/~/"
    response_presence = json.loads(requests.request("GET", f"{url}presence", headers=Main_Header).text)
    Recent_Status = response_presence.get('telephonyStatus')
    presenceStatus = response_presence.get('presenceStatus')
    dndStatus = response_presence.get('dndStatus')

    response_Account = json.loads(requests.request("GET", url, headers=Main_Header).text)
    Customer_Id = response_Account.get('id')
    Current_customer = response_Account.get('contact').get('firstName') +" "+ response_Account.get('contact').get('lastName')
    Call_History_Url = f"{Endpoint_Url}extension/~/call-log/"

    response = json.loads(requests.request("GET", Call_History_Url, headers=Main_Header).text)
    Get_Recods = response.get('records')
    for i in Get_Recods:
        if i != None:
            callerId = i.get('id')
            Call_Direction = i.get('direction')
            Action = i.get('action')
            Calling_Status =  i.get('result')
            Caller_To = i.get('to').get('phoneNumber')
            Caller_From =  i.get('from').get('phoneNumber')
            Called_extension = i.get('extension').get('id')
            Call_Duration = i.get('duration')
            extensionNumber = i.get('from').get('extensionNumber')
            extensionId = i.get('from').get('extensionId')
            Call_Start_Time_store = list()
            Ringing_Time = i.get('startTime')
            # __________Convert utc to local time zone__________________
            Call_Start_Time_UTC = i.get('startTime')
            time_utc = datetime.fromisoformat(str(Call_Start_Time_UTC).replace("Z", "+00:00"))
            local_tz = tz.gettz()
            Call_Start_Time_Local = time_utc.astimezone(local_tz)
            # _________________End Here__________________________________
  
            if Call_Duration:
                if Call_Duration >=1:
                    new_time = Call_Start_Time_Local - timedelta(seconds=Call_Duration)  # Add the seconds to the current time
                    Call_Start_Time_store.append(new_time)
            try:
                StartTime = Call_Start_Time_store[0]
            except:
                StartTime = Call_Start_Time_store
            sessionId = i.get('sessionId')
            Cname = i.get('from').get('name')
            dateUpdated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            rc_call_history = {
                "sessionId": sessionId,
                "calledExtension": Called_extension,
                "callDirection": Call_Direction,
                "callerFrom": Caller_From,
                "cname": Cname,
                "callerTo": Caller_To,
                "callingStatus":Calling_Status,
                "recentStatus":Recent_Status,
                "callStartTimeUTC": StartTime,
                "ringingTime":Ringing_Time,
                "callDuration": Call_Duration,
                # "currentCustomer":Current_customer,
                "customerID":str(Customer_Id),
                "callStartTimeLocal": Call_Start_Time_Local,
                "dateUpdated" :str(dateUpdated)
            }
            yield rc_call_history


def Get_Recording_Content():
    url = f"{Endpoint_Url}recording/12728313005/R"
    response = requests.request("GET", url, headers=Main_Header)
    with open('file.mp3', 'wb') as f:
        f.write(response.content)

def Create_Call_Recordings():
    Call_fun = call()
    Get_TelephonyId = Call_fun.get('id')
    Create_Url = f"{Endpoint_Url}telephony/sessions/{Get_TelephonyId}"
    Get_Parties_Id = [parties_id.get('id') for parties_id in json.loads(requests.request("GET", Create_Url, headers=Main_Header).text).get('parties')][0] #Get Party Id
    time.sleep(2)
    Get_Recording_Id = json.loads(requests.request("POST", f"{Create_Url}/parties/{Get_Parties_Id}/recordings", headers=Main_Header).text).get('id') #Get Recroding Id
    time.sleep(20)
    Recording_response = requests.request("GET", f"{Endpoint_Url}recording/{Get_Recording_Id}/content", headers=Main_Header)
    # Create File into .mp3 format
    with open(Get_Recording_Id + 'file.mp3', 'wb') as f:
        f.write(Recording_response.content)

# Create_Call_Recordings()

# Capture all Recordings and place in S3 bucket provided
def CaptureAllRecordings():
    del Main_Header['Content-Type'] #Del Old content-Type
    Main_Header['contentType'] = "audio/x-wav" #Add new content-Type
    url = "https://platform.ringcentral.com/restapi/v1.0/account/~/call-log?withRecording=true"
    # Capture All Recordings
    Get_all_Recording_id = [rec.get('recording').get('id') for rec in json.loads(requests.request("GET", url, headers=Main_Header).text).get('records')]
    for Id in Get_all_Recording_id:
        # Get Recording using Id
        Rec_Url = "https://platform.ringcentral.com/restapi/v1.0/account/~/recording/{Id}/content"
        Store_Rec = requests.request("GET", url, headers=Main_Header)
        folder_path = 'Recording_mp3'
        file_name = Id+'file.mp3'
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(Store_Rec.content)

def Stop_Recordings():
    Call_fun = call()
    Get_TelephonyId = Call_fun.get('id')
    url = f"{Endpoint_Url}extension/~/telephony/sessions/{Get_TelephonyId}/parties/~/recordings/stop"
    response = json.loads(requests.request("POST", url, headers=Main_Header).text)
    print(response)


 