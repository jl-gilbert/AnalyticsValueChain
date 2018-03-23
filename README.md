# LeBron James Stat Predictions

### Developer: Joe Gilbert

Product Owner: Tong Yin

QA: Grace Cui

## Project Charter

Assist fans and participants in fantasy sports with short-term decisions by using features of a current matchup to predict the major statistics (points, assists, rebounds) that Lebron James will record in his next matchup. 

**Vision**: Provide information to fans or others interested in Lebron James’ statistics by predicting what they will be in his next game.

**Mission**: Use historical data to build a model that will predict a particular player’s statistics in his upcoming matchup. 

**Success criteria**: A web app that will be updated daily to reflect the predicted statistics for Lebron James in his next game, with predictions that are subjectively reasonable. 

 
## Suggested steps to deploy app

### 1. Clone repository.

### 2. If using Anaconda, create conda environment:

    ```
    conda env create -f project_environment.yml
    ```
	
	All below steps work under the assumption that a conda env is being used. If a Python virtualenv is being used instead, the user will need to translate steps for activating the environment, etc.
	If not using Anaconda, create Python virtualenv and install required packages:
    
    ```
    pip install -r requirements.txt
    ```

	You may need to change your version of Python for the above step to work without returning errors. Python 3.5 will work.
	
### 3. Run unit tests.

	Navigate to root directory "AnalyticsValueChain".
	```
	pytest
	```
	
### 4. Register for an account at MySportsFeeds.com with access to postgame data fields for in progress seasons. This will give you a username and password. 

	Make a file named config.py in the "develop" directory.
	```
	username = '<your MySportsFeeds username>'
	password = '<your MySportsFeeds password>'
	```
	
	
### 5. Make a configuration file with information on the SQL database you will be storing the data in. A MySQL instance is recommended for guaranteed compatibility. 

	Name this file dbconfig.py and put it in the "app" directory
	```
	SQLALCHEMY_DATABASE_URI  = '<URI for the database you will be using>'
	```



### 6. Create the initial dataset with historical data. Run the following from the root directory of the project. 

    ```
    source activate project_env
	python create_initial_db.py
    ```
	
	This code will take several hours to run, as it requires many calls to the API (which throttles traffic to limit a user to 250 requests every 5 minutes.
	Once this process is finished, the game table in the database will have data for every game up to the day before running the process. 

### 7. Update the data and make first models:

    ```
    source activate project_env
	python update_db.py
    ```
	This will update the game table to the current day, train a model, find the next game, and make predictions for that game. 

### 8. Set up the crontab to make the required updates to data, model, and predictions on a daily basis. 

	First, edit the daily_update_script.bash file to make it appropriate for your environment
	
	```
	source /home/ec2-user/anaconda3/envs/project_env/bin/activate project_env
	cd AnalyticsValueChain
	python update_db.py
	```
	
	The first line needs to take care of activating the correct conda environment (such as this example does) or python virtualenv if you are using that.
	The second line moves the working directory from the one in which the crontab runs to the root directory of the project. 
	In the above example, the crontab runs in /home/ec2-user/ and the project root directory is /home/ec2-user/AnalyticsValueChain
	
	Once daily_update_script.bash has been configured appropriately, input the following as the crontab.
	
	```
	0 <hour> * * * <path to project directory>/daily_update_script.bash
	```
	
	The hour should be selected depending on what time of day you want the data/model/prediction to be updated at. This is dependent on the API having updated, if it has not been an error message will be written to the logs stating so. 
	
	
### 9. Launch the app:

    ```
	source activate project_env
    python lbjapp.py
    ```

You can then go to the IP address where the app is running and use the app.

## Reproducibility

Once the app is running, it will store all predictions in a table in the database. If for some reason you want to recreate predictions for an old game, be sure to train a model only with data from before that game in order to get the same results as would have been predicted at that time. 


## Pivotal Tracker Project Link: 

https://www.pivotaltracker.com/n/projects/2143914
