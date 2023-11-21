from collections import defaultdict
def mastery(attempts):
 grouped=defaultdict(list)
 for item in attempts:
  if item["rule"] not in {"madd","qalqalah","ghunnah","ikhfa","idgham","iqlab"}:raise ValueError("unknown rule in progress")
  grouped[item["rule"]].append(bool(item["correct"]))
 return {rule:{"attempts":len(values),"accuracy":round(sum(values)/len(values),3),"needs_review":len(values)<3 or sum(values)/len(values)<.8} for rule,values in grouped.items()}
def next_rule(report):
 candidates=[(v["accuracy"],v["attempts"],rule) for rule,v in report.items() if v["needs_review"]]
 return min(candidates)[2] if candidates else None
