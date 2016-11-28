import random as rand

from deuces import Evaluator
from pypokerengine.players import BasePokerPlayer

from pokerEngine.HandStrength import  getSklanskyClass, opponentAgressivness, getAllCards, handStrength
from pokerEngine.historyHandling import addRowToHistory, addResultOfGame
from pokerEngine.utils import extractInfoFromState, cardToCardObject, getBoardToCardsObject, evaluate


class JustGoodCardsPlayer(BasePokerPlayer):
  actionsHistory = []

  def __init__(self, history, hashOfGame, actionsHistory):
    super(JustGoodCardsPlayer, self).__init__(history, hashOfGame)
    self.actionsHistory = actionsHistory

  def set_action_ratio(self, fold_ratio, call_ratio, raise_ratio):
    ratio = [fold_ratio, call_ratio, raise_ratio]
    scaled_ratio = [ 1.0 * num / sum(ratio) for num in ratio]
    self.fold_ratio, self.call_ratio, self.raise_ratio = scaled_ratio

  def declare_action(self, valid_actions, hole_card, round_state):

    opponentAgressivnessScore  = opponentAgressivness(self)
    opponentAgressivnessScoreLast7Round = opponentAgressivness(self, 2)
    card1InString, card2InString = hole_card[0], hole_card[1]
    cardObject1 = cardToCardObject(card1InString)
    cardObject2 = cardToCardObject(card2InString)
    pot, levelOfBetting, cardsOnBoard, roundCount, isOnSmallblind, isOnBigBlind, smallBlindAmount, bigBlindAmount, stackOfPlayer, stackOfOpponent = extractInfoFromState(self.uuid, round_state)
    cardsOnBoardObjects = getBoardToCardsObject(cardsOnBoard)
    allCardsObjectOnBoard = cardsOnBoardObjects[:2 + levelOfBetting - 1]
    evaluator = Evaluator()
    if len(cardsOnBoardObjects) > 0:  # if there is any card on board - so after flop every case
      handStrengthLibrary = evaluate(evaluator, allCardsObjectOnBoard, cardObject1, cardObject2)
    else:  # preFLop
      handStrengthLibrary = 0
    sklanskyClass = getSklanskyClass(card1InString, card2InString)

    cards = getAllCards()
    cards.remove(cardObject1)
    cards.remove(cardObject2)
    for boardCard in cardsOnBoardObjects:
      cards.remove(boardCard)
    evaluator = Evaluator()
    if len(cardsOnBoardObjects) > 0:
      HS = handStrength(cardsOnBoardObjects, cardObject1, cardObject2, cards, evaluator)
    else:
      HS = 0

    EHS, PPOT, NPOT = 0,0,0
    # if len(cardsOnBoardObjects) > 0:  # if there is any card on board - so after flop every case
    #   EHS, HS, PPOT, NPOT = effectiveHandStrength(cardsOnBoardObjects, handStrength, cardObject1, cardObject2)
    # else:
    #   EHS, HS, PPOT, NPOT = 0, 0, 0, 0



    if len(cardsOnBoardObjects) == 0: #PREFLOP
        if sklanskyClass <= 4:
            action = self.__betOrCall()
        else:
            action = "fold"
    else: #FLOP+
        if handStrengthLibrary < 1800:
            action = self.__betOrCall()
        else:
            action = "fold"
    if action == "raise":
        amount = 40
    else:
        amount = 0
        # handle -BigBlind and smallBlind
    if levelOfBetting == 1 and action != "fold":
        if isOnSmallblind:
            realAmountToPlay = amount - smallBlindAmount
        elif isOnBigBlind:
            realAmountToPlay = amount - bigBlindAmount
        else:  # no blind
            realAmountToPlay = amount
    else:
        realAmountToPlay = amount

    addRowToHistory(self.historyDF,
                    [self.hashOfGame, self.uuid, hole_card[0], hole_card[1], action, realAmountToPlay, pot,
                     levelOfBetting, cardsOnBoard, roundCount, isOnSmallblind, isOnBigBlind
                      , smallBlindAmount, bigBlindAmount, stackOfPlayer, stackOfOpponent,
                     sklanskyClass, EHS, HS, PPOT, NPOT, handStrengthLibrary, opponentAgressivnessScore,
                     opponentAgressivnessScoreLast7Round])
    return action, amount

  def __betOrCall(self):
    r = rand.random()
    if r <= 0.5 :
      return "call"
    else:
      return "raise"

  def __choice_action(self, valid_actions):
    r = rand.random()
    if r <= self.fold_ratio:
      return valid_actions[0]
    elif r <= self.call_ratio:
      return valid_actions[1]
    else:
      return valid_actions[2]


  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, new_action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    playersActioInThisGame = {}
    for player in round_state["seats"]:
      uuid = player['uuid']
      playersActioInThisGame[uuid] = []
    actions =  round_state["action_histories"]
    for stageOfRound, listOfActions in sorted(actions.items()):
        print stageOfRound, listOfActions
        for actionObject in listOfActions:
            uuid = actionObject["uuid"]
            action = actionObject["action"]
            playersActioInThisGame[uuid].append(action)
    for uuid in playersActioInThisGame:
        if uuid not in self.actionsHistory:
            self.actionsHistory[uuid] = []
        if uuid == self.uuid:
            actions = playersActioInThisGame[uuid]
            self.actionsHistory[uuid].append(actions)

    roundCount = round_state["round_count"]
    if len(winners) == 1:
      uuidOfWinner = winners[0]["uuid"]
      if uuidOfWinner == self.uuid:
        addResultOfGame(self.historyDF, self.hashOfGame, roundCount, uuidOfWinner, round_state)
    else:
      addResultOfGame(self.historyDF, self.hashOfGame, roundCount, "more winners", round_state)  # TODO handle this