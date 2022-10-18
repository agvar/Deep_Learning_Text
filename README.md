![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)

# Twitter Sentiment Prediction

## Description

The project was created as part of the Springboard Machine Learning Bootcamp capstone project.  
It predicts the sentiment ( positive, negetive,neutral ) on real-time tweets . Tweets are read using the tweepy API with a python Producer process, and pushed into a Kinesis data stream . A consumer python process reads the tweets and calls the prediction API to predict the sentiment.  
The API is a TensorFlow Serving application that uses a BERT model to make predictions. The response predications are displayed on a Streamlit to depict trends.  
The twitter topic to be used when pulling tweets can be configured ,along with the number of tweets to be pulled, at a time.
The raw tweets and the predictions are stored on AWS S3 as json files

## Table of Contents

- [Installation](#installation)
- [Process Flow](#process-flow)
- [Data Analysis](#data-analysis)
- [Project Organization](#project-organization)
- [License](#license)

## Installation

To install the prediction api -> (https://github.com/agvar/Deep_learning_Text/blob/master/Prediction_API/README )
To install the twitter consumer and producer ->  
To install the Deep Learning BERT analysis,notebook ,data preprocessing ->

## Process Flow

![Architecture Diagram](https://github.com/agvar/Deep_Learning_Text/blob/759f9643dfa38685bf119824ce07c7ab1086d662/images/deep_learning_project_architecture.jpeg)

## Data Analysis

The analysis done on the twitter train datasets is at : [Data Analysis](https://github.com/agvar/Prediction_Text/blob/2acd88106dab4106de90d4dc10e5608af0af78c7/Sentiment_Prediction_DS/notebooks/Sentiment_analysis.ipynb)

## Project Organization

    ├── LICENSE
    ├── README.md                  <- The top-level README for developers using this project.
    ├── visualization              <- Streamlist dashboard folder
    ├── Deep_Learning_DS           <- Python notebooks ,models folder
    ├── twitter_streaming          <- consumer and producer modules for reading from tweepy and writing to Kineses, S3
    └── images                     <- images,diagrams for the project

## License

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
