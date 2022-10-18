
import requests
import json
from scipy.stats import logistic

def make_prediction(instances):
   data = json.dumps({"signature_name": "serving_default", "instances": instances})
   headers = {"content-type": "application/json"}
   json_response = requests.post(url, data=data, headers=headers)
   predictions = json.loads(json_response.text)
   return predictions

if __name__=="__main__":
    #url="http://localhost:8501/v1/models/sentiment_model:predict"
    host='18.237.187.44'
    port='8501'
    model_name='sentiment_model'
    url = "http://{0}:{1}/v1/models/{2}:predict".format(host,port,model_name)

    instances=["this was not a bad day"]
    '''predictions=logistic.cdf(make_prediction(instances)['predictions'][0][0])
    if predictions>0.5:
        print("Positive")
    else:
        print("Negetive")
        '''

    predictions=make_prediction(instances)['predictions']
    print(argmax(predictions))