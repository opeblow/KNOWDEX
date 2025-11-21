from agent.custom_types import citation
from typing import List,Dict

class CitationManager:
    def __init__(self):
        self.citations:List[citation]=[]
        self.next_number=1

    def add(self,title:str,url:str,snippet:str="")->int:
        citation=citation(number=self.next_number,title=title,url=url,snippet=snippet)
        self.citations.append(citation)
        self.next_number+=1
        return citation.number
    
    def format__reference(self):
        if not self.citations:
            return ""
        lines=["\n\nSources:"]
        for c in self.citations:
            lines.append(f"[{c.number}]{c.title}\n{c.url}\n")
        return "\n".join(lines)


    