import pandas as pd

from historyHandling import createCsv


def loadCsv(name):
    return  pd.read_csv(name)

def addRowToHistory(df, row):
    df.loc[len(df)] = [len(df)] + row #index + row

def saveToCSv(df, name):
    df.to_csv(name)

def generateHash():
    import hashlib
    import time
    hash = hashlib.sha1()
    hash.update(str(time.time()))
    return hash.hexdigest()


from pypokerengine.api.game import setup_config, start_poker

import multiprocessing

from pokerEngine.players.RandomPlayer import  RandomPlayer
from pokerEngine.players.JustGoodCardsPlayer import JustGoodCardsPlayer


if __name__ == '__main__':
    multiprocessing.freeze_support()


    nameCsv = "historyE.csv" #historyC
    history = createCsv(nameCsv)

    distributions = [{"Fold": 0.1, "Call": 0.5, "Bet": 0.4},  {"Fold": 0.3, "Call": 0.3, "Bet": 0.3},
                     {"Fold": 0.4, "Call": 0.2, "Bet": 0.1},  {"Fold": 0, "Call": 1, "Bet": 0}]
    for distribution1 in distributions:
        for distribution2 in distributions:
            print(distribution1, distribution2)
            for game in range(3):
                hashOfGame = generateHash()
                actionsHistory = {}
                # AgresivPlayer = RandomPlayer(history, hashOfGame, {"Fold": 0.1, "Call": 0.5, "Bet": 0.4}, actionsHistory)
                # FullRandomPlayer =  RandomPlayer(history, hashOfGame, {"Fold": 0.3, "Call": 0.3, "Bet": 0.3}, actionsHistory)
                # PassivePlayer = RandomPlayer(history, hashOfGame, {"Fold": 0.4, "Call": 0.2, "Bet": 0.1}, actionsHistory)
                # ExtremePassivePlayer2 = RandomPlayer(history, hashOfGame, {"Fold": 0, "Call": 1, "Bet": 0}, actionsHistory)
                # ExtremePassivePlayer1 = RandomPlayer(history, hashOfGame, {"Fold": 0, "Call": 1, "Bet": 0}, actionsHistory)
                #
                # FishPlayer =  RandomPlayer(history, hashOfGame, {"Fold": 0.0, "Call": 0.9, "Bet": 0.1})
                ### import all players

                config = setup_config(max_round=100, initial_stack=1500, small_blind_amount=20)

                config.register_player(name="p1", algorithm=RandomPlayer(history, hashOfGame, distribution1, actionsHistory))
                config.register_player(name="p2", algorithm=JustGoodCardsPlayer(history, hashOfGame, actionsHistory))
                # config.register_player(name="p3", algorithm=)
                game_result = start_poker(config, verbose=1)
                saveToCSv(history, nameCsv)
                print "result"
                print game_result
                print actionsHistory
                exit()