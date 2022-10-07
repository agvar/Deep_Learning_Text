import sys
import os
import tweepy
from datetime import datetime
import json
import argparse
import boto3
from pathlib import Path
from dotenv import load_dotenv
import configparser

#Streaming class override
class TwitterStreamListener(tweepy.StreamListener):
    def __init__(self,s3_resource,kinesis_client,stream_name,s3_bucket,s3_folder,file_max_tweet=100,collect_max_tweet=10):
        super(TwitterStreamListener,self).__init__()
        self.file_max_tweet=file_max_tweet
        self.tweet_counter=0
        self.data_list=[]
        self.collect_max_tweet=collect_max_tweet
        self.s3_resource=s3_resource
        self.kinesis_client=kinesis_client
        self.stream_name=stream_name
        self.s3_bucket=s3_bucket
        self.s3_folder=s3_folder

    def process_tweet(self,tweet):
        if "extended_tweet" in tweet:
            extended_tweet_text=tweet["extended_tweet"]["full_text"]
        else:
            extended_tweet_text=None
        if "text" in tweet:
            text = tweet["text"]
        else:
            text=None

        if "time_zone" in tweet["user"]:
            time_zone=tweet["user"]["time_zone"]
        else:
            time_zone=None

        data={"tweet_id":tweet["id"],
            "created_at":tweet["created_at"],
            "text":text,
            "extended_tweet_text":extended_tweet_text,
            "source":tweet["source"],
            "user":tweet["user"]["id"],
            "followers_count":tweet['user']["followers_count"],
            "friends_count":tweet['user']["friends_count"],
            "geo_enabled":tweet["user"]["geo_enabled"],
            "time_zone":time_zone,
            "geo":tweet["geo"],
            "coordinates":tweet["coordinates"]

            }
        return(data)

    def save_tweet_s3(self):
        current_ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        s3_file = self.s3_resource.Object(self.s3_bucket, self.s3_folder + current_ts + '.json')
        try:
            return_s3 = s3_file.put(Body=(bytes(json.dumps(self.data_list).encode('UTF-8'))))
            print(f'file {s3_file} saved on S3')
        except:
            print(f"Failed to upload files to s3 bucket :{s3_bucket}")
            sys.exit(1)
        if return_s3['ResponseMetadata']['HTTPStatusCode'] != 200:
            print(f"Failed to upload files to s3 bucket :{s3_bucket}")
            sys.exit(1)

    def push_tweet_stream(self):
        try:
            response_stream = self.kinesis_client.put_record(StreamName=stream_name, Data=json.dumps(self.data_list),PartitionKey='partition_key')

        except Exception as e:
            print(f"Failed writing to stream:{e}")
            sys.exit(1)

        if response_stream['ResponseMetadata']['HTTPStatusCode'] != 200:
            print(f"Failed to push data to stream :{stream_name}")
            sys.exit(1)
        shard_id=response_stream['ShardId']
        shard_sequence=response_stream['SequenceNumber']
        print(f"{len(self.data_list)} records pushed to {shard_id} ,shard sequence{shard_sequence} on {stream_name}")

    def on_status(self,status):
        tweet=status._json
        data=self.process_tweet(tweet)
        self.tweet_counter+=1
        if self.tweet_counter % 1000==0:
            print(f"Processed tweets:{self.tweet_counter}")
        if self.tweet_counter>self.collect_max_tweet:
            return False
        else:
            if len(self.data_list)<self.file_max_tweet:
                self.data_list.append(data)
            if len(self.data_list)==self.file_max_tweet:
                self.save_tweet_s3()
                self.push_tweet_stream()
                self.data_list=[]

    def on_error(self,status_code):
       print(f"Error status code is{status_code}")
       if status_code==420:
            return False
    

def main(API_key, API_secret_key,Access_token, Acess_token_secret,region,stream_name,s3_bucket,s3_folder,stream_filter,stream_language):
    # Authentication and creation of an api object
    auth = tweepy.OAuthHandler(API_key, API_secret_key)
    auth.set_access_token(Access_token, Acess_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
        print("Twitter Authentication OK")
    except Exception as e:
        print(f"Error during authentication{e}")
        sys.exit(1)

    #creating kinesis client and s3 resource
    try:
        kinesis_client=boto3.client('kinesis',region_name=region)
        print("kinesis resource OK")
    except Exception as e:
        print(e)
        sys.exit(1)
    try:
        s3_resource = boto3.resource('s3')
        print("S3 resource OK")
    except Exception as e:
        print(e)
        sys.exit(1)

    print("Creating tweepy listener")
    try:
        twitterstreamlistener=TwitterStreamListener(s3_resource,kinesis_client,stream_name,s3_bucket,s3_folder,args.file_max_tweet,args.collect_max_tweet)
        twitter_stream=tweepy.Stream(auth=api.auth,listener=twitterstreamlistener)
        twitter_stream.filter(track=[stream_filter],languages=[stream_language])
        print("Pushing tweets to stream complete")
    except Exception as e:
        print(f"Error creating tweepy listener : {e}")
        sys.exit(1)

if __name__=='__main__':
    try:
        dotenv_path=Path(__file__).resolve().parents[2]
        load_dotenv()
        API_key=os.getenv('API_key')
        API_secret_key=os.getenv('API_secret_key')
        Access_token=os.getenv('Access_token')
        Acess_token_secret=os.getenv('Acess_token_secret')
    except Exception as e:
        print(f"Error reading from .env file at {dotenv_path}: {e}")
        sys.exit(1)
    
    try:
        config_path=Path(__file__).resolve().parents[2] / 'twitter_streaming.ini'
        config=configparser.ConfigParser()
        config.read(config_path)
        region=config.get('AWS resources','region')
        stream_name=config.get('AWS resources','stream_name')
        entiment_prediction_endpoint=config.get('AWS resources','sentiment_prediction_endpoint')
        s3_bucket=config.get('AWS resources','s3_bucket')
        s3_folder=config.get('AWS resources','s3_folder_input')
        stream_filter=config.get('twitter','stream_filter')
        stream_language=config.get('twitter','stream_language')
        file_max_tweet_limit=int(config.get('twitter','file_max_tweet_limit'))
        collect_max_tweet_limt=int(config.get('twitter','collect_max_tweet_limt'))
    except Exception as e:
        print(f"error reading from {config_path}:{e}")
        sys.exit(1)

    parser=argparse.ArgumentParser()
    parser.add_argument(f'file_max_tweet',help='The maximum number of tweeets to be stored in a file, needs to be less than {file_max_tweet_limit}',type=int)
    parser.add_argument(f'collect_max_tweet',help='The maximum number of tweeets to be collected, needs to be less than {collect_max_tweet_limt}', type=int)
    args=parser.parse_args()

    if args.file_max_tweet>file_max_tweet_limit or args.collect_max_tweet>collect_max_tweet_limt:
        print(f"The maximum tweets to be collected or tweets per file are over the limit ")
        sys.exit(1)
    if args.file_max_tweet>args.collect_max_tweet:
        print(f"The maximum tweets to be collected cannot be greater than the tweets per file.")
        sys.exit(1)

    main(API_key, API_secret_key,Access_token, Acess_token_secret,region,stream_name,s3_bucket,s3_folder,stream_filter,stream_language)






