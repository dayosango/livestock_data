# livestock-data-generator

MATCH (animal:animal)-[:born_at]->(site:site)
RETURN site.id AS SiteID, site.site_type AS SiteType, COUNT(animal) AS NumberOfAnimals
ORDER BY SiteID****
