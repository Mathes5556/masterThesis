from deuces import Card, Evaluator
from pokerEngine.utils import extractInfoFromState, cardToCardObject, getBoardToCardsObject, evaluate
import copy
#Card.print_pretty_cards(board)
import time

def getAllCards():
    result = []
    STR_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    colors = ["c", "d", "s", "h"]

    for cardRank in STR_RANKS:
        for color in colors:
            card = Card.new(cardRank + color)
            result.append(card)
    return result

def getAllPairsFromCards(cards):
    result = []
    for card1 in cards:
        for card2 in cards:
            if card1 != card2:
                result.append((card1, card2))
    return result


def worker(evaluator, cardsOnBoardObjects ,turnCard, riverCard, cardObject1, cardObject2, opponentCard1,
                                opponentCard2, currentIndex, return_dict):
    '''worker function'''
    opponentRankHere = evaluate(evaluator, cardsOnBoardObjects + [turnCard, riverCard], opponentCard1,
                                opponentCard2)
    # opponentRankHere = evaluate(cardsOnBoardObjects + [turnCard], opponentCard1, opponentCard2)

    myRankHere = evaluate(evaluator, cardsOnBoardObjects + [turnCard, riverCard], cardObject1, cardObject2)

    if myRankHere < opponentRankHere:
        return_dict[currentIndex]["ahead"] += 1
    elif myRankHere == opponentRankHere:
        return_dict[currentIndex]["tied"] += 1
    else:
        return_dict[currentIndex]["behind"] += 1
    print return_dict


def handStrength(cardsOnBoardObjects, cardObject1, cardObject2, cards, evaluator):
    ahead, tied, behind = 0, 0, 0
    ourRank = evaluate(evaluator, cardsOnBoardObjects, cardObject1, cardObject2)
    possibilitiesForOpponents = getAllPairsFromCards(cards)
    for opponentCard1, opponentCard2 in possibilitiesForOpponents:
        oppRank = evaluate(evaluator, cardsOnBoardObjects, opponentCard1, opponentCard2)
        if ourRank < oppRank:
            ahead += 1
        elif ourRank == oppRank:
            tied += 1
        else:
            behind += 1
    handstrength = (ahead + tied / 2) / float(ahead + tied + behind)
    return handstrength


