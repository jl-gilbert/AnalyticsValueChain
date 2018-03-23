import pytest
import sys
sys.path.append("../")
from develop import dataPullProcessFunctions as dppf
from datetime import datetime


def test_date_to_api():
    """Tests function that converts date object to string for API call."""
    testdate = datetime(2018, 3, 10).date()
    assert dppf.date_to_api_format(testdate) == '20180310'


def test_extract_lbj_stats():
    """Tests function that pulls relevant stats out of json dict."""
    testjson = {'stats': {'Pts': {'#text': '1'},
                          'Reb': {'#text': '2'},
                          'Ast': {'#text': '3'},
                          'Fg2PtAtt': {'#text': '4'},
                          'Fg2PtMade': {'#text': '5'},
                          'Fg3PtAtt': {'#text': '6'},
                          'Fg3PtMade': {'#text': '7'},
                          'FtAtt': {'#text': '8'},
                          'FtMade': {'#text': '9'},
                          'PlusMinus': {'#text': '10'},
                          'MinSeconds': {'#text': '600'}}}
    assert dppf.extract_lbj_stats(testjson) == {'Pts': 1,
                                                'Rbs': 2,
                                                'Ast': 3,
                                                '2ptAtt': 4,
                                                '2ptMade': 5,
                                                '3ptAtt': 6,
                                                '3ptMade': 7,
                                                'FtAtt': 8,
                                                'FtMade': 9,
                                                'PlusMinus': 10,
                                                'MinutesPlayed': 10}
