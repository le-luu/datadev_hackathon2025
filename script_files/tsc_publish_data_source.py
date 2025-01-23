###########################################
### Tableau DataDev Hackathon 2024-2025 ###
### Name: Le Luu                        ###
###########################################

#Extract data from API and load the data on Tableau Cloud

import requests
import pandas as pd
from datetime import date, timedelta
from tableauhyperapi import HyperProcess, Telemetry, \
    Connection, CreateMode, \
    NOT_NULLABLE, NULLABLE, SqlType, TableDefinition, \
    Inserter, \
    escape_name, escape_string_literal, \
    TableName, \
    HyperException
import tableauserverclient as TSC
from pathlib import Path
import os
import warnings

#Extract the data from open-meteo API
def extract_weather_data(adding_days):
    # Import the weather API link to extract data
    # The latitude and longitude is in New York
    # The data starts from 01/01/2022 to the current day
    api_link = ("https://archive-api.open-meteo.com/v1/archive?latitude=40.7143&longitude=-74.006"
                "&hourly=temperature_2m&temperature_unit=fahrenheit&wind_speed_unit=mph"
                "&timezone=America%2FNew_York&start_date=2022-01-01&end_date=" + str(date.today()))
    
    # Send the GET request and receive the response
    response = requests.get(api_link)
    data = response.json()
    df = pd.DataFrame(data['hourly'])

    # Convert 'time' to datetime 
    df['time'] = pd.to_datetime(df['time'])

    # Convert the value in temperature_2m column to numeric
    df['temperature_2m'] = pd.to_numeric(df['temperature_2m'], errors='coerce')

    # Generate future timestamps with the specified adding_days parameter
    latest_date = df['time'].max().date() #Get the latest day after extracting data
    # Create a future_dates array to store the list of future days until the adding_days
    future_dates = []
    for day in range(1, adding_days+1):
        future_dates.append(latest_date+timedelta(days=day))

    # Create a future timestamp for each future_dates as the format: YYYY-MM-DD hh:00:00
    # The hour will be from 0 to 23
    future_timestamps_df = pd.DataFrame({
        'time': [pd.Timestamp(f"{day} {hour:02}:00:00") for day in future_dates for hour in range(24)],
        'temperature_2m': pd.NA  # Assign the null values for the future timestamp
    })
    
    # Ignore the warning because there are null values in the temperature_2m column
    # Keep the null values to predict the data later
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        # concatenate 2 dataframes df and future_timestamps_df together
        df = pd.concat([df, future_timestamps_df], ignore_index=True)  


    return df

# Create a table to insert the data and store the hyper file locally
def insert_data(df, path_to_database, extract_table):

    print("")
    print("=============================================================")
    print("======== Creating a single table with hyper file  ===========")
    print("=============================================================")
    # Clean the DataFrame to ensure all values in "temperature_2m" are valid floats
    df['temperature_2m'] = pd.to_numeric(df['temperature_2m'], errors='coerce')

    # Output the CSV File at the current directory to train the ML model later
    file_path = 'weather_data.csv'
    df.to_csv(file_path, index=False)

    print()
    print(f'=> Writing data in {file_path} file located at {os.path.abspath(file_path)}')

    # Use itertuples to construct the data row by row
    # Later Inserter requires that structure to insert the data to hyper
    rows_to_insert = df.itertuples(index=False, name=None)

    # Start the Hyper Process
    # send Telemetry on Hyper API usage to Tableau
    with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:

        # Open a connection to the hyper file with the database is the name of the hyperfile
        # Set the create mode is CREATE_AND_REPLACE
        # if the the database exists, replace it by a new database
        with Connection(endpoint=hyper.endpoint,
                        database=path_to_database,
                        create_mode=CreateMode.CREATE_AND_REPLACE) as connection:

            # Create schema and table
            connection.catalog.create_schema(schema=extract_table.table_name.schema_name)
            connection.catalog.create_table(table_definition=extract_table)

            # Use the class Inserter to insert the data into hyper. The insertion happens row by row.
            # https://tableau.github.io/hyper-db/lang_docs/java/com/tableau/hyperapi/Inserter.html
            with Inserter(connection, extract_table) as inserter:
                inserter.add_rows(rows=rows_to_insert)
                inserter.execute() #call execute after inserting the last row to finallize the insert

            # Verify the data in the table by counting the number of rows in the extract_table
            row_count = connection.execute_scalar_query(
                query=f"SELECT COUNT(*) FROM {extract_table.table_name}"
            )
            print()
            print(f"=> {row_count} Rows are INSERTED in table {extract_table.table_name}")
        print("")
        print("===> Connection to the Hyper file has been CLOSED <===")

