import os

import pytest

from btc_research.research import ExperimentFamily, Hypothesis
from btc_research.research.supabase import SupabaseResearchClient


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"), reason="Supabase integration credentials not configured")
def test_supabase_can_insert_and_read_family() -> None:
    family = ExperimentFamily("test-family", "integration-test")
    with SupabaseResearchClient() as db:
        rows = db.insert_family(family)
        assert rows
        fetched = db.select("experiment_families", "select=family_key&family_key=eq.test-family")
        assert fetched and fetched[0]["family_key"] == "test-family"


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"), reason="Supabase integration credentials not configured")
def test_supabase_can_insert_hypothesis() -> None:
    family = ExperimentFamily("test-family-h", "integration-test")
    hypothesis = Hypothesis.create("test-hypothesis", family.family_id, "test", 60, "two_sided")
    with SupabaseResearchClient() as db:
        db.insert_family(family)
        rows = db.insert_hypothesis(hypothesis)
        assert rows and rows[0]["hypothesis_key"] == hypothesis.hypothesis_id
