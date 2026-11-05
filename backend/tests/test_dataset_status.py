from ml.dataset_status import inventory, markdown


def test_inventory_separates_research_evidence_from_production_approval():
    report = inventory()
    assert report["legacy"]["status"] == "revoked_corrupted_labels"
    assert report["verified_core"]["rows"] == 787
    assert report["verified_core"]["sources"] == {
        "china": 499, "desharnais": 81, "maxwell": 62, "kitchenham": 145,
    }
    assert report["expanded_development"]["rows"] == 891
    assert report["external_diagnostic"]["rows"] == 24
    assert report["research_collection_rows"] == 915
    assert report["production_ml_status"]["approved"] is False
    assert "not a production-approval claim" in markdown(report)
