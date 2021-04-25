# INRIX-Datasets
This repository houses all objects associated with the storage, loading, and summarization of data-sets from INRIX (https://inrix.com/). The repository uses branching to archive previous INRIX data-set projects that are no longer compatible with current INRIX data-sets (pre-2017 TMC-based versus XD based projects). The default main branch contains the most recent project. Archived project versions are kept as separate release branches.

## INRIX data-sets location and acquisition
### Pre-2017 INRIX data-sets
Prior to 2017, INRIX data-sets were acquired by SANDAG with limited documentation available at this time. The data-sets are stored as monthly zip archives on SANDAG's network containing two csv files. One file containing the speed data for the month and another the TMC link metadata for the INRIX TMC network for that month. Additionally, SANDAG acquired the geo-spatial locations of TMC links for a pre-2017 (year is un-documented but assumed to be 2016) INRIX TMC network from a third party vendor wherein post-contract the original dataset and documentation were deleted per the agreement. A non-original geo-spatial network of the TMC links altered to conform to SANDAG's highway network (year is un-documented but assumed to be 2016) persists. SANDAG also created a manual lookup of this TMC link network to SANDAG's highway network, and this cross-reference is also saved with limited documentation.

### 2019 INRIX data-sets
INRIX data-sets were acquired by SANDAG's Data Solutions group from INRIX. The data-sets are stored as quarterly zip archives on SANDAG's network along with a shapefile containing all INRIX XD-based segments for the state of California.


## Loading INRIX data-sets
### Pre-2017 INRIX data-sets (Archived as release branch)
The data-sets described are loaded into SANDAG's internal SQL server environment via this project.

Ensure the INRIX SQL objects created by the inrixObjects.sql file in the project sql folder exist in the target database on the SQL server instance of interest specified in the settings.py file located in the python folder. If they do not exist, or it is wished to completely start anew, run the inrixObjects.sql in the target database of interest to drop and create all INRIX related SQL objects.

Create the Python interpreter from the provided environment.yml file located in the Python folder of the project. Set the interpreter as the default Python interpreter associated with this project. Run the Python file main.py from the project python folder. It will sequentially load the INRIX zip archive speed and TMC metadata data-sets located in the file system folder specified in the settings.py file located in the python folder appending geo-spatial information (where it exists) from the tmcGeoPre2017.csv file located in the data folder to the TMC metadata data-sets. Finally, it will load SANDAG's manually created cross-reference file tmcHwyCovXRef2015.csv located in the data folder.

### 2019 INRIX data-sets (Current default branch)
The data-sets described are loaded into SANDAG's internal SQL server environment via this project.

Ensure the INRIX SQL objects created by the inrixObjects.sql file in the project sql folder exist in the target database on the SQL server instance of interest specified in the settings.py file located in the python folder. If they do not exist, or it is wished to completely start anew, run the inrixObjects.sql in the target database of interest to drop and create all INRIX related SQL objects.

Create the Python interpreter from the provided environment.yml file located in the Python folder of the project. Set the interpreter as the default Python interpreter associated with this project. Run the Python file main.py from the project python folder. It will sequentially load the INRIX zip archive speed and XD shape file metadata data-sets (the XD shape file metadata data-set is assumed to be in the project data folder as a zip archive named USA_California.zip) located in the file system folders specified in the main Python file.
