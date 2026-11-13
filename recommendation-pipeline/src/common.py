from pathlib import Path
import json
import logging
ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'configs/config.json').read_text())
def path(*parts):
 p=ROOT.joinpath(*parts); p.parent.mkdir(parents=True,exist_ok=True); return p
def save_json(target,obj):
 target.write_text(json.dumps(obj,indent=2,default=str),encoding='utf-8')
logging.basicConfig(level=logging.INFO,format='%(asctime)s | %(levelname)s | %(message)s')
LOGGER=logging.getLogger('recommendation-pipeline')
