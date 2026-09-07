"""
Candidate Matcher: Discovers semantic candidate pairs across documents
using entity normalization and attribute similarity.
"""

import re
from typing import List, Tuple, Dict
from app.models.schema import Fact

ENTITY_SYNONYMS = {
    "delhivery": "Delhivery Limited",
    "delhivery limited": "Delhivery Limited",
    "delhivery private limited": "Delhivery Limited",
    "the company": "Delhivery Limited",
    "our company": "Delhivery Limited",
    "company": "Delhivery Limited",
    "indian logistics market": "Indian Logistics Sector",
    "indian logistics sector": "Indian Logistics Sector",
    "logistics sector": "Indian Logistics Sector"
}

def normalize_entity(entity: str) -> str:
    cleaned = entity.strip().lower()
    return ENTITY_SYNONYMS.get(cleaned, entity.strip())

def tokenize_attribute(attr: str) -> set:
    tokens = re.findall(r'\w+', attr.lower())
    # Exclude trivial stopwords
    stop_words = {"the", "a", "an", "of", "and", "in", "to", "for", "with", "from", "by", "as"}
    return {t for t in tokens if t not in stop_words}

def compute_similarity(attr1: str, attr2: str) -> float:
    set1 = tokenize_attribute(attr1)
    set2 = tokenize_attribute(attr2)
    if not set1 or not set2:
        return 0.0
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

class CandidateMatcher:
    @staticmethod
    def find_candidate_pairs(facts: List[Fact], min_similarity: float = 0.35) -> List[Tuple[Fact, Fact]]:
        """
        Find candidate pairs across documents that likely refer to the same subject metric or claim.
        Avoids quadratic explosion by grouping by normalized entity.
        """
        candidate_pairs: List[Tuple[Fact, Fact]] = []
        
        # Group facts by normalized entity
        entity_groups: Dict[str, List[Fact]] = {}
        for f in facts:
            norm_e = normalize_entity(f.entity)
            entity_groups.setdefault(norm_e, []).append(f)

        for entity, group in entity_groups.items():
            n = len(group)
            for i in range(n):
                for j in range(i + 1, n):
                    fact_a = group[i]
                    fact_b = group[j]

                    # Prioritize cross-document comparisons, but allow same-document if attributes strongly match
                    is_cross_doc = fact_a.document_id != fact_b.document_id
                    sim = compute_similarity(fact_a.attribute, fact_b.attribute)
                    
                    # Direct attribute keyword matches (e.g. both about EBITDA, Revenue, Tonnage, Pin-code, Workforce, Director)
                    direct_topic_match = False
                    keywords = ["revenue", "ebitda", "shipment", "tonnage", "tonnes", "workforce", "team", "pin", "nwc", "director", "secretary", "female"]
                    a_attr_lower = fact_a.attribute.lower()
                    b_attr_lower = fact_b.attribute.lower()
                    for kw in keywords:
                        if kw in a_attr_lower and kw in b_attr_lower:
                            direct_topic_match = True
                            break

                    if (is_cross_doc and (sim >= min_similarity or direct_topic_match)) or (not is_cross_doc and direct_topic_match and a_attr_lower == b_attr_lower):
                        candidate_pairs.append((fact_a, fact_b))

        return candidate_pairs
