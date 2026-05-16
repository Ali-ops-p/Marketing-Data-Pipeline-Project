-- Classify products into price categories
SELECT 
	ProductID,
	ProductName,
	Price,
CASE 
	WHEN Price < 50 THEN 'Low Price'
	WHEN Price BETWEEN 50 and 200 THEN 'Medium Price'
	ELSE 'High Price'
END AS PriceCategory
FROM dbo.products
