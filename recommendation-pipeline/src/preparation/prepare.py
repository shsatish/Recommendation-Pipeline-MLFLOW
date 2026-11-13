"""Global time-based holdout, no future interactions in train."""
import pandas as pd
from src.common import CONFIG,LOGGER,path,save_json
def run():
 df=pd.read_csv(path('data','processed','validated_interactions.csv'),parse_dates=['timestamp']).sort_values(['timestamp','interaction_id']).reset_index(drop=True)
 cutoff=int(len(df)*(1-CONFIG['test_fraction'])); train=df.iloc[:cutoff]; test=df.iloc[cutoff:]
 assert len(train)>0 and len(test)>0 and train.timestamp.max()<=test.timestamp.min()
 train.to_csv(path('data','processed','train.csv'),index=False); test.to_csv(path('data','processed','test.csv'),index=False)
 result={'train_rows':len(train),'test_rows':len(test),'latest_train_timestamp':train.timestamp.max().isoformat(),'earliest_test_timestamp':test.timestamp.min().isoformat(),'strategy':'global_time_based'}
 save_json(path('reports','split_report.json'),result); LOGGER.info('PREPARATION: train=%d test=%d',len(train),len(test));return result
