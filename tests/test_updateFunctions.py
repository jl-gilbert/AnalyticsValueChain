import pytest
import sys
sys.path.append("../")
from develop import updateFunctions as uF


def test_reverse_engineer_stats():
    testdata = {'rpg': 3,
                'apg': 4,
                'plusmin': 5,
                '2ptm': 5,
                '3ptm': 2.5,
                'ftm': 8,
                '2pt_pct': 0.5,
                '3pt_pct': 0.25,
                'ft_pct': 0.8}
    assert uF.reverse_engineer_stats(10, testdata) == {'season_rebounds': 30,
                                                       'season_assists': 40,
                                                       'season_plusminus': 50,
                                                       'season_2ptm': 50,
                                                       'season_3ptm': 25,
                                                       'season_ftm': 80,
                                                       'season_2pta': 100,
                                                       'season_3pta': 100,
                                                       'season_fta': 100}
