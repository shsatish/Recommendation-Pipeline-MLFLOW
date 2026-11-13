"""Check nulls, types, dates, ranges, duplicates and foreign keys; quarantine errors."""
import pandas as pd
from src.common import LOGGER,path,save_json

def _entities(frame,columns,key,label):
 if not set(columns)<=set(frame.columns): raise ValueError(f'{label} missing required columns')
 reason=pd.Series('',index=frame.index,dtype=object)
 for col in columns: reason.loc[frame[col].isna()|frame[col].astype(str).str.strip().eq('')]+=f'missing_{col};'
 for col in [key,'age' if label=='users' else 'release_year']:
  reason.loc[pd.to_numeric(frame[col],errors='coerce').isna()]+=f'invalid_type_{col};'
 reason.loc[frame.duplicated(key,keep='first')]+='duplicate_id;'
 good=frame.loc[reason.eq('')].copy(); good[key]=good[key].astype(int)
 bad=frame.loc[reason.ne('')].copy(); bad['error_reason']=reason.loc[reason.ne('')]
 return good,bad

def run():
 users=pd.read_csv(path('data','raw','users.csv')); items=pd.read_csv(path('data','raw','items.csv'))
 raw=pd.read_csv(path('data','raw','interactions.csv'),dtype=str)
 users,eu=_entities(users,['user_id','age','country','preferred_category'],'user_id','users')
 items,ei=_entities(items,['item_id','title','category','release_year'],'item_id','items')
 required=['interaction_id','user_id','item_id','rating','timestamp']
 if not set(required)<=set(raw.columns): raise ValueError('Interaction schema invalid')
 reasons=pd.Series('',index=raw.index,dtype=object)
 for col in required: reasons.loc[raw[col].isna()|raw[col].str.strip().eq('')]+=f'missing_{col};'
 for col in ['interaction_id','user_id','item_id','rating']:
  num=pd.to_numeric(raw[col],errors='coerce'); reasons.loc[num.isna()|(num.notna()&(num%1!=0))]+=f'invalid_type_{col};'
 rate=pd.to_numeric(raw.rating,errors='coerce'); reasons.loc[rate.notna()&~rate.between(1,5)]+='invalid_rating;'
 dates=pd.to_datetime(raw.timestamp,errors='coerce',utc=True,format='mixed'); reasons.loc[dates.isna()]+='invalid_timestamp;'
 uid=pd.to_numeric(raw.user_id,errors='coerce'); iid=pd.to_numeric(raw.item_id,errors='coerce')
 reasons.loc[uid.notna()&~uid.isin(users.user_id)]+='unknown_user;'
 reasons.loc[iid.notna()&~iid.isin(items.item_id)]+='unknown_item;'
 reasons.loc[raw.duplicated('interaction_id',keep='first')]+='duplicate_interaction_id;'
 reasons.loc[raw.duplicated(['user_id','item_id'],keep='first')]+='duplicate_user_item;'
 bad=raw.loc[reasons.ne('')].copy(); bad['error_reason']=reasons.loc[reasons.ne('')]
 valid=raw.loc[reasons.eq('')].copy()
 for col in ['interaction_id','user_id','item_id','rating']: valid[col]=pd.to_numeric(valid[col]).astype(int)
 valid['timestamp']=pd.to_datetime(valid.timestamp,utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
 for name,df in [('users',users),('items',items),('interactions',valid)]:df.to_csv(path('data','processed',f'validated_{name}.csv'),index=False)
 for name,df in [('users',eu),('items',ei),('interactions',bad)]:df.to_csv(path('data','errors',f'{name}_invalid.csv'),index=False)
 counts={}
 for reason in bad.error_reason:
  for r in filter(None,reason.split(';')):counts[r]=counts.get(r,0)+1
 report={'raw_interactions':len(raw),'valid_interactions':len(valid),'quarantined_interactions':len(bad),'invalid_users':len(eu),'invalid_items':len(ei),'reason_counts':counts,'status':'PASS_WITH_QUARANTINE' if len(valid) else 'FAIL'}
 save_json(path('reports','validation_report.json'),report)
 if valid.empty:raise ValueError('No clean interactions')
 LOGGER.info('VALIDATION: %d valid, %d quarantined',len(valid),len(bad))
 return report
