# Mapa de armonización de categorías. clave = etiqueta actual, valor = canónica.
# None = se deja como está.
MAPA = {
 "remote sensing":"Remote sensing",
 "time series":"Time series", "aggregation":"Time series", "DTW":"Time series",
 "Spatio-temporal analysis":"Time series",
 "rodents":"Rodents", "colilargo":"Rodents", "reservoirs":"Rodents",
 "population dynamics":"Population dynamics", "Abundance":"Population dynamics",
 "phenology":"Population dynamics",
 "habitat use":"Habitat use",
 "public health":"Public health",
 "gis":"GIS", "gdal":"GDAL",
 "Machine Learning":"Machine learning", "machine learning":"Machine learning",
 "mosquito":"Mosquitoes", "Mosquito":"Mosquitoes",
 "invasive species":"Invasive species", "Invasive plants":"Invasive species",
 "outbreak":"Outbreaks", "outbreaks":"Outbreaks",
 "Arbovirus":"Arboviruses", "West Nile Fever":"Arboviruses",
 "clustering":"Clustering", "spatial clustering":"Clustering", "hotspots":"Clustering",
 "SDM":"Species distribution models", "ENM":"Species distribution models",
 "Ecological niche modeling":"Species distribution models",
 "Habitat suitability":"Species distribution models", "MaxEnt":"Species distribution models",
 "LULC":"Land use / land cover", "LULCC":"Land use / land cover",
 "LST":"Land surface temperature",
 "OBIA":"Image analysis", "Computer vision":"Image analysis", "VHR":"Image analysis",
 "GRASS GIS":"GRASS", "TGRASS":"GRASS", "add-on":"GRASS", "pymodis":"GRASS",
 "Dengue Fever":"Dengue",
 "Hantavirus pulmonary syndrome":"Hantavirus", "Rodent-borne viruses":"Hantavirus",
 "modeling":"Modeling", "Mathematical modeling":"Modeling",
 "Process-based models":"Modeling", "theory-based models":"Modeling",
 "zero-inflated":"Modeling", "bayesian":"Modeling", "Forecast":"Modeling",
 "open source":"FOSS4G", "OSGeo":"FOSS4G", "software development":"FOSS4G",
 "Open Data":"FOSS4G", "Operative systems":"FOSS4G", "operational":"FOSS4G",
 "Landsat-8":"Landsat",
 "Chlorophyll-a":"Ocean color", "blooms":"Ocean color", "ocean color":"Ocean color",
 "asthma":"Air pollution", "allergic rhinitis":"Air pollution", "air pollution":"Air pollution",
 "essential biodiversity variables":"Biodiversity monitoring",
 "biodiversity monitoring":"Biodiversity monitoring",
 "Species assemblages":"Biodiversity monitoring",
 "zoonosis":"Disease ecology", "Eco-epidemiology":"Disease ecology",
 "disease ecology":"Disease ecology",
 "Vector":"Vector-borne diseases", "Urban vector":"Vector-borne diseases",
 "Vector-borne disease":"Vector-borne diseases", "Mosquito-borne disease":"Vector-borne diseases",
 "NTD":"Vector-borne diseases",
 "Phlebotominae surveillance":"Surveillance", "Ovitraps":"Surveillance",
 "Prevention":"Surveillance",
 "risk":"Risk mapping", "risk stratification":"Risk mapping",
 "Predictive mapping":"Risk mapping", "Fire risk":"Risk mapping", "Exposure":"Risk mapping",
 "Southern cone":"South America", "Latin American and the Caribbean":"South America",
 "Patagonia":"Argentina",
 "sandflies":"Sandflies", "ticks":"Ticks",
 "Genotype diversity":"Genetics", "genetics":"Genetics",
 "Temperature":"Climate", "evapotranspiration":"Climate",
 "Mother-to-child transmission":"Chagas", "EMTCT plus":"Chagas",
 "cholera":"Cholera", "tutorial":"Tutorial",
 # decisiones que dejo señaladas y NO aplico:
 #   "Sentinel-2"  → sensor distinto de Landsat, queda aparte
 #   "Argentine Hemorrhagic Fever" → arenavirus, no hantavirus; queda aparte
 #   "SDG" → demasiado general para plegarlo a Public health; queda aparte
}

# Etiquetas que se eliminan del sitio (decisión de Vero, 1-sep-2026).
# Al eliminar la canónica se van también todas las formas que la alimentaban:
# p.ej. FOSS4G se lleva open source, OSGeo, Open Data, Operative systems,
# operational y software development.
BORRAR = {
    "Cholera", "Malaria", "SDG",
    "Argentina", "South America", "Europe",      # lugares
    "FOSS4G", "GDAL", "R", "Tutorial", "Workshop",
}
