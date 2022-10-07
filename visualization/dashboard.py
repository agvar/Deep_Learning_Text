import streamlit as st
import pandas as pd
import numpy as np
import configparser
from pathlib import Path
import sys
import boto3
import io
from datetime import datetime
from botocore.errorfactory import ClientError
import json
import traceback
import seaborn as sns
import matplotlib.pyplot as plt
import time


def get_latest_ts_s3(s3_bucket,file_loc_ts_s3) :
    '''
    Retrieves the latest processed timestamp that was saved to file
    '''
    try:
        s3_resource.Object(s3_bucket,file_loc_ts_s3).load()    
        s3_file_ts=s3_resource.Object(s3_bucket,file_loc_ts_s3)
        ts_latest_s3=datetime.strptime(s3_file_ts.get()['Body'].read().decode('utf-8'),'%Y-%m-%d %H:%M:%S') 
    except ClientError: 
        print(f"s3 latest timestamp not found , using default date of {default_ts}")
        ts_latest_s3=datetime.strptime(default_ts,'%Y-%m-%d %H:%M:%S') 
    return ts_latest_s3


def get_dfs_s3(s3_bucket,s3_file_day_df,s3_file_month_df,s3_file_source_df) :
    '''
    Retrieves the latest dataframes that were saved to file
    '''
    try:
        file_day_df=s3_file_day_df.get()['Body'].read().decode('utf-8')
        file_month_df=s3_file_month_df.get()['Body'].read().decode('utf-8')
        file_source_df=s3_file_source_df.get()['Body'].read().decode('utf-8')
    except ClientError: 
        print(f"older version of dataframes not found, using defaults")
        file_day_df=pd.DataFrame(columns=['model_api_sentiment','created_day','count'])
        file_month_df=pd.DataFrame(columns=['model_api_sentiment','created_month','count'])
        file_source_df=pd.DataFrame(columns=['model_api_sentiment','source_cleaned','count'])
    return ts_latest_s3

def save_latest_ts_s3(s3_file_ts,latest_ts_updated):
    '''
    Saves latest processed timestamp  to file
    '''
    if s3_file_ts and latest_ts_updated:
        try:
                latest_ts_updated_bytes=datetime.strftime(latest_ts_updated,'%Y-%m-%d %H:%M:%S').encode('utf-8')
                s3_file_ts.put(Body=latest_ts_updated_bytes)
                print(f"latest timestamp updated is {s3_file_ts.get()['Body'].read().decode('utf-8')}")
        except ClientError as e:
                print(f"Unable to save timestamp file -{e}")
    else:
        print("no file to save")

def save_df_as_files():
        try:
                latest_ts_updated_bytes=datetime.strftime(latest_ts_updated,'%Y-%m-%d %H:%M:%S').encode('utf-8')
                s3_file_ts.put(Body=latest_ts_updated_bytes)
                print(f"latest timestamp updated is {s3_file_ts.get()['Body'].read().decode('utf-8')}")
        except ClientError as e:
                print(f"Unable to save timestamp file -{e}")



