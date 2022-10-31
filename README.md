![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white) ![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=for-the-badge&logo=TensorFlow&logoColor=white) ![Keras](https://img.shields.io/badge/Keras-%23D00000.svg?style=for-the-badge&logo=Keras&logoColor=white)

# Twitter Sentiment Prediction (Deep Learning)

## Description

The project is used to predict the sentiment ( positive, negative, neutral ) on real-time tweets, read using the tweepy API with a python Producer process. The tweets are pushed into a Kinesis data stream from where a python Consumer process reads them and invokes the Tensorflow Serving API to predict the sentiment.
The TensorFlow Serving application uses a BERT model and a classifier layer on top to make predictions. The response predictions are displayed on a Streamlit dashboard to depict trends.
The Twitter topic to be used when pulling tweets can be configured, along with the number of tweets to be pulled, at a time. The raw tweets and the predictions are stored on AWS S3 as JSON files.

## Table of Contents

- [Process Flow](#process-flow)
- [Data Collection, Preparation,](#data-collection,-preparation)
- [Model selection, Model training](#model-selection,-Model-training)
- [Installation](#installation)
- [Project Organization](#project-organization)
- [Credits](#credits)
- [License](#license)

## Process Flow

![Architecture Diagram](https://github.com/agvar/Deep_Learning_Text/blob/759f9643dfa38685bf119824ce07c7ab1086d662/images/deep_learning_project_architecture.jpeg)

## Data Collection, Preparation

Datasets used:

1. Sentiment140 Dataset Details  
   **Source** : http://help.sentiment140.com/for-students  
   **Description**: The training data was automatically created, as opposed to having humans manual annotate tweets. In the approach used, any tweet with positive emoticons, like :), were positive, and tweets with negative emoticons, like :(, were negative. We used the Twitter Search API to collect these tweets by using keyword search. This is described in the following paper(https://cs.stanford.edu/people/alecmgo/papers/TwitterDistantSupervision09.pdf) The data is a CSV with emoticons removed.
2. Twitter Airline Sentiment Dataset  
   **Source** -https://www.kaggle.com/crowdflower/twitter-airline-sentiment  
   **Description** :This data originally came from Crowdflower's Data for Everyone library.
   As the original source says,a sentiment analysis job about the problems of each major U.S. airline. Twitter data was scraped from February of 2015 and contributors were asked to first classify positive, negative, and neutral tweets, followed by categorizing negative reasons (such as "late flight" or "rude service").

## Model selection, training

The final model used , is trained in the following notebook which uses BERT+ classification layer to predict Positive,Negetive and Neutral sentiment, trained on the airline tweet sentiment dataset.
This used the BERT model from the tensorflow hub:  
[Notebook for Analysis using BERT+classifier for Postive ,Negetive and Neutral sentiment](https://github.com/agvar/Deep_Learning_Text/blob/5810ef018688c973ec6594b9bc29ed8def713692/deep_learning_DS/notebooks/Deep_Learning_BERT_Sentiment_Analysis_keras_v3.ipynb)

Other models that were considered are as follows:

1. The previous model used , is trained in the following notebook which uses BERT+ classification layer to predict Positive,and Negetive sentiment trained on the twitter 140 sentiment data:  
   [Notebook for initial Analysis](https://github.com/agvar/Deep_Learning_Text/blob/5810ef018688c973ec6594b9bc29ed8def713692/deep_learning_DS/notebooks/Deep_Learning_BERT_Sentiment_Analysis_keras.ipynb)

2. Analysis , model selection using tensorflow (multiple ways of reading input)  
   [Notebook for Analysis using BERT+classifier for Postive and Negetive sentiment](https://github.com/agvar/Deep_Learning_Text/blob/5810ef018688c973ec6594b9bc29ed8def713692/deep_learning_DS/notebooks/Deep_Learning_BERT_Sentiment_Analysis_keras_cleaned.ipynb)

3. Analysis using Hugging Face transformers model with tensorflow:  
   [Notebook for Hugging Face for Postive and Negetive sentiment](https://github.com/agvar/Deep_Learning_Text/blob/master/deep_learning_DS/notebooks/Deep_Learning_BERT_Sentiment_Analysis.ipynb)

4. Analysis using Hugging Face transformers model with tensorflow on Google Colab:  
   [Colab Notebook for Hugging Face for Postive and Negetive sentiment](https://github.com/agvar/Deep_Learning_Text/blob/master/deep_learning_DS/notebooks/Colab_Deep_Learning_BERT_Sentiment_Analysis.ipynb)

5. Analysis using Doc2Vec with gensim  
   [Notebook for Analysis using doc2vec](https://github.com/agvar/Deep_Learning_Text/blob/master/deep_learning_DS/notebooks/Deep_Learning_Doc2vec_Sentiment_Analysis.ipynb)

## Installation

Clone the repository  
`git clone git@github.com:agvar/Deep_Learning_Text.git`

#### Running the Tensor Flow model on local

To install docker: https://docs.docker.com/engine/install/

##### Download the saved tensorflow model from s3 to local.

The folder structure for the saved tensorflow models on S3 are as follows:

    ├── dataset20200101projectfiles
        ├── models
            ├── sentiment_model
                ├──1                                     <- first sentiment model for only positive and negetive  predictions
                    ├──assets
                       ├──vocab.txt
                    ├──keras_metadata.pb
                    ├──saved_model.pb
                    ├──variables
                       ├──variables.data-00000-of-00001
                       ├──variables.index
                ├──2                                      <- latest sentiment model for positive,negetive and neutral predictions
                    ├──assets
                       ├──vocab.txt
                    ├──keras_metadata.pb
                    ├──saved_model.pb
                    ├──variables
                       ├──variables.data-00000-of-00001
                       ├──variables.index

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

#### Install the AWS Kinesis consumer and producer

`pip install -r requirements.txt`

Modify the ./twitter_streaming/twitter_streaming.ini file as needed to update the following:  
`stream_filter` ->set the filter on tweets to be processed  
`stream_language` -> sets the tweet language to look for  
`file_max_tweet_limit` -> maximum of tweets to be processed into a single json file  
`collect_max_tweet_limt` -> maximum of tweets to be processed on a single run.

**To execute Producer process**  
`python ./twitter_streaming/twitter_streaming/producer/twitter_stream_message_producer.py`

**To execute Consumer process**
`python ./twitter_streaming/twitter_streaming/consumer/twitter_stream_message_consumer.py`
The consumer process reads tweets from Kinesis and calls the tensorFlow api to make predictions and stores them on s3.

#### To run the dashboard using Streamlit

For installation steps for Streamlit on windows -> [ Streamlit installation ](https://github.com/agvar/Deep_Learning_Text/blob/master/visualization/readme.md)
For windows,in the Anaconda Navigator terminal that appears :
`streamlit run dashboard.py`

## Project Organization

    ├── LICENSE
    ├── README.md                  <- The top-level README for developers using this project.
    ├── visualization              <- Streamlist dashboard folder
    ├── Deep_Learning_DS           <- Python notebooks ,models folder
    ├── twitter_streaming          <- consumer and producer modules for reading from tweepy and writing to Kineses, S3
    └── images                     <- images,diagrams for the project

## Credits

https://ileriayo.github.io/markdown-badges/  
https://docs.docker.com/engine/install/

## License

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
