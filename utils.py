from deuces import Card, Evaluator

def cardToCardObject(card):
    if card is None:
        return None
    return Card.new(card[1] + card[0].lower())

def getBoardToCardsObject(cardsOnBoard):
    result = []
    for card in cardsOnBoard:
        if card is not None:
            result.append(cardToCardObject(card))
    return result

def evaluate(evaluator, allCardsObjectOnBoard, cardObject1, cardObject2):
    try:
        # return 1
        return evaluator.evaluate(allCardsObjectOnBoard, [cardObject1, cardObject2])
    except:
        Card.print_pretty_cards(allCardsObjectOnBoard)
        Card.print_pretty_cards([cardObject1, cardObject2])
        raise ValueError("chcek last cards, some problem with eval")

def proccesCardsOnBoard(cardsOnBoard):
    if len(cardsOnBoard) == 0:
        return [None, None, None, None, None]
    elif len(cardsOnBoard) == 3:
        return [cardsOnBoard[0], cardsOnBoard[1], cardsOnBoard[2], None, None]
    elif len(cardsOnBoard) == 4:
        return [cardsOnBoard[0], cardsOnBoard[1], cardsOnBoard[2], cardsOnBoard[3], None]
    elif len(cardsOnBoard) == 5:
        return [cardsOnBoard[0], cardsOnBoard[1], cardsOnBoard[2], cardsOnBoard[3], cardsOnBoard[4]]
    raise ValueError

def extractInfoFromState(uuid, round_state):
    pot = round_state["pot"]["main"]["amount"] #TODO handle side pot
    levelOfBetting = len(round_state["action_histories"]) #1->PreFlop; 2->afterFlop etc
    cardsOnBoard = proccesCardsOnBoard(round_state["community_card"])
    roundCount  = round_state["round_count"]
    for i, seat in enumerate(round_state["seats"]):
        if uuid == seat["uuid"]:
            stackOfPlayer = seat["stack"]
            positionOnTable = i
        else: #oponentInforioma
            stackOfOpponent = seat["stack"]
        print seat

    print uuid, positionOnTable

    isOnSmallblind = int(positionOnTable == round_state["small_blind_pos"] and levelOfBetting == 1)
    isOnBigBlind = int(positionOnTable == round_state["big_blind_pos"] and levelOfBetting == 1)

    isOnDealerBtn =  positionOnTable == round_state["dealer_btn"]
    smallBlindAmount = round_state["small_blind_amount"]
    bigBlindAmount = smallBlindAmount * 2
    numberOfOpponents = len(round_state["seats"])
    return pot, levelOfBetting, cardsOnBoard, roundCount, isOnSmallblind, isOnBigBlind, smallBlindAmount, bigBlindAmount, stackOfPlayer, stackOfOpponent
