import os
import time
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()

testing_data = pd.read_excel(os.getenv("input_data_file"))

# replaces NaN with None for future string comparison logic
testing_data = testing_data.replace({pd.NaT: None, np.nan: None})

# filter our dataset to only include rows with groups
testing_data = testing_data[testing_data['Question Groups'] != 'None']

testing_data['Assistant Output'] = 'None'
testing_data['Error Flags'] = 'None'
testing_data['Response Times'] = 'None'

question_groups_list = []
for value in testing_data['Question Groups'].unique():
    grouped_df = testing_data[testing_data['Question Groups'] == value].copy()
    grouped_df = grouped_df[['Question Groups', 'Question',  'Assistant Output', 'Error Flags', 'Response Times']]
    question_groups_list.append(grouped_df)


apikey = os.getenv("api_key")
assistant_url = os.getenv("assistant_url")
assistant_environment_id = os.getenv("assistant_environment_id")

# authenticating to wxa instance
auth = HTTPBasicAuth("apikey", apikey)

wxa_params = {
    "version": "2023-07-15"
}

# watsonx assistant api functions for a batch test

# creates an assistant session, 1 per question group
def create_assistant_session():
    url = f'{assistant_url}/v2/assistants/{assistant_environment_id}/sessions'

    try:
        response = requests.post(url, params=wxa_params, auth=auth).json()
        session_id = response['session_id']
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return session_id

# queries the assistant
def query_assistant(session_id, query):
    print('-' * 41)
    print(f'1) Input:\n\n{query}\n')
    start = time.time()

    # wxa api message request
    url = f'{assistant_url}/v2/assistants/{assistant_environment_id}/sessions/{session_id}/message'
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "input": {
            "text": query
        }
    }

    try:
        response = requests.post(url, params=wxa_params, headers=headers, json=data, auth=auth).json()
    except Exception as e:
        print(f"An error occurred: {e}")
    
    end = time.time()
    query_results = ""
    print("2) Output:\n")
    for index, item in enumerate(response["output"]["generic"], 1):
        if item["response_type"] == "text":
            print(item['text'] + "\n")
            query_results += item['text'] + "\n\n"
    query_results += "\n"
    
    api_response_time = round(end - start,2)
    print(f'3) API response time:\n\n{str(api_response_time)}\n')

    return query_results, api_response_time

# deletes an assistant session
def delete_assistant_session(session_id):
    url = f'{assistant_url}/v2/assistants/{assistant_environment_id}/sessions/{session_id}'
    
    try:
        response = requests.delete(url, params=wxa_params, auth=auth)
    except Exception as e:
        print(f"An error occurred: {e}")

# query all groups
def batch_assistant_query(question_group_df):
    time.sleep(3)
    session_id = create_assistant_session()

    for index, row in question_group_df.iterrows():
        time.sleep(3)
        flags = ""
        query_results, api_response_time = query_assistant(session_id, row['Question'])
        row['Assistant Output'] = query_results
        
        # error handling
        if ("I'm sorry, I've run into an error processing your request. Please try the same question again.  Thank you!" in query_results):
            if (api_response_time > 30):
                flags += "Timeout Error\n"
            else:
                flags += "Processing Error\n"
        
        
        row['Response Times'] = api_response_time
        row['Flags'] = flags
        
        

    delete_assistant_session(session_id)

    

count = 1
for df in question_groups_list:
    print(f'-------------Testing group {count}-------------\n')
    batch_assistant_query(df)
    count += 1

# create the final dataframe to be exported to an excel sheet
concatenated_rows = []

for df in question_groups_list:
    for index, row in df.iterrows():
        concatenated_rows.append(row)

question_groups_df_combined = pd.DataFrame(concatenated_rows)



# write the dataframe to an excel file
writer = pd.ExcelWriter(os.getenv("output_data_file"), engine='xlsxwriter')
question_groups_df_combined.to_excel(writer, index=False, sheet_name='Sheet1')
workbook = writer.book
worksheet = writer.sheets['Sheet1']
cell_format = workbook.add_format({'text_wrap': True, 'valign': 'top', 'align': 'left'})
for i, column in enumerate(question_groups_df_combined.columns):
    worksheet.set_column(i, i, 40, cell_format)
worksheet.set_column(3, 3, 70, cell_format)
writer.close()