# After storing the hyper file locally, publish the hyper file to Tableau Cloud using TSC
def publish_hyper(token_name,token_value,site_name,server_address,project_name,hyper_name,path_to_database):

    # Set up connection to Tableau Server/ Cloud using TSC
    tableau_auth = TSC.PersonalAccessTokenAuth(token_name=token_name, personal_access_token=token_value, site_id=site_name)
    server = TSC.Server(server_address, use_server_version=True)
    

    print("")
    print("=============================================================")
    print("===== Setting up connection to publish data on Cloud ========")
    print("=============================================================")
    print("")
    print(f"... Signing into {site_name} site at {server_address}")

    # Sign in Tableau Cloud with the credentials info
    with server.auth.sign_in(tableau_auth):
        # Define the publish mode - Overwrite, Append, or CreateNew
        publish_mode = TSC.Server.PublishMode.Overwrite
        
        # Get project_id from project_name
        all_projects, pagination_item = server.projects.get()
        for project in TSC.Pager(server.projects):
            if project.name == project_name:
                project_id = project.id
    
        # Create the datasource object with the project_id
        datasource = TSC.DatasourceItem(project_id)
        
        print(f"==> Publishing {hyper_name} to {project_name}")
        # Publish datasource
        datasource = server.datasources.publish(datasource, path_to_database, publish_mode)
        print("")
        print("*** Datasource is Published Successfully!!! ***")
        print("")
        print("Datasource ID:              {0}".format(datasource.id))
        print(f"Datasource Name:            {hyper_name}")
        print(f"Located in Project Name:    {project_name}")

# Define the main function to run the program
def main():

    # Store the credentials info into variables
    hyper_name = 'weather_data.hyper'
    server_address = 'https://10ax.online.tableau.com/'
    site_name = 'leluudev'
    project_name = 'Weather API Project'
    token_name = 'test_hyperapi'
    token_value = os.getenv("TABLEAU_PAT_VALUE")  

    # Check if the token is set
    if not token_value:
        print("API token not found")
        return

    path_to_database = Path(hyper_name)

    # Define the Hyper table schema
    extract_table = TableDefinition(
        table_name=TableName("Extract", "Weather_Dataset"),
        columns=[
            TableDefinition.Column(name="time", type=SqlType.timestamp()),
            TableDefinition.Column(name="temperature_2m", type=SqlType.double())
        ],
    )
    print("")
    print("=============================================================")
    print("======    Tableau DataDev Hackathon 2024-2025          ======")
    print("======    Forecasting Temperature Hourly in New York   ======")
    print("======    Created By: Le Luu                           ======")
    print("=============================================================")
    print("")
    # Ask user for the number of days to predict
    print(f"Today is {str(date.today())}\nHow many days from today do you want to predict the temperature?")
    # Check if the user enter correct number
    while True:
        try:
            days_add = int(input("Enter a number: "))
            if days_add > 0:
                break
            else:
                print("Please enter a number greater than 0")
        except ValueError:
            print("Invalid input. Please enter a valid integer")

    # Call the extract_weather_data function
    df = extract_weather_data(days_add)  # Ensure this function is updated to accept days_add

    # Create a table to insert data with the hyper schema info
    insert_data(df, path_to_database, extract_table)

    # Publish Hyper file to Tableau Cloud/Server
    publish_hyper(
        token_name=token_name,
        token_value=token_value,
        site_name=site_name,
        server_address=server_address,
        project_name=project_name,
        hyper_name=hyper_name,
        path_to_database=path_to_database,
    )


# Run the script
if __name__ == "__main__":
    main()