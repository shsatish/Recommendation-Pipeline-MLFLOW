"""Persist reusable user, item, and user-item features computed from train only."""
import pandas as pd
from src.common import LOGGER,path
CATALOG=[
 ('user_id','user','integer','User primary key','users'),('user_avg_rating','user','float','Historical mean rating','train'),
 ('user_activity_count','user','integer','Historical interaction count','train'),('preferred_category','user','string','Declared favorite category','users'),
 ('days_since_last_interaction','user','float','Days since last train event at train cutoff','train'),
 ('item_id','item','integer','Item primary key','items'),('category','item','string','Movie genre','items'),
 ('item_popularity','item','integer','Historical interaction count','train'),('item_avg_rating','item','float','Historical mean rating','train'),
 ('rating','interaction','integer','Training label (1-5)','train'),('category_match','interaction','boolean','User preference equals item genre','users+items')]
def run():
 tr=pd.read_csv(path('data','processed','train.csv'),parse_dates=['timestamp']);users=pd.read_csv(path('data','processed','validated_users.csv'));items=pd.read_csv(path('data','processed','validated_items.csv'))
 u=tr.groupby('user_id').agg(user_avg_rating=('rating','mean'),user_activity_count=('rating','size'),last_timestamp=('timestamp','max')).reset_index()
 u['days_since_last_interaction']=(tr.timestamp.max()-u.last_timestamp).dt.total_seconds()/86400
 u=users.merge(u.drop(columns='last_timestamp'),on='user_id',how='left');u['user_avg_rating']=u.user_avg_rating.fillna(tr.rating.mean());u['user_activity_count']=u.user_activity_count.fillna(0).astype(int);u['days_since_last_interaction']=u.days_since_last_interaction.fillna(-1)
 i=tr.groupby('item_id').agg(item_popularity=('rating','size'),item_avg_rating=('rating','mean')).reset_index()
 i=items.merge(i,on='item_id',how='left');i['item_popularity']=i.item_popularity.fillna(0).astype(int);i['item_avg_rating']=i.item_avg_rating.fillna(tr.rating.mean())
 features=tr.merge(u[['user_id','preferred_category','user_avg_rating','user_activity_count','days_since_last_interaction']],on='user_id').merge(i[['item_id','category','item_popularity','item_avg_rating']],on='item_id')
 features['category_match']=(features.preferred_category==features.category).astype(int)
 u.to_csv(path('data','features','user_features.csv'),index=False);i.to_csv(path('data','features','item_features.csv'),index=False);features.to_csv(path('data','features','training_features.csv'),index=False)
 pd.DataFrame(CATALOG,columns=['feature','entity','type','description','source']).to_csv(path('reports','feature_catalog.csv'),index=False)
 LOGGER.info('FEATURES: %d user, %d item, %d training rows',len(u),len(i),len(features))
 return {'user_rows':len(u),'item_rows':len(i),'training_feature_rows':len(features)}
