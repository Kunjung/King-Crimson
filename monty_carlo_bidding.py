import math
import random
import sys
from copy import deepcopy
import time
from bid_heuristic import find_bid_winning_version_1
from play_heuristic import king_crimson_heuristic
from collections import Counter

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

all_cards = [str(face) + str(suit) for face in range(1, 14) for suit in ('S', 'C', 'H', 'D')]
all_cards = [get_face(card) for card in all_cards]

def generate_3_cards(my_cards, history=[]):
    card1, card2, card3 = [], [], []
    cards_to_choose_from = all_cards[:]
    for my_card in my_cards:
        if my_card in cards_to_choose_from:
            cards_to_choose_from.remove(my_card)
    history_cards_set = set()  # creates empty set
    for history in history:
        previous_cards = history[1]
        for prev_card in previous_cards:
            prev_card = prev_card[0:2]
            history_cards_set.add(prev_card)
    for history_card in history_cards_set:
        if history_card in cards_to_choose_from:
            cards_to_choose_from.remove(history_card)
    # for card 1
    card_length = len(my_cards)
    for i in range(card_length):
        new_choice = random.choice(cards_to_choose_from)
        card1.append(new_choice)
        cards_to_choose_from.remove(new_choice)
    # for card 2
    for i in range(card_length):
        new_choice = random.choice(cards_to_choose_from)
        card2.append(new_choice)
        cards_to_choose_from.remove(new_choice)
    # for card 3
    card3 = card3 + cards_to_choose_from
    return my_cards, card1, card2, card3

# def generate_3_cards(my_cards):
#     card1, card2, card3 = [], [], []
#     cards_to_choose_from = all_cards[:]
#     for card in my_cards:
#         if card in cards_to_choose_from:
#             cards_to_choose_from.remove(card)
#     # each card set should have at least one spade card
#     # one spade for card1
#     spade_options = [card for card in cards_to_choose_from if 'S' in card]
#     spade_choice = random.choice(spade_options)
#     card1.append(spade_choice)
#     spade_options.remove(spade_choice)
#     cards_to_choose_from.remove(spade_choice)
#     # one spade for card2
#     spade_choice = random.choice(spade_options)
#     card2.append(spade_choice)
#     spade_options.remove(spade_choice)
#     cards_to_choose_from.remove(spade_choice)
#     # one spade for card3
#     spade_choice = random.choice(spade_options)
#     card3.append(spade_choice)
#     spade_options.remove(spade_choice)
#     cards_to_choose_from.remove(spade_choice)

#     # assuming at least one face card for all
#     face_options = [card for card in cards_to_choose_from if card[0] in ('J', 'K', 'Q', 'A')]
#     face_count_card1 = sum([1 for card in card1 if card[0] in ('J', 'K', 'Q', 'A')])
#     if face_count_card1 == 0:
#         # choose non-spade face option for card1
#         face_choice = random.choice(face_options)
#         card1.append(face_choice)
#         face_options.remove(face_choice)
#         cards_to_choose_from.remove(face_choice)
#     face_count_card2 = sum([1 for card in card2 if card[0] in ('J', 'K', 'Q', 'A')])
#     if face_count_card2 == 0:
#         # choose non-spade face option for card1
#         face_choice = random.choice(face_options)
#         card2.append(face_choice)
#         face_options.remove(face_choice)
#         cards_to_choose_from.remove(face_choice)
#     face_count_card3 = sum([1 for card in card3 if card[0] in ('J', 'K', 'Q', 'A')])
#     if face_count_card3 == 0:
#         # choose non-spade face option for card1
#         face_choice = random.choice(face_options)
#         card3.append(face_choice)
#         face_options.remove(face_choice)
#         cards_to_choose_from.remove(face_choice)

#     # for card 1
#     for i in range(13 - len(card1)):
#         new_choice = random.choice(cards_to_choose_from)
#         card1.append(new_choice)
#         cards_to_choose_from.remove(new_choice)
#     # for card 2
#     for i in range(13 - len(card2)):
#         new_choice = random.choice(cards_to_choose_from)
#         card2.append(new_choice)
#         cards_to_choose_from.remove(new_choice)
#     # for card 3
#     card3 = card3 + cards_to_choose_from
#     return my_cards, card1, card2, card3

map_high_cards = {
    10: 'T',
    11: 'J',
    12: 'Q',
    13: 'K',
    14: '1'
}

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

# def random_heuristic(cards, played=[]):
#     return random.choice(cards)

