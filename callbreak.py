from __future__ import division

from copy import deepcopy
from mcts import mcts
from functools import reduce
import operator
import random

def find_card_rank(card):
    map_cards = {
        '1': '14',
        'T': '10',
        'J': '11',
        'Q': '12',
        'K': '13',
    }
    for key in map_cards:
        if key in card[:1]:
            card = card.replace(key, map_cards[key])
    if '1' in card:
        card = int(card[:2])
    else:
        card = int(card[:1])
    return card

def find_certain_score(my_cards, others_remaining_cards):
    certain_score = 0
    if '1S' in my_cards and 'KS' in my_cards:
        certain_score += 2
    elif '1S' in my_cards:
        certain_score += 1
    elif '1S' not in others_remaining_cards and 'KS' in my_cards:
        certain_score += 1
    # others_spades = [card for card in others_remaining_cards if 'S' in card]
    # my_spades = [card for card in my_cards if 'S' in card]
    # if len(others_spades) == 0:
    #     certain_score += len(my_spades)
    return certain_score

def find_current_score_from_history(history_list, my_index):
    current_score = 0
    for history in history_list:
        winner_index = history[2]
        if my_index == winner_index:
            current_score += 1
    return current_score

map_high_cards = {
    10: 'T',
    11: 'J',
    12: 'Q',
    13: 'K',
    14: '1'
}

def find_winning_card(cards):
    first_card = cards[0]
    first_suit = first_card[1]
    # print(first_suit)
    spade_cards = [card for card in cards if 'S' in card]
    if len(spade_cards) >= 1:
        spade_max = find_max_card(spade_cards)
        if spade_max > 9:
            spade_max_face = map_high_cards[spade_max]
        else:
            spade_max_face = str(spade_max)
        return spade_max_face + 'S'
    else:
        valid_cards = [card for card in cards if first_suit in card]
        max_suit = find_max_card(valid_cards)
        if max_suit > 9:
            max_suit_face = map_high_cards[max_suit]
        else:
            max_suit_face = str(max_suit)
        return max_suit_face + first_suit

def get_face(card):
    if card[0:2] == '10':
        return 'T' + card[2]
    elif card[0:2] == '11':
        return 'J' + card[2]
    elif card[0:2] == '12':
        return 'Q' + card[2]
    elif card[0:2] == '13':
        return 'K' + card[2]
    else:
        return card

all_cards = {str(face) + str(suit) for face in range(1, 14) for suit in ('S', 'C', 'H', 'D')}
all_cards = {get_face(card) for card in all_cards}

def find_max_card(cards):
    if len(cards) == 0:
        return 0
    map_cards = {
        '1': '14',
        'T': '10',
        'J': '11',
        'Q': '12',
        'K': '13',
    }
    mapped_cards = []
    for card in cards[:]:
        for key in map_cards:
            if key in card[:1]:
                card = card.replace(key, map_cards[key])
        if '1' in card:
            card = int(card[:2])
        else:
            card = int(card[:1])
        mapped_cards.append(card)
    return int(max(mapped_cards))