def create_latest_dffiles(ts_latest_s3):   
    '''
    reads incremental file into a dataframe. The last_modified time of the file is compared to the saved timestamp,
    to determine if the file needs to be read from.
    Creates dataframe and charts on incremental data
    '''
    ts_list=[]
    counter=0
    df_filelist=pd.DataFrame(columns=columns)
    print(f"latest timestamp : {ts_latest_s3}")

    for file in s3_resource.Bucket(s3_bucket).objects.filter(Prefix=s3_folder):
        file_last_mod_ts=file.last_modified.replace(tzinfo = None)
        if file_last_mod_ts > ts_latest_s3:           
            try:
                data=file.get()['Body'].read()
                if data:
                    json_data=json.loads(data)
                    df=pd.DataFrame(json_data)
                    df_filelist=pd.concat([df,df_filelist])
                    ts_list.append(file_last_mod_ts)
                    counter+=1
            except Exception as e:
                print(f"Error reading file: {e}")
    
    if not df_filelist.empty:
        latest_ts_updated=ts_list[-1] 
        with placeholder.container():
            #create dataframe and values
            df_filelist['created_day']= pd.to_datetime(df_filelist.created_at).dt.date
            df_filelist['created_month']= pd.to_datetime(df_filelist.created_at).dt.month
            df_sentiment_day=df_filelist.groupby(['model_api_sentiment','created_day'])['tweet_id'].agg(['count']).reset_index() 
            df_sentiment_month=df_filelist.groupby(['model_api_sentiment','created_month'])['tweet_id'].agg(['count']).reset_index() 
            df_source=df_filelist.groupby(['source_cleaned'])['tweet_id'].agg(['count']).reset_index() 
            #add counts from previous runs
            df_sentiment_day=df_sentiment_day.add


            total_tweets=len(df_filelist)
            postive_tweets=len(df_filelist[df_filelist['model_api_sentiment']=='Positive'])
            negetive_tweets=len(df_filelist[df_filelist['model_api_sentiment']=='Negetive'])
            total_days= df_filelist['created_day'].nunique()   
            source_list= df_filelist['source_cleaned'].unique()
            
            #add KPIs for total tweets and total negetive and positive tweets  

            kpi1, kpi2, kpi3,kpi4 = st.columns(4)       
            kpi1.metric(label="Total Tweets",value=int(total_tweets),delta=10)        
            kpi2.metric(label="Postive Tweets",value=int(postive_tweets),delta=10 )
            kpi3.metric(label="Negetive Tweets",value=int(negetive_tweets),delta=-10)
            kpi4.metric(label="Days Tweets collected",value=int(total_days),delta=10)
            # add charts and tables
            fig_col1, fig_col2 = st.columns(2)

            with fig_col1:
                st.markdown("### Tweet Sentiment by Day")
                fig1=plt.figure(figsize=(10,4))
                sns.lineplot(data=df_sentiment_day, x='created_day', y='count', hue='model_api_sentiment')
                st.pyplot(fig1)
                st.markdown("### Tweets Sentiment by Month table ")
                st.table(df_sentiment_month[['created_month','model_api_sentiment','count']])
            
            with fig_col2:
                st.markdown("### Tweets by Source")
                fig2,ax=plt.subplots(figsize=(10,4))
                ax.hist(x=df_filelist['source_cleaned'])
                st.pyplot(fig2)
                st.markdown("### Tweets by source ")
                st.table(df_source)
        return latest_ts_updated
    else:
        print(f"No file in s3 location : {s3_bucket}/{s3_folder} after latest timestamp of {ts_latest_s3}")
        return None,None

#main

st.set_page_config(
        page_title="Dashboard for Tweet Sentiment",
        page_icon="✅",
        layout="wide",
        )
st.title("Dashboard for tweet Sentiment")
placeholder = st.empty()

config_path=Path(__file__).resolve().parents[0] / 'dashboard.ini'
s3_resource=boto3.resource('s3')
default_ts='1973-01-01 00:00:00'
columns=['tweet_id', 'created_at', 'text', 'extended_tweet_text', 'source','user', 'followers_count', 'friends_count', 'geo_enabled', 'time_zone','geo', 'coordinates','model_api_sentiment','source_cleaned']

try:
        config=configparser.ConfigParser()       
        config.read(config_path)
        region=config.get('AWS resources','region')
        s3_bucket=config.get('AWS resources','s3_bucket')
        s3_folder=config.get('AWS resources','s3_folder_output')
        file_loc_ts_s3=config.get('AWS resources','file_loc_ts_s3')
        file_loc_day_df=config.get('AWS resources','file_loc_day_df')
        file_loc_month_df=config.get('AWS resources','file_loc_month_df')
        file_loc_source_df=config.get('AWS resources','file_loc_source_df')
        s3_file_ts=s3_resource.Object(s3_bucket,file_loc_ts_s3)
        s3_file_day_df=s3_resource.Object(s3_bucket,file_loc_day_df)
        s3_file_month_df=s3_resource.Object(s3_bucket,file_loc_month_df)
        s3_file_source_df=s3_resource.Object(s3_bucket,file_loc_source_df)

except Exception as e:
        print(f"error reading from {config_path}:{e}")
        sys.exit(1)
try:
        for seconds in range(200):
            ts_latest_s3=get_latest_ts_s3(s3_bucket,file_loc_ts_s3)
            file_day_df,file_month_df,file_source_df=get_latest_ts_s3(s3_bucket,s3_file_day_df,s3_file_month_df,s3_file_source_df)
            latest_ts_updated=create_latest_dffiles(ts_latest_s3)
            save_df_as_files()
            #save_latest_ts_s3(s3_file_ts,latest_ts_updated)
            print('sleeping')
            time.sleep(30)
            print('waking up')
except Exception as e:
        print(f"error :{e},{traceback.format_exc()}")
        sys.exit(1)


    
