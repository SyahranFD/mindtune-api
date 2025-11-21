import os
import json
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

load_dotenv(find_dotenv())
def call_hf_api(content: str) -> str:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.getenv("HF_TOKEN"),
        timeout=120.0  # Set timeout to 120 seconds
    )

    try:
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
    except Timeout:
        raise Exception("Connection timeout when calling AI service. The service might be overloaded.")
    except ConnectionError:
        raise Exception("Connection error when connecting to AI service. Please check your network.")
    except RequestException as e:
        raise Exception(f"Request error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def build_prompt_playlist_healing(
    pre_mood: int,
    phq9: int,
    location: str,
    top_ids: Optional[List[str]] = None
) -> str:
    prompt = {
        "system": (
            "You are a clinical-aware music recommender for a healing-mode web app. "
            "Your output MUST be exactly a JSON object with four keys: "
            "'playlist_title' (string), 'description' (string), "
            "'playlist' (array of objects with 'title' and 'artist'), and 'genres' (array of strings)."
        ),
        "instructions": {
            "goal": (
                "Generate a therapeutic Spotify playlist to help regulate mood using the ISO principle: "
                "start by reflecting the user's current affect (based on pre_mood) and then gently uplift toward calm, relief, or hope. "
                "Create a playlist title and description that feel compassionate, soothing, and emotionally validating. "
                "Songs must align with the mood journey and safety criteria. "
                "Only include real, existing songs and artists that can be found on Spotify; prioritize popular and culturally relevant tracks for the user's location."
            ),
            "title_guidelines": {
                "creativity_required": True,
                "avoid_cliches": ["Gentle", "Gentle Dawn", "Calm", "Serenity", "Quiet", "Stillness"],
                "length_words_range": [3, 6],
                "no_colon_or_em_dash": True,
                "prefer_location_language": True,
                "thematic_requirements": "Evocative, hopeful, and culturally resonant; reflect ISO journey without generic adjectives."
            },
            "audio_feature_guidelines": {
                "map_pre_mood_to_valence": True,
                "target_uplift_valence": 0.20,
                "start_energy_range": [0.20, 0.45],
                "final_energy_range": [0.55, 0.80],
                "require_tempo_variation_percent": 50,  # require at least ~50% tempo spread across playlist
                "start_tempo_bpm_range": [60, 90],
                "middle_tempo_bpm_range": [75, 110],
                "final_tempo_bpm_range": [95, 130],
                "tempo_crescendo_required": True,
                "encourage_instrumentation_mix": True
            },
            "sequencing_guidelines": {
                "early_tracks": "Tracks 1–5 mirror current affect: lower energy/tempo, valence near current mood.",
                "middle_tracks": "Tracks 6–11 gradually increase valence, energy, and tempo; introduce more rhythmic drive.",
                "final_tracks": "Tracks 12–15 reach a confident, upbeat resolution: higher energy and tempo within safe lyrical themes.",
                "end_section_min_high_energy_tracks": 3
            },
            "diversity_guidelines": {
                "max_tracks_per_artist": 1,
                "min_unique_genres": 3,
                "min_unique_decades": 2,
                "avoid_too_many_similar_sounding": True,
                "prefer_varied_vocal_styles": True,
                "prefer_mix_of_international_and_local_artists": True,
                "avoid_specific_titles": ["Holocene", "Heartbeats", "Fast Car"],
                "avoid_covers_or_near_duplications": True
            },
            "curation_rules": {
                "do_not_repeat_artist_names": True,
                "do_not_repeat_track_titles": True,
                "include_at_least_one_instrumental_or_ambient_track": True,
                "prefer_popular_tracks": True,
                "include_at_least_one_track_from_user_top_ids_if_fit": True,
                "playlist_length_exact": 15
            },
            "safety": {
                "avoid_explicit_unless_allowed": True,
                "avoid_triggering_lyrics": True
            },
            "location_guidelines": {
                "user_location_applied": True,
                "prefer_local_language_and_artists": True,
                "include_at_least_five_local_tracks": True,
                "examples_of_locations": ["Indonesia", "United States", "Japan", "Brazil"]
            },
            "output_format": (
                "Return ONLY a valid JSON object with this structure format:\n\n"
                "{\n"
                "  \"playlist_title\": \"<playlist title>\",\n"
                "  \"description\": \"<1–2 sentences describing the playlist>\",\n"
                "  \"playlist\": [\n"
                "    {\"title\": \"<song title 1>\", \"artist\": \"<artist name 1>\"},\n"
                "    {\"title\": \"<song title 2>\", \"artist\": \"<artist name 2>\"}\n"
                "  ],\n"
                "  \"genres\": [\"<genre 1>\", \"<genre 2>\", \"<genre 3>\"]\n"
                "}\n\n"
                "DO NOT copy or reuse the example titles, artists, or genres. "
                "Generate completely new and context-appropriate content for the current user data. "
                "Ensure playlist tracks follow the diversity and curation rules above. "
                "The \"playlist\" array MUST contain exactly 15 items. "
                "Choose only real and verifiable songs/artists; prioritize well-known/popular tracks relevant to the user's location. "
                "If a user's phq9_score >= phq_threshold_referral (20), include a compassionate referral suggestion as part of the description (one short sentence) but still return the JSON structure exactly as specified."
            )
        },
        "user": {
            "pre_mood_slider": pre_mood,
            "phq9_score": phq9,
            "user_location": location or "Indonesia",
            "top_spotify_ids": top_ids or []
        }
    }
    return json.dumps(prompt, indent=2)