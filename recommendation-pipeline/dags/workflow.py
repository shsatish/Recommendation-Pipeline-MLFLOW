"""Dependency-ordered Python orchestration; schedule using cron or Task Scheduler."""
from datetime import datetime,timezone
from time import perf_counter
import traceback
from src.common import LOGGER,path,save_json
from src.ingestion.ingest import run as ingest
from src.validation.validate import run as validate
from src.preparation.prepare import run as prepare
from src.transformation.transform import run as transform
from src.features.build_features import run as features
from src.training.train import run as train
from src.evaluation.evaluate import run as evaluate
STAGES=[('ingestion',ingest),('validation',validate),('preparation',prepare),('transformation',transform),('features',features),('training',train),('evaluation',evaluate)]
def main():
 history={'run_id':datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),'status':'RUNNING','steps':[]}
 for name,fn in STAGES:
  start=perf_counter()
  try:
   result=fn();history['steps'].append({'stage':name,'status':'SUCCESS','duration_seconds':round(perf_counter()-start,3),'details':result})
  except Exception as exc:
   history['steps'].append({'stage':name,'status':'FAILED','error':str(exc),'traceback':traceback.format_exc()});history['status']='FAILED';save_json(path('reports','last_workflow_run.json'),history);raise
 history['status']='SUCCESS';history['completed_at_utc']=datetime.now(timezone.utc).isoformat();save_json(path('reports','last_workflow_run.json'),history)
 content=f"RUN ID: {history['run_id']}\nSTATUS: {history['status']}\n\n"+'\n'.join(f"{s['stage']:<16} {s['status']:<10} {s['duration_seconds']:>7.3f} sec" for s in history['steps'])+'\n'
 path('reports','successful_run.txt').write_text(content);print('\n'+'='*49+'\n'+content+'='*49);return history
if __name__=='__main__':main()
