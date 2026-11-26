"""Dense (embedding) side of the hybrid retriever (handbook Phase 5.1).

Bi-encoder: sentence-transformers/all-MiniLM-L6-v2 (the handbook's CPU baseline). Vectors are L2-normalised, so
the dot product is the cosine similarity. With 56 KB entries an exact numpy search replaces FAISS IndexFlatIP
(same result, no extra dependency).
Document embeddings are cached in kb/index/dense_<model>.npy together with dense_<model>.json, which records the
model name and the KB fingerprint; a cache built for another model or another KB version is never reused.
"""
import json, os, re

import numpy as np

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class DenseEncoder:
    def __init__(self, root, entries, kb_sha, model_name=DEFAULT_MODEL):
        from sentence_transformers import SentenceTransformer   # heavy import, only when dense retrieval is used
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        safe = re.sub(r"[^\w.-]", "_", model_name)
        d = os.path.join(root, "kb", "index"); os.makedirs(d, exist_ok=True)
        vec, meta = os.path.join(d, f"dense_{safe}.npy"), os.path.join(d, f"dense_{safe}.json")
        ids = [e["case_number"] for e in entries]
        ok = os.path.exists(vec) and os.path.exists(meta)
        if ok:
            m = json.load(open(meta, encoding="utf-8"))
            ok = m.get("model") == model_name and m.get("kb_sha256") == kb_sha and m.get("case_numbers") == ids
        if ok:
            self.doc = np.load(vec)
        else:
            self.doc = self.encode([e["retrieval_text"] for e in entries])
            np.save(vec, self.doc)
            json.dump(dict(model=model_name, kb_sha256=kb_sha, case_numbers=ids, dim=int(self.doc.shape[1])),
                      open(meta, "w", encoding="utf-8"), indent=1)
        self._cache = {}

    def encode(self, texts):
        v = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.ascontiguousarray(np.asarray(v, dtype=np.float32))

    def cosines(self, query_text):
        """Cosine similarity of the query with every KB entry (cached per query text)."""
        if query_text not in self._cache:
            self._cache[query_text] = self.doc @ self.encode([query_text])[0]
        return self._cache[query_text]
