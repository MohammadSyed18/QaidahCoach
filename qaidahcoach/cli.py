import argparse,json
from .exercises import generate,to_dicts
def main():
 p=argparse.ArgumentParser();p.add_argument("rule");p.add_argument("--count",type=int,default=3);p.add_argument("--seed",type=int,default=1);a=p.parse_args();print(json.dumps(to_dicts(generate(a.rule,a.count,a.seed)),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
