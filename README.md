# PirnaStudyCase
Study case developed with Nicolás Salazar and Claudia Montecinos to investigate the groundwater flow system in Pirna - Sachsen, Deutschland.

**SMARTControl** was developed to handle sensor's data. The database is currently being stored locally in the file 'Data/database.db'. The package also encompasses functionalities to process real-time data and visualize it as a dashboard. **SMARTControl** is a high-level tool developed specifically to targetthe needs of the project. Therefore, with the functionalities here present, it will not be possible to adapt it to your workflow without changing slightly the source code. However, the functionalities are relatively well documented, easy to understand and dependent on widely-used python packages.


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
		
	* *Open the anaconda prompt*
		* Go to the folder where you cloned the repository (PirnaStudyCase)
		* Create a new environment and install the requirements (as of December 2022):
			* Just type once you're in the folder:
				* conda create --name PirnaStudyCase --file spec-file.txt
				
4. Run the app:
	* If you accomplish the steps above, type:
		* run app.py

## The Database
*The database* is developed using *sqalchemy* models was specifically designed to target monitoring divers but in a way that it also enables the addition of other tables and types of measurements in the future. The models are present in the python module **SMARTControl.CreateDatabase** and can be used if such a task is desired. The database schema is as follows:

![plot](Figures/schema.png)

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
		* *APIDate*
		* *CheckDuplicateEntry*
		* *DiverData*
		* *DiverStatus*
		* *HydroProfile*
		* *Isolines*
		* *LongTimeSeries*
		* *ShortTimeSeries*
		* *MonitoringPointData*
		* *SartEndDate*
		* *Table*
		* *UpdateID*
		* *VariableID*
3. **utils.py**
		* **Dashboard map plotting capabilities**
			* *arrow_head*
			* *Folium_arrows*
			* *Folium_contour*
			* *Folium_map*
		* *Gradient*
		* *InterpolationGradient*
		* *BoundaryCondition*
		* *CompleteMissingDates*
		* *ControlPoints*
		* *DbCon*
		* *TimeToString*
		* *GetMonitoringPointData*
		* *GetDivers*
		* *GetDiverData*
		* *CompleteMissingDates*
		* *Process*
		* *GetVariableID*
		* *Process*
		* *prepare_query*
		* *PrepareIsolines
		
4. **api.py**: a module to access APIs that hinges on two classes. Internal dependencies are: SmartControl.utils and SmartControl.queries.
	* *Inowas
	* *PegelAlarm*
	* Both classes count on the Request method to access the api data after fetching preliminary information in the 'database.db' file.

5. **update.py**: a module to wrangle the APIs' to input it into the database. It fetches information about the database and deploy the utils to automate the task.
	* *Internal dependencies*: SmartControl.utils, SmartControl.queries as queries
		* *Functions*:
			* *InowasLongAPItoSQL*: standalone function to update database form diver data.
			* *SequenceUpdate*: Loop over diver's parameters to update the database according to the last date present in there.
			* *Update*: Deployment of the SequenceUpdate as batch process
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
		