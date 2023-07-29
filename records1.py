import requests,json,time,os
Endpoint_Url = "https://platform.ringcentral.com/restapi/v1.0/account/~/"
Main_Header = {
    'Authorization': 'Bearer U0pDMDFQMjNQQVMwMHxBQUFka2VMYzVXOXpBclRvUFhKVlhZTGVDT19scmtnYjU3TWo4MWlDc0p3bzNpTFpEblRKd01HNVNleURSb2R3U0ZyQnczUTFpY3liZXhRZktmZWlBMlBqTXAyTHlmV2VSZW93dThwa1pzY1JfTjhvRFJnU3cwRURGYWpvR3ZBckpiaWRCaWdzVHIwc0RFQmd2WFRzaUNUM3MtTkJVSVZpTzYxM1I5MjVjZEFqSW1KVF9VX0cwVnNEV1FXeGVJY2NzMGJRc1l2bHJmZ3xIRTN5YlF8NzhSSzRYMDJTOGg3Z2xJb21JYWpyQXxBUXxBQXxBQUFBQUt6VUtRNA',
    'Content-Type': 'application/json'
    }



url = f"{Endpoint_Url}active-calls"
response = json.loads(requests.request("GET", url, headers=Main_Header).text)
Get_Recods = response.get('records')
for i in Get_Recods:
    if i != None:
        Store_TelephoneId = i.get('telephonySessionId')
        Create_Url = f"{Endpoint_Url}telephony/sessions/{Store_TelephoneId}"

        Get_Parties_Id = [parties_id.get('id') for parties_id in json.loads(requests.request("GET", Create_Url, headers=Main_Header).text).get('parties')][0] #Get Party Id
        # Start Recording
        Get_Recording_Id = json.loads(requests.request("POST", f"{Create_Url}/parties/{Get_Parties_Id}/recordings", headers=Main_Header).text).get('id') #Get Recroding Id
        # time.sleep(10)
        # Recording_response = requests.request("GET", f"{Endpoint_Url}recording/{Get_Recording_Id}/content", headers=Main_Header)
        # Stop Recording
        url = f"{Endpoint_Url}extension/~/telephony/sessions/{Store_TelephoneId}/parties/~/recordings/stop"
        response = json.loads(requests.request("POST", url, headers=Main_Header).text)
        print(response)



    
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





# How many Active caller waiting to be answered
url = f"{Endpoint_Url}active-calls"
queued_callers = 0
response = json.loads(requests.request("GET", url, headers=Main_Header).text).get('records')
for call in response:
    if call["result"] in ["Ringing", "CallConnected"]:
        queued_callers += 1
print(f"Number of queued callers: {queued_callers}")
