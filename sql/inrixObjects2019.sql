/*
Removes all INRIX objects and re-creates them. Do not run unless intention
is to drop all INRIX data objects. 
*/
SET NOCOUNT ON
GO


/*****************************************************************************/
-- remove all INRIX objects
-- commented out for safety
--DROP TABLE IF EXISTS [speed_inrix].[speed_data_15min]
--DROP SCHEMA IF EXISTS [speed_inrix]
--GO


/*****************************************************************************/
-- create INRIX schema and tables

-- schemas
CREATE SCHEMA [speed_inrix]
GO


-- INRIX speed dataset 2019 15 min data
CREATE TABLE [speed_inrix].[speed_data_15min](
	[Date_Time] [datetimeoffset](0) NOT NULL,
	[Segment_ID] [int] NOT NULL,
	[UTC_Date_Time] [datetimeoffset](0) NOT NULL,
	[Speed(km/hour)] [float] NULL,
	[Hist_Av_Speed(km/hour)] [float] NULL,
	[Ref_Speed(km/hour)] [float] NOT NULL,
	[Travel_Time(Minutes)] [float] NULL,
	[CValue] [float] NULL,
	[Pct_Score30] [float] NULL,
	[Pct_Score20] [float] NULL,
	[Pct_Score10] [float] NULL,
	[Road_Closure] [char](1) NOT NULL,
	[Corridor/Region Name] [varchar](50) NOT NULL,
	[vintage_id] [int] NOT NULL,
	INDEX [ccsi_speed_data_15min] CLUSTERED COLUMNSTORE
) ON [PRIMARY]
GO