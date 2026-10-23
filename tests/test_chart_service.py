import pandas as pd
import pytest

from services import chart_service

DF = pd.DataFrame({"player": ["A", "B", "C"], "runs": [30, 20, 10]})


@pytest.mark.parametrize("kind", chart_service.CHART_TYPES)
def test_every_chart_type_builds(kind):
    fig = chart_service.build_chart(kind, DF, "player", "runs", "t")
    assert len(fig.data) >= 1


def test_unknown_chart_type_raises():
    with pytest.raises(ValueError):
        chart_service.build_chart("Radar", DF, "player", "runs", "t")