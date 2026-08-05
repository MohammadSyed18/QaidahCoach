from dataclasses import dataclass
from .exercises import RULES,generate
@dataclass(frozen=True)
class SessionPlan: exercises:list;rules:list[str];seed:int
def mixed_session(rules:list[str],count:int,seed:int=1):
 if not rules or any(r not in RULES for r in rules):raise ValueError("session contains an unknown rule")
 if count<1:raise ValueError("count must be positive")
 items=[]
 for i in range(count):items.extend(generate(rules[i%len(rules)],1,seed+i))
 return SessionPlan(items,rules,seed)
def check_answer(exercise,answer):
 normalized=answer.strip().lower().replace("ā","a")
 expected=exercise.answer.lower().replace("ā","a")
 return {"correct":normalized==expected,"expected":exercise.answer,"explanation":exercise.explanation}
