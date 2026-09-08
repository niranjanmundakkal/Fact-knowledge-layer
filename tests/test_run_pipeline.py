import sys
import os
import io

# Ensure parent path in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.knowledge_layer import KnowledgeLayerService
from app.storage.database import DatabaseManager

def test_pipeline():
    print("Testing pipeline...")
    res = KnowledgeLayerService.load_starter_dataset()
    print("Documents loaded:", res["loaded_documents"])
    stats = res["stats"]
    print(f"Total Facts: {stats.total_facts}")
    print(f"Total Relationships: {stats.total_relationships}")
    print(f"Corroborations: {stats.corroborations_count}")
    print(f"Contradictions: {stats.contradictions_count}")
    print(f"Reconciled: {stats.reconciled_count}")

    facts = DatabaseManager.get_all_facts()
    print(f"\nExtracted {len(facts)} sample facts:")
    for f in facts[:5]:
        print(f"- [{f.document_name} P.{f.page_number}] {f.entity} -> {f.attribute}: {f.value}")

    rels = DatabaseManager.get_all_relationships()
    print(f"\nExtracted {len(rels)} relationships:")
    for r in rels[:5]:
        print(f"- [{r.relationship_type.value} - {r.reconciliation_category.value}] {r.fact_a.attribute} vs {r.fact_b.attribute}")
        print(f"  Reasoning snippet: {r.reasoning[:120]}...")

if __name__ == "__main__":
    test_pipeline()
