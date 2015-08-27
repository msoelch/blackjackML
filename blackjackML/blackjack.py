import random
import itertools
import blackjackML as bjml

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["c", "d", "h", "s"]
RANK_VALUE = {'A': 11,'2': 2,'3': 3,'4': 4,'5': 5,'6': 6,'7': 7,'8': 8,'9': 9,'10': 10,'J': 10,'Q': 10,'K': 10}


class Card(object):
    """ A playing card. """
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return self.rank + self.suit

    def value(self):
        return RANK_VALUE[self.rank]

    def is_ace(self):
        return self.rank=='A'


class Deck(object):
    """ One or multiple decks of playing cards """
    def __init__(self, n_decks=1):
        simple_cards = list(itertools.product(RANKS, SUITS))
        self.cards = [Card(*tuple) for tuple in simple_cards] * n_decks
        self.shuffle()

    def __str__(self):
        return ' '.join([str(card) for card in self.cards]) if self.cards else 'empty Deck'

    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw_cards(self, n_cards=1):
        return [self.cards.pop() for _ in range(n_cards)]
        
    def cards_left(self):
        return len(self.cards)


class Hand(object):
    """ A hand of playing cards. """
    def __init__(self, cards=[]):
        self.clear(new_cards=cards)

    def clear(self, new_cards):
        self.cards = new_cards
        self.bet = 0
        self.stand = False
        self.out = False
        self.dd = 0

    def __str__(self):
        return ' '.join([str(card) for card in self.cards]) if self.cards else 'empty Hand  '

    def sorted_list(self):
        return sorted([card.rank for card in self.cards])
        
    def add(self,card):
        self.cards.append(card)
        
    def value(self):
        ace = sum([card.is_ace() for card in self.cards])
        val = sum([card.value() for card in self.cards])
        while val > 21 and ace > 0:
            val -= 10
            ace -= 1
        return val
        
    def is_triple_seven(self):
        return (len(self.cards) == 3) and all([card.rank==7 for card in self.cards])
        
    def is_blackjack(self):
        return (len(self.cards) == 2) and (self.value() == 21)
        
    def can_split(self):
        return (len(self.cards) == 2) and (self.cards[0].rank == self.cards[1].rank)

    def is_busted(self):
        return self.value() > 21

    def has_ace(self):
        return 'A' in [card.rank for card in self.cards]


class History(object):
    def __init__(self):
        self.game = []

class Table(object):
    def __init__(self, players, n_decks):
        self.n_decks = n_decks
        self.players = players
        self.dealer = bjml.Dealer()
        self.reset()
        
    def reset(self):
        self.deck = Deck(self.n_decks)
        self.reset_players()
        self.reset_dealer()
        self.game_state = []
        self.action = []
        self.gain = 0

    def reset_players(self):
        for p in self.players:
            p.reset([Hand(self.deck.draw_cards(n_cards=2))])

    def reset_dealer(self):
        self.dealer.reset([Hand(self.deck.draw_cards(n_cards=1))])

    def play_dealer(self):
        while any(self.dealer.wants_cards()):
            mask = self.dealer.wants_cards()
            new_cards = self.deck.draw_cards(n_cards=sum(mask))
            self.dealer.add_cards(new_cards, mask)
        return self.dealer.hands[0]


    def play_a_game(self, game_id):
        self.reset()
        for p in self.players:
            p.bet()
            p.split_hand(self.dealer.hands[0])
            p.double_down(self.dealer.hands[0])

            while any(p.wants_cards(self.dealer.hands[0])):
                # one new card for each hand player p wants to keep playing
                mask = p.wants_cards(self.dealer.hands[0])
                new_cards = self.deck.draw_cards(n_cards=sum(mask))
                p.add_cards(new_cards, mask)

            dhand = self.play_dealer()

            information = self.evaluate_p_vs_d(p, dhand)

            p.process_information(information,game_id)


    def evaluate_p_vs_d(self, p, dhand):
        gains = [0] * len(p.hands)
        for i, phand in enumerate(p.hands):
            #print phand, '/', dhand
            if phand.is_busted():
                # player loses
                gains[i] = -p.bets[i]
            elif dhand.is_blackjack() and phand.is_blackjack():
                ###drawn
                gains[i] = 0
            elif dhand.is_blackjack():
                ###player loses
                gains[i] = -p.bets[i]
            elif phand.is_blackjack():
                ###player wins
                gains[i] = 1.5*p.bets[i]
            elif dhand.is_busted():
                ###player wins
                gains[i] = p.bets[i]
            elif dhand.value() < phand.value():
                ###player wins
                gains[i] = p.bets[i]
            elif dhand.value() == phand.value():
                ###drawn
                gains[i] = 0
            else:
                ###player loses
                gains[i] = -p.bets[i]
        #print gains
        return {'gains': gains
                }

class GameState(object):
    def __init__(self,ins,spl,ddo,h1,dh):
        self.ins = ins
        self.spl = spl
        self.ddo = ddo
        self.h1 = h1
        self.dh = dh
        
    def __hash__(self):
        return hash((self.ins,self.spl,self.ddo,self.h1.__str__(),"-",self.dh.__str__()))
    
class Strategy(object):
    def __init__(self):
        self.table = {}










