# PirnaStudyCase
Study case developed by Saulo Vieira da Silva Filho, Nicolás Salazar and Claudia Montecinos to investigate the groundwater flow system in Pirna - Sachsen, Deutschland.

**SMARTControl** was developed to handle sensor's data. The database is currently being stored locally in the file 'Data/database.db'. The package also encompasses functionalities to process real-time data and visualize it as a dashboard. **SMARTControl** is a high-level tool developed specifically to targetthe needs of the project. Therefore, with the functionalities here present, it will not be possible to adapt it to your workflow without changing slightly the source code. However, the functionalities are relatively well documented, easy to understand and dependent on widely-used python packages.


## Current status

**This is an alpha version of an update app at a very early stage.**
* Important information about it
	1. Source of data: PegelAlarm and Inowas sensor web
	2. Where the database is stored:
		* In local repo
		* updates are commited to git and github
	3. Problem
		* Github is not a good solution for hosting a database
	4. Challenges
		* host the database online
		* deploy app.py online
		* schedule runs on an online serve for this app_update.py
	5. What to do next
		* Check if when cloning this repo locally the app will work well          


## SMARTControl at a glance

1. The **dashboard** is present in the file **app.py** and can be run from the commmand line by using: **python app.py**. Just make sure you are in the same folder ;)

2. How to use **SMARTControl**: in **JupyterNotebooks/Examples.ipynb** you can find examples on how to deploy its functionalities.


## Set-up 101

Step-by-step on how to setup a python ecossystem and deploy this.