class Callbreak():
    def __init__(self, my_cards={}, history_cards=[], player_list=[], my_player=None, current_player=None, 
            round=None, played_cards=[], current_player_index=None, player_bids=[1,1,1,1], player_scores=[0,0,0,0], context=None, player_constraints=[None, None, None, None]):
        self.my_cards = my_cards
        if my_cards == {}:
            self.my_cards = {'1C', '1S', 'TS', '6S', '1H', 'JH', '7H', 'KC', '8C', '7C', 'KD', 'QD', 'JD'}
        self.history_cards = history_cards
        self.player_list = player_list
        self.my_player = my_player
        self.my_player_index = self.player_list.index(self.my_player)
        self.current_player = current_player
        self.round = round
        self.played_cards = played_cards
        self.current_player_index = current_player_index
        history_cards_set = set()  # creates empty set
        for history in history_cards:
            previous_cards = history[1]
            for prev_card in previous_cards:
                prev_card = prev_card[0:2]
                history_cards_set.add(prev_card)
        self.history_cards_set = history_cards_set
        self.cards_to_choose_from = set(all_cards)
        for my_card in self.my_cards:
            if my_card in self.cards_to_choose_from:
                self.cards_to_choose_from.remove(my_card)

        for history_card in self.history_cards_set:
            if history_card in self.cards_to_choose_from:
                self.cards_to_choose_from.remove(history_card)
        for played_card in self.played_cards:
            if played_card in self.cards_to_choose_from:
                self.cards_to_choose_from.remove(played_card)

        self.player_bids = player_bids
        self.player_scores = player_scores
        # self.my_bid = my_bid
        # self.my_score = my_score
        self.context = context
        self.player_constraints = player_constraints
        self.game_completed = False

    def getCurrentPlayer(self):
        # 1 is my player
        # -1 is other player
        if self.my_player == self.current_player:
            return 1
        else:
            return -1

    def getPossibleActions(self):  # the possible actions will be limited by the self.player_constraints
        possibleActions = []
        # for i in range(len(self.board)):
        #     for j in range(len(self.board[i])):
        #         if self.board[i][j] == 0:
        #             possibleActions.append(Action(player=self.currentPlayer, x=i, y=j))
        # check if suit played is present in current cards
        if len(self.played_cards) == 0:
            first_played_suit = ''  # '' means i can play any card
            first_played_card = None
        else:
            first_played_card = self.played_cards[0]
            first_played_suit = first_played_card[1]

        # find max_other_card played
        if len(self.played_cards) > 0:
            new_played = [card for card in self.played_cards if first_played_suit in card[0:2]]
            max_played_card = int(find_max_card(new_played))
        else:
            max_played_card = 0

        if self.current_player == self.my_player:
            # logic for when it is my turn
            # there is certainty of what cards i can choose from
            options = {card for card in self.my_cards if first_played_suit in card}
            if len(options) == 0:  # when length of options is 0, it means i don't have that suit, so i can play suit
                options = {card for card in self.my_cards if 'S' in card}
                new_played = [card for card in self.played_cards if 'S' in card[0:2]]
                max_played_card = int(find_max_card(new_played))
            if len(options) == 0:  # if options is still 0, include all cards as options
                options = {card for card in self.my_cards}
                # reset max_played_card rank
                # but this time use the least ranked card by setting max_played_card to 0
                max_played_card = 0
            options = tuple(options)
            options_greater_than_max_played_card = [option for option in options if find_card_rank(option) > max_played_card]
            options_greater_than_max_played_card = [option for option in options_greater_than_max_played_card if first_played_suit in option or 'S' in option]

            options_less_than_max_played_card = [option for option in options if find_card_rank(option) < max_played_card]
            options_less_than_max_played_card = [option for option in options_less_than_max_played_card if first_played_suit in option or 'S' in option]

            if len(options_greater_than_max_played_card) > 0:
                options = options_greater_than_max_played_card
                options_rankings = [find_card_rank(option) for option in options_greater_than_max_played_card]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = options_greater_than_max_played_card[best_index]

                # Don't waste high ranking non-spade cards if one player has already played a spade
                # e.g. if 9D is the first card and 2nd card is 2S, if i have ['TD', '5D'] I shouldn't play TD
                # as i would lose to 2S, so instead I should play 5D here
                new_played = [card for card in self.played_cards if 'S' in card[0:2]]
                if len(new_played) >= 1 and 'S' not in best_option and first_played_suit != 'S':
                    new_options = [card for card in self.my_cards if first_played_suit in card]
                    if len(new_options) >= 1:
                        # confirm that i actually have a non-spade card
                        # only choose new best option if my non-spade card count is greater than 0
                        options_rankings = [find_card_rank(option) for option in new_options]
                        min_option_rank = min(options_rankings)
                        best_index = options_rankings.index(min_option_rank)
                        best_option = new_options[best_index]
                        options = [best_option]

            elif len(options_less_than_max_played_card) > 0:
                options = options_less_than_max_played_card
                options_rankings = [find_card_rank(option) for option in options_less_than_max_played_card]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = options_less_than_max_played_card[best_index]

                # Don't throw away spade needlessly
                # When the first player played a non-spade card and someone else played a spade card
                # If I don't have that first player played suit and also dont' have a spade card that can with the 2nd, 3rd players spade card
                # I don't have to play spade and instead can play any other card
                new_played = [card for card in self.played_cards if 'S' in card[0:2]]
                if len(new_played) >= 1 and 'S' in best_option and first_played_suit != 'S':

                    # i'm already checking for options with spades less than 2nd, 3rd player
                    # so my current spade card will not win,
                    # so i have to play a non-spade card of least rank
                    new_options = tuple(card for card in self.my_cards if 'S' not in card)
                    if len(new_options) >= 1:
                        # confirm that i actually have a non-spade card
                        # only choose new best option if my non-spade card count is greater than 0
                        options_rankings = [find_card_rank(option) for option in new_options]
                        min_option_rank = min(options_rankings)
                        best_index = options_rankings.index(min_option_rank)
                        best_option = new_options[best_index]
                        options = [best_option]
        else:
            # logic for when it is not my turn
            # there is not certainty of what cards they can choose from
            # so they'll be allowed to choose from self.cards_to_choose_from
            constrained_cards_to_choose_from = {card for card in self.cards_to_choose_from}
            
            spade_eliminated = self.player_constraints[self.current_player_index]['diamond_eliminated']
            club_eliminated = self.player_constraints[self.current_player_index]['club_eliminated']
            heart_eliminated = self.player_constraints[self.current_player_index]['heart_eliminated']
            diamond_eliminated = self.player_constraints[self.current_player_index]['diamond_eliminated']

            spade_greater_than_rank = self.player_constraints[self.current_player_index]['spade_greater_than_rank']
            club_greater_than_rank = self.player_constraints[self.current_player_index]['club_greater_than_rank']
            heart_greater_than_rank = self.player_constraints[self.current_player_index]['heart_greater_than_rank']
            diamond_greater_than_rank = self.player_constraints[self.current_player_index]['diamond_greater_than_rank']

            if spade_eliminated:
                constrained_cards_to_choose_from = {card for card in constrained_cards_to_choose_from if 'S' not in card}
            if club_eliminated:
                constrained_cards_to_choose_from = {card for card in constrained_cards_to_choose_from if 'C' not in card}
            if heart_eliminated:
                constrained_cards_to_choose_from = {card for card in constrained_cards_to_choose_from if 'H' not in card}
            if diamond_eliminated:
                constrained_cards_to_choose_from = {card for card in constrained_cards_to_choose_from if 'D' not in card}

            if not spade_eliminated:
                negative_constrained_spades = {card for card in constrained_cards_to_choose_from if 'S' in card and find_card_rank(card) <= spade_greater_than_rank}
                # negative_constrained_spades = set(negative_constrained_spades)
                # constrained_cards_to_choose_from = set(constrained_cards_to_choose_from)
                constrained_cards_to_choose_from -= negative_constrained_spades
                # constrained_cards_to_choose_from = list(constrained_cards_to_choose_from)
            if not club_eliminated:
                negative_constrained_clubs = {card for card in constrained_cards_to_choose_from if 'C' in card and find_card_rank(card) <= club_greater_than_rank}
                # negative_constrained_clubs = set(negative_constrained_clubs)
                # constrained_cards_to_choose_from = set(constrained_cards_to_choose_from)
                constrained_cards_to_choose_from -= negative_constrained_clubs
                # constrained_cards_to_choose_from = list(constrained_cards_to_choose_from)
            if not heart_eliminated:
                negative_constrained_hearts = {card for card in constrained_cards_to_choose_from if 'H' in card and find_card_rank(card) <= heart_greater_than_rank}
                # negative_constrained_hearts = set(negative_constrained_hearts)
                # constrained_cards_to_choose_from = set(constrained_cards_to_choose_from)
                constrained_cards_to_choose_from -= negative_constrained_hearts
                # constrained_cards_to_choose_from = list(constrained_cards_to_choose_from)
            if not diamond_eliminated:
                negative_constrained_diamonds = {card for card in constrained_cards_to_choose_from if 'D' in card and find_card_rank(card) <= diamond_greater_than_rank}
                # negative_constrained_diamonds = set(negative_constrained_diamonds)
                # constrained_cards_to_choose_from = set(constrained_cards_to_choose_from)
                constrained_cards_to_choose_from -= negative_constrained_diamonds
                # constrained_cards_to_choose_from = list(constrained_cards_to_choose_from)

            options = {card for card in constrained_cards_to_choose_from if first_played_suit in card}

            if len(options) == 0:  # when length of options is 0, it means i don't have that suit, so i can play suit
                options = {card for card in constrained_cards_to_choose_from if 'S' in card}
                new_played = [card for card in self.played_cards if 'S' in card[0:2]]
                max_played_card = int(find_max_card(new_played))
            if len(options) == 0:  # if options is still 0, include all cards as options
                options = {card for card in self.cards_to_choose_from}
                # reset max_played_card rank
                # but this time use the least ranked card by setting max_played_card to 0
                max_played_card = 0
            options = tuple(options)
            options_greater_than_max_played_card = [option for option in options if find_card_rank(option) > max_played_card]
            options_greater_than_max_played_card = [option for option in options_greater_than_max_played_card if first_played_suit in option or 'S' in option]

            options_less_than_max_played_card = [option for option in options if find_card_rank(option) < max_played_card]
            options_less_than_max_played_card = [option for option in options_less_than_max_played_card if first_played_suit in option or 'S' in option]

            if len(options_greater_than_max_played_card) > 0:
                options = options_greater_than_max_played_card
                options_rankings = [find_card_rank(option) for option in options_greater_than_max_played_card]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = options_greater_than_max_played_card[best_index]

                # Don't waste high ranking non-spade cards if one player has already played a spade
                # e.g. if 9D is the first card and 2nd card is 2S, if i have ['TD', '5D'] I shouldn't play TD
                # as i would lose to 2S, so instead I should play 5D here
                new_played = [card for card in self.played_cards if 'S' in card[0:2]]
                if len(new_played) >= 1 and 'S' not in best_option and first_played_suit != 'S':
                    new_options = tuple(card for card in constrained_cards_to_choose_from if first_played_suit in card)
                    if len(new_options) >= 1:
                        # confirm that i actually have a non-spade card
                        # only choose new best option if my non-spade card count is greater than 0
                        options_rankings = [find_card_rank(option) for option in new_options]
                        min_option_rank = min(options_rankings)
                        best_index = options_rankings.index(min_option_rank)
                        best_option = new_options[best_index]
                        options = [best_option]

            elif len(options_less_than_max_played_card) > 0:
                options = options_less_than_max_played_card
                options_rankings = [find_card_rank(option) for option in options_less_than_max_played_card]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = options_less_than_max_played_card[best_index]

                # Don't throw away spade needlessly
                # When the first player played a non-spade card and someone else played a spade card
                # If I don't have that first player played suit and also dont' have a spade card that can with the 2nd, 3rd players spade card
                # I don't have to play spade and instead can play any other card
                new_played = [card for card in self.played_cards if 'S' in card[0:2]]
                if len(new_played) >= 1 and 'S' in best_option and first_played_suit != 'S':

                    # i'm already checking for options with spades less than 2nd, 3rd player
                    # so my current spade card will not win,
                    # so i have to play a non-spade card of least rank
                    new_options = tuple(card for card in constrained_cards_to_choose_from if 'S' not in card)
                    if len(new_options) >= 1:
                        # confirm that i actually have a non-spade card
                        # only choose new best option if my non-spade card count is greater than 0
                        options_rankings = [find_card_rank(option) for option in new_options]
                        min_option_rank = min(options_rankings)
                        best_index = options_rankings.index(min_option_rank)
                        best_option = new_options[best_index]
                        options = [best_option]

        # print("First card: ", first_played_card)
        # print("First Suit: ", first_played_suit)
        # print("Current Player: ", self.current_player)
        # print("Options: ", options)

        for option in options:
            possible_action = Action(player=self.current_player, card=option)
            possibleActions.append(possible_action)
        return possibleActions

    def takeAction(self, action):
        newState = deepcopy(self)
        # newState = self
        # newState.history_cards_set.add(action.card)
        ## after card is played in action.card
        ## the my_cards list decreases by 1
        ## but at the same time. since the player is changed to someone else.
        ## their card is completely different than mine
        ## their card becomes a random card generated out of the whole set - my_cards - action.card - history_cards
        ## also the length of their card will be exactly my card length
        
        # if len(newState.my_cards) == 1:
        #     newState.game_completed = True
        
        newState.played_cards.append(action.card)
        if len(newState.played_cards) == 4:
            # check the winner
            fourth_player = newState.current_player
            fourth_player_index = newState.current_player_index
            
            first_player_index = (newState.current_player_index + 1) % 4
            second_player_index = (newState.current_player_index + 2) % 4
            third_player_index = (newState.current_player_index + 3) % 4

            first_player = newState.player_list[first_player_index]
            second_player = newState.player_list[second_player_index]
            third_player = newState.player_list[third_player_index]

            first_card = newState.played_cards[0][0:2]
            second_card = newState.played_cards[1][0:2]
            third_card = newState.played_cards[2][0:2]
            fourth_card = deepcopy(action.card)[0:2]
            four_cards = [first_card, second_card, third_card, fourth_card]

            winner_card = find_winning_card(four_cards)
            # print([first_card, second_card, third_card, fourth_card])
            # print("Winner -------------------------------------------------------> ", winner_card)
            winner_index = four_cards.index(winner_card)

            # new_history = [first_player_index, deepcopy(four_cards), winner_index]
            new_history = [first_player_index, four_cards, winner_index]
            newState.history_cards.append(new_history)

            # After 4 cards, the played cards should be reset to empty list for next state
            newState.played_cards = []
            # Finally change the score values in the self.player_scores list
            newState.player_scores[winner_index] += 1

            for i in range(4):
                score = newState.player_scores[i]
                bid = newState.player_bids[i]
                if score >= 8 and bid == 8:
                    newState.game_completed = True

            if newState.current_player == newState.my_player:
                # logic for when it is my turn
                # there is certainty of what cards i can choose from
                newState.my_cards.remove(action.card)
                if len(newState.my_cards) == 0:
                    newState.game_completed = True
            else:
                # logic for when it is not my turn
                # there is not certainty of what cards they can choose from
                # so they'll be allowed to choose from self.cards_to_choose_from
                newState.cards_to_choose_from.remove(action.card)
                if len(newState.cards_to_choose_from) == 0:
                    newState.game_completed = True
            
            # Also change the current_player and current_player_index for the newState to the current winner index
            newState.current_player_index = winner_index
            newState.current_player = newState.player_list[winner_index]
        else:
            # not 4 players, so winner cannot be decided
            # change the current player to the next indexed player list
            next_player_index = (newState.current_player_index + 1) % 4
            newState.current_player_index = next_player_index
            newState.current_player = newState.player_list[next_player_index] ## change by index to next player
            
            if len(newState.played_cards) == 0:
                first_played_suit = ''  # '' means i can play any card
                first_played_card = None
            else:
                first_played_card = newState.played_cards[0]
                first_played_suit = first_played_card[1]

            # find max_other_card played
            if len(newState.played_cards) > 0:
                new_played = [card for card in newState.played_cards if first_played_suit in card[0:2]]
                max_played_card = int(find_max_card(new_played))
            else:
                max_played_card = 0

            if newState.current_player == newState.my_player:
                # logic for when it is my turn
                # there is certainty of what cards i can choose from
                options = {card for card in newState.my_cards if first_played_suit in card}
                if len(options) == 0:  # when length of options is 0, it means i don't have that suit, so i can play suit
                    options = {card for card in newState.my_cards if 'S' in card}
                    new_played = [card for card in newState.played_cards if 'S' in card[0:2]]
                    max_played_card = int(find_max_card(new_played))
                if len(options) == 0:  # if options is still 0, include all cards as options
                    options = {card for card in newState.my_cards}
                    # reset max_played_card rank
                    # but this time use the least ranked card by setting max_played_card to 0
                    max_played_card = 0
                options = tuple(options)
                options_greater_than_max_played_card = [option for option in options if find_card_rank(option) > max_played_card]
                options_greater_than_max_played_card = [option for option in options_greater_than_max_played_card if first_played_suit in option or 'S' in option]

                options_less_than_max_played_card = [option for option in options if find_card_rank(option) < max_played_card]
                options_less_than_max_played_card = [option for option in options_less_than_max_played_card if first_played_suit in option or 'S' in option]

                if len(options_greater_than_max_played_card) > 0:
                    options = options_greater_than_max_played_card
                    options_rankings = [find_card_rank(option) for option in options_greater_than_max_played_card]
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = options_greater_than_max_played_card[best_index]

                    # Don't waste high ranking non-spade cards if one player has already played a spade
                    # e.g. if 9D is the first card and 2nd card is 2S, if i have ['TD', '5D'] I shouldn't play TD
                    # as i would lose to 2S, so instead I should play 5D here
                    new_played = [card for card in newState.played_cards if 'S' in card[0:2]]
                    if len(new_played) >= 1 and 'S' not in best_option and first_played_suit != 'S':
                        new_options = [card for card in newState.my_cards if first_played_suit in card]
                        if len(new_options) >= 1:
                            # confirm that i actually have a non-spade card
                            # only choose new best option if my non-spade card count is greater than 0
                            options_rankings = [find_card_rank(option) for option in new_options]
                            min_option_rank = min(options_rankings)
                            best_index = options_rankings.index(min_option_rank)
                            best_option = new_options[best_index]
                            options = [best_option]

                elif len(options_less_than_max_played_card) > 0:
                    options = options_less_than_max_played_card
                    options_rankings = [find_card_rank(option) for option in options_less_than_max_played_card]
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = options_less_than_max_played_card[best_index]

                    # Don't throw away spade needlessly
                    # When the first player played a non-spade card and someone else played a spade card
                    # If I don't have that first player played suit and also dont' have a spade card that can with the 2nd, 3rd players spade card
                    # I don't have to play spade and instead can play any other card
                    new_played = [card for card in newState.played_cards if 'S' in card[0:2]]
                    if len(new_played) >= 1 and 'S' in best_option and first_played_suit != 'S':

                        # i'm already checking for options with spades less than 2nd, 3rd player
                        # so my current spade card will not win,
                        # so i have to play a non-spade card of least rank
                        new_options = tuple(card for card in newState.my_cards if 'S' not in card)
                        if len(new_options) >= 1:
                            # confirm that i actually have a non-spade card
                            # only choose new best option if my non-spade card count is greater than 0
                            options_rankings = [find_card_rank(option) for option in new_options]
                            min_option_rank = min(options_rankings)
                            best_index = options_rankings.index(min_option_rank)
                            best_option = new_options[best_index]
                            options = [best_option]
                # logic for when it is my turn
                # there is certainty of what cards i can choose from
                card_chosen = random.choice(options)
                newState.played_cards.append(card_chosen)
                newState.my_cards.remove(card_chosen)
            else:
                # logic for when it is not my turn
                # there is not certainty of what cards they can choose from
                # so they'll be allowed to choose from self.cards_to_choose_from
                constrained_cards_to_choose_from = {card for card in self.cards_to_choose_from}
                
                spade_eliminated = self.player_constraints[self.current_player_index]['diamond_eliminated']
                club_eliminated = self.player_constraints[self.current_player_index]['club_eliminated']
                heart_eliminated = self.player_constraints[self.current_player_index]['heart_eliminated']
                diamond_eliminated = self.player_constraints[self.current_player_index]['diamond_eliminated']

                spade_greater_than_rank = self.player_constraints[self.current_player_index]['spade_greater_than_rank']
                club_greater_than_rank = self.player_constraints[self.current_player_index]['club_greater_than_rank']
                heart_greater_than_rank = self.player_constraints[self.current_player_index]['heart_greater_than_rank']
                diamond_greater_than_rank = self.player_constraints[self.current_player_index]['diamond_greater_than_rank']

                if spade_eliminated:
                    constrained_cards_to_choose_from = {card for card in constrained_cards_to_choose_from if 'S' not in card}
                if club_eliminated:
                    constrained_cards_to_choose_from = {card for card in constrained_cards_to_choose_from if 'C' not in card}
                if heart_eliminated:
                    constrained_cards_to_choose_from = {card for card in constrained_cards_to_choose_from if 'H' not in card}
                if diamond_eliminated:
                    constrained_cards_to_choose_from = {card for card in constrained_cards_to_choose_from if 'D' not in card}

                if not spade_eliminated:
                    negative_constrained_spades = {card for card in constrained_cards_to_choose_from if 'S' in card and find_card_rank(card) <= spade_greater_than_rank}
                    # negative_constrained_spades = set(negative_constrained_spades)
                    # constrained_cards_to_choose_from = set(constrained_cards_to_choose_from)
                    constrained_cards_to_choose_from -= negative_constrained_spades
                    # constrained_cards_to_choose_from = list(constrained_cards_to_choose_from)
                if not club_eliminated:
                    negative_constrained_clubs = {card for card in constrained_cards_to_choose_from if 'C' in card and find_card_rank(card) <= club_greater_than_rank}
                    # negative_constrained_clubs = set(negative_constrained_clubs)
                    # constrained_cards_to_choose_from = set(constrained_cards_to_choose_from)
                    constrained_cards_to_choose_from -= negative_constrained_clubs
                    # constrained_cards_to_choose_from = list(constrained_cards_to_choose_from)
                if not heart_eliminated:
                    negative_constrained_hearts = {card for card in constrained_cards_to_choose_from if 'H' in card and find_card_rank(card) <= heart_greater_than_rank}
                    # negative_constrained_hearts = set(negative_constrained_hearts)
                    # constrained_cards_to_choose_from = set(constrained_cards_to_choose_from)
                    constrained_cards_to_choose_from -= negative_constrained_hearts
                    # constrained_cards_to_choose_from = list(constrained_cards_to_choose_from)
                if not diamond_eliminated:
                    negative_constrained_diamonds = {card for card in constrained_cards_to_choose_from if 'D' in card and find_card_rank(card) <= diamond_greater_than_rank}
                    # negative_constrained_diamonds = set(negative_constrained_diamonds)
                    # constrained_cards_to_choose_from = set(constrained_cards_to_choose_from)
                    constrained_cards_to_choose_from -= negative_constrained_diamonds
                    # constrained_cards_to_choose_from = list(constrained_cards_to_choose_from)

                options = {card for card in constrained_cards_to_choose_from if first_played_suit in card}

                if len(options) == 0:  # when length of options is 0, it means i don't have that suit, so i can play suit
                    options = {card for card in constrained_cards_to_choose_from if 'S' in card}
                    new_played = [card for card in self.played_cards if 'S' in card[0:2]]
                    max_played_card = int(find_max_card(new_played))
                if len(options) == 0:  # if options is still 0, include all cards as options
                    options = {card for card in self.cards_to_choose_from}
                    # reset max_played_card rank
                    # but this time use the least ranked card by setting max_played_card to 0
                    max_played_card = 0
                options = tuple(options)
                options_greater_than_max_played_card = [option for option in options if find_card_rank(option) > max_played_card]
                options_greater_than_max_played_card = [option for option in options_greater_than_max_played_card if first_played_suit in option or 'S' in option]

                options_less_than_max_played_card = [option for option in options if find_card_rank(option) < max_played_card]
                options_less_than_max_played_card = [option for option in options_less_than_max_played_card if first_played_suit in option or 'S' in option]

                if len(options_greater_than_max_played_card) > 0:
                    options = options_greater_than_max_played_card
                    options_rankings = [find_card_rank(option) for option in options_greater_than_max_played_card]
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = options_greater_than_max_played_card[best_index]

                    # Don't waste high ranking non-spade cards if one player has already played a spade
                    # e.g. if 9D is the first card and 2nd card is 2S, if i have ['TD', '5D'] I shouldn't play TD
                    # as i would lose to 2S, so instead I should play 5D here
                    new_played = [card for card in self.played_cards if 'S' in card[0:2]]
                    if len(new_played) >= 1 and 'S' not in best_option and first_played_suit != 'S':
                        new_options = tuple(card for card in constrained_cards_to_choose_from if first_played_suit in card)
                        if len(new_options) >= 1:
                            # confirm that i actually have a non-spade card
                            # only choose new best option if my non-spade card count is greater than 0
                            options_rankings = [find_card_rank(option) for option in new_options]
                            min_option_rank = min(options_rankings)
                            best_index = options_rankings.index(min_option_rank)
                            best_option = new_options[best_index]
                            options = [best_option]

                elif len(options_less_than_max_played_card) > 0:
                    options = options_less_than_max_played_card
                    options_rankings = [find_card_rank(option) for option in options_less_than_max_played_card]
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = options_less_than_max_played_card[best_index]

                    # Don't throw away spade needlessly
                    # When the first player played a non-spade card and someone else played a spade card
                    # If I don't have that first player played suit and also dont' have a spade card that can with the 2nd, 3rd players spade card
                    # I don't have to play spade and instead can play any other card
                    new_played = [card for card in self.played_cards if 'S' in card[0:2]]
                    if len(new_played) >= 1 and 'S' in best_option and first_played_suit != 'S':

                        # i'm already checking for options with spades less than 2nd, 3rd player
                        # so my current spade card will not win,
                        # so i have to play a non-spade card of least rank
                        new_options = tuple(card for card in constrained_cards_to_choose_from if 'S' not in card)
                        if len(new_options) >= 1:
                            # confirm that i actually have a non-spade card
                            # only choose new best option if my non-spade card count is greater than 0
                            options_rankings = [find_card_rank(option) for option in new_options]
                            min_option_rank = min(options_rankings)
                            best_index = options_rankings.index(min_option_rank)
                            best_option = new_options[best_index]
                            options = [best_option]
            
                # logic for when it is not my turn
                # there is not certainty of what cards they can choose from
                # so they'll be allowed to choose from self.cards_to_choose_from
                card_chosen = random.choice(options)
                newState.played_cards.append(card_chosen)
                newState.cards_to_choose_from.remove(card_chosen)

        return newState

    def isTerminal(self):
        # current_score = find_current_score_from_history(self.history_cards, self.current_player_index)
        # current_player_bid = self.context['players'][self.current_player]['bid']
        # print('current score', current_score)
        # print('current player bid', current_player_bid)
        # if current_score >= current_player_bid:
        #     return True
        # if self.my_score - 1 >= self.my_bid:
        #     return True
        # elif len(self.my_cards) == 1:
        #     return True
        # else:
        #     return False
        if self.game_completed:
            return True

        if len(self.my_cards) == 0 or len(self.cards_to_choose_from) == 0:
            return True

        # cards_to_choose_from = all_cards[:]
        # for my_card in self.my_cards:
        #     if my_card in cards_to_choose_from:
        #         cards_to_choose_from.remove(my_card)

        # for history_card in self.history_cards_set:
        #     if history_card in cards_to_choose_from:
        #         cards_to_choose_from.remove(history_card)
        # certain_score = find_certain_score(self.my_cards, cards_to_choose_from)
        # if len(self.my_cards) <= 1:
        #     return True
        return False
        ## todo:
        ## might need to decrease search depth by checking if I have enough certain spades to reach my_bid
        ## i.e. if len(certain_spades) + my_score >= my_bid: return True

    def getReward(self):
        for i in range(4):
            score = self.player_scores[i]
            bid = self.player_bids[i]
            player_id = self.player_list[i]
            if score >= 8 and bid == 8:
                if player_id == self.my_player:
                    reward = 1000
                else:
                    reward = -1000
                return reward

        my_index = self.player_list.index(self.my_player)
        my_score = self.player_scores[my_index]
        my_bid = self.player_bids[my_index]
        if my_score >= my_bid:
            reward = my_score + (my_score - my_bid) / 10.0
            return reward
        elif my_score < my_bid:
            reward = (my_bid * -1) + my_score / 10.0  ## receives the negative value of what you bid
            return reward
        return 0


