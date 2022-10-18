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
from io import StringIO


def get_latest_ts_s3(s3_bucket,file_loc_ts_s3) :
    '''
    Retrieves the latest processed timestamp that was saved to file
    '''
    global last_procesed_ts
    try:
        s3_resource.Object(s3_bucket,file_loc_ts_s3).load()    
        s3_file_ts=s3_resource.Object(s3_bucket,file_loc_ts_s3)
        last_procesed_ts=datetime.strptime(s3_file_ts.get()['Body'].read().decode('utf-8'),'%Y-%m-%d %H:%M:%S') 
        print(f'last_procesed_ts{last_procesed_ts}')
    except ClientError: 
        print(f"s3 latest timestamp not found , using default date of {default_ts}")
        last_procesed_ts=datetime.strptime(default_ts,'%Y-%m-%d %H:%M:%S') 



def get_dfs_s3() :
    '''
    Reads the dataframes and counts that were saved to file and 
    assigns them as previous dataframes.
    '''
    global prev_df_sentiment_day
    global prev_df_sentiment_month
    global prev_df_source
    #global prev_sentiment_counts
    global prev_day_list
    try:
        prev_df_sentiment_day=pd.read_csv(StringIO(s3_file_day_df.get()['Body'].read().decode('utf-8')))
        prev_df_sentiment_month=pd.read_csv(StringIO(s3_file_month_df.get()['Body'].read().decode('utf-8')))
        prev_df_source=pd.read_csv(StringIO(s3_file_source_df.get()['Body'].read().decode('utf-8')))
    except ClientError: 
        print(f"older version of dataframes files not found, using defaults")
    
    try:
        prev_day_list=pd.read_csv(StringIO(s3_file_day_list.get()['Body'].read().decode('utf-8')))
        prev_day_list=prev_day_list['day'].values.tolist()
    except ClientError: 
        print(f"older version of counts  files not found, using defaults")
   


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

def save_df_as_files(s3_bucket,file_loc,data):
        try:
            csv_buffer = StringIO()
            data.to_csv(csv_buffer)
            s3_resource = boto3.resource('s3')
            s3_resource.Object(s3_bucket, file_loc).put(Body=csv_buffer.getvalue())
            print(f'saving dataframe  {data} as {file_loc}')
        except ClientError as e:
                print(f"Unable to save dataframe {data} to file")

def create_latest_dffiles(counter=-1):   
    '''
    reads incremental file into a dataframe. The last_modified time of the file is compared to the saved timestamp,
    to determine if the file needs to be read from.
    Creates dataframe and charts on incremental data
    '''
    ts_list=[]
    counter=0
    df_filelist=pd.DataFrame(columns=columns)
    global prev_df_sentiment_day
    global prev_df_sentiment_month
    global prev_df_source
    global last_procesed_ts
    global prev_day_list
    global initial_run_flag

    print('starting diff process')
    print(f'check last_procesed_ts{last_procesed_ts}')
    for file in s3_resource.Bucket(s3_bucket).objects.filter(Prefix=s3_folder):
        file_last_mod_ts=file.last_modified.replace(tzinfo = None)
        if file_last_mod_ts > last_procesed_ts:           
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
    print(f'length of filelist df {len(df_filelist)}')
    if not(df_filelist.empty) or (initial_run_flag ):
        print('entering df and rensing calc')
        if not(df_filelist.empty):  
            last_procesed_ts=ts_list[-1] 
        print(f'assign last_procesed_ts{last_procesed_ts}')
        check_new_files_flag=1
        with placeholder.container():
            #create dataframe and values
            df_filelist['created_day']= pd.to_datetime(df_filelist.created_at).dt.date
            df_filelist['created_month']= pd.to_datetime(df_filelist.created_at).dt.strftime("%y-%m")


            df_sentiment_day=df_filelist.groupby(['model_api_sentiment','created_day'])['tweet_id'].agg(['count']).reset_index().rename(columns={'count':'sum'})
            df_sentiment_month=df_filelist.groupby(['model_api_sentiment','created_month'])['tweet_id'].agg(['count']).reset_index().rename(columns={'count':'sum'})
            df_source=df_filelist.groupby(['source_cleaned'])['tweet_id'].agg(['count']).reset_index().rename(columns={'count':'sum'})

            #calculate previous counts 
            if prev_df_sentiment_month.empty:
                prev_total_tweets_count,prev_postive_tweets_count,prev_negetive_tweets_count,prev_neutral_tweets_count=0,0,0,0
            else:
                prev_total_tweets_count=prev_df_sentiment_month['sum'].sum()
                prev_postive_tweets_count=prev_df_sentiment_month[prev_df_sentiment_month['model_api_sentiment']=='Positive']['sum'].sum()
                prev_negetive_tweets_count=prev_df_sentiment_month[prev_df_sentiment_month['model_api_sentiment']=='Negative']['sum'].sum()
                prev_neutral_tweets_count=prev_df_sentiment_month[prev_df_sentiment_month['model_api_sentiment']=='Neutral']['sum'].sum()
            if prev_df_sentiment_day.empty:
                prev_total_day_count=0
            else:
                prev_total_day_count= len(prev_day_list)


            #concat latest dataframe to previous dataframes 
            df_sentiment_day=pd.concat([df_sentiment_day,prev_df_sentiment_day])
            df_sentiment_day=df_sentiment_day.groupby(['model_api_sentiment','created_day'])['sum'].agg(['sum']).reset_index() 
            df_sentiment_month=pd.concat([df_sentiment_month,prev_df_sentiment_month])
            df_sentiment_month=df_sentiment_month.groupby(['model_api_sentiment','created_month'])['sum'].agg(['sum']).reset_index() 
            df_source=pd.concat([df_source,prev_df_source])
            df_source=df_source.groupby(['source_cleaned'])['sum'].agg(['sum']).reset_index() 

            #assign prev datframes to current
            prev_df_sentiment_day=df_sentiment_day
            prev_df_sentiment_month=df_sentiment_month
            prev_df_source=df_source

            #calculate total counts 
            total_tweets_count=df_sentiment_month['sum'].sum()
            postive_tweets_count=df_sentiment_month[df_sentiment_month['model_api_sentiment']=='Positive']['sum'].sum()
            negetive_tweets_count=df_sentiment_month[df_sentiment_month['model_api_sentiment']=='Negative']['sum'].sum()
            neutral_tweets_count=df_sentiment_month[df_sentiment_month['model_api_sentiment']=='Neutral']['sum'].sum()
            total_days= df_sentiment_day['created_day'].unique().tolist()
            for day in prev_day_list:
                total_days.append(day)
            total_days=list(set(total_days))
            total_days_count=len(set(total_days))
            prev_day_list= total_days
            
            
            #add KPIs for total tweets and total negetive and positive tweets  
            kpi1, kpi2, kpi3,kpi4,kpi5 = st.columns(5)       
            kpi1.metric(label="Total Tweets",value=int(total_tweets_count),delta=int(total_tweets_count-prev_total_tweets_count))        
            kpi2.metric(label="Postive Tweets",value=int(postive_tweets_count),delta=int(postive_tweets_count- prev_postive_tweets_count))
            kpi3.metric(label="Negative Tweets",value=int(negetive_tweets_count),delta=int(negetive_tweets_count-prev_negetive_tweets_count))
            kpi4.metric(label="Neutral Tweets",value=int(neutral_tweets_count),delta=int(neutral_tweets_count-prev_neutral_tweets_count))
            kpi5.metric(label="Days Tweets collected",value=int(total_days_count),delta=int(total_days_count-prev_total_day_count))
            # add charts and tables
            fig_col1, fig_col2 = st.columns(2)

            with fig_col1:
                st.markdown("### Tweet Sentiment by Month")
                fig1=plt.figure()
                sns.lineplot(data=df_sentiment_month, x='created_month', y='sum', hue='model_api_sentiment')
                st.pyplot(fig1)
                st.markdown("### Tweets Sentiment by Month table ")
                st.table(df_sentiment_month[['created_month','model_api_sentiment','sum']].sort_values(by='created_month'))
            
            with fig_col2:
                st.markdown("### Tweets by Source")
                fig2,ax=plt.subplots()
                sns.stripplot(data=df_source,x='source_cleaned',y='sum')
                st.pyplot(fig2)
                st.markdown("### Tweets by source ")
                st.table(df_source[['source_cleaned','sum']])
            
    else:
        print(f"No file in s3 location : {s3_bucket}/{s3_folder} after latest timestamp of {last_procesed_ts}")
        check_new_files_flag=0
    
    initial_run_flag=0
    return check_new_files_flag


