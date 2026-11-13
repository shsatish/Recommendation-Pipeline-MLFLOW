"""Deterministic movie dataset with intentional data-quality errors."""
import numpy as np
import pandas as pd
from src.common import CONFIG,path,LOGGER
GENRES=['Action','Comedy','Drama','Documentary','Sci-Fi','Romance']
def run():
 rng=np.random.default_rng(CONFIG['seed']); nu=CONFIG['users']; ni=CONFIG['items']; n=CONFIG['interactions']
 users=pd.DataFrame({'user_id':np.arange(1,nu+1),'age':rng.integers(18,67,nu),'country':rng.choice(['IN','US','DE','GB'],nu),'preferred_category':rng.choice(GENRES,nu)})
 items=pd.DataFrame({'item_id':np.arange(1,ni+1),'title':[f'Movie {i:03d}' for i in range(1,ni+1)],'category':rng.choice(GENRES,ni),'release_year':rng.integers(1995,2026,ni)})
 ids=rng.choice(nu*ni,size=n,replace=False); uid=ids//ni+1; iid=ids%ni+1
 pref=users.set_index('user_id').loc[uid,'preferred_category'].to_numpy(); cat=items.set_index('item_id').loc[iid,'category'].to_numpy()
 score=3+1.3*(pref==cat)+rng.normal(0,0.6,ni)[iid-1]+rng.normal(0,.85,n)
 timestamp=pd.Timestamp('2025-01-01',tz='UTC')+pd.to_timedelta(rng.integers(0,420,n),unit='D')+pd.to_timedelta(rng.integers(0,86400,n),unit='s')
 data=pd.DataFrame({'interaction_id':np.arange(1,n+1),'user_id':uid,'item_id':iid,'rating':np.clip(np.rint(score),1,5).astype(int),'timestamp':timestamp.astype(str)})
 bad=data.iloc[:7].copy(); bad['user_id']=bad['user_id'].astype(object); bad.loc[0,'rating']=8; bad.loc[1,'user_id']=999999; bad.loc[2,'timestamp']='not-a-date'; bad.loc[3,'item_id']=999999; bad.loc[4,'rating']=np.nan; bad.loc[5,'interaction_id']=data.loc[6,'interaction_id']; bad.loc[6,'user_id']='wrong-type'
 data=pd.concat([data,bad],ignore_index=True)
 for name,frame in [('users',users),('items',items),('interactions',data)]: frame.to_csv(path('data','raw',f'{name}.csv'),index=False)
 LOGGER.info('INGESTION: %d users, %d items, %d raw interactions',len(users),len(items),len(data))
 return {'users':len(users),'items':len(items),'interactions':len(data)}
