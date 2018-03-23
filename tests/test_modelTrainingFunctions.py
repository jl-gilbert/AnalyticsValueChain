import pandas as pd
import sys
sys.path.append("../")
from develop import modelTrainingFunctions as mTF


def test_convert_home_away():
    """Tests function that converts home/away to binary numeric variable."""
    testframe = pd.DataFrame.from_dict({
            'home_away': ['home', 'home', 'away']})
    mTF.convert_home_away(testframe)
    result = [testframe.home_away.values[0].astype(int),
              testframe.home_away.values[1].astype(int),
              testframe.home_away.values[2].astype(int)]
    assert result == [1, 1, 0]


def test_extract_predictors():
    """Tests function that extracts predictor columns from dataframe."""
    testframe = pd.DataFrame.from_dict({
            'pts': [1],
            'rbs': [1],
            'ast': [1],
            'home_away': [1],
            'lbj_days_rest': [1],
            'lbj_2pt_pct': [1],
            'lbj_3pt_pct': [1],
            'lbj_ft_pct': [1],
            'lbj_2pt_mpg': [1],
            'lbj_3pt_mpg': [1],
            'lbj_ft_mpg': [1],
            'lbj_rbs_pgm': [1],
            'lbj_ast_pgm': [1],
            'lbj_plusminpg': [1],
            'opp_def_eff': [1],
            'opp_off_eff': [1]})
    assert len(mTF.extract_predictors(testframe).columns) == 13
   