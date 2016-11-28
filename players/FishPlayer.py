from deuces import Evaluator
from pypokerengine.players import BasePokerPlayer

from pokerEngine.HandStrength import  getSklanskyClass, effectiveHandStrength, opponentAgressivness
from pokerEngine.historyHandling import addRowToHistory, addResultOfGame
from pokerEngine.utils import extractInfoFromState, cardToCardObject, getBoardToCardsObject, evaluate


class FishPlayer(BasePokerPlayer):
    # if len(allCardsObjectOnBoard) == 3:
    #     actions =  round_state["action_histories"]
    #     for stageOfRound, listOfActions in actions.items():
    #         print stageOfRound, actions
    #     exit()


    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        # print valid_actions
        opponentAgressivnessScore = opponentAgressivness(self)
        opponentAgressivnessScoreLast7Round = opponentAgressivness(self, 7)
        card1InString, card2InString = hole_card[0], hole_card[1]
        cardObject1 = cardToCardObject(card1InString)
        cardObject2 = cardToCardObject(card2InString)
        call_action_info = valid_actions[1]
        action = call_action_info["action"]
        amount = call_action_info["amount"]
        pot, levelOfBetting, cardsOnBoard, roundCount, isOnSmallblind, isOnBigBlind, smallBlindAmount, bigBlindAmount, stackOfPlayer, stackOfOpponent = extractInfoFromState(
            self.uuid, round_state)
        cardsOnBoardObjects = getBoardToCardsObject(cardsOnBoard)
        allCardsObjectOnBoard = cardsOnBoardObjects[:2 + levelOfBetting - 1]
        evaluator = Evaluator()
        print cardsOnBoardObjects
        if len(cardsOnBoardObjects) > 0 : # if there is any card on board - so after flop every case
            handStrength = evaluate(evaluator, allCardsObjectOnBoard, cardObject1, cardObject2)
        else: # preFLop
            handStrength = 0
        sklanskyClass = getSklanskyClass(card1InString, card2InString)

        if len(cardsOnBoardObjects) > 0:  # if there is any card on board - so after flop every case
            EHS, HS, PPOT, NPOT = effectiveHandStrength(cardsOnBoardObjects, handStrength, cardObject1, cardObject2)
        else:
            EHS, HS, PPOT, NPOT  = 0, 0, 0, 0

        #handle -BigBlind and smallBlind
        if levelOfBetting == 1:
            if isOnSmallblind:
                realAmountToPlay = amount - smallBlindAmount
            elif isOnBigBlind:
                realAmountToPlay = amount - bigBlindAmount
            else: #no blind
                realAmountToPlay = amount
        else:
            realAmountToPlay = amount

        addRowToHistory(self.historyDF,
                        [self.hashOfGame, self.uuid, hole_card[0], hole_card[1], action, realAmountToPlay, pot,
                         levelOfBetting, cardsOnBoard, roundCount, isOnSmallblind, isOnBigBlind
                            , smallBlindAmount, bigBlindAmount, stackOfPlayer, stackOfOpponent,
                         sklanskyClass, EHS, HS, PPOT, NPOT, handStrength, opponentAgressivnessScore,
                         opponentAgressivnessScoreLast7Round])
        # print(self.historyDF)
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):

        playersActioInThisGame = {}
        for player in round_state["seats"]:
            uuid = player['uuid']
            playersActioInThisGame[uuid] = []

        actions = round_state["action_histories"]
        for stageOfRound, listOfActions in sorted(actions.items()):
            print stageOfRound, listOfActions
            for actionObject in listOfActions:
                uuid = actionObject["uuid"]
                action = actionObject["action"]
                # actions = [value if value != "RAISE" else actionObject["paid"] for value in actions]
                playersActioInThisGame[uuid].append(action)
                # if action == "":
                #
                # print actionObject
                # print action
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
            addResultOfGame(self.historyDF, self.hashOfGame, roundCount, "more winners",
                            round_state)  # TODO handle this
            print winners
            # raise ValueError("handle this case of more winners")
            # pridat HS z wiki do dat