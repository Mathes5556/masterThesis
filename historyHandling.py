import pandas as pd


def createCsv(name):
    history = pd.DataFrame(columns=["hashOfGame", "uuid", "playerCard1", "playerCard2", "action", "amount", "pot",
    "levelOfBetting", "cardsOnBoard", "roundCount", "isOnSmallblind", "isOnBigBlind"
    ,"smallBlindAmount", "bigBlindAmount", "stackOfPlayer", "stackOfOpponent", "sklanskyClass",
    "EHS", "HS", "PPOT", "NPOT",  "handStrengthFromLibrary", "opponentAgressivnessScore", "opponentAgressivnessScoreLast7Round",
    "winnerOfRound", "finalPotInGame"])

    # history = pd.DataFrame(columns=["idOfGame", "player", "cardOnHand1", "cardOnHand2",  "action", "amountOfAction, "
    #                                 "pot", "levelOfBetting", "cardsOnBoard", "roundCount", "isOnSmallblind", "isOnBigBlind",
    #                                 "isOnBigBlind", "smallBlindAmount", "bigBlindAmount", "stackOfPlayer", "stackOfOpponent"])

    history.to_csv(name)
    return history

def loadCsv(name):
    return  pd.read_csv(name)

def addRowToHistory(df, row):
    row = row + ["", ""] #for winner and final pot
    df.loc[len(df)] =  row

def saveToCSv(df, name):
    df.to_csv(name)

def addResultOfGame(historyDF, hashOfGame, roundCount, uuidOfWinner, roundState):
    finalPotInGame = roundState["pot"]["main"]["amount"]  # TODO handle side pot
    historyDF.ix[(historyDF.hashOfGame == hashOfGame) & (historyDF.roundCount == roundCount), ["winnerOfRound", "finalPotInGame"]] = [uuidOfWinner, finalPotInGame]
    saveToCSv(historyDF, "history.csv")