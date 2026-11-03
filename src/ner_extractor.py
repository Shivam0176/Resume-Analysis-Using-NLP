from functools import lru_cache


MODEL_NAME = "oksomu/resume-ner"
MAX_TOKENS = 400
OVERLAP_TOKENS = 50


@lru_cache(maxsize=1)
def load_ner_model():
    import torch
    from transformers import pipeline

    device = 0 if torch.cuda.is_available() else -1

    return pipeline(
        "token-classification",
        model=MODEL_NAME,
        aggregation_strategy="simple",
        device=device,
    )


def chunk_text(
    text: str,
    tokenizer,
    max_tokens: int = MAX_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
) -> list[str]:
    if not text.strip():
        return []

    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False,
    )

    if len(token_ids) <= max_tokens:
        return [text]

    if overlap_tokens >= max_tokens:
        raise ValueError("Overlap must be smaller than max_tokens.")

    chunks = []
    step = max_tokens - overlap_tokens
    start = 0

    while start < len(token_ids):
        end = min(start + max_tokens, len(token_ids))
        chunk_ids = token_ids[start:end]

        chunk = tokenizer.decode(
            chunk_ids,
            skip_special_tokens=True,
        ).strip()

        if chunk:
            chunks.append(chunk)

        if end == len(token_ids):
            break

        start += step

    return chunks


def extract_entities(text: str) -> dict[str, list[str]]:
    ner_model = load_ner_model()
    chunks = chunk_text(text, ner_model.tokenizer)

    entities = {}
    seen_entities = set()

    for chunk in chunks:
        results = ner_model(chunk)

        for entity in results:
            label = entity["entity_group"]
            value = entity["word"].strip()

            if not value:
                continue

            entity_key = (label, value.lower())

            if entity_key in seen_entities:
                continue

            seen_entities.add(entity_key)
            entities.setdefault(label, []).append(value)

    return entities


def extract_skills(text: str) -> set[str]:
    entities = extract_entities(text)

    return {
        skill.lower().strip()
        for skill in entities.get("SKILL", [])
    }
