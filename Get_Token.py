import time,configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests,json
import os
config = configparser.ConfigParser()
config.read('database.ini')
email = config.get('Authorization', 'EMAIL')
password = "#x4SVBJ@3BXm"


url= "https://platform.ringcentral.com/restapi/oauth/token"
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic NGxMOVV0T2NRUmVQcTEwXzh0OVlvQTpqRGhkUDdGbVM1YUVNV1B6czBQVGRnQWstWFVQRnlTc0NsUk9QNFRENDRJZw=='
    }
auth_code_url= "https://platform.ringcentral.com/restapi/oauth/authorize?client_id=4lL9UtOcQRePq10_8t9YoA&redirect_uri=https://www.google.com/&response_type=code"

def get_authorize_code(url):
    '''
    Getting authorization code by selenium
    '''
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options,service_args=['--timeout=1200'])
    driver.get(url)
    time.sleep(5)
    driver.find_element(By.XPATH, "//input[@id='credential']").send_keys(email)
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[@data-test-automation-id='loginCredentialNext']").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//input[@name='Password']").send_keys(password)
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[@data-test-automation-id='signInBtn']").click()
    time.sleep(5)
    driver.find_element(By.XPATH, "//button[@data-test-automation-id='authorizeBtn']").click()
    time.sleep(2)
    authorization_token_url=driver.current_url
    authorization_token = authorization_token_url.split("=")[1]
    return (authorization_token)

def get_referesh_token():
    '''
    Getting referesh token by hitting post oauth2 api 
    '''
    authorization_token=get_authorize_code(auth_code_url)
    print(authorization_token)
    payload = f'grant_type=authorization_code&code={authorization_token}&redirect_uri=https%3A%2F%2Fwww.google.com%2F'
    response = json.loads(requests.request("POST", url, headers=headers, data=payload).text)
    Refresh_Token = response.get('refresh_token')
    with open('refersh_token.txt','w') as file:
        file.write(str(Refresh_Token))
    return Refresh_Token

# def get_access_token():
#     # Getting acess token by hitting post oauth2 api 
#     with open('refersh_token.txt','r') as file:
#         Refresh_Token = file.read()
#         payload=f'grant_type=refresh_token&refresh_token={Refresh_Token}&client_id=4lL9UtOcQRePq10_8t9YoA'
#         response = requests.request("POST", url, headers=headers, data=payload)
#         if 429 == response.status_code:
#             print("______________Request rate exceeded________________________")
#             time.sleep(60)
#         if 200 == response.status_code :
#             print("Success Create Access Token")
#             response = json.loads(requests.request("POST", url, headers=headers, data=payload).text)
#             Get_Token = response.get('access_token')
#             return Get_Token
#         else:
#             print("Re-genrate Refresh token")
#             Refresh_Token=get_referesh_token()
#             payload=f'grant_type=refresh_token&refresh_token={Refresh_Token}&client_id=4lL9UtOcQRePq10_8t9YoA'
#             response = json.loads(requests.request("POST", url, headers=headers, data=payload).text)
#             Get_Token = response.get('access_token')



def get_access_token():
    
    with open('token.txt','r') as file:
        Refresh_Token = file.read()
    if os.stat("token.txt").st_size == 0:
        print("NoneNoneNoneNone")
        Refresh_Token=get_referesh_token()
        print(Refresh_Token)
        with open('token.txt','w') as file:
            file.write(str(Refresh_Token))
            payload=f'grant_type=refresh_token&refresh_token={Refresh_Token}&client_id=4lL9UtOcQRePq10_8t9YoA'
            response = json.loads(requests.request("POST", url, headers=headers, data=payload).text)
            Get_Token = response.get('access_token')
            # print(Get_Token)
            return Get_Token
    else:
        payload=f'grant_type=refresh_token&refresh_token={Refresh_Token}&client_id=4lL9UtOcQRePq10_8t9YoA'
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response,"print(response)")
        if 200 == response.status_code :
            response = json.loads(requests.request("POST", url, headers=headers, data=payload).text)
            Get_Token = response.get('access_token')
            # print(Get_Token)
            return Get_Token
        else:
            refresh_Token=get_referesh_token()
            with open('token.txt','w') as file:
                file.write(str(Refresh_Token))
                payload=f'grant_type=refresh_token&refresh_token={refresh_Token}&client_id=4lL9UtOcQRePq10_8t9YoA'
                response = json.loads(requests.request("POST", url, headers=headers, data=payload).text)
                Get_Token = response.get('access_token')
                # print(Get_Token)
                return Get_Token
           
