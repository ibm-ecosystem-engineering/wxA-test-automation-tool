<!-- ABOUT THE PROJECT -->

# watsonx Assistant Testing Automation Tool

The watsonx Assistant Testing Automation Tool is used to batch test question groups against a watsonx Assistant instance. The script ingests an excel file with questions, uses the watsonx Assistant API to query the assistant, and outputs an excel file with the results. The goal of the tool is to reduce execution time for running tests and identifying potential recurring errors.

<!-- GETTING STARTED -->

## Getting Started

### Prerequisites

The following prerequisites are required to run the tester:

1. Python3
2. IBM Cloud api key (this must be for the same cloud account that hosts the assistant instance)
3. watsonx Assistant service instance url
4. watsonx Assistant environment id

### Installation

1. Clone the repo

   ```bash
   git clone git@github.ibm.com:EE-WW-BuildLab/wxa-test-automation-tool.git
   ```

2. Change directory into wxa-test-automation-tool

   ```bash
   cd wxa-test-automation-tool
   ```

3. Create a python virtual environment

   ```bash
   python3 -m venv virtual-env
   source virtual-env/bin/activate
   pip3 install -r requirements.txt
   ```

4. Copy env file to .env

   ```bash
   cp env .env
   ```

5. Configure parameters in .env and set the values of your environment
   1. `input_data_file`: the name of your input excel file (should be .xslx). For file configuration details, see [Configuring Your Input Excel File](#configuring-your-input-excel-file)
   2. `output_data_file`: the name of your output excel file (should be .xlsx)
   3. `api_key`: your ibm cloud api key. It should have access to the account that contains your assistant
   4. Within your assistant UI, click "Assistant settings" on the bottom left -> navigate to Assistant IDs and API details -> click view details
      1. `assistant_url`: your Service instance URL
      2. `assistant_environment_id`: the environment id which contains your configured assistant (ex: Draft Environment ID or Live Environment ID)

6. Run the following to start the script

   ```bash
   python3 main.py
   ```

7. Run the following command to exit the python virtual environment:

   ```bash
   deactivate
   ```

## Configuring your Input Excel File

The repository contains a sample input file that you can copy, edit, and use to test.

The input excel file must have the following three columns (**note:** they are spelling and case sensitive):

1. "Question Groups"
   1. This column acts as a label for questions that should be asked to the assistant in one session.
   2. Example values:
      1. "Group 1"
      2. "Group 2"
      3. "Group 3"
2. "Question"
   1. This column contains the question to be asked to the assistant.

## Understanding the Results

You can observe real time results in the terminal. Each time a questions is asked, you can view the input, response time, and output.

When all tests are completed, an output excel file with your results is created using the name specified in your env file. The output file contains the question groups, questions, assistant results, error flags, and response times.

### Error Flags

1. Processing error: occurs when the assistant returns a general processing error
2. Timeout error: occurs when the assistant response takes greater than 30 seconds