class Action():
    def __init__(self, player, card):
        self.player = player
        self.card = card

    def __str__(self):
        return str((self.player, self.card))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.player == other.player and self.card == other.card

    def __hash__(self):
        return hash((self.card, self.player))

if __name__=="__main__":
    my_cards = ['1C', '1S', 'TS', '6S', '1H', 'JH', '7H', 'KC', '8C', '7C', 'KD', 'QD', 'JD']

    # Play is called at every hand of the game where the user should throw a card.
    # Request data format:
    # {
    #     "playerId": "P1",
    #     "playerIds": ["P0", "P1", "P2", "P3"],
    #     "cards": [ "QS", "9S", "2S", "KH", "JH", "4H", "JC", "9C", "7C", "6C", "8D", "6D", "3D"],
    #     "played": [
    #         "2H/0",
    #         "8H/0"
    #     ],
    #     "history": [
    #         [3, ["QS/0", "6S/0", "TH/0", "2S/0"], 3],
    #         [1, ["TS/0", "KS/0", "1S/0", "5S/0"], 3],
    #     ]
    #     Format of history: 'start idx, [cards in clockwise order of player ids], winner idx'
    # }
    # history_cards = [
    #     [3, ["QS/0", "6S/0", "TH/0", "2S/0"], 3],
    #     [1, ["TS/0", "KS/0", "1S/0", "5S/0"], 3],
    # ]

    body = {
        "timeBudget": 211,
        "playerId": "P0",
        "playerIds": [
            "P0",
            "Bot-1",
            "Bot-2",
            "Bot-3"
        ],
        "cards": [
            "4S",
            "5C"
        ],
        "played": [],
        "history": [
            [
            3,
            [
                "7H",
                "1H",
                "3H",
                "4H"
            ],
            0
            ],
            [
            0,
            [
                "4C",
                "JC",
                "KC",
                "3C"
            ],
            2
            ],
            [
            2,
            [
                "7C",
                "TC",
                "QC",
                "3S"
            ],
            1
            ],
            [
            1,
            [
                "5S",
                "6S",
                "7S",
                "8S"
            ],
            0
            ],
            [
            0,
            [
                "2D",
                "KD",
                "1D",
                "4D"
            ],
            2
            ],
            [
            2,
            [
                "2C",
                "9C",
                "1C",
                "TS"
            ],
            1
            ],
            [
            1,
            [
                "QD",
                "TD",
                "3D",
                "JD"
            ],
            1
            ],
            [
            1,
            [
                "5D",
                "2S",
                "6D",
                "8D"
            ],
            2
            ],
            [
            2,
            [
                "6C",
                "JS",
                "8C",
                "QS"
            ],
            1
            ],
            [
            1,
            [
                "7D",
                "KS",
                "1S",
                "9D"
            ],
            3
            ],
            [
            3,
            [
                "TH",
                "KH",
                "5H",
                "6H"
            ],
            0
            ]
        ],
        "context": {
            "round": 1,
            "players": {
            "P0": {
                "totalPoints": 0,
                "bid": 3,
                "won": 3
            },
            "Bot-1": {
                "totalPoints": 0,
                "bid": 4,
                "won": 4
            },
            "Bot-2": {
                "totalPoints": 0,
                "bid": 2,
                "won": 3
            },
            "Bot-3": {
                "totalPoints": 0,
                "bid": 2,
                "won": 1
            }
            }
        }
    }

    body = {
        "timeBudget": 1277,
        "playerId": "P0",
        "playerIds": [
            "P0",
            "Bot-1",
            "Bot-2",
            "Bot-3"
        ],
        "cards": [
            "1S",
            "KS",
            "QS",
            "9H",
            "6H",
            "2H",
            "JC",
            "5C",
            "9D",
            "8D",
            "7D",
            "1D",
            "2D"
        ],
        "played": [
        ],
        "history": [],
        "context": {
            "round": 1,
            "players": {
            "P0": {
                "totalPoints": 0,
                "bid": 3,
                "won": 0
            },
            "Bot-1": {
                "totalPoints": 0,
                "bid": 7,
                "won": 0
            },
            "Bot-2": {
                "totalPoints": 0,
                "bid": 2,
                "won": 0
            },
            "Bot-3": {
                "totalPoints": 0,
                "bid": 4,
                "won": 0
            }
            }
        }
    }

    my_cards = body['cards']
    my_player = body['playerId']
    context = body['context']

    if len(my_cards) == 13:  # use certain bid and bid value for score and bid
        my_score = body['context']['players'][my_player]['won']
        my_bid = body['context']['players'][my_player]['bid']
    else:
        my_score = body['context']['players'][my_player]['won']
        my_bid = body['context']['players'][my_player]['bid']

    print("My Score: " + str(my_score))
    print("My Bid: " + str(my_bid))

    my_score = 0

    history_cards = body['history']
    player_list = body['playerIds']
    current_player = body['playerId']
    round = body['context']['round']
    played_cards = body['played']
    current_player_index = player_list.index(current_player)
    current_player_index = 0

    player_bids = [3,3,3,3]
    # player_bids = [1,1,1,1]
    player_scores = [0,0,0,0]

    # for i in range(4):
    #     player_id = player_list[i]
    #     player_bid = context['players'][player_id]['bid']
    #     player_score = context['players'][player_id]['won']
    #     player_bids[i] = player_bid
    #     player_scores[i] = player_score

    player_constraints = [None, None, None, None]
    for i in range(4):
        spade_eliminated = False
        club_eliminated = False
        heart_eliminated = False
        diamond_eliminated = False
        
        spade_greater_than_rank = 0
        club_greater_than_rank = 0
        heart_greater_than_rank = 0
        diamond_greater_than_rank = 0

        constraint = {
            'spade_eliminated': spade_eliminated,
            'club_eliminated': club_eliminated,
            'heart_eliminated': heart_eliminated,
            'diamond_eliminated': diamond_eliminated,

            'spade_greater_than_rank': spade_greater_than_rank,
            'club_greater_than_rank': club_greater_than_rank,
            'heart_greater_than_rank': heart_greater_than_rank,
            'diamond_greater_than_rank': diamond_greater_than_rank,
        }
        player_constraints[i] = constraint


    # history_cards = []
    # player_list = [
    #     "P0",
    #     "Bot-1",
    #     "Bot-2",
    #     "Bot-3"
    # ]
    # my_player = "P0"
    # current_player = "P0"
    # round = 1  # test with round 1 only for now  # possibly no need to use round parameter
    # # played_cards = [
    # #     "2H/0",
    # #     "8H/0"
    # # ]
    # played_cards = [
    #     "TH",
    #     "4H"
    # ]
    # print("Intersection: ", set(played_cards).intersection(set(my_cards)))
    # current_player_index = player_list.index(current_player)
    # my_score = 0
    # my_bid = 1

    #######################################################################
    # start MCTS algorithm here
    #######################################################################
    initialState = Callbreak(
        my_cards=set(my_cards), history_cards=history_cards, 
        player_list=tuple(player_list), my_player=my_player, current_player=current_player,
        round=round, played_cards=played_cards, current_player_index=current_player_index,
        player_scores=player_scores, player_bids=player_bids, context=context, player_constraints=player_constraints
    )
    searcher = mcts(timeLimit=1000)  # 1000 milliseconds
    # searcher = mcts(timeLimit=50000)
    try:
        action = searcher.search(initialState=initialState)
    except Exception as e:
        print("Exception raised")
        print(e)
        action = searcher.search(initialState=initialState)

    print("Action is: ")
    print(action.card)