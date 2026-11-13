"""Precision, Recall, NDCG, catalog coverage and intra-list diversity."""
import math
import numpy as np
import pandas as pd
from src.common import CONFIG,LOGGER,path,save_json
from src.training.train import Recommender
def run():
 test=pd.read_csv(path('data','processed','test.csv'));items=pd.read_csv(path('data','features','item_features.csv'));r=Recommender()
 positive=test[test.rating>=CONFIG['positive_rating_threshold']].groupby('user_id').item_id.apply(set).to_dict();users=sorted(positive)
 genre=items.set_index('item_id').category.to_dict();k=CONFIG['k'];results=[]
 for model in ['popularity','personalized']:
  ps=[];rs=[];ns=[];ds=[];unique=set()
  for user in users:
   suggestions=r.recommend(int(user),model,k);truth=positive[user];hits=[int(a in truth) for a in suggestions]
   ps.append(sum(hits)/k);rs.append(sum(hits)/len(truth));dcg=sum(v/math.log2(i+2) for i,v in enumerate(hits));ideal=sum(1/math.log2(i+2) for i in range(min(len(truth),k)));ns.append(dcg/ideal if ideal else 0)
   unique.update(suggestions)
   if len(suggestions)>1:ds.append(sum(genre[a]!=genre[b] for i,a in enumerate(suggestions) for b in suggestions[i+1:])/(len(suggestions)*(len(suggestions)-1)/2))
  results.append({'model':model,'precision_at_k':round(float(np.mean(ps)),4),'recall_at_k':round(float(np.mean(rs)),4),'ndcg_at_k':round(float(np.mean(ns)),4),'coverage':round(len(unique)/len(items),4),'diversity':round(float(np.mean(ds)),4),'k':k,'evaluated_users':len(users)})
 df=pd.DataFrame(results);df.to_csv(path('reports','model_comparison.csv'),index=False);save_json(path('reports','model_comparison.json'),results)
 try:
  import mlflow
  mlflow.set_tracking_uri(path('reports','mlruns').as_uri());mlflow.set_experiment('movie_recommendation_pipeline')
  for row in results:
   with mlflow.start_run(run_name=row['model']):
    mlflow.log_params({'k':k,'seed':CONFIG['seed'],'algorithm':row['model'],'split':'chronological','relevance_threshold':CONFIG['positive_rating_threshold']})
    mlflow.log_metrics({n:row[n] for n in ['precision_at_k','recall_at_k','ndcg_at_k','coverage','diversity']})
    mlflow.log_artifact(str(path('reports','model_comparison.csv')));mlflow.log_artifact(str(path('reports','feature_catalog.csv')))
  backend='mlflow'
 except ImportError:
  backend='offline_json_only_mlflow_not_installed';save_json(path('reports','offline_experiments.json'),{'note':'This is not an MLflow run. Install requirements and rerun for actual MLflow tracking.','parameters':CONFIG,'runs':results})
 save_json(path('reports','tracking_status.json'),{'tracking_backend':backend});LOGGER.info('EVALUATION (%s):\n%s',backend,df.to_string(index=False))
 return {'tracking_backend':backend,'results':results}
