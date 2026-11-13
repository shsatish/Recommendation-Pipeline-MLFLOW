"""Train-only user activity, item popularity and user-item matrix."""
import pandas as pd
from src.common import LOGGER,path
def run():
 df=pd.read_csv(path('data','processed','train.csv'))
 u=df.groupby('user_id').agg(activity_count=('rating','size'),average_rating=('rating','mean')).reset_index()
 i=df.groupby('item_id').agg(popularity=('rating','size'),average_rating=('rating','mean')).reset_index()
 m=df.pivot_table(index='user_id',columns='item_id',values='rating',fill_value=0)
 u.to_csv(path('data','processed','user_activity.csv'),index=False);i.to_csv(path('data','processed','item_popularity.csv'),index=False);m.to_csv(path('data','processed','user_item_matrix.csv'))
 LOGGER.info('TRANSFORMATION: user activity, item popularity and %s matrix',m.shape)
 return {'users':len(u),'items':len(i),'matrix_shape':list(m.shape)}
