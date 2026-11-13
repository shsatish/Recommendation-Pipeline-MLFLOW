"""Popularity baseline and personalized content-category preference model."""
import numpy as np
import pandas as pd
from src.common import CONFIG,LOGGER,path,save_json
def run():
 tr=pd.read_csv(path('data','processed','train.csv'));items=pd.read_csv(path('data','features','item_features.csv'))
 global_mean=float(tr.rating.mean());smoothing=8
 items['quality_prior']=(items.item_popularity*items.item_avg_rating+smoothing*global_mean)/(items.item_popularity+smoothing)
 items['popularity_score']=items.quality_prior*np.log1p(items.item_popularity)
 genre=tr.merge(items[['item_id','category']],on='item_id');genre['strength']=genre.rating-3
 profile=genre.groupby(['user_id','category']).agg(genre_score=('strength','mean'),count=('strength','size')).reset_index();profile['genre_score']*=profile['count']/(profile['count']+2)
 items.to_csv(path('models','item_scores.csv'),index=False);profile.to_csv(path('models','user_genre_profiles.csv'),index=False)
 save_json(path('models','metadata.json'),{'seed':CONFIG['seed'],'global_mean':global_mean,'smoothing':smoothing,'personalization':'smoothed_user_genre_profile'})
 LOGGER.info('TRAINING: 2 recommenders trained');return {'models':2,'global_rating':global_mean,'smoothing':smoothing}
class Recommender:
 def __init__(self):
  self.items=pd.read_csv(path('models','item_scores.csv'));tr=pd.read_csv(path('data','processed','train.csv'))
  self.seen=tr.groupby('user_id').item_id.apply(set).to_dict()
  profiles=pd.read_csv(path('models','user_genre_profiles.csv'))
  self.affinity={(int(r.user_id),r.category):float(r.genre_score) for r in profiles.itertuples()}
  self.preference=pd.read_csv(path('data','features','user_features.csv')).set_index('user_id').preferred_category.to_dict()
  self.max_pop=max(1,float(self.items.popularity_score.max()))
 def recommend(self,user,model,k=5):
  data=self.items[~self.items.item_id.isin(self.seen.get(user,set()))].copy()
  if model=='popularity':data['score']=data.popularity_score
  elif model=='personalized':
   data['affinity']=[self.affinity.get((user,g),0) for g in data.category]
   data['match']=(data.category==self.preference.get(user)).astype(int)
   data['score']=1.8*data.affinity+0.6*data.match+0.35*(data.quality_prior-3)+0.1*data.popularity_score/self.max_pop
  else:raise ValueError(f'Unknown model {model}')
  return data.sort_values(['score','item_id'],ascending=[False,True]).head(k).item_id.astype(int).tolist()
