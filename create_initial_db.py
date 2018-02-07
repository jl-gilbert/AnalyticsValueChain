"""
Creates initial database using previous seasons' data
and data from thus far in this year.

Only run once to create database, then use update_db.py
"""

from app import db
from develop import dataPullProcessFunctions as dppf
from app.models import Game


def build_db():
    db.drop_all()
    db.create_all()
    print("Db Created.")
    schedule2015 = dppf.schedule('2015-2016-regular','until-20151031')
    for game in schedule2015.games:
        game_stats = Game(date = game['date'],
                          opponent = game['opponent'],
                          home_away = game['home/away'],
                          lbj_days_rest = game['days_rest'],
                          lbj_2pt_pct = game['season_2pt_pct'],
                          lbj_3pt_pct = game['season_3pt_pct'],
                          lbj_ft_pct = game['season_ft_pct'],
                          lbj_2pt_mpg = game['season_2ptpg'],
                          lbj_3pt_mpg = game['season_3ptpg'],
                          lbj_ft_mpg = game['season_ftpg'],
                          lbj_rbs_pgm = game['season_rpg'],
                          lbj_ast_pgm = game['season_apg'],
                          lbj_plusminpg = game['season_plusminpg'],
                          opp_def_eff = game['opp_def_eff'],
                          opp_off_eff = game['opp_off_eff'],
                          pts = game['lbj_pts'],
                          rbs = game['lbj_rbs'],
                          ast = game['lbj_ast'])
        db.session.add(game_stats)
        db.session.commit()
    db.session.close()
    
if __name__ == "__main__":
    build_db()