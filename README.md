# PirnaStudyCase
Study case developed with Nicolás Salazar and Claudia Montecinos to investigate the groundwater flow system in Pirna - Sachsen, Deutschland.

## Important files for the database - update 20221028

1. Data/Groundwater levels/GWLDatabase.csv
* This is the database with relative values whereby G data wells are stored as depth to groundwater and GWM, as water column above diver
* When deploying the algorithms, we need to convert it to hydraulic heads
* Groundwater temperature is also present in G wells
2. Data/Groundwater levels/WellsCoords.csv
* Well coordinates with the altitude of the cases
* Filter depth is still missing here
3. OrganizeWaterLevels.ipynb
* The file that was used to generate the database.csv is 