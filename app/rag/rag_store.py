import os
import json
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import time


class SpotifyRAG:
    """
    Memuat index FAISS + metadata dari folder `data/spotify_index/` dan
    menyediakan fungsi pencarian serta kurasi playlist sesuai prinsip ISO.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'spotify_index')
        self.index: Optional[faiss.Index] = None
        self.tracks: Optional[pd.DataFrame] = None
        self.emb_model_name: Optional[str] = None
        self.emb_model: Optional[SentenceTransformer] = None

    def load(self) -> None:
        index_path = os.path.join(self.base_dir, 'faiss.index')
        meta_path = os.path.join(self.base_dir, 'tracks.parquet')
        info_path = os.path.join(self.base_dir, 'metadata.json')

        if not (os.path.exists(index_path) and os.path.exists(meta_path)):
            raise FileNotFoundError(f"RAG index tidak ditemukan di {self.base_dir}. Pastikan menaruh 'faiss.index' dan 'tracks.parquet'.")

        self.index = faiss.read_index(index_path)
        self.tracks = pd.read_parquet(meta_path)

        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                info = json.load(f)
                self.emb_model_name = info.get('embedding_model', 'sentence-transformers/all-mpnet-base-v2')
        else:
            self.emb_model_name = 'sentence-transformers/all-mpnet-base-v2'

        self.emb_model = SentenceTransformer(self.emb_model_name)

    def _encode_query(self, text: str) -> np.ndarray:
        vec = self.emb_model.encode([text], normalize_embeddings=True)
        return np.asarray(vec, dtype='float32')

    def search_tracks(self, query: str, k: int = 200) -> pd.DataFrame:
        if self.index is None or self.tracks is None:
            self.load()
        q = self._encode_query(query)
        scores, idxs = self.index.search(q, k)
        idxs = idxs[0]
        scores = scores[0]
        df = self.tracks.iloc[idxs].copy()
        df['score'] = scores
        # Bersihkan NaN genres
        df['genres'] = df['genres'].fillna('')
        return df

    @staticmethod
    def _map_pre_mood_to_targets(pre_mood: int) -> Dict[str, Tuple[float, float]]:
        # pre_mood asumsi 0-10; jika berbeda, clamp
        m = max(0, min(10, pre_mood))
        # valence awal lebih rendah, meningkat
        start_valence = 0.15 + (m * 0.03)  # baseline naik sedikit dengan mood
        end_valence = min(0.75, start_valence + 0.25)
        # energy progresi ringan ke sedang
        start_energy = 0.20 if m <= 4 else 0.30
        end_energy = 0.55 if m <= 4 else 0.60
        return {
            'valence': (max(0.05, start_valence), end_valence),
            'energy': (start_energy, end_energy)
        }

    @staticmethod
    def _minutes_to_track_count(desired_minutes: str, avg_duration_ms: float = 210000.0) -> Tuple[int, int]:
        # desired_minutes seperti "30-45" atau "30"
        try:
            if '-' in desired_minutes:
                a, b = desired_minutes.split('-')
                min_m = int(a)
                max_m = int(b)
            else:
                min_m = max_m = int(desired_minutes)
        except Exception:
            min_m, max_m = 30, 45
        # Perkiraan jumlah track berdasarkan rata-rata durasi
        avg_min = avg_duration_ms / 60000.0
        min_tracks = max(8, int(min_m / avg_min))
        max_tracks = max(min_tracks + 2, int(max_m / avg_min))
        return (min_tracks, max_tracks)

    def curate_iso_playlist(
        self,
        pre_mood: int,
        phq9: int,
        desired_minutes: str,
        top_ids: Optional[List[str]] = None,
        location: str = 'Indonesia'
    ) -> pd.DataFrame:
        # Gunakan satu base query, lalu lakukan boosting generik berdasar location
        base_query = (
            "healing therapeutic calm compassionate gentle uplifting safety non-explicit vocal pop familiar"
        )
        candidates = self.search_tracks(base_query, k=600)

        # Filter safety dasar
        if 'explicit' in candidates.columns:
            try:
                candidates = candidates[candidates['explicit'] != True]
            except Exception:
                pass
        candidates = candidates.dropna(subset=['valence','energy','tempo'])

        # Popularitas (jika tersedia) untuk prefer lagu yang lebih populer
        pop_col = 'popularity' if 'popularity' in candidates.columns else None
        if pop_col:
            candidates['popularity'] = pd.to_numeric(candidates['popularity'], errors='coerce').fillna(50.0)
        else:
            candidates['popularity'] = 50.0

        # Normalisasi kolom genres
        try:
            candidates['genres'] = candidates['genres'].fillna('')
        except Exception:
            pass

        # Boosting generik: utamakan konten lokal sesuai 'location' dan tambahkan sedikit konten English/American
        loc = (location or '').lower().strip()
        local_synonyms = {
            'indonesia': ['indones', 'indo', 'bahasa indonesia', 'dangdut', 'pop indonesia'],
            'japan': ['japan', 'japanese', 'j-pop'],
            'korea': ['korea', 'korean', 'k-pop'],
            'malaysia': ['malay', 'malaysian'],
            'philippines': ['philippine', 'tagalog', 'opm'],
            'thailand': ['thai', 'thailand'],
            'vietnam': ['vietnam', 'viet'],
            'china': ['chinese', 'mandarin', 'c-pop'],
            'taiwan': ['taiwan', 'taiwanese', 'mandopop'],
            'hong kong': ['cantopop', 'cantonese', 'hong kong'],
            'singapore': ['singapore', 'singaporean']
        }
        english_synonyms = ['english', 'american', 'us', 'usa', 'british', 'uk', 'international']
        indian_synonyms = ['india', 'indian', 'bollywood', 'hindi', 'punjabi', 'tamil', 'telugu', 'malayalam', 'kannada', 'marathi', 'bengali']

        # Tentukan pattern lokal
        local_patterns = local_synonyms.get(loc, [loc])
        # Mask lokal dan english
        mask_local = candidates['genres'].str.contains('|'.join([p for p in local_patterns if p]), case=False, regex=True)
        mask_english = candidates['genres'].str.contains('|'.join(english_synonyms), case=False, regex=True)
        mask_indian = candidates['genres'].str.contains('|'.join(indian_synonyms), case=False, regex=True)

        # Boost lokasi dan english, penalti Indian jika bukan lokasi India
        candidates['loc_boost'] = mask_local.astype(float) * 0.40
        candidates['en_boost'] = mask_english.astype(float) * 0.15
        if loc and not loc.startswith('india'):
            candidates['locale_penalty'] = mask_indian.astype(float) * (-0.30)
        else:
            candidates['locale_penalty'] = 0.0

        # Saring lagu kurang populer: pakai ambang moderat agar lebih familiar
        if pop_col:
            candidates = candidates[candidates['popularity'] >= 60.0]

        # Boost user top_ids jika tersedia (cocok ke kolom 'uri' atau 'track_id')
        if top_ids:
            top_set = set([t.lower() for t in top_ids])
            def boost(row):
                for col in ['uri','track_id']:
                    v = str(row.get(col, '')).lower()
                    if v and v in top_set:
                        return 0.15
                return 0.0
            candidates['score'] = candidates['score'] + candidates.apply(boost, axis=1)

        targets = self._map_pre_mood_to_targets(pre_mood)
        v0, v1 = targets['valence']
        e0, e1 = targets['energy']

        # Skor progresi ISO: dekat dengan kurva valence/energy yang meningkat
        # Buat rank gabungan yang mengutamakan valence rendah ke tinggi dan energy rendah ke sedang
        def iso_score(row):
            v = float(row['valence'])
            e = float(row['energy'])
            # preferensi berada dalam rentang target
            sv = -abs(max(v0, min(v1, v)) - ((v0+v1)/2))
            se = -abs(max(e0, min(e1, e)) - ((e0+e1)/2))
            # Acousticness netral-sedikit positif, tidak memaksa instrumental
            ac = float(row.get('acousticness', 0.0))
            # Instrumentalness diberi penalti agar menghindari lagu instrumental
            ins = float(row.get('instrumentalness', 0.0))
            # Tempo moderat lebih disukai
            tp = float(row.get('tempo', 100.0))
            tempo_pref = -abs(tp - 95.0) / 200.0
            pop = float(row.get('popularity', 50.0)) / 100.0
            locb = float(row.get('loc_boost', 0.0))
            enb = float(row.get('en_boost', 0.0))
            pen = float(row.get('locale_penalty', 0.0))
            return (row['score'] * 0.50) + (sv * 0.8) + (se * 0.6) + (ac * 0.05) + (ins * -0.20) + tempo_pref + (pop * 0.45) + locb + enb + pen

        candidates['iso_score'] = candidates.apply(iso_score, axis=1)
        # Tambahkan sedikit jitter agar hasil tidak selalu identik
        rng = np.random.default_rng(int(time.time()) // 60)  # berubah tiap menit
        candidates['iso_score'] = candidates['iso_score'] + rng.uniform(-0.03, 0.03, size=len(candidates))
        candidates = candidates.sort_values('iso_score', ascending=False)

        # Hapus pengulangan artist dan title
        # serta pastikan variasi genre
        seen_artists = set()
        seen_titles = set()
        filtered = []
        for _, r in candidates.iterrows():
            artist_key = str(r['artist']).strip().lower()
            title_key = str(r['title']).strip().lower()
            if artist_key in seen_artists or title_key in seen_titles:
                continue
            seen_artists.add(artist_key)
            seen_titles.add(title_key)
            filtered.append(r)
        cand_df = pd.DataFrame(filtered)

        # Perkirakan jumlah track yang dibutuhkan
        avg_dur = float(cand_df['duration_ms'].mean()) if len(cand_df) else 210000.0
        min_tracks, max_tracks = self._minutes_to_track_count(desired_minutes, avg_dur)
        target_count = min(max_tracks, 18)
        target_count = max(min_tracks, target_count)

        # Susun progresi: awal valence/energy rendah, meningkat
        # Ambil segmen awal (reflect), tengah (transition), akhir (uplift)
        n = target_count
        n1 = max(3, int(n * 0.3))
        n3 = max(3, int(n * 0.3))
        n2 = max(1, n - n1 - n3)

        def segment(df, valence_min, valence_max, energy_min, energy_max, count):
            seg = df[(df['valence'] >= valence_min) & (df['valence'] <= valence_max) & (df['energy'] >= energy_min) & (df['energy'] <= energy_max)]
            return seg.head(count)

        seg1 = segment(cand_df, v0, min(v0+0.10, v1), e0, min(e0+0.10, e1), n1)
        seg2 = segment(cand_df, min(v0+0.05, v1), min(v0+0.18, v1), min(e0+0.08, e1), min(e0+0.20, e1), n2)
        seg3 = segment(cand_df, min(v0+0.15, v1), v1, min(e0+0.18, e1), e1, n3)
        iso_df = pd.concat([seg1, seg2, seg3]).drop_duplicates(subset=['title','artist']).head(n)

        # Variasi tempo: sorting progresi halus
        iso_df = iso_df.sort_values(['valence','energy','tempo','popularity'], ascending=[True, True, True, False]).reset_index(drop=True)
        return iso_df

    def pick_progression_with_uplift(self, df: pd.DataFrame, count: int = 10) -> pd.DataFrame:
        """
        Pilih sejumlah 'count' lagu dengan progresi: reflect -> transition -> uplift.
        Pastikan track terakhir paling energetik.
        """
        if df is None or len(df) == 0:
            return df.head(count)
        count = max(3, int(count))
        # Distribusi segmen
        n_reflect = max(2, int(count * 0.3))
        n_transition = max(2, int(count * 0.4))
        n_uplift = max(1, count - n_reflect - n_transition)

        reflect = df.sort_values(['valence','energy','popularity'], ascending=[True, True, False]).head(n_reflect)
        remain = df.drop(reflect.index)
        transition = remain.sort_values(['valence','energy','popularity'], ascending=[True, True, False]).head(n_transition)
        remain2 = remain.drop(transition.index)
        uplift = remain2.sort_values(['energy','valence','popularity'], ascending=[False, False, False]).head(n_uplift)
        combined = pd.concat([reflect, transition, uplift]).drop_duplicates(subset=['title','artist']).head(count)

        # Pastikan track terakhir paling energetik
        if len(combined) >= 2:
            combined = combined.copy()
            idx_last = combined['energy'].idxmax()
            ordered = combined.drop(idx_last)
            last = combined.loc[[idx_last]]
            out = pd.concat([ordered, last])
            return out.reset_index(drop=True)
        return combined.reset_index(drop=True)

    @staticmethod
    def to_catalog(df: pd.DataFrame, max_items: int = 80) -> List[Dict]:
        items = []
        for _, r in df.head(max_items).iterrows():
            items.append({
                'title': str(r.get('title','')).strip(),
                'artist': str(r.get('artist','')).strip(),
                'genres': [g.strip() for g in str(r.get('genres','')).split(',') if g.strip()],
                'duration_ms': int(r.get('duration_ms', 0)) if pd.notna(r.get('duration_ms')) else None,
                'valence': float(r.get('valence', 0.0)) if pd.notna(r.get('valence')) else None,
                'energy': float(r.get('energy', 0.0)) if pd.notna(r.get('energy')) else None,
                'tempo': float(r.get('tempo', 0.0)) if pd.notna(r.get('tempo')) else None,
                'liveness': float(r.get('liveness', 0.0)) if pd.notna(r.get('liveness')) else None,
                'acousticness': float(r.get('acousticness', 0.0)) if pd.notna(r.get('acousticness')) else None,
                'instrumentalness': float(r.get('instrumentalness', 0.0)) if pd.notna(r.get('instrumentalness')) else None,
                'danceability': float(r.get('danceability', 0.0)) if pd.notna(r.get('danceability')) else None,
                'year': int(r.get('year')) if pd.notna(r.get('year')) else None,
                'uri': str(r.get('uri')) if pd.notna(r.get('uri')) else None,
                'track_id': str(r.get('track_id')) if pd.notna(r.get('track_id')) else None,
            })
        return items

    @staticmethod
    def filter_to_catalog(playlist: List[Dict], catalog: List[Dict]) -> Tuple[List[Dict], List[str]]:
        # Pastikan hanya item yang persis ada di katalog (title+artist exact match)
        cat_set = set([(c['title'].strip().lower(), c['artist'].strip().lower()) for c in catalog])
        valid = []
        dropped = []
        for t in playlist:
            key = (str(t.get('title','')).strip().lower(), str(t.get('artist','')).strip().lower())
            if key in cat_set:
                valid.append({'title': t['title'], 'artist': t['artist']})
            else:
                dropped.append(f"{t.get('title')} - {t.get('artist')}")
        return valid, dropped