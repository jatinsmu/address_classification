# Conversational Agent for Address Enrichment and Classification

## Description

This project was implemented as a part of a public hackathon.
This project can be used for identifying residential and civic addresses in the Halifax region through an interactive chatbot powered by Google Dialogflow. Machine Learning Classification model is implemented as the backend prediction system for the project which is supplemented by real time web analysis of the address. This project can be deployed using Flask framework.

## Installation

```Python 3+```

### Libraries Used ###
```Pickle``` 
```Numpy```
```Pandas```
```Sklearn```
```requests```
```bs4```
```google_images_download ```
```Flask```

## Usage ##

- ```building_model.ipynb``` file contains the code to build the Machine Learning model which is trained on Open Dataset of Civic and Residential Addresses. The dataset contained in this Github repository is a clean dataset, as a result of previous data cleaning using Excel.
- ```image_text_combined.py``` file serves as the main entry point to the project. It can be hosted as a webhook using Flask Server.
It will take input from the Dialogflow Chatbot, get the prediction results and web results from our process, then it will compare the model results with the web scrapped results and then finally a result which is a combination of both will be displayed to user in the same chatbot window.
- ```TestData_v8.csv``` This is the clean dataset after multiple iterations of data cleaning on MS Excel.
- ```model.pkl``` This is the saved Random Forest model which is used for prediction.
