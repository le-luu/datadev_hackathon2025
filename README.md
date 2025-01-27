# Tableau DataDev Hackathon 2024-2025

![image](https://github.com/le-luu/datadev_hackathon2025/blob/main/img/pipeline.png)

### Ideas:
-	Create an automated workflow to extract data from the Weather API using Tableau tools
-	Schedule the workflow for real-time analysis
-	Publish the data source on Tableau Cloud/ Server and refresh data
-	Build a Machine Learning model to predict the data from the published data source
-	Apply the Machine Learning model in Tableau Desktop using TabPy
-	Build the dashboard in Tableau Desktop to show the predicted data and compare it with the actual data
  
### Challenges:
-	TabPy is required to extract data from an API and parse JSON using the Script tool in Tableau Prep Builder. However, workflows containing the Script tool in Tableau Prep Builder cannot be published to Tableau Cloud.
 ![image](https://github.com/le-luu/datadev_hackathon2025/blob/main/img/cannot_publish_script_step_on_Tableau_Cloud.png)
(Source: https://help.tableau.com/current/prep/en-us/prep_scripts_TabPy.htm)

-	Due to this limitation, it is not possible to schedule the workflow for data refresh on Tableau Cloud. Therefore, I need to find an alternative solution to schedule the workflow to run daily.
-	Once the data source is published on Tableau Cloud, downloading it via Tableau Server Client (TSC) and converting the Hyper file or .tdsx file into a DataFrame can be a complex process.
-	Develop a machine learning model and integrate it into Tableau Desktop via TabPy.
-	Consider how to make the machine learning model accessible in Tableau Desktop for all users, including those without a Computer Science background.


### List of APIs and Dev Tools
1. Weather API: https://open-meteo.com/
	  Extract data from the Weather API.
2. Tableau HyperAPI: https://tableau.github.io/hyper-db/docs/
	After transforming the data in Python, use HyperAPI to convert data into a hyper file to upload the data source to Tableau Cloud.
3. Tableau Server REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api.htm
	Use Tableau Server Client in Python to access Tableau Cloud using PAT and publish the hyper file on Tableau Cloud.
4. TabPy Server: https://tableau.github.io/TabPy/
	Deploy the Python function to forecast the temperature on TabPy and apply Python script in Tableau Desktop.
5. Jupyter Notebook
	Use Jupyter Notebook to run the Python script and deploy the function on TabPy server.

### Further Improvements
-	Currently, the Python script (loading the data source script, training, and deploying function on TabPy) is run manually in the terminal or Python IDE. To schedule it to run daily to load the data source in Tableau Cloud, need to use the OS system to schedule the task, or use Amazon Web Services (AWS Lambda, EC2, or Glue) to schedule the task.
-	The data source is replaced on Tableau Cloud when running the Python script. In the future, I will find a way to append the new data to the current data source instead of replacing the whole data source all the time.
-	Add more types of regression models to compare the predicted values and errors. 
-	Create a dashboard to show how good of running the regression model by showing the evaluation metrics when comparing the actual data and predicted data.

### Instructions
- You need to install Python in your local computer
- Fork the repository and clone it to your local computer
- Open the Command Prompt (for Windows) and Terminal (for Mac), change the directory to the datadev_hackathon2025
    ```
    cd datadev_hackathon2025
    ```
- Install and activate the virtual environment
    ```
    pip install virtualenv
    virtualenv venv
    venv\Scripts\activate
    ```    
- Install the packages in the Command Prompt
    ```
    pip install -r requirements.txt
    ```
    It may takes a few minutes to install all packages:
    - requests
    - pandas
    - tableauhyperapi
    - tableauserverclient
    - scikit-learn
    - matplotlib
    - numpy
    - tabpy
- From the datadev_hackathon2025, change your directory to script_files folder
    ```
    cd script_files
    ```
- Set up Tableau Cloud
    - Log in into your Tableau Cloud
    - Create a new Project (E.g: My project name is "Weather API Project")
    - Generate your Personal Access Token (PAT) in Settings (keep your token_name and token_value)
    - Make sure that you get information of server_address, site_name, project_name, token_name, and token_value
- In the script_files folder, use any Text Editor or Python IDE to open the tsc_publish_data_source.py file. In the main function, modify the information of server_address, site_name, project_name, token_name, token_value. Finally, save the Python script file.
- In the Command Prompt, run that script. It will publish the data source into the project that you created on Tableau Cloud. It will also generate 2 new files (weather_data.hyper and weather_data.csv) in the scripts_files folder.
    ```
    python tsc_publish_data_source.py
    ```
- Then, activate TabPy in the Command Prompt (if you already installed TabPy on Cloud, skip this step)
    ```
    tabpy
    ```
    It will activate TabPy with your localhost and port number by default is 9004
- In the script_files folder, use Jupyter Notebook to open the Deploy_Weather_Forecast_Tabpy.ipynb
    - If you already set up TabPy on Tableau Cloud, get the information of host, port number, username, password
    - If you didn't set up TabPy on Tableau Cloud, you can run the script with localhost and port number by default is 9004
    - On the last cell, make sure that the host and port number is correct
    - I run all the cells by going to the Cell menu and choose Run All
    - This step will deploy the model on TabPy Server
    - On webbrowser, you can type: localhost:9004 to view the deployed function on TabPy
- Open Tableau Dashboard folder, open Tableau workbook Temperature_forecast.twb
    - Connect to the Tableau Cloud where you store the weather_data data source
    - Go to Help \ Settings and Performance \ Manage Analytics Extension Connection
    - Choose TabPy
    - Enter your host and port number (E.g: host: localhost and port number: 9004) and save it
- Now you can run the Workbook to track the temperature each day hourly in New York

![image](https://github.com/le-luu/datadev_hackathon2025/blob/main/img/Forecasting_temp_data_dashboard.png)

Have fun!
