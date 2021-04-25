# INRIX-Datasets
This repository houses all objects associated with the storage, loading, and summarization of data-sets from INRIX (https://inrix.com/).

## INRIX data-sets location and acquisition
### Pre-2017 INRIX data-sets
Prior to 2017, INRIX data-sets were acquired by SANDAG with limited documentation available at this time. The data-sets are stored as monthly zip archives on SANDAG's network containing two csv files. One file containing the speed data for the month and another the TMC link metadata for the INRIX TMC network for that month. Additionally, SANDAG acquired the geo-spatial locations of TMC links for a pre-2017 (year is un-documented but assumed to be 2016) INRIX TMC network from a third party vendor wherein post-contract the original dataset and documentation were deleted per the agreement. A non-original geo-spatial network of the TMC links altered to conform to SANDAG's highway network (year is un-documented but assumed to be 2016) persists. SANDAG also created a manual lookup of this TMC link network to SANDAG's highway network, and this cross-reference is also saved with limited documentation.

## Loading INRIX data-sets
### Pre-2017 INRIX data-sets
The data-sets described above are loaded into SANDAG's internal SQL server environment via this project.

Ensure the INRIX SQL objects created by the inrixObjects.sql file in the project sql folder exist in the target database on the SQL server instance of interest specified in the settings.py file located in the python folder. If they do not exist, or it is wished to completely start anew, run the inrixObjects.sql in the target database of interest to drop and create all INRIX related SQL objects.

Create the Python interpreter from the provided environment.yml file located in the Python folder of the project. Set the interpreter as the default Python interpreter associated with this project. Run the Python file main.py from the project python folder. It will sequentially load the INRIX zip archive speed and TMC metadata data-sets located in the file system folder specified in the settings.py file located in the python folder appending geo-spatial information (where it exists) from the tmcGeo2016.csv file located in the data folder to the TMC metadata data-sets. Finally, it will load SANDAG's manually created cross-reference file tmcHwyCovXRef2016.csv located in the data folder.
