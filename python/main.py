import os
import pandas as pd
import settings  # import user created settings file
from zipfile import ZipFile


# load the INRIX TMC geometry file to get the TMC WKT geometry ----
# the year of the TMC network is currently unknown and was
# created in 2016 with limited documentation
tmcGeo = pd.read_csv("../data/tmcGeo2016.csv")


# load all zip files in the data folder ----
# into their respective PeMS SQL object
for root, dirs, files in os.walk(settings.folder):
    # for each file in the data folder
    for file in files:
        print("Loading: " + file)
        path = os.path.join(root, file)

        # for each file in the data folder
        if not file.endswith(".zip"):
            pass  # ignore non-zip files
        else:
            with ZipFile(path) as zipfile:  # within the zip archive
                # extract speed data to data folder
                speedCsv = file.rstrip(".zip") + ".csv"
                speedPath = os.path.join(root, speedCsv)
                zipfile.extract(member=speedCsv, path=root)

                # bulk insert speed data to SQL Server
                with settings.conn.cursor() as cursor:
                    sql = "BULK INSERT [inrix].[speed_data_pre2017] FROM '" + \
                          os.path.realpath(speedPath) + "' " + \
                          "WITH (FIRSTROW = 2, TABLOCK, CODEPAGE = 'ACP', " + \
                          "FIELDTERMINATOR=',', ROWTERMINATOR='0x0a');"
                    cursor.execute(sql)
                    cursor.commit()

                # remove extracted speed data
                os.remove(speedPath)

                print("Loaded: Speed data-set")

                # for the TMC metadata
                with zipfile.open("TMC_Identification.csv") as tmcData:
                    # read in TMC metadata as a pandas DataFrame
                    df = pd.read_csv(tmcData)

                    # add date column indicating metadata reference date
                    # zip archive naming convention is year_month_<<weekday/weekend>>.zip
                    df["metadata_date"] = pd.to_datetime(file[0:4] + "-" + file[5:7] + "-01")

                    # merge TMC geometry shape file with metadata table
                    df = df.merge(right=tmcGeo,
                                  how="left",
                                  left_on="tmc",
                                  right_on="tmc_code")

                    # load pandas DataFrame to temporary table
                    df.to_sql(name="tempMetadata",
                              schema="inrix",
                              con=settings.engine,
                              if_exists="replace",
                              index=False)

                    # insert to TMC metadata table transforming WKT to geometry
                    # and drop the temporary table
                    with settings.conn.cursor() as cursor:
                        sql = "INSERT INTO [inrix].[tmc_metadata_pre2017] " \
                              "SELECT [metadata_date],[tmc],[road],[direction]," \
                              "[intersection],[state],[county],[zip]," \
                              "[miles],[road_order]," \
                              "geometry::STGeomFromText([shape], 2230).MakeValid() " \
                              "FROM [inrix].[tempMetadata]; " \
                              "DROP TABLE [inrix].[tempMetadata]"
                        cursor.execute(sql)
                        cursor.commit()

                    print("Loaded: TMC Metadata")


# load the manually created cross-reference between the 2016 ----
# INRIX TMC geometry and SANDAGs 2016 highway coverage
# note this assumes the SQL instance can see this projects location
with settings.conn.cursor() as cursor:
    sql = "BULK INSERT [inrix].[highway_coverage_xref_pre2017] FROM '" + \
          os.path.realpath("../data/tmcHwyCovXRef2016.csv") + "' " + \
          "WITH (FIRSTROW = 2, TABLOCK, CODEPAGE = 'ACP', " + \
          "FIELDTERMINATOR=',', ROWTERMINATOR='0x0a');"
    cursor.execute(sql)
    cursor.commit()
