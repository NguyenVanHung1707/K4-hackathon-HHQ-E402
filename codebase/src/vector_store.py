import os
import re
from typing import List, Dict, Any, Tuple

try:
    from codebase.src.config import get_settings
except ImportError:
    from config import get_settings


class RAGVectorStore:
    """Hệ thống Vector Store & 2-Step Retrieval Logic (Anchor-Enrichment)."""

    def __init__(self):
        self.settings = get_settings()
        self.chroma_client = None
        self.slide_collection = None
        self.transcript_collection = None

        # Primary vector storage (ChromaDB) or in-memory fallback
        try:
            import chromadb
            os.makedirs(self.settings.chroma_db_dir, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=self.settings.chroma_db_dir)
            self.slide_collection = self.chroma_client.get_or_create_collection("slide_core")
            self.transcript_collection = self.chroma_client.get_or_create_collection("transcript_context")
            print(f"[RAGVectorStore] Initialized ChromaDB at {self.settings.chroma_db_dir}")
        except Exception as e:
            print(f"[RAGVectorStore] ChromaDB notice ({e}), using in-memory store.")
            self._slide_memory: List[Dict[str, Any]] = []
            self._transcript_memory: List[Dict[str, Any]] = []

    def chunk_transcript(self, text: str, transcript_id: str) -> List[Dict[str, Any]]:
        """Cắt transcript thành các đoạn kèm mã trích dẫn dòng [transcript_id:Lxx-Lyy]."""
        lines = text.strip().split("\n")
        chunks = []
        chunk_size = 8
        
        for i in range(0, len(lines), chunk_size):
            end_idx = min(i + chunk_size, len(lines))
            chunk_lines = lines[i:end_idx]
            chunk_text = "\n".join(chunk_lines).strip()
            if len(chunk_text) > 20:
                citation = f"[{transcript_id}:L{i+1}-L{end_idx}]"
                chunks.append({
                    "id": f"{transcript_id}_chunk_{i}",
                    "text": chunk_text,
                    "citation": citation,
                    "transcript_id": transcript_id,
                    "line_start": i + 1,
                    "line_end": end_idx
                })
        return chunks

    def ingest_slide(self, slide_id: str, content: str) -> int:
        """Nạp nội dung Slide PDF vào Vector DB (Khối Slide Core - Anchor)."""
        sections = content.split("\n\n")
        count = 0
        for idx, sec in enumerate(sections):
            sec = sec.strip()
            if len(sec) < 15:
                continue
            count += 1
            doc_id = f"slide_{slide_id}_{idx}"
            if self.slide_collection:
                self.slide_collection.upsert(
                    ids=[doc_id],
                    documents=[sec],
                    metadatas=[{"slide_id": slide_id, "type": "slide_core"}]
                )
            else:
                self._slide_memory.append({"id": doc_id, "text": sec, "slide_id": slide_id})
        return count

    def ingest_transcript(self, transcript_id: str, text: str) -> int:
        """Nạp nội dung Transcript vào Vector DB (Khối Transcript Context - Enrichment)."""
        chunks = self.chunk_transcript(text, transcript_id)
        for chunk in chunks:
            if self.transcript_collection:
                self.transcript_collection.upsert(
                    ids=[chunk["id"]],
                    documents=[chunk["text"]],
                    metadatas={
                        "transcript_id": transcript_id,
                        "citation": chunk["citation"],
                        "line_start": chunk["line_start"],
                        "line_end": chunk["line_end"]
                    }
                )
            else:
                self._transcript_memory.append(chunk)
        return len(chunks)

    def two_step_retrieval(self, query: str, transcript_id: str = "T-01") -> Dict[str, Any]:
        """Quy trình 2-Step Retrieval Logic:
        Step 1 (Anchor): Tìm các khái niệm cốt lõi từ Slide.
        Step 2 (Enrichment): Tìm ngữ cảnh chi tiết & ví dụ từ Transcript matching với khái niệm mỏ neo.
        """
        anchors = []
        enrichments = []

        # Step 1: Slide Core Retrieval
        if self.slide_collection and self.slide_collection.count() > 0:
            res = self.slide_collection.query(query_texts=[query], n_results=2)
            if res and res.get("documents"):
                anchors = res["documents"][0]
        else:
            anchors = [item["text"] for item in getattr(self, "_slide_memory", []) if query.lower() in item["text"].lower()][:2]

        # Step 2: Transcript Context Retrieval
        if self.transcript_collection and self.transcript_collection.count() > 0:
            res = self.transcript_collection.query(query_texts=[query], n_results=3)
            if res and res.get("documents"):
                docs = res["documents"][0]
                metas = res["metadatas"][0] if res.get("metadatas") else []
                for doc, meta in zip(docs, metas):
                    enrichments.append({
                        "text": doc,
                        "citation": meta.get("citation", f"[{transcript_id}:L10-L20]"),
                        "transcript_id": meta.get("transcript_id", transcript_id)
                    })
        else:
            mem = getattr(self, "_transcript_memory", [])
            for item in mem:
                if query.lower() in item["text"].lower():
                    enrichments.append(item)
                if len(enrichments) >= 3:
                    break

        return {
            "query": query,
            "anchor_concepts": anchors,
            "enrichment_context": enrichments
        }
