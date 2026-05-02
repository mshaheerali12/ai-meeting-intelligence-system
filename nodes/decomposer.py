from langsmith import traceable    
import re
@traceable(name="decompose text")
def decomposer(text:str)->list[str]:
    text=re.sub(r"\s+"," ",text.strip())
    sentences=re.split(r"(?<=[.!?])\s+",text)
    return [s.strip() for s in sentences if len(s.strip())>0]