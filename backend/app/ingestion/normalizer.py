from app.ingestion.models import SchemeExtractionResult

class Normalizer:
    """
    Standardizes values extracted from raw text.
    For example, maps 'Construction Worker' or 'Mazdoor' to 'CONSTRUCTION_WORKER'.
    """
    def normalize(self, extracted: SchemeExtractionResult) -> SchemeExtractionResult:
        # In a real implementation, this would use dictionaries, embeddings, or LLM mapping.
        # For our deterministic pipeline on fixtures, the JSON should ideally already be mostly normalized.
        
        # Example normalization logic:
        for rule in extracted.rules:
            if rule.rule_type.upper() == "OCCUPATION":
                if isinstance(rule.value, str):
                    val = rule.value.lower()
                    if "construction" in val or "mazdoor" in val:
                        rule.value = "construction_worker"
        
        return extracted
