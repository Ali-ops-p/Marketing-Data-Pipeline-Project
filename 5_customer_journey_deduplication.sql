/*
 -- CTE to get show the duplicated records in the customer_journey table
WITH DuplicateRecords AS (
SELECT 
	JourneyID,
	CustomerID,
	ProductID,
	VisitDate,
	Stage,
	Action,
	Duration,
	-- Checking Duplicates Orders
	ROW_NUMBER() OVER(PARTITION BY CustomerID, ProductID, VisitDate, Stage, Action ORDER BY JourneyID) AS row_num
FROM dbo.customer_journey)

-- Know the duplicated records on the table
SELECT *
FROM DuplicateRecords
WHERE row_num > 1
ORDER BY JourneyID */

 -- USE Sub-query to get the cleaned Data:
SELECT 
	JourneyID,
	CustomerID,
	ProductID,
	VisitDate,
	Stage,
	Action,
	COALESCE(Duration, Avg_Duration) AS Duration, -- Replace Null Duration with the average duration for that VisitDate
	row_num
FROM (
SELECT 
	JourneyID,
	CustomerID,
	ProductID,
	VisitDate,
	UPPER(Stage) AS Stage, -- UPPER Stage column
	Action,
	Duration,
	AVG(Duration) OVER(PARTITION BY VisitDate) AS Avg_Duration, -- Calculate average duration for each VisitDate
	ROW_NUMBER() OVER(PARTITION BY CustomerID, ProductID, VisitDate, UPPER(Stage), Action ORDER BY JourneyID) AS row_num
	FROM dbo.customer_journey)t
	WHERE row_num = 1 -- Keep only the first occurrence of duplicates