def getSklanskyClass(card1, card2):
    #http://www.thepokerbank.com/strategy/basic/starting-hand-selection/sklansky-groups/
    SKLANSKY_TABLE = {1 : ["AA", "AKs", "KK", "QQ", "JJ"],
             2 : ["AK", "AQs", "AJs", "KQs", "TT"],
             3 : ["AQ", "ATs", "KJs", "QJs", "JTs", "99"],
             4 : ["AJ", "KQ", "KTs", "QTs", "J9s", "T9s", "98s", "88"],
             5 : ["A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "KJ", "QJ", "JT", "Q9s", "T8s", "97"],
             6 : ["AT", "KT", "QT", "J8s", "86s", "75s", "65s", "55", "54s"],
             7 : ["K9s", "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s", "J9", "T9", "98", "64s", "53s", "44", "43s", "33", "22"],
             8 : ["A9", "K9", "Q9", "J8", "J7s", "T8", "96s", "87", "85s", "76", "74s", "65", "54", "42s", "32s"]
             }
    DEFAULT_CLASS = 9 #if no other class is matched
    card1Value, card1Color = card1[1], card1[0]
    card2Value, card2Color = card2[1], card2[0]
    isSameColorS = "s" if card1Color == card2Color else ""
    combination1 = card1Value + card2Value + isSameColorS #JTs
    combination2 = card2Value + card1Value + isSameColorS #TJs
    combination1WithouSuitChar = card1Value + card2Value  # JT
    combination2WithouSuitChar = card2Value + card1Value  # TJ
    ## first try to match suit combination
    for skalanskyClass, cardsInRow in SKLANSKY_TABLE.items():
        if combination1 in cardsInRow or combination2 in cardsInRow:
            return skalanskyClass
    ## secondly try to match without suit combination
    for skalanskyClass, cardsInRow in SKLANSKY_TABLE.items():
        if combination1WithouSuitChar in cardsInRow or combination2WithouSuitChar in cardsInRow:
            return skalanskyClass
    #if no class was found return 9 class
    return DEFAULT_CLASS


def effectiveHandStrength(cardsOnBoardObjects, currentHandStrength, cardObject1, cardObject2):
    ## https://en.wikipedia.org/wiki/Poker_Effective_Hand_Strength_(EHS)_algorithm
    #TODO
        # 1, potencial extremne dobrych kariet (? x < 500) TODO
        # 2, potencial extremne zlych kariet (? x > 6000) TODO
        # 3, potencial na turne TODO
        # 4, celkovy potencial => zaklad EHS DONE
        # 5, NPOT is the Negative POTential DONE
        # 6, PPOT is the Positive POTential DONE
        # 7, HS is the current Hand Strength DONE
        # 8, potential before FLOP TODO

        # 10, 

    myRank = currentHandStrength
    forbiddenCardInSimulation = [cardObject1] + [cardObject2] + cardsOnBoardObjects
    if cardsOnBoardObjects[0] is not None:  # if there is any card on board - so after flop every case
        HAND_POTENTIAL_TOTAL = {"ahead": 0, "tied": 0, "behind": 0}
        HAND_POTENTIAL = {
            "ahead":  {"ahead": 0, "tied": 0, "behind": 0},
            "tied": {"ahead": 0, "tied": 0, "behind": 0},
            "behind": {"ahead": 0, "tied": 0, "behind": 0},
        }
        STR_RANKS = ["2", "3", "4", "5", "6", "7", "8"]# "9", "T", "J", "Q", "K", "A"]
        colors = ["c", "d", "s", "h"]#, "s", ]

        cards = getAllCards()
        cards.remove(cardObject1)
        cards.remove(cardObject2)
        for boardCard in cardsOnBoardObjects:
            cards.remove(boardCard)
        evaluator = Evaluator()
        HS = handStrength(cardsOnBoardObjects, cardObject1, cardObject2, cards, evaluator)
        start = time.clock()
        alreadyComputedOpponentsCardsHashes = []
        wasAlreadyTurn = len(cardsOnBoardObjects) == 4
        wasAlreadyRiver = len(cardsOnBoardObjects) == 5
        if wasAlreadyRiver:
            return HS, HS, HS, HS
        # from multiprocessing import Manager, Process, Pool
        # import multiprocessing
        # multiprocessing.freeze_support()
        # manager = Manager()
        # return_dict = manager.dict(HAND_POTENTIAL)
        # jobs = []
        # pool = Pool(processes=4)
        # mgr = Manager()
        # return_dict = mgr.dict()
        possibilitiesForOpponents = getAllPairsFromCards(cards)
        for opponentCard1, opponentCard2  in possibilitiesForOpponents:
            hashOfCards = hash(str(cardObject1) + str(cardObject2))
            hashOfCardsOpponents = hash(str(opponentCard1) + str(opponentCard2))# + str(isSameColorOfCardsOpponent))
            hashOfCardsReverseOrderOpponents = hash(str(opponentCard2) + str(opponentCard1))# + str(isSameColorOfCardsOpponent))

            # Card.print_pretty_cards([cardObject2, cardObject1] + cardsOnBoardObjects)
            # Card.print_pretty_cards([opponentCard1, cardObject2])
            goFurther =  opponentCard1 not in forbiddenCardInSimulation \
                         and opponentCard2 not in forbiddenCardInSimulation\
                         and opponentCard1 != opponentCard2 \
                         and hashOfCardsReverseOrderOpponents not in alreadyComputedOpponentsCardsHashes \
                         and hashOfCardsOpponents  not in alreadyComputedOpponentsCardsHashes
            if goFurther:
                alreadyComputedOpponentsCardsHashes.append(hashOfCardsOpponents)
                alreadyComputedOpponentsCardsHashes.append(hashOfCardsReverseOrderOpponents)
                opponentRank = evaluate(evaluator, cardsOnBoardObjects, opponentCard1, opponentCard2)

                if myRank < opponentRank:
                    index = "ahead"
                elif myRank == opponentRank:
                    index = "tied"
                else:
                    index = "behind"
                HAND_POTENTIAL_TOTAL[index] += 1
                if not wasAlreadyTurn:
                    for turnCard, riverCard in possibilitiesForOpponents:
                        if turnCard == opponentCard1 or turnCard == opponentCard2 or riverCard == opponentCard1 or riverCard == opponentCard2:
                            continue
                        # Card.print_pretty_cards(cardsOnBoardObjects + [turnCard, riverCard] + [opponentCard1, opponentCard2])

                        opponentRankHere = evaluate(evaluator, cardsOnBoardObjects + [turnCard, riverCard], opponentCard1,
                                                    opponentCard2)
                        # opponentRankHere = evaluate(cardsOnBoardObjects + [turnCard], opponentCard1, opponentCard2)
                        # Card.print_pretty_cards(cardsOnBoardObjects + [turnCard, riverCard] + [cardObject1, cardObject2])
                        myRankHere = evaluate(evaluator, cardsOnBoardObjects + [turnCard, riverCard], cardObject1,
                                              cardObject2)
                        if myRankHere < opponentRankHere:
                            HAND_POTENTIAL[index]["ahead"] += 1
                        elif myRankHere == opponentRankHere:
                            HAND_POTENTIAL[index]["tied"] += 1
                        else:
                            HAND_POTENTIAL[index]["behind"] += 1
                        HAND_POTENTIAL_TOTAL[index] += 1
                else: #just river card
                    for riverCard in cards:
                        if riverCard == opponentCard1 or riverCard == opponentCard2:
                            continue
                        myRankHere = evaluate(cardsOnBoardObjects + [riverCard], cardObject1, cardObject2)
                        opponentRankHere = evaluate(cardsOnBoardObjects + [riverCard], opponentCard1, opponentCard2)
                        if myRankHere < opponentRankHere:
                            HAND_POTENTIAL[index]["ahead"] += 1
                        elif myRankHere == opponentRankHere:
                            HAND_POTENTIAL[index]["tied"] += 1
                        else:
                            HAND_POTENTIAL[index]["behind"] += 1
                        HAND_POTENTIAL_TOTAL[index] += 1
                    # pool.map(worker, (evaluator, cardsOnBoardObjects ,turnCard, riverCard, cardObject1, cardObject2, opponentCard1,
                    #                                  opponentCard2, index, return_dict))

                    # # p = Process(target=worker, args=(evaluator, cardsOnBoardObjects ,turnCard, riverCard, cardObject1, cardObject2, opponentCard1,
                    # #                                 opponentCard2, index, return_dict))
                    # # jobs.append(p)
                    # # p.start()
                    # # #
                    # # end = time.clock()
                    # # print end - start, "TIME"
                    # # print "1", cardsOnBoardObjects + [turnCard, riverCard], opponentCard1, opponentCard2
                    # # print "2", cardsOnBoardObjects + [turnCard, riverCard], cardObject1, cardObject2
                    #

                # # Mark pool as closed -- no more tasks can be added.
                # pool.close()
                # print "pool to run"
                # # Wait for tasks to exit
                # pool.join()
                # print return_dict
                # exit()
                # print("jobs are inn")
                # for proc in jobs:
                #     proc.join()
                # print return_dict
                # exit()
                #
        print HAND_POTENTIAL

        print time.clock() - start, "TIME"
        print("karty")
        Card.print_pretty_cards([cardObject2, cardObject1] )
        print  "board"
        Card.print_pretty_cards(cardsOnBoardObjects)

        HP = HAND_POTENTIAL
        PPOT = (HP["behind"]["ahead"] + HP["behind"]["tied"] / 2 + HP["tied"]["ahead"] / 2) / float(HAND_POTENTIAL_TOTAL["behind"] + HAND_POTENTIAL_TOTAL["tied"])
        NPOT = (HP["ahead"]["behind"] + HP["tied"]["behind"] / 2 + HP["ahead"]["tied"] / 2) / float(HAND_POTENTIAL_TOTAL["ahead"] + HAND_POTENTIAL_TOTAL["tied"])
        print HP["ahead"]["behind"] , HP["tied"]["behind"] , HP["ahead"]["tied"] ,HAND_POTENTIAL_TOTAL["ahead"] , HAND_POTENTIAL_TOTAL["tied"]
        print "NPOT", NPOT
        print "PPOT", PPOT

        print "HS", HS
        EHS = HS*(1 - NPOT) + (1 - HS)*PPOT
        print "EHS", EHS

        return EHS, HS, PPOT, NPOT











        # exit()
        #
        #
        # # print
        # # print "hand potential"
        # # print HAND_POTENTIAL_TOTAL
        # # print HAND_POTENTIAL
        #
        # import pickle
        #
        # a = {'hello': 'world'}
        #
        # with open('memory.pickle', 'wb') as handle:
        #     pickle.dump(a, handle)
        # print "memory zapisana"
        # with open('memory.pickle', 'rb') as handle:
        #     b = pickle.load(handle)
        #
        # print a == b
        #
        # exit()
    #     Ppot = (HP[behind][ahead] + HP[behind][tied] / 2 + HP[tied][ahead] / 2) / (HAND_POTENTIAL_TOTAL[behind] + HAND_POTENTIAL_TOTAL[tied])
    #
    #     Npot = (HP[ahead][behind] + HP[tied][behind] / 2 + HP[ahead][tied] / 2) / (HAND_POTENTIAL_TOTAL[ahead] + HAND_POTENTIAL_TOTAL[tied])
    # addRowToHistory(self.historyDF, [self.hashOfGame, self.uuid, hole_card[0], hole_card[1], action, amount, pot,


def getAggresivnessRank(listOfActionsInRounds, lastXround=None):
    result = 0
    if lastXround is not None:
        listOfActionsInRoundsToExplore = listOfActionsInRounds[len(listOfActionsInRounds)-lastXround:]
    else:
        listOfActionsInRoundsToExplore = listOfActionsInRounds
    for actions in listOfActionsInRoundsToExplore:
        for action in actions:
            if action in ["SMALLBLIND", "BIGBLIND", "FOLD"]:
                result += 0
            elif action == "CALL":
                result += 1
            elif action == "RAISE":
                result += 10 #TODO here will be bet/amount_to_call
    return result


def opponentAgressivness(self, lastXround=None):
    print "my", self.uuid
    for playerUUID in self.actionsHistory:
        if playerUUID != self.uuid:
            return getAggresivnessRank(self.actionsHistory[playerUUID], lastXround)
    return 0