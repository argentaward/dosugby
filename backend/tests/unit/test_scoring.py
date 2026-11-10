from dataclasses import replace
from datetime import datetime

from app.modules.recommendations.scoring import Candidate, Preferences, passes_filters, rank, score

_DEFAULT_TAGS = {"audience": frozenset({"family"}), "vibe": frozenset({"active"})}


def _candidate(cid: int = 1, **overrides: object) -> Candidate:
    return replace(Candidate(id=cid, tags=_DEFAULT_TAGS), **overrides)


class TestPassesFilters:
    def test_no_preferences_accepts_everything(self) -> None:
        assert passes_filters(_candidate(), Preferences())

    def test_rejects_place_over_budget(self) -> None:
        assert not passes_filters(_candidate(price_level=3), Preferences(max_price=1))

    def test_indoor_preference_rejects_outdoor_place(self) -> None:
        assert not passes_filters(_candidate(is_indoor=False), Preferences(indoor=True))

    def test_mixed_place_matches_any_indoor_preference(self) -> None:
        assert passes_filters(_candidate(is_indoor=None), Preferences(indoor=True))
        assert passes_filters(_candidate(is_indoor=None), Preferences(indoor=False))

    def test_required_audience_must_match(self) -> None:
        prefs = Preferences(tags={"audience": frozenset({"couple"})})
        assert not passes_filters(_candidate(), prefs)

    def test_non_required_group_does_not_filter(self) -> None:
        prefs = Preferences(tags={"vibe": frozenset({"culture"})})
        assert passes_filters(_candidate(), prefs)


class TestScore:
    def test_weights_by_group(self) -> None:
        prefs = Preferences(tags={"audience": frozenset({"family"}), "vibe": frozenset({"active"})})
        assert score(_candidate(), prefs) == 3 + 2

    def test_unknown_group_has_default_weight(self) -> None:
        candidate = _candidate(tags={"season": frozenset({"winter"})})
        assert score(candidate, Preferences(tags={"season": frozenset({"winter"})})) == 1

    def test_no_match_is_zero(self) -> None:
        assert score(_candidate(), Preferences(tags={"vibe": frozenset({"food"})})) == 0


class TestRank:
    def test_orders_by_score_then_promoted_then_freshness(self) -> None:
        prefs = Preferences(tags={"vibe": frozenset({"active", "calm"})})
        best = _candidate(1, tags={"vibe": frozenset({"active", "calm"})})
        promoted = _candidate(2, tags={"vibe": frozenset({"active"})}, is_promoted=True)
        fresh = _candidate(
            3, tags={"vibe": frozenset({"active"})}, verified_at=datetime(2026, 1, 1)
        )
        stale = _candidate(4, tags={"vibe": frozenset({"active"})})

        result = rank([stale, fresh, promoted, best], prefs, limit=10)

        assert [item.candidate.id for item in result] == [1, 2, 3, 4]

    def test_respects_limit_and_filters(self) -> None:
        candidates = [_candidate(i, price_level=i) for i in range(5)]
        result = rank(candidates, Preferences(max_price=2), limit=2)
        assert [item.candidate.id for item in result] == [0, 1]
