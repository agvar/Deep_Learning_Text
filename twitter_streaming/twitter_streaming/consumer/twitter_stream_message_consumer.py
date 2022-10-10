import sys
import os
import tweepy
from datetime import datetime
import json
import argparse
import boto3
import requests
import configparser
from pathlib import Path
from dotenv import load_dotenv
from scipy.stats import logistic
import re


def save_tweet_s3(s3_resource,data_list,s3_bucket,s3_folder):
    current_ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    s3_file = s3_resource.Object(s3_bucket, s3_folder + current_ts + '.json')
    return_s3 = s3_file.put(Body=(bytes(json.dumps(data_list).encode('UTF-8'))))
    if return_s3['ResponseMetadata']['HTTPStatusCode'] != 200:
        print(f"Failed to upload files to s3 bucket :{s3_bucket}")
        sys.exit(1)
    print(f'Saved {s3_file} on S3 with {len(data_list)} records')

def read_tweet_stream(s3_resource,kinesis_client,stream_name,sentiment_prediction_endpoint):

    predict_api_headers = {"content-type": "application/json"}
    try:
        response_shards = kinesis_client.list_shards(StreamName=stream_name)
        print(f'Connected to kinesis stream {stream_name} in {region}')
    except Exception as e:
        print(f"Failed to get shards for kinesis stream {stream_name} in {region}:{e}")
        sys.exit(1)

    for shard in response_shards['Shards']:
        try:
            response_shard_iterator=kinesis_client.get_shard_iterator(
                StreamName=stream_name,
                ShardId=shard['ShardId'],
                ShardIteratorType='TRIM_HORIZON'
                )
        except Exception as e:
            print(f"Failed to get shards:{e}")
        ShardId = shard['ShardId']
        ShardIterator=response_shard_iterator['ShardIterator']
        print(f'reading {ShardId} from {stream_name}')
        while ShardIterator:
            data_records=kinesis_client.get_records(ShardIterator=ShardIterator)
            if len(data_records['Records'])>0:                
                for record in data_records['Records']:
                    tweets=json.loads(record['Data'])
                    tweet_list=[]
                    for tweet in tweets:
                        if tweet['extended_tweet_text']:
                            tweet_text=tweet['extended_tweet_text']
                        else:
                            tweet_text = tweet['text']
                    
                        try:
                            data = json.dumps({"signature_name": "serving_default", "instances": [tweet_text]})                          
                            json_response = requests.post(sentiment_prediction_endpoint, data=data, headers=predict_api_headers)
                            sentiment_prediction = json.loads(json_response.text).get('predictions')
                            prediction=logistic.cdf(sentiment_prediction[0][0])
                            if prediction>0.5:
                              predict_out='Positive'
                            else:
                              predict_out='Negative'
                            tweet['model_api_sentiment'] = predict_out
                             
                            source_cleaned=re.match(r'.*>(.*)<.*',tweet['source']).group(1)
                            if 'android' in source_cleaned.lower():
                                tweet['source_cleaned']='Android'
                            elif 'iphone' in source_cleaned.lower():
                                tweet['source_cleaned']='Iphone'
                            elif 'mac' in source_cleaned.lower():
                                tweet['source_cleaned']='Mac'
                            elif 'ipad' in source_cleaned.lower():
                                tweet['source_cleaned']='Ipad'                               
                            else:
                                tweet['source_cleaned']='Web'                             
                                
                            
                        except Exception as e:
                            print(f'unable to post request on {sentiment_prediction_endpoint}  : {e}') 
                            sys.exit(1)
                        tweet_list.append(tweet)
                    
                    save_tweet_s3(s3_resource,tweet_list,s3_bucket,s3_folder)
 
                ShardIterator=data_records['NextShardIterator']
            else:
                break

def main(region,stream_name,sentiment_prediction_endpoint,s3_bucket,s3_folder):
    try:
        kinesis_client=boto3.client('kinesis',region_name=region)
        print(f'connected to kinesis client in {region}')
    except Exception as e:
        print(f'unable to connect to kinesis client: {e}')
        sys.exit(1)
    try:
        s3_resource = boto3.resource('s3')
    except Exception as e:
        print(f'unable to connect to s3: {e}')
        sys.exit(1)
    
    read_tweet_stream(s3_resource,kinesis_client,stream_name,sentiment_prediction_endpoint)

if __name__=='__main__':
    try:
        dotenv_path=Path(__file__).resolve().parents[2]
        load_dotenv()
        API_key=os.getenv('API_key')
        API_secret_key=os.getenv('API_secret_key')
        Access_token=os.getenv('Access_token')
        Acess_token_secret=os.getenv('Acess_token_secret')
    except Exception as e:
        print(f"error reading from .env file at {dotenv_path}: {e}")
        sys.exit(1)
    
    try:
        config_path=Path(__file__).resolve().parents[2] / 'twitter_streaming.ini'
        config=configparser.ConfigParser()
        config.read(config_path)
        region=config.get('AWS resources','region')
        stream_name=config.get('AWS resources','stream_name')
        sentiment_prediction_endpoint=config.get('AWS resources','sentiment_prediction_endpoint')
        s3_bucket=config.get('AWS resources','s3_bucket')
        s3_folder=config.get('AWS resources','s3_folder_output')
    except Exception as e:
        print(f"error reading from {config_path}:{e}")
        sys.exit(1)
    
    main(region,stream_name,sentiment_prediction_endpoint,s3_bucket,s3_folder)
    





