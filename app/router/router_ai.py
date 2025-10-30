from fastapi import APIRouter, Depends
from typing import List, Optional
import json

from ..service import service_ai

router_ai = APIRouter()


@router_ai.get("/test-playlist-healing")
def test_playlist_healing(
    pre_mood: int,
    phq9: int,
    locale: str,
    desired_minutes: str,
):
    prompt = service_ai.build_prompt_playlist_healing(
        pre_mood=pre_mood,
        phq9=phq9,
        locale=locale,
        desired_minutes=desired_minutes,
    )

    result_str = service_ai.call_hf_api(prompt)
    result_parsed = json.loads(result_str)

    return {
        "result": result_parsed 
    }