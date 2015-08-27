import blackjackML as bjml

class Strategy(object):
    #note: it is the strategy's responsibility to stick to the rules and stop when busted
    def __init__(self, hands):
        self.hands = hands

    def wants_to_hit(self, hands, dhand):
        pass
        # needs to return a list of bools, one for each hand

    def wants_to_split_hand(self, hands, dhand):
        pass

    def wants_to_double_down(self, hands, dhand):
        pass


class OptimalStrategy(Strategy):
    def wants_to_hit(self, hands, dhand):
        hit = [True] * len(hands)
        for i, hand in enumerate(hands):
            dv = dhand.value()
            mv = hand.value()
            if hand.has_ace(): #not unique
                if (dv <= 8 or dv == 11) and mv >= 18:
                    hit[i] = False
                elif (dv == 10 or dv == 9) and mv >= 19:
                    hit[i] = False
            else:
                if dv <= 3 and mv >= 13:
                    hit[i] = False
                elif dv in [4,5,6] and mv >= 12:
                    hit[i] = False
                elif dv >= 7 and mv >= 17:
                    hit[i] = False
        return hit

    def wants_to_split_hand(self, hand, dhand):
        #if we arrive here, a split is possible
        mv = hand.value() / 2 # card value
        dv = dhand.value()
        if mv in [8,11]:
            return True
        if mv == 9:
            return dv in range(2,7) +[8,9]
            # 7 left out on purpose
        if mv == 7:
            return dv in range(2,9)
        if mv in [2,3,6]:
            return dv in range(2,8)
        if mv == 4:
            return dv == 5
        return False

    def wants_to_double_down(self, hand, dhand):
        dv = dhand.value()
        mv = dhand.value()
        if hand.has_ace():
            if mv == 11:
                return dv in range(2,11)
            elif mv == 10:
                return dv in range(2,10)
            elif mv == 9:
                return dv in range(2,7)
        else:
            if mv == 18:
                return dv in range (4,7)
            if mv == 17:
                return dv in range(3,7)
            if mv in range(13,17):
                return dv in [5,6]
            if mv == 12:
                return dv == 5
        return False


class DealerStrategy(Strategy):
    def wants_to_hit(self, hands, dhand):
        return [self.hands[0].value() < 17]
        # needs to return a list of bools, one for each hand

    def wants_to_split_hand(self, hands, dhand):
        return False

    def wants_to_double_down(self, hands, dhand):
        return False


class Player(object):
    """ A Player. """
    def __init__(self, name, credit=0, strategy_class=OptimalStrategy):
        self.credit = credit
        self.name = name
        self.history = bjml.History()
        self.strategy_class = strategy_class
        self.reset(hands=[])

    def reset(self, hands):
        self.dd = False
        self.hands = hands
        self.strategy = self.strategy_class(self.hands)
        self.bets = self.bet()

    def add_cards(self, new_cards, mask):
        for hand, draw in zip(self.hands, mask):
            if draw:
                hand.add(new_cards.pop())

    def wants_cards(self, dhand=[]):
        """tell the table how many cards you want"""
        if self.dd and len(self.hands[0].cards) < 3:
            return [True] * len(self.hands)
        if self.can_play():
            return self.strategy.wants_to_hit(self.hands, dhand)
        return [False] * len(self.hands)

#    def show_hands(self):
#        return self.hands()

    def bet(self, bets=[10]):
        self.bets = bets

#    def stands(self):
#        return not any(self.strategy.wants_to_hit())

    def can_play(self):
        #TODO
        return True

    def split_hand(self, dhand):
        for i, hand in enumerate(self.hands):
            if hand.can_split() and self.strategy.wants_to_split_hand(hand, dhand):
                self.hands = [bjml.Hand(cards=[card]) for card in hand.cards]
                self.bets += [self.bets[i]]

    def double_down(self, dhand):
        if all([self.strategy.wants_to_double_down(hand, dhand) for hand in self.hands]):
            self.bets = [bet*2 for bet in self.bets]
            self.dd = True

    def process_information(self, information, game_id):
        self.credit += sum(information['gains'])
        if game_id % 100 == 0:
            print self.credit

class Dealer(Player):
    """ Dealer, a player with a predefined strategy. """
    def __init__(self):
        super(Dealer, self).__init__(name='Dealer', credit=0, strategy_class=DealerStrategy)
        self.is_dealer = True

    def has_ace(self):
        return self.hands[0].has_ace()