1. [Install Miniconda](https://docs.conda.io/en/latest/miniconda.html): Miniconda is a slight version of conda package manager. It solves conflicts and can make your life easier in case you are not experienced with python.

2. [Install Gitbash](https://git-scm.com/downloads): git is a version manager very important in the programming world. It will be used to clone this repository to your local environment.

3. Clone this repository:
	* Open the git bash interface
	* Go to the folder where you would like to setup the environment.
		* Important commands:
			* cd (change directory): 
				* Example: cd c:/users/MyUser/PirnaCaseStudy 
			* mkdir (make directory):
				* Create a new folder from the bash interface
			* cd .. :
				* Move to the upper directory
	* Create a folder to clone this repo
		* git clone https://github.com/SauloVSFh/PirnaStudyCase
		
	* Open the anaconda prompt
		* Go to the folder where you cloned the repository (PirnaStudyCase)
		* Create a new environment and install the requirements (as of December 2022):
			* Just type once you're in the folder:
				* pip install -r requirements.txt
				* Not available at the moment: conda create --name PirnaStudyCase --file spec-file.txt 			
4. Run the app:
	* If you accomplish the steps above, type:
		* python app.py

## The Database
*The database* is developed using *sqalchemy* models was specifically designed to target monitoring divers but in a way that it also enables the addition of other tables and types of measurements in the future. The models are present in the python module **SMARTControl.CreateDatabase** and can be used if such a task is desired. The database schema is as follows:

![plot](https://github.com/SauloVSFh/PirnaStudyCase/blob/master/Figures/Schema.png?raw=true)

* Some possibilities are listed below:

	1. Hydrogeological Tests: a table for hydrogeological tests can be created in the future in case it is needed. This table could have slug test and pumping tests data added and a relationship established with the MonitoringPoints table. 


	2. Hydrochemical analysis: a table to store chemical data can be created. In this case the optimal procedure would be creating a table with columns for index (integer), date of analysis (time stamp), element (integer), and value (float). This table could be related to the Variables table, where the hydrogeochemical variables could be added with their respective description and units.
	

## Important modules of the **SMARTControl** package.

Below, a brief description of each python module and its classes and functions is given.

1. **CreateDatabase.py**
	* Database tables and connections created as classes and models
	* If executed and .db is non existent, it creates a database
2.	**queries.py**
	* Get : instance class to retrieve data. The methods below are currently available:
		* *APIDate*: Function to get the last date in the database and pass it as a searching mechanism to retrieve the API. It returns the first date and the first timestamp to search in the API.
		* *CheckDuplicateEntry* : it checks duplicate entries in the PointsMeasurements table and drop these values. It returns a dataframe with less or equal number of rows than the input frame.
		* *DiverData*: get class method to retrieve sensor data. It returns a dataframe to merge well and diver data.
		* *DiverStatus*: it returns a dataframe joining divers, wells, drills and the current status with regards to the divers' last update.
		* *HydroProfile*: long query for the hydrogeological profiles. They can be index by drill.
		* *Isolines*:•	query used to retrieve monitoring data for a given variable and time.
		* *LongTimeSeries*: Long query for the PointsMeasurements. The resultant query is stored in a pandas.core.frame.DataFrame format as a class attribute.
		* *ShortTimeSeries*: query for the PointsMeasurements per well. The resultant query is stored in a pandas.core.frame.DataFrame format as a class attribute.
		* *MonitoringPointData*: function to retrieve information about all the monitoring points.
		* *SartEndDate*: Function to get the start and end date of the database
		* *Table*: it retrieves the entire raw table from database
		* *UpdateID*: get the last update from the PointsMeasurements table
		* *VariableID*: it returns the ID of a specific variable as integer.
3. **utils.py**
	* **Dashboard map plotting capabilities**:
		* *arrow_head*: function to create arrow heads based on coordinates, gradient and a scale standard parameter. It returns a dataframe with information with geometric information of arrow heads.
		* *Folium_arrows*: it creates a Folium field of arrows.
		* *Folium_contour*: it creates a Folium contour map.
		* *Folium_map*: it creates a Folium map centered in the region of interest.
	* **Workflow**
		* *InterpolationGradient*: class method to interpolate data the Scipy cubic method and find the gradient of the potentiometric surface. 
		* *BoundaryCondition*: function to add the river head boundary to the Isolines query before interpolating data. It basically uses spreads across boundary points the value read in the river gage.
		* *CompleteMissingDates*: fill time gaps with numpy.nan data for hourly data from unix time stamp column.
		* *ControlPoints*: function to distribute fictious points in the river border and interpolate the levels.
		* *DbCon*: function that returns important variables to connect to the database using sqlalchemy.
		* *TimeToString*: convert pandas timestamp to string to be passed into the pegel API.
		* *Process*: function that process the input dataframe and prepare it to be appended to the PointsMeasurements table.  It first deploys the checkDuplicateEntry function and checks if there is any duplicate entry , and then deploys the CompleteMissingDates function to fill gaps with numpy.nan.
		* *prepare_query*: function to further process the Get.Isolines method and screen out values that should not be used in the PrepareIsolines function.

	* **Management of database**
		* *FixOutliers*:  function to reset outliers based on threshold. From quick analysis, when the diver depth is 12.4 in the Pirna Test site. The best is threshold is 108. The ouliers are values below what is expect and are obtained when the divers are exposed to the atmospheric pressure. In other words, when they are removed from the well and the reading is transmitted to the database.
		* *FixValueByDate*: function to replace value to null using date interval.
		
			
4. **api.py**: a module to access APIs that hinges on two classes. Internal dependencies are: SmartControl.utils and SmartControl.queries. Both classes count on the Request method to access the api data after fetching preliminary information in the 'database.db' file.
	* *GetDivers*: function to get all the divers from https://sensors.inowas.com/list and merge it with the database information.
	* *Inowas* and *PegelAlarm*: instance classes with and __init__ method that produces an URL to retrieve data from the APIs using the last update in the database. 
		* *Request*: classes' method to request a json file and produce a dataframe compatible with the database. 

5. **update.py**: a module to wrangle the APIs' to input it into the database. It fetches information about the database and deploy the utils to automate the task.
	* *Internal dependencies*: SmartControl.utils, SmartControl.queries as queries
		* *Functions*:
			* *Update*: Deployment of the SequenceUpdate as batch process
			* *SequenceUpdate*: Loop over diver's parameters to update the database according to the last date present in there.
			* *InowasLongAPItoSQL*: standalone function to update database form diver data.
		* *Class and methods*:
			* *RL*:
				* *RiverAPItoSQL*: Method to prepare Pegel Alarm sensor data
				* *Update*: update the retrieve data
	* If executed as **__main__**:
		* It updates the database by fetching the last date and updates the text file **LOG_UPDATE.txt** in the 'Data' folder. There, information for all the previous automatic updates are available.
		
5. **Jupyter notebooks**
	* *Resources* :Still not-so-organized files to do a series of tasks.
		* *Files for*:
			* Data analysis and wrangling
			* Testing functions before their deployement
			* Dashboard development
			
	* **Examples.ipynb**: Where you can find examples on how to use **SMARTControl**.
	
	* **app.ipynb**: Dashboard in jupyter notebook.
		
