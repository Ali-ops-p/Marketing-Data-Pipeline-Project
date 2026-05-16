-- Join customers with geography to get location details
SELECT 
	c.CustomerID,
	c.CustomerName,
	c.Email,
	c.Gender,
	c.Age,
	g.Country,
	g.City
FROM dbo.customers c
LEFT JOIN geography g ON c.GeographyID = g.GeographyID