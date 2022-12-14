# PirnaStudyCase
Study case developed with Nicolás Salazar and Claudia Montecinos to investigate the groundwater flow system in Pirna - Sachsen, Deutschland.

## Important files

1. **CreateDatabase.py**
	* Database tables and connections created as classes and models
	* If executed and .db is non existent, it creates a database
2.	**Functions.py**
	* Class Handles (data wrandling and retrieval)
		* *TimeToString*
		* *GetMonitoringPointData*
		* *GetDivers*
		* *GetDiverData*
		* *CompleteMissingDates*
		* *Process*
		* *GetVariableID*
		* *CheckDuplicaEntry*
		* *GetAPIDate*
		* *GetUpdateID*
	* Instances of Handles for database update: LongUpdateDiverData and UpdateRiverData (instances from Handles)
		* Batch functions to automatically update the database
			* *Process*
			* *Request*
			* *Update*
		* Batch functions deployment.
			* *RiverAPItoSQL* : standalone function to update database form river data
			* *SequenceUpdate* : Loop over diver's parameters to update the database according to the last date present in there.
			* *InowasLongAPItoSQL* : Loop over sensors to deploy *SequenceUpdate* as a batch process
	* If executed as **__main__**:
		* it updates the database by fetching the last date and updates the text file LOG_UPDATE in the 'Data' folder. There, information for all the previous automatic updates are available.
		

3.	**InputDatabase.py**
	* Function to input the database from tables that were preparede in the folder Data/Tables
	
4. **Querying.py**
	* Classes to retrieve dataas a pandas dataframe. For improving performance of the dashboard, the retrieved dataframes are stored within the attribute **Runs** withing each class.
		* *HydroProfile* : retrieve the drilling tests as a long dataframe
		* *Isolines* : retrieve head data for a giver year, month, day and hour
		* *TimeSeries* : retrieve the entire data for a given variable	

5. **Jupyter notebooks**
	* Still not-so-organized files to do a series of tasks.
	* Files for:
		* Data analysis and wrangling
		* Testing functions before their deployement
		* Dashboard development
		