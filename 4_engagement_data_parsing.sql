SELECT 
	EngagementID,
	ContentID,
	CampaignID,
	ProductID,
	-- Clean up ContentType by replacing 'Socialmedia' with 'Social Media' and converting to uppercase
	UPPER(REPLACE(ContentType, 'Socialmedia', 'Social Media')) AS ContentType,
	-- Split ViewsClicksCombined into separate Views and Clicks columns
	LEFT(ViewsClicksCombined, CHARINDEX('-', ViewsClicksCombined) -1) AS Views,
	RIGHT(ViewsClicksCombined, LEN(ViewsClicksCombined) - CHARINDEX('-', ViewsClicksCombined)) AS Clicks,
	Likes,
	-- Format EngagementDate to 'yyyy.MM.dd'
	FORMAT(CONVERT(DATE, EngagementDate), 'dd.MM,yyyy') AS EngagementDate
FROM dbo.engagement_data
-- Filter out records where ContentType is 'Newsletter'
WHERE ContentType != 'Newsletter'
