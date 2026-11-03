from functools import lru_cache



MODEL_NAME = "oksomu/resume-ner"

@lru_cache(maxsize=1)
def load_ner_model():
    import torch
    from transformers import pipeline

    device = 0 if torch.cuda.is_available() else -1
    return pipeline(
        "token-classification",
        model="oksomu/resume-ner",
        aggregation_strategy="simple",
        device=device
        
    )


def extract_entities(text: str) -> dict[str,list[str]]:
    ner_model = load_ner_model()
    results = ner_model(text)
    entities = {}

    for entity in results:
        label = entity["entity_group"]
        value = entity["word"].strip()

        if value:
            entities.setdefault(label, []).append(value)

    return entities

def extract_skills(text:str)->set[str]:
    entities = extract_entities(text)

    return {
        skill.lower().strip()
        for skill in entities.get("SKILL",[])
    }
