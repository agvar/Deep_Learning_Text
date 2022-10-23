![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white) ![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=for-the-badge&logo=TensorFlow&logoColor=white) ![Keras](https://img.shields.io/badge/Keras-%23D00000.svg?style=for-the-badge&logo=Keras&logoColor=white)

# Twitter Sentiment Prediction

## Description

The project was created as part of the Springboard Machine Learning Bootcamp capstone project.  
It predicts the sentiment ( positive, negetive,neutral ) on real-time tweets ,read using the tweepy API with a python Producer process.The tweets are pushed into a Kinesis data stream from where a a consumer python process reads thm and calls the prediction API to predict the sentiment.  
The API is a TensorFlow Serving application that uses a BERT model and a classifier layer on top to make predictions. The response predications are displayed on a Streamlit dashboard to depict trends.  
The twitter topic to be used when pulling tweets can be configured ,along with the number of tweets to be pulled, at a time.
The raw tweets and the predictions are stored on AWS S3 as json files

## Table of Contents

- [Installation](#installation)
- [Process Flow](#process-flow)
- [Data Analysis](#data-analysis)
- [Project Organization](#project-organization)
- [Credits](#credits)
- [License](#license)

## Installation

Clone the repository
`git clone git@github.com:agvar/Deep_Learning_Text.git`

#### Data Collection, Preparation,Model selection, Model training

The final model used , is trained in the following notebook which uses BERT+ classification layer to predict Positive,Negetive and Neutral sentiment, trained on the airline tweet sentiment dataset()
This used the BERT model from the tensorflow hub

[Notebook for Analysis using BERT+classifier for Postive ,Negetive and Neutral sentiment](https://github.com/agvar/Deep_Learning_Text/blob/5810ef018688c973ec6594b9bc29ed8def713692/deep_learning_DS/notebooks/Deep_Learning_BERT_Sentiment_Analysis_keras_v3.ipynb)

Other models that were considered are as follows:
The previous model used , is trained in the following notebook which uses BERT+ classification layer to predict Positive,and Negetive sentiment trained on the twitter 140 sentiment data()

[Notebook for initial Analysis](https://github.com/agvar/Deep_Learning_Text/blob/5810ef018688c973ec6594b9bc29ed8def713692/deep_learning_DS/notebooks/Deep_Learning_BERT_Sentiment_Analysis_keras.ipynb)

Other models that were considered are as follows:
Detailed analysis , model selection using tensorflow (multiple ways of reading input)
[Notebook for Analysis using BERT+classifier for Postive and Negetive sentiment](https://github.com/agvar/Deep_Learning_Text/blob/5810ef018688c973ec6594b9bc29ed8def713692/deep_learning_DS/notebooks/Deep_Learning_BERT_Sentiment_Analysis_keras_cleaned.ipynb)

Analyse using Hugging Face transformers model with tensorflow:

Analyse using Doc2Vec with gensim

#### Running the Tensor Flow model on local

To install docker: https://docs.docker.com/engine/install/

##### Download the saved tensorflow model from s3 to local.

The folder structure for th saved models on S3 are as follows:

Create a models folder for the model on local
`mkdir models`
Download the model from the s3 location to the models folder on local
`aws s3 cp s3://dataset20200101projectfiles/models/ . --recursive `

`docker run -p 8501:8501 --name sentiment_model --mount type=bind,source=./Deep_Learning_Text/deep_learning_DS/models/sentiment_model,target=/models/sentiment_model -e MODEL_NAME=sentiment_model -t tensorflow/serving:2.8.0`

#### Moving the Tensor Flow model to an EC2 machine and runing it with docker

Login to AWS and create an EC2 instance.  
The one that was used for the project was a Deep Learning AMI GPU TensorFlow 2.10.0 on Amazon Linux, which had most of the deep learning libraries and docker pre-installed.

Connect to the instance using the EC2 key-pair  
`ssh -i "path/.ssh/<ec2keypair>" ec2-user@<public dns> `

Update the packages on the EC2 instance
`-[ec2-user ~]$ sudo yum update -y `  
If Docker is not installed on the EC2 machine, follow the below installation steps:
`[ec2-user ~]$ sudo yum install docker -y `
Start the Docker Service on EC2  
`[ec2-user ~]$ sudo service docker start `

Pull docker image for TensorFlow serving  
`sudo docker pull tensorflow/serving:2.8.0`
(note: When trying to use the latest docker image-tensorflow/serving:latest - a memory error was encountered)

Grant permission to access s3 from ec2:  
https://aws.amazon.com/premiumsupport/knowledge-center/ec2-instance-access-s3-bucket/

Copy the model from s3 to ec2  
`aws s3 cp s3://dataset20200101projectfiles/models/ . --recursive `
(Note: When trying to access the s3 location of the saved model,we encountered an error with tensorflow having access issues with S3)

Run the following Docker container run command , using 8501 as the port

`docker run -p 8501:8501 --name sentiment_model --mount type=bind,source=//e//python_projects/Deep_Learning_Text/deep_learning_DS/models/sentiment_model,target=/models/sentiment_model -e MODEL_NAME=sentiment_model -t tensorflow/serving:2.8.0`

Add port 8501 in the security group for inbound traffic from local machine

To install the twitter consumer and producer

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

## Credits

https://ileriayo.github.io/markdown-badges/

## License

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