def random_heuristic(my_cards, played_cards):
    options = []
    if len(played_cards) == 0:
        first_played_suit = ''  # '' means i can play any card
        first_played_card = None
    else:
        first_played_card = played_cards[0]
        first_played_suit = first_played_card[1]

    # find max_other_card played
    if len(played_cards) > 0:
        new_played = [card for card in played_cards if first_played_suit in card[0:2]]
        max_played_card = int(find_max_card(new_played))
    else:
        max_played_card = 0
    options = [card for card in my_cards if first_played_suit in card]
    if len(options) == 0:  # when length of options is 0, it means i don't have that suit, so i can play suit
        options = [card for card in my_cards if 'S' in card]
        new_played = [card for card in played_cards if 'S' in card[0:2]]
        max_played_card = int(find_max_card(new_played))
    if len(options) == 0:  # if options is still 0, include all cards as options
        options = [card for card in my_cards]
        # reset max_played_card rank
        # but this time use the least ranked card by setting max_played_card to 0
        max_played_card = 0
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
        new_played = [card for card in played_cards if 'S' in card[0:2]]
        if len(new_played) >= 1 and 'S' not in best_option and first_played_suit != 'S':
            new_options = [card for card in my_cards if first_played_suit in card]
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
        new_played = [card for card in played_cards if 'S' in card[0:2]]
        if len(new_played) >= 1 and 'S' in best_option and first_played_suit != 'S':

            # i'm already checking for options with spades less than 2nd, 3rd player
            # so my current spade card will not win,
            # so i have to play a non-spade card of least rank
            new_options = [card for card in my_cards if 'S' not in card]
            if len(new_options) >= 1:
                # confirm that i actually have a non-spade card
                # only choose new best option if my non-spade card count is greater than 0
                options_rankings = [find_card_rank(option) for option in new_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = new_options[best_index]
                options = [best_option]
    return random.choice(options)


def simulate_game_one_round(my_cards, my_first_card, card1, card2, card3, start_index=0, playerIds=[], history=[]):
    four_player_cards = [my_cards[:], card1[:], card2[:], card3[:]]

    # playerId = "P0"  # only player id changes for each player
    # playerIds = [
    #     "P0",
    #     "Bot-1",
    #     "Bot-2",
    #     "Bot-3"
    # ]  # here it assumes that i have the first player at the very beginning of the round
    playerPoints = [
        0,
        0,
        0,
        0
    ]

    winner_player_index = start_index
    playerId = playerIds[winner_player_index]
    card_length = len(my_cards)
    for i in range(card_length):
        first_player_index = (winner_player_index + 0) % 4
        second_player_index = (winner_player_index + 1) % 4
        third_player_index = (winner_player_index + 2) % 4
        fourth_player_index = (winner_player_index + 3) % 4
        
        first_player = playerIds[first_player_index]
#         print("First Player is: ", first_player)

        first_player_cards = four_player_cards[first_player_index]
        second_player_cards = four_player_cards[second_player_index]
        third_player_cards = four_player_cards[third_player_index]
        fourth_player_cards = four_player_cards[fourth_player_index]

        played = []

        # first_card = random_heuristic(first_player_cards, played)
        first_body = {
            'history': history,
            'played': played,
            'cards': first_player_cards,
            'playerIds': playerIds,
            'playerId': playerIds[first_player_index]
        }
        first_card = king_crimson_heuristic(first_body)
        if i == 0:
            first_card = my_first_card
        played.append(first_card)
        first_player_cards.remove(first_card)

        # second_card = random_heuristic(second_player_cards, played)
        second_body = {
            'history': history,
            'played': played,
            'cards': second_player_cards,
            'playerIds': playerIds,
            'playerId': playerIds[second_player_index]
        }
        second_card = king_crimson_heuristic(second_body)
        played.append(second_card)
        second_player_cards.remove(second_card)

        # third_card = random_heuristic(third_player_cards, played)
        third_body = {
            'history': history,
            'played': played,
            'cards': third_player_cards,
            'playerIds': playerIds,
            'playerId': playerIds[third_player_index]
        }
        third_card = king_crimson_heuristic(third_body)
        played.append(third_card)
        third_player_cards.remove(third_card)

        # fourth_card = random_heuristic(fourth_player_cards, played)
        fourth_body = {
            'history': history,
            'played': played,
            'cards': fourth_player_cards,
            'playerIds': playerIds,
            'playerId': playerIds[fourth_player_index]
        }
        fourth_card = king_crimson_heuristic(fourth_body)
        played.append(fourth_card)
        fourth_player_cards.remove(fourth_card)


        four_cards = played[:]

        winner_card = find_winning_card(four_cards)
        winner_player_index = four_cards.index(winner_card)

        winner_point = playerPoints[winner_player_index]
        winner_point += 1
        playerPoints[winner_player_index] = winner_point

        new_history = [first_player_index, deepcopy(four_cards), winner_player_index]
        history.append(new_history)

    # print(playerPoints)
    # print(history)
    return playerPoints

def find_score(point, bid):
    if (point - bid) < 0:
        # negative score, so turn to absolute value and subtract by 1
        return -1 * bid
    else:
        integer_value = bid
        decimal_value = (point - bid) / 10
        decimal_value = round(decimal_value, 1)
        return round(integer_value + decimal_value, 1)

def find_average(scores):
    if len(scores) == 0:
        return 0
    return sum(scores)/len(scores)


def find_average_points_from_simulation(my_cards, history=[], num_iterations=5000, my_player_index=0, start_index=0, playerIds=[]):
    t1 = time.time()
    # my_points = []
    # card_scores = {}
    # for my_first_card in my_cards:
    #     card_scores[my_first_card] = 0
    #     for i in range(int(num_iterations/len(my_cards))):
    #         four_cards = generate_3_cards(my_cards)
    #         my_point = simulate_game_one_round(four_cards[0], my_first_card, four_cards[1], four_cards[2], four_cards[3], start_index=start_index, playerIds=playerIds)
    #         my_points.append(my_point[my_player_index])
    #     count_data = Counter(my_points)
    #     most_common_point = count_data.most_common(3)
    #     card_scores[my_first_card] = most_common_point

    card_scores = {}
    card_points = {}
    for my_first_card in my_cards:
        card_points[my_first_card] = []
    
    for i in range(int(num_iterations/len(my_cards))):
        four_cards = generate_3_cards(my_cards, history=history)
        for my_first_card in my_cards:
            my_point = simulate_game_one_round(four_cards[0], my_first_card, four_cards[1], four_cards[2], four_cards[3], start_index=start_index, playerIds=playerIds, history=[])
            card_points[my_first_card].append(my_point[my_player_index])
    
    for card in card_points:
        card_point = card_points[card]
        average_point = find_average(card_point)
        card_scores[card] = average_point
        # count_data = Counter(card_point)
        # most_common_point = count_data.most_common(3)
        # card_scores[card] = most_common_point


    t2 = time.time()

    print("Time taken: ", (t2 - t1) * 1000, " milliseconds")

    # average_point = find_average(my_points)

    # print("average point is ", sum(my_points)/len(my_points))

    # count_data = Counter(my_points)
    # print("Item Count: ----------------------------> ", count_data.most_common(4))
    # most_common_point = count_data.most_common(1)
    # print("Most Common Item is: ------------------------->", most_common_point)
    # print("average", average_point)
    # return average_point
    # return most_common_point[0][0]
    return card_scores
    
if __name__ == '__main__':
    my_cards = ['1S','TS','8S','5S','4S','2S','KH','TH','4H','TD','9D','7D','9C']
    my_cards = ['KS','JS','5S','KH','6H','QC','8C','6C','2C','KD','JD','8D','7D']
    # my_cards = ['KS','9S','2S','TH','6H','4H','2H','QC','5C','QD','8D','7D','4D']
    # my_cards = ['QS','JS','8S','7S','6S','3S','3H','JC','9C','7C','6C','4C','2C']
    my_cards = ['1S','9S','6S','5S','4S','2S','KH','KC','TC','1D','TD','7D','2D']
    # print(find_average_points_from_simulation(my_cards, num_iterations=8000))
    # print(find_average_points_from_simulation(my_cards, num_iterations=4000))
    # for cards in generate_3_cards(my_cards):
    #     print(cards)

    # sys.exit(0)
    start_index = 0
    print("Start Index: -------------------------------------------> ", start_index)
    my_player_id = 'P0'
    playerIds = [
        "P0",
        "Bot-1",
        "Bot-2",
        "Bot-3"
    ]
    my_player_index = playerIds.index(my_player_id)
    print("First Player is: ", playerIds[start_index])

    print("my_cards:  ", my_cards)
    bid_value, certain_bid = find_bid_winning_version_1(my_cards)
    print("certain bid -------------------------------> ", certain_bid)
    print('bid before monte average: ', bid_value)
    history = []
    # monte_average_bid_value = find_average_points_from_simulation(my_cards, num_iterations=400)

    card_scores = find_average_points_from_simulation(my_cards, history=history, num_iterations=100, my_player_index=my_player_index, start_index=start_index, playerIds=playerIds)

    print("Card Scores")
    best_card = None
    best_score = -1000
    for card_score in card_scores.items():
        print(card_score)
        card, score = card_score
        if score > best_score:
            best_score = score
            best_card = card

    print()
    print("Best Score: ", best_score)
    print("Best Card: ", best_card)

    print()
    # my_cards, card1, card2, card3 = generate_3_cards(my_cards)
    # simulate_game_one_round(my_cards, card1, card2, card3)