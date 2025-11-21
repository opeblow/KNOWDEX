from pydantic import BaseModel
from typing import Any,Dict

class BaseTool(BaseModel):
    name:str
    description:str
    parameters:Dict[str,Any]

    async def run(self,**kwargs)->str:
        raise NotImplementedError(f"Tool {self.name} not implemented.")