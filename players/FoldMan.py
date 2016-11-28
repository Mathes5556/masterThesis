from pypokerengine.players import BasePokerPlayer
from pokerEngine.historyHandling import addRowToHistory
from pokerEngine.utils import extractInfoFromState

class FoldMan(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    action, amount = 'fold', 0
    pot, levelOfBetting, cardsOnBoard, roundCount, isOnSmallblind, isOnBigBlind, smallBlindAmount, bigBlindAmount, stackOfPlayer, stackOfOpponent = extractInfoFromState(
      self.uuid, round_state)
    addRowToHistory(self.historyDF, [self.hashOfGame, self.uuid, hole_card[0], hole_card[1], action, amount, pot,
                                     levelOfBetting, cardsOnBoard, roundCount, isOnSmallblind, isOnBigBlind
      , smallBlindAmount, bigBlindAmount, stackOfPlayer, stackOfOpponent])
    return action, amount

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, new_action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    print "winnnneeeeer", winners