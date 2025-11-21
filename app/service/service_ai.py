import os
import json
from typing import List, Optional, Dict
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from app.rag.rag_store import SpotifyRAG
import numpy as np

load_dotenv(find_dotenv())

# Inisialisasi RAG store (index FAISS + metadata)
_rag_store: Optional[SpotifyRAG] = None

def get_rag_store() -> SpotifyRAG:
    global _rag_store
    if _rag_store is None:
        _rag_store = SpotifyRAG()
        _rag_store.load()
    return _rag_store

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
    desired_minutes: str,
    top_ids: Optional[List[str]] = None
) -> str:
    rag = get_rag_store()
    # Ambil kandidat berdasarkan ISO kurasi di RAG
    iso_df = rag.curate_iso_playlist(
        pre_mood=pre_mood,
        phq9=phq9,
        desired_minutes=desired_minutes,
        top_ids=top_ids,
        location=location or 'Indonesia'
    )
    # Pilih tepat 10 lagu dengan lagu terakhir paling energetik
    iso10 = rag.pick_progression_with_uplift(iso_df, count=10)
    catalog = rag.to_catalog(iso10, max_items=10)

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
                "Songs must align with the mood journey and safety criteria, and be familiar/popular for the user's locale."
            ),
            "strict_rules": (
                "You MUST ONLY select tracks from the provided CATALOG. "
                "Use the exact 'title' and 'artist' values from CATALOG, no inventions. "
                "Do not repeat artists or titles. Do NOT include instrumental or ambient-only tracks; prefer vocal tracks. "
                "Avoid explicit content. Provide exactly 10 tracks. "
                "Prioritize popular and familiar tracks for the user's locale. "
                "The LAST track must be the most energetic/uplifting among the ten. "
                "For 'genres', aggregate distinct genres from the selected tracks. "
                "Location preference: if user_location is 'Indonesia', prioritize Indonesian-language/pop Indonesia tracks and include English/American ones; if 'Japan', prioritize Japanese-language tracks and include English/American ones."
            ),
            "audio_feature_guidelines": {
                "map_pre_mood_to_valence": True,
                "start_energy_range": [0.15, 0.40],
                "final_energy_range": [0.35, 0.6],
                "prefer_vocal_tracks": True,
                "require_tempo_variation_percent": 40
            },
            "diversity_guidelines": {
                "max_tracks_per_artist": 1,
                "min_unique_genres": 3,
                "min_unique_decades": 2,
                "avoid_too_many_similar_sounding": True,
                "prefer_varied_vocal_styles": True,
                "prefer_mix_of_international_and_local_artists": True
            },
            "safety": {
                "avoid_explicit_unless_allowed": True,
                "avoid_triggering_lyrics": True
            },
            "catalog": catalog,
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
                "ONLY use items from CATALOG."
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

def validate_ai_output(ai_json: Dict, catalog: List[Dict], count: int = 10) -> Dict:
    # Pastikan playlist hanya berisi item yang ada di katalog
    playlist = ai_json.get('playlist', [])
    rag = get_rag_store()
    valid, dropped = rag.filter_to_catalog(playlist, catalog)
    # Pastikan tepat 'count' lagu: jika kurang, tambahkan dari katalog sisa; jika lebih, pangkas
    cat_keys = [(c['title'].strip().lower(), c['artist'].strip().lower()) for c in catalog]
    valid_keys = [(t['title'].strip().lower(), t['artist'].strip().lower()) for t in valid]
    # Tambahkan dari katalog yang belum ada
    for k in cat_keys:
        if len(valid) >= count:
            break
        if k not in valid_keys:
            c = next((x for x in catalog if (x['title'].strip().lower(), x['artist'].strip().lower()) == k), None)
            if c:
                valid.append({'title': c['title'], 'artist': c['artist']})
                valid_keys.append(k)
    # Pangkas jika lebih dari 'count'
    if len(valid) > count:
        valid = valid[:count]

    # Reorder agar track terakhir paling energetik
    cat_map = {(c['title'].strip().lower(), c['artist'].strip().lower()): c for c in catalog}
    energies = []
    for t in valid:
        key = (t['title'].strip().lower(), t['artist'].strip().lower())
        energies.append(float(cat_map.get(key, {}).get('energy', 0.0)))
    if valid:
        max_idx = int(np.argmax(energies))
        if max_idx != len(valid) - 1:
            last = valid[max_idx]
            rest = [t for i, t in enumerate(valid) if i != max_idx]
            valid = rest + [last]
    ai_json['playlist'] = valid
    # Sertakan URIs jika tersedia untuk mengurangi kegagalan pencarian di Spotify
    playlist_uris: List[str] = []
    for t in valid:
        key = (t['title'].strip().lower(), t['artist'].strip().lower())
        uri = cat_map.get(key, {}).get('uri')
        if uri:
            playlist_uris.append(uri)
    if playlist_uris:
        ai_json['playlist_uris'] = playlist_uris
    # Perbarui genres dari katalog valid
    genres = []
    for t in valid:
        key = (t['title'].strip().lower(), t['artist'].strip().lower())
        g = cat_map[key].get('genres', [])
        for gg in g:
            if gg and gg not in genres:
                genres.append(gg)
    ai_json['genres'] = genres
    # Tambahkan catatan jika ada yang di-drop
    if dropped:
        ai_json['note'] = f"Dropped non-catalog tracks: {len(dropped)}"
    return ai_json