# dirt (tycho viewer)

For too long, the power generation sector has obscured, under reported, or failed to track smoke-stack emissions from the 4,693 fossil-fueled power plants in the world. Despite the fact that the power sector is responsible for roughly a third of total human-caused greenhouse gas emissions, data attributing emissions to specific plants or days of operation has historically not been tracked. This project was founded on the belief that a small number of large, dirty power plants are likely responsible for a significant proportion of cumulative power sector emissions. With knowledge of where these plants are policy makers, activists, and regulators may be better equipped to scrutinize the impact the oversized contribution towards climate change they are causing. Dirtiest Power Plants uses new multi-spectral satellite data sources along with a sophisticated machine learning model and robust data sources to provide and independent solution to this problem.

This repository hosts a web app (www.dirtiestpowerplants.com) showcasing some of the results from [Tycho](www.github.com/skoeb/tycho), a power sector emission monitoring model, capable of predicitng daily CO2, NOX, and SO2 emissions for every power plant in the world. 

Key views on the web app include:
- A bubble map of the every power plant in the world by 2019 emissions.
- Table ranking every country in the world by 2019 emissions. 
- Lookup cards for the dirtiest power plants in a given country.
- A data explorer page that will serve as a dashboard.
- Additional details and methodology about Tycho. 

The web app is built using Flask, with jQuery for interactive components loading data from PostgreSQL to populate Plotly charts.

