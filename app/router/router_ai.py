from fastapi import APIRouter, Depends
from typing import List, Optional
import json

from ..service import service_ai

router_ai = APIRouter()


@router_ai.post("/test-playlist-healing")
def test_playlist_healing(
    pre_mood: int,
    phq9: int,
    locale: str,
    genres: List[str],
    allow_explicit: bool,
    desired_minutes: int,
):
    # Build the prompt using the service function
    prompt = service_ai.build_prompt_playlist_healing(
        pre_mood=pre_mood,
        phq9=phq9,
        locale=locale,
        genres=genres,
        allow_explicit=allow_explicit,
        desired_minutes=desired_minutes,
    )
    
    # Call the HF API with the generated prompt
    result_str = service_ai.call_hf_api(prompt)
    
    # Parse the result string to a Python object
    try:
        # Attempt to parse the result as JSON
        result_parsed = json.loads(result_str)
    except json.JSONDecodeError:
        # If parsing fails, return the raw string
        result_parsed = result_str
    
    # Return both the prompt and the result
    return {
        "result": result_parsed       # Parsed result
    }