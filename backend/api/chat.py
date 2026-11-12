from fastapi import APIRouter
from pydantic import BaseModel
from backend.core.resources import rag

router=APIRouter()


class chat_request(BaseModel):
    question:str


@router.post("/query")
def ask_question(request:chat_request):

    answer=rag.ask(request.question)

    return answer 