if __name__=="__main__":

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

    # initilalze the previous  run dataframes
    initial_run_flag=1
    check_new_files_flag=1
    last_procesed_ts=None
    prev_day_list=[]
    prev_df_sentiment_day=pd.DataFrame(columns=['model_api_sentiment','created_day','sum'])
    prev_df_sentiment_month=pd.DataFrame(columns=['model_api_sentiment','created_month','sum'])
    prev_df_source=pd.DataFrame(columns=['source_cleaned','count'])

    try:
            config=configparser.ConfigParser()       
            config.read(config_path)
            region=config.get('AWS resources','region')
            s3_bucket=config.get('AWS resources','s3_bucket')
            s3_folder=config.get('AWS resources','s3_folder_output')
            file_loc_ts_s3=config.get('AWS resources','file_loc_ts_s3')
            file_loc_sentiment_counts=config.get('AWS resources','file_loc_sentiment_counts')
            file_loc_day_list=config.get('AWS resources','file_loc_day_list')
            file_loc_day_df=config.get('AWS resources','file_loc_day_df')
            file_loc_month_df=config.get('AWS resources','file_loc_month_df')
            file_loc_source_df=config.get('AWS resources','file_loc_source_df')
            s3_file_ts=s3_resource.Object(s3_bucket,file_loc_ts_s3)
            s3_file_sentiment_counts=s3_resource.Object(s3_bucket,file_loc_sentiment_counts)
            s3_file_day_list=s3_resource.Object(s3_bucket,file_loc_day_list)
            s3_file_day_df=s3_resource.Object(s3_bucket,file_loc_day_df)
            s3_file_month_df=s3_resource.Object(s3_bucket,file_loc_month_df)
            s3_file_source_df=s3_resource.Object(s3_bucket,file_loc_source_df)

    except Exception as e:
            print(f"error reading from {config_path}:{e},,{traceback.format_exc()}")
            sys.exit(1)

    #check the previous timestamps and dataframes 
    #ts_latest_s3
    get_latest_ts_s3(s3_bucket,file_loc_ts_s3)
    get_dfs_s3()
    print(f'version 3 {prev_df_sentiment_day}')
    while check_new_files_flag:
            check_new_files_flag=create_latest_dffiles(last_procesed_ts)
            print('sleeping')
            time.sleep(30)
            print('waking up')

    save_df_as_files(s3_bucket,file_loc_day_df,prev_df_sentiment_day)
    save_df_as_files(s3_bucket,file_loc_month_df,prev_df_sentiment_month)
    save_df_as_files(s3_bucket,file_loc_source_df,prev_df_source)
    save_df_as_files(s3_bucket,file_loc_day_list,pd.DataFrame(prev_day_list,columns=['day']))
    save_latest_ts_s3(s3_file_ts,last_procesed_ts)
    
