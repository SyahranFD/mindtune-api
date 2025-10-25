import os
import json
from typing import List, Optional
from openai import OpenAI

def call_hf_api(content: str) -> str:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b:groq",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
    )

    return completion.choices[0].message.content

def build_prompt_playlist_healing(
        pre_mood: int,
        phq9: int,
        locale: str,
        desired_minutes: int,
        top_ids: Optional[List[str]] = None
) -> str:
    prompt = {
        "system": (
            "You are a clinical-aware music recommender for a healing-mode web app. "
            "Your output MUST be exactly a JSON object with two keys: "
            "'playlist' (array of strings in 'title - artist' format) "
            "and 'genres' (array of strings representing dominant genres in the playlist)."
        ),
        "instructions": {
            "triage": {
                "phq_threshold_referral": 20
            },
            "goal": (
                "Generate a therapeutic Spotify playlist to help regulate mood using ISO-principle: "
                "start mirroring current affect then gently uplift toward a calm/hopeful state."
            ),
            "audio_feature_guidelines": {
                "map_pre_mood_to_valence": True,
                "target_uplift_valence": 0.20,
                "start_energy_range": [0.15, 0.40],
                "final_energy_range": [0.35, 0.6],
                "acousticness_min": 0.6
            },
            "safety": {
                "avoid_explicit_unless_allowed": True,
                "avoid_triggering_lyrics": True
            },
            "duration_minutes": desired_minutes,
            "output_format": (
                "Return ONLY a valid JSON object with this structure:\n\n"
                "{\n"
                "  \"playlist\": [\"Holocene - Bon Iver\", \"Sunset Lover - Petit Biscuit\"],\n"
                "  \"genres\": [\"indie folk\", \"chillwave\", \"ambient pop\"]\n"
                "}\n\n"
                "No explanations or text outside the JSON."
            ),
        },
        "user": {
            "pre_mood_slider": pre_mood,
            "phq9_score": phq9,
            "user_locale": locale or "id-ID",
            "top_spotify_ids": top_ids or []
        }
    }
    return json.dumps(prompt, indent=2)