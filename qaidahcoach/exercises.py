from dataclasses import dataclass,asdict
from random import Random
RULES={
 "madd":[("قَالَ","qāla","The long ā is held for the taught count."),("فِي","fī","The long ī is a madd letter here.")],
 "qalqalah":[("أَحَدْ","aḥad","The final dāl has a light echo when stopped."),("يَجْعَلْ","yajʿal","The sākin jīm is articulated with qalqalah.")],
 "ghunnah":[("إِنَّ","inna","The doubled nūn carries a nasal sound."),("ثُمَّ","thumma","The doubled mīm carries ghunnah.")],
 "ikhfa":[("مِنْ ثَمَرَةٍ","min thamaratin","Nūn sākinah before thā is read with ikhfa." )],
 "idgham":[("مِنْ رَبِّهِمْ","min rabbihim","Nūn sākinah before rā merges without ghunnah in this category.")],
 "iqlab":[("مِنْ بَعْدِ","min baʿdi","Nūn sākinah before bā changes to a concealed mīm sound.")],
}
@dataclass(frozen=True)
class Exercise: id:str;rule:str;arabic:str;transliteration:str;prompt:str;answer:str;explanation:str;sample_label:str="Carefully labeled instructional sample"
def generate(rule:str,count:int=3,seed:int=1):
 if rule not in RULES: raise ValueError("unknown rule")
 if count<1 or count>20: raise ValueError("count must be 1..20")
 rng=Random(seed);items=RULES[rule];out=[]
 for i in range(count):
  arabic,latin,note=items[rng.randrange(len(items))];out.append(Exercise(f"{rule}-{seed}-{i}",rule,arabic,latin,f"Which rule is illustrated by {arabic} ({latin})?",rule,note))
 return out
def to_dicts(items):return [asdict(x) for x in items]
