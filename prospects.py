import base64
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import pandas as pd
import warnings
import undetected_chromedriver as uc
import os
from dotenv import load_dotenv

load_dotenv()

email = os.getenv('email')
password = os.getenv('password')

options = Options()
options.add_argument('--headless')
driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Ignore the PerformanceWarning
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# Constants
code_url = os.getenv('code_url')
token_url = os.getenv('token_url')
authUrl = os.getenv('authUrl')

fetchString = '{{"cn":"ApiV2::ProspectsController","sp":null,"sv":[],"id":{},"v":1}}'
paginatedUrl = "https://api.outreach.io/api/v2/prospects?count=false&page%5Bafter%5D={}&page%5Bsize%5D=1000"

def get_code(code_url:str)->str:
    print("Getting code")
    driver.get(code_url)
    url = driver.current_url
    if 'code' not in url:
        driver.find_element(By.ID, 'user_email').send_keys(email)
        driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/button').click()
        driver.find_element(By.ID, 'user_password').send_keys(password)
        driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div[1]/div[2]/form/div[3]/div[3]/button').click()
        url = driver.current_url
    return url.split('code=')[1]

def get_accessToken(token_url:str)->str:
    print("Getting access token")
    code = get_code(code_url)
    payload = authUrl + code
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", token_url, headers=headers, data=payload)
    return json.loads(response.text).get('access_token')

def get_prospects_data():
    try:
        token = get_accessToken(token_url)
        chunk_size = 1000  # Adjust this value based on your available memory
        df_list = []  # List to store chunks of dataframes

        # while True:
        #     try:
        #         start_prospects_input = input("Enter the start value: ")
        #         start_prospects = int(start_prospects_input)
        #         if start_prospects <= 0:
        #             raise ValueError("Please enter a positive integer.")
        #         break  # Break out of the loop if a valid input is provided
        #     except ValueError:
        #         print("Invalid input. Please enter a valid positive integer.")

        start_prospects = 1
        json_string = fetchString.format(start_prospects)
        base64_encoded = base64.b64encode(json_string.encode()).decode()
        url = paginatedUrl.format(base64_encoded)

        counter = 0
        while (True):
            print(f"Getting data from {start_prospects} to {start_prospects + chunk_size}. Loop counter: {counter}")

            payload = {}
            headers = {
                'Authorization': f'Bearer {token}'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            status_code = response.status_code

            if status_code == 401:
                token = get_accessToken(token_url)
            else:
                jsonData = json.loads(response.text)
                datas = jsonData.get('data')
                df_chunk = pd.DataFrame()

                for data in datas:
                    id = data.get('id')
                    try:
                        id = int(id)
                        if (id == 0): raise ValueError
                    except ValueError:
                        print(f"Skipping iteration for id: {id}. Not convertible to int.")
                        continue  # Skip to the next iteration if id is not convertible to int
                    attributes = data.get('attributes')
                    df_chunk.at[id, 'id'] = id
                    for k in attributes.keys():
                        if k != 'contactHistogram':
                            if isinstance(attributes[k], list):
                                df_chunk.at[id, k] = ', '.join(map(str, attributes[k]))
                            else:
                                df_chunk.at[id, k] = ""
                                df_chunk.at[id, k] = attributes[k]
                    df_chunk.at[id, 'creator'] = ""
                    df_chunk.at[id, 'owner'] = ""
                    try:
                        relationships = data.get('relationships')
                        try:
                            if (relationships and relationships.get('creator')):
                                df_chunk.at[id, 'creator'] = relationships['creator']['data']['id']
                        except Exception as e:
                            pass
                        try:
                            if (relationships and relationships.get('owner')):
                                df_chunk.at[id, 'owner'] = relationships['owner']['data']['id']
                        except Exception as e:
                            pass
                    
                    except Exception as e:
                        pass

                df_list.append(df_chunk)
                last_id = df_chunk.index[-1]
                start_prospects = df_chunk.at[last_id, 'id']

                counter += 1

                if not jsonData.get('links') or not jsonData['links'].get('next'):
                    break

                url = jsonData['links']['next']

    except Exception as e:
        print(e)
        pass

    driver.quit()
    
    # Concatenate all chunks into one dataframe
    df = pd.concat(df_list, ignore_index=True)

    df.to_csv('outreach_prospects-data.csv', index=False)
    print("Data file created in the same folder with the name outreach_prospects-data.csv")

if __name__ == "__main__":
    get_prospects_data()
