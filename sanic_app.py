# This contains the basic code that you will need to view the game on the snadbox.
# You will provide all the moves of all the bots in the sandbox.
# The sandbox is for testing purposes only so, the API data format can change
# when quelifiers begin.
# The sandbox is provided so that you can get familiar with buliding bots before
#  the event actually begings.

# To seutp: `pip install flask, flask_cors`
# To run: python app.py

import json

import logging
import sys
import time
import math
from mcts import mcts
from callbreak import Callbreak
# import pandas as pd

import os
import pickle
import ast
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from monty_carlo_bidding import find_average_points_from_simulation


# filename = 'mlp_model_score_69_5_layer.sav'
# filename = 'mlp_model_score_69_5_layer_may_21.sav'
filename = 'mlp_model_may_23_max.sav'  # trying now with regularizatoin alpha = 1 # model weights retrained to reduce recklessness
# changed to add latest dataset with low recklessness 4

filename = 'mlp_model_may_23_max_2_layers.sav'  # hidden layer decreased from 3 to 2  # high scorer 5700

filename = 'mlp_model_may_25.sav'  # model of May 25  # high scorer 5790

filename = 'mlp_model_may_27.sav' # trying new model

filename = 'mlp_model_may_27_max_data.sav'  # latest model with 300k data points

filename = 'mlp_model_may_29.sav'

filename = 'mlp_model_may_29_first.sav'

filename = 'mlp_model_may_29_400k.sav'  # trained on 400k data points

filename = 'mlp_model_may_29_400k_extra_hidden_layer.sav'

filename = 'mlp_may_30.sav'  # new high scorer - 5830

filename = 'mlp_may_31.sav'

filename = 'mlp_june_2.sav'  # test new model trained on 525K data points X

filename = 'mlp_june_3.sav'  # 600k data

filename = 'mlp_june_4.sav'  # 680k data X

filename = 'mlp_june_7.sav'  # X

filename = 'mlp_june_8.sav'

filename = 'mlp_may_31.sav'

filename = 'mlp_june_10.sav'

filename = 'model_june_26_three_combo_4_hidden_layers.sav'  # 340k data

filename = 'model_june_27_three_combo_4_hidden_layers.sav'

filename = 'model_june_27_three_combo_12pm.sav'  # X

filename = 'model_june_27_three_combo_5pm_safe_bid.sav'

filename = 'model_june_28_three_combo_12pm_safe_bid.sav'

# load the model from disk
loaded_model = pickle.load(open(filename, 'rb'))


def next_winning_card(winning_card):
    # if found AC, should return KC
    # if found KC, should return QC

    suit = winning_card[1]
    number = winning_card[0]
    if number == '1':
        next_number = 'K' + str(suit)
    elif number == 'K':
        next_number = 'Q' + str(suit)
    elif number == 'Q':
        next_number = 'J' + str(suit)
    elif number == 'J':
        next_number = 'T' + str(suit)
    elif number == 'T':
        next_number = '9' + str(suit)
    elif number != '2':
        next_number = int(number) - 1
        next_number = str(next_number) + str(suit)
    else:
        next_number = '2' + str(suit)
    return next_number


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


def get_all_cards():
    all_cards = []
    for suit in ['S','H','C','D']:
        for rank in [1,2,3,4,5,6,7,8,9,'T','J','Q','K']:
            card = str(rank) + suit
            all_cards.append(card)
    return all_cards


def mlp_bid_predict(cards):
    def find_parameters(cards):
        all_cards = get_all_cards()
        # cards = ast.literal_eval(cards)
        final_parameters_list = []
        for card in all_cards:
            # final_parameters[card] = 1 if card in cards else 0
            if card in cards:
                val = 1
            else:
                val = 0
            final_parameters_list.append(val)
        
        # print("final_parameters", final_parameters_list)
        # print(pd.DataFrame(final_parameters))
        return np.array(final_parameters_list).reshape(1, -1)

    parameterized_test_card = find_parameters(cards)

    y_0_predict = loaded_model.predict(parameterized_test_card)
    print('y_0_predict ', y_0_predict[0])
    predicted_bid = y_0_predict
    return predicted_bid

# result = loaded_model.score(X_test, y_test)
# print(result)


# load the model from disk
# model_filename = 'decision_tree_model.sav'
# loaded_model = pickle.load(open(model_filename, 'rb'))


# try:
#     import colorlog
# except ImportError:
#     pass

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    format      = '%(asctime)s - %(levelname)-8s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if 'colorlog' in sys.modules and os.isatty(2):
        cformat = '%(log_color)s' + format
        f = colorlog.ColoredFormatter(cformat, date_format,
              log_colors = { 'DEBUG'   : 'reset',       'INFO' : 'reset',
                             'WARNING' : 'bold_yellow', 'ERROR': 'bold_red',
                             'CRITICAL': 'bold_red' })
    else:
        f = logging.Formatter(format, date_format)
    ch = logging.StreamHandler()
    ch.setFormatter(f)
    root.addHandler(ch)

setup_logging()
log = logging.getLogger(__name__)

debug = True
# debug = False

# log.debug('Hello Debug')
# log.info('Hello Info')
# log.warn('Hello Warn')
# log.error('Hello Error')
# log.critical('Hello Critical')

from sanic import Sanic, text
from sanic import response
from sanic.log import logger

# from cors import add_cors_headers
# from options import setup_options

from sanic_cors import CORS, cross_origin

app = Sanic(__name__)
CORS(app)

# Add OPTIONS handlers to any route that is missing it
# app.register_listener(setup_options, "before_server_start")

# Fill in CORS headers
# app.register_middleware(add_cors_headers, "response")

# @app.route("/", methods=["GET", "POST"])
# async def do_stuff(request):
#     return text("...")

from heuristic_search import king_crimson_heuristic, find_available_options_of_cards_that_can_be_played


@app.route("/hi", methods=["GET"])
def hi(request):
    """
    This function is required to check for the status of the server.
    When docker containers are spun, this endpoint is called continuously
    to check if the docker container is ready or not.  
    Alternatively, if you need to do some pre-processing,
    do it first and then add this endpoint.
    """
    return response.json({"value": "hello"})

def spades_greater_than_4(my_spades):
    if len(my_spades) >= 5:
        certain_bid = len(my_spades) - 4
        # print(certain_bid)
        remaining_spades = my_spades[:4]
        # print(remaining_spades)
        return certain_bid, remaining_spades
    else:
        # print(my_spades)
        return 0, my_spades

def find_card_value(card):
    if '1' in card:
        return 14
    elif 'T' in card:
        return 10
    elif 'J' in card:
        return 11
    elif 'Q' in card:
        return 12
    elif 'K' in card:
        return 13
    else:
        return int(card[0])

def find_parameters(cards):
    cards = ast.literal_eval(cards)
    print('literal cards', cards)
    
    ace_spade_present = 1 if '1S' in cards else 0
    ace_club_present = 1 if '1C' in cards else 0
    ace_heart_present = 1 if '1H' in cards else 0
    ace_diamond_present = 1 if '1D' in cards else 0
    
    king_spade_present = 1 if 'KS' in cards else 0
    king_club_present = 1 if 'KC' in cards else 0
    king_heart_present = 1 if 'KH' in cards else 0
    king_diamond_present = 1 if 'KD' in cards else 0
    
    spade_count = sum([1 for card in cards if 'S' in card])
    club_count = sum([1 for card in cards if 'C' in card])
    heart_count = sum([1 for card in cards if 'H' in card])
    diamond_count = sum([1 for card in cards if 'D' in card])
    
    spade_sum = sum([find_card_value(card) for card in cards if 'S' in card])
    club_sum = sum([find_card_value(card) for card in cards if 'C' in card])
    heart_sum = sum([find_card_value(card) for card in cards if 'H' in card])
    diamond_sum = sum([find_card_value(card) for card in cards if 'D' in card])
    
    final_parameters = {
        'ace_spade_present': ace_spade_present,
        'ace_club_present': ace_club_present,
        'ace_heart_present': ace_heart_present,
        'ace_diamond_present': ace_diamond_present,
        'king_spade_present': king_spade_present,
        'king_club_present': king_club_present,
        'king_heart_present': king_heart_present,
        'king_diamond_present': king_diamond_present,
        'spade_count': spade_count,
        'club_count': club_count,
        'heart_count': heart_count,
        'diamond_count': diamond_count,
        'spade_sum': spade_sum,
        'club_sum': club_sum,
        'heart_sum': heart_sum,
        'diamond_sum': diamond_sum
    }
    return final_parameters

def find_card_encoding(my_cards):
    parameters = find_parameters(repr(my_cards))
    print('parameters', parameters)
    values = []
    for parameter in parameters:
        values.append(parameters[parameter])
    # X = pd.DataFrame(parameters, columns=[param for param in parameters])
    # return X
    return values

# def find_bid_from_model(my_cards):
#     my_card_encoding = find_card_encoding(my_cards)
#     predicted_bid = loaded_model.predict([my_card_encoding])[0]
#     return predicted_bid - 1

def find_min_card(cards):
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
    return int(min(mapped_cards))

def find_bid_version_6(my_cards):
    bid_value = 0
    if '1S' in my_cards:
        bid_value += 1
    if 'KS' in my_cards:
        bid_value += 0.8
    if 'QS' in my_cards:
        bid_value += 0.7
    if 'JS' in my_cards:
        bid_value += 0.6
    count_spades = sum([1 for card in my_cards if 'S' in card])
    count_spades_other_than_top = sum([1 for card in my_cards if 'S' in card and card[0] not in ('1', 'K', 'Q', 'J')])
    logger.warning('number of spades is ' + str(count_spades))
    if count_spades >= 5:
        bid_value += 2
    elif count_spades >= 4:
        bid_value += 1
    bid_value += count_spades_other_than_top/2
    if '1C' in my_cards:
        bid_value += 1
    if '1D' in my_cards:
        bid_value += 1
    if '1H' in my_cards:
        bid_value += 1
    if '1C' in my_cards and 'KC' in my_cards:
        bid_value += 1
    if '1D' in my_cards and 'KD' in my_cards:
        bid_value += 1
    if '1H' in my_cards and 'KH' in my_cards:
        bid_value += 1

    card_sum = find_sum_of_card_numbers([card for card in my_cards if 'S' not in card])
    if card_sum < 104 * 9/12:
        # i've got a bad card, so i need to decrease my bid vaue
        bid_value -= 1
    if card_sum < 82 * 9/12:
        # one more reduction because of really bad card
        bid_value -= 2
    if bid_value < 1:
        bid_value = 1
    # if bid_value > 3.0:
    #     bid_value = 3

    bid_value = round(bid_value, 0)  # convert 2.6 to 3.0
    return bid_value

def find_card_value(card):
    if 'S' in card:
        start = 13
    else:
        start = 0
    face_value = find_max_card([card])
    return start + face_value

def find_bid_with_mapping(my_cards):
    
    # map from cards (41 to 273) range into bid (1 to 8) range
    card_total = sum([find_card_value(card) for card in my_cards])
    # bid = 1 + ((card_total - 41)/(273 - 41) * (8 - 1))
    
    bid = 1 + ((card_total - 49)/(272 - 49) * (8 - 1))

    return bid

def find_certain_bid(my_spades):
    ##################################
    # certain spade Finder
    global debug
    if debug:
        print("original spades is: ", my_spades)
    if len(my_spades) == 1 and '1S' in my_spades:
        return 1, []
    winning_spade_sequence = ['1S','KS','QS','JS','TS','9S','8S','7S','6S','5S','4S','3S','2S']
    winning_forward = 0
    spent_spade_count = 0
    certain_bid = 0
    winning = '1S'
    my_spades_copy = [copy for copy in my_spades]
    original_my_spade_count = len(my_spades_copy)
    my_lowest_spade = my_spades_copy[-1]
    i = 0
    matched_winning_spades = []
    searching_next = False
    searching_found = False
    previous_matched = True
    spend_if_found_count = 0

    my_remaining_spade_count = len(my_spades_copy)  # start with all my spades count
    while find_max_card([winning]) > find_max_card([my_lowest_spade]):
        winning = winning_spade_sequence[i]
        print("Searching for Winning: ", winning)
        if winning in my_spades:
            if searching_next == True:
                ## since it was set to true, it meant a card was skipped and cards were spent to find that card
                ## so set search_found to true
                searching_found = True
                spent_spade_count += spend_if_found_count
                spend_if_found_count = 0
            print('Matched: ', winning)
            previous_matched = True
            matched_winning_spades.append(winning)
            certain_bid += 1
            my_spades_copy.remove(winning)
            # decrease my remaining spade count
            my_remaining_spade_count -= 1
        else:
            # move forward in winning sequence but start from same part in my spades
            searching_next = True
            searching_found = False
            print("skipping ", winning)
            if previous_matched == True:
                # when the previous was matched, but now i am in searching mode, so i start from 0
                # only add the skipped counts to spent spade count when searching_found becomes true
                spend_if_found_count = 1
            else:
                spend_if_found_count += 1
            # also decrease my remaining spade count as i had to skip
            my_remaining_spade_count -= 1
            # change the previous matched to False as one had to be skipped
            previous_matched = False
        if my_remaining_spade_count <= 0:
            print("early stopping ...............................")
            break
        print("spend_if_found_count: ", spend_if_found_count)
        print("previous matched: ", previous_matched)
        i += 1
    print('-----------------')
    print("matched winning spades is: ", matched_winning_spades)
    print('certain bid is: ', certain_bid)
    print('spent spade count is: ', spent_spade_count)
    print("searching_next ", searching_next)
    print("searching found ", searching_found)
    print("previous matched: ", previous_matched)
    print("spend_if_found_count = ", spend_if_found_count)
    if searching_found:
        # donot use remaining cards to calculate cards
        # i.e. set uncertain spades to empty list
        print("original spades count: ", original_my_spade_count)
        if certain_bid + spent_spade_count == original_my_spade_count:
            print('exactly equal so no more remaining spades')
            uncertain_spades = []
        else:
            print('certain bid and spend spade count not equal, so there are remaining spades')
            uncertain_spades = my_spades_copy[(certain_bid + spent_spade_count - 1):]
    else:
        # search was not found, so use the remaining spades
        # after subtracting the spent spade count
        # uncertain_spades = [card for card in my_spades_copy if card not in matched_winning_spades][spent_spade_count:]
        uncertain_spades = [card for card in my_spades_copy if card not in matched_winning_spades]
        uncertain_spades = uncertain_spades[::-1][spent_spade_count:]
    if certain_bid < len(my_spades)/2 and len(uncertain_spades) == 0:
        print("calling bid resettter here -------------------------------------> ")
        if '1S' in my_spades and 'KS' in my_spades and 'QS' in my_spades:
            # three certain count
            # remaining spades are uncertain bid
            return 3, [spade for spade in my_spades if spade[0] not in ('1', 'K', 'Q')]
        elif '1S' in my_spades and 'KS' in my_spades:
            # two certain count
            # and remaining spades are uncertain bid
            return 2, [spade for spade in my_spades if spade[0] not in ('1', 'K')]
        elif '1S' in my_spades:
            # 1 certain count
            # and remaining spades are uncertain_bid
            return 1, [spade for spade in my_spades if spade[0] not in ('1',)]
        return 0, my_spades
    else:
        return certain_bid, uncertain_spades

# bid calculation from winning_version_1
def find_bid_winning_version_1(my_cards, round=1):
    global debug
    bid_value = 0
    certain_bid = 0
    if '1S' in my_cards and 'KS' in my_cards and 'QS' in my_cards and 'JS' in my_cards:
        certain_bid = 4
    elif '1S' in my_cards and 'KS' in my_cards and 'QS' in my_cards:
        certain_bid = 3
    elif '1S' in my_cards and 'KS' in my_cards:
        certain_bid = 2
    elif '1S' in my_cards:
        certain_bid = 1
    bid_value += certain_bid

    count_spades = 0
    if certain_bid == 4:
        count_spades = sum([1 for card in my_cards if 'S' in card and card[0] not in ('1', 'K', 'Q', 'T')])
        uncertain_spades = [card for card in my_cards if 'S' in card and card[0] not in ('1', 'K', 'Q', 'T')]
    elif certain_bid == 3:
        count_spades = sum([1 for card in my_cards if 'S' in card and card[0] not in ('1', 'K', 'Q')])
        uncertain_spades = [card for card in my_cards if 'S' in card and card[0] not in ('1', 'K', 'Q')]
    elif certain_bid == 2:
        count_spades = sum([1 for card in my_cards if 'S' in card and card[0] not in ('1', 'K')])
        uncertain_spades = [card for card in my_cards if 'S' in card and card[0] not in ('1', 'K')]
    elif certain_bid == 1:
        count_spades = sum([1 for card in my_cards if 'S' in card and card[0] not in ('1')])
        uncertain_spades = [card for card in my_cards if 'S' in card and card[0] not in ('1')]
    else:
        count_spades = sum([1 for card in my_cards if 'S' in card])
        uncertain_spades = [card for card in my_cards if 'S' in card]


    count_all_spades = sum([1 for card in my_cards if 'S' in card])

    # increase bid for high value cards
    king_combo_used = False
    if certain_bid <= 1:
        if 'KS' in my_cards and 'QS' in my_cards and 'JS' in my_cards and 'TS' in my_cards:
            bid_value += 3
            certain_bid += 3
            king_combo_used = True
            uncertain_spades = [card for card in uncertain_spades if card[0] not in ('K','Q','J','T')]
        elif 'KS' in my_cards and 'QS' in my_cards and 'JS' in my_cards:
            bid_value += 2
            certain_bid += 2
            king_combo_used = True
            uncertain_spades = [card for card in uncertain_spades if card[0] not in ('K','Q','J')]
        elif 'KS' in my_cards and 'QS' in my_cards:
            bid_value += 1
            certain_bid += 1
            king_combo_used = True
            uncertain_spades = [card for card in uncertain_spades if card[0] not in ('K','Q')]
        elif 'QS' in my_cards and 'JS' in my_cards and 'TS' in my_cards:
            bid_value += 1
            certain_bid += 1
            king_combo_used = True
            uncertain_spades = [card for card in uncertain_spades if card[0] not in ('Q','J','T')]
        elif 'JS' in my_cards and 'TS' in my_cards and '9S' in my_cards and count_all_spades >= 5:
            bid_value += 1
            certain_bid += 1
            king_combo_used = True
            uncertain_spades = [card for card in uncertain_spades if card[0] not in ('J','T','9')]
        # elif 'KS' in my_cards and count_all_spades >= 5:
        #     bid_value += 1
        #     certain_bid += 1
        #     king_combo_used = True
        #     uncertain_spades = [card for card in uncertain_spades if card[0] not in ('K',)]

    # new certain bid function. skips all the bid and certain bid calculation done above
    # and creates new values for certain bid, bid_value, and uncertain spades
    certain_bid = 0
    bid_value = 0

    my_spades = [card for card in my_cards if 'S' in card]
    greater_bid, uncertain_spades = spades_greater_than_4(my_spades)
    certain_bid, uncertain_spades = find_certain_bid(my_spades)
    if debug:
        print("Result Certain Bid: ", certain_bid)
        print("Result Uncertain Spades: ", uncertain_spades)
    certain_bid += greater_bid
    bid_value += certain_bid
    
    # increase bid value when high number of spades
    high_spade_count_used = False
    if count_all_spades >= 10:
        certain_bid = 8
        bid_value = 8
        high_spade_count_used = True
        return 8, 8
    elif count_all_spades >= 9:
        certain_bid = 7
        bid_value = 7
        high_spade_count_used = True
    elif count_all_spades >= 8:
        # since having 8 spades with me means only 5 spades are remaining
        # each other will have at least 1 means highest is 3 spades
        # so if i play only spades, i can spend 3 of my spades and with the next 5 spades
        # gain 5 points certainly
        certain_bid = 6
        bid_value = 6
        high_spade_count_used = True
    elif count_all_spades >= 7:  # scored 5058
    # elif count_all_spades >= 7 and '1S' in my_cards:  # scored 4933
        # when i have 7, remaining spades is 6
        # so i will win at least 4
        if certain_bid < 5:
            certain_bid = 5
            bid_value = 5
            high_spade_count_used = True
        # elif certain_bid == 1:
        #     # when i have ace spade an my length of spades is >= 7
        #     certain_bid = 5
        #     bid_value = 5
        #     high_spade_count_used = True
    # elif count_all_spades >= 6:
    #     if certain_bid < 3:
    #         certain_bid = 3
    #         bid_value = 3
    #         high_spade_count_used = True

    else:
        # use only half of the total remaining spade count
        count_spades = len(uncertain_spades)
        remaining_spade_bid = count_spades/2

        # if all uncertain spades are less than or equal to 6
        # don't consider remaining spade bid
        # i.e. set remaining_spade_bid to 0
        uncertain_less_than_6 = [spade for spade in uncertain_spades if find_max_card([spade]) <= 5]  # scored 5058
        # uncertain_less_than_6 = [spade for spade in uncertain_spades if find_max_card([spade]) <= 4]  # scored 5010
        # uncertain_less_than_6 = [spade for spade in uncertain_spades if find_max_card([spade]) <= 6]  # scored 5049
        if len(uncertain_less_than_6) == len(uncertain_spades) and count_all_spades <= 5:
            remaining_spade_bid = 0
            # remaining_spade_bid = count_spades/3.5
        
        # remaining_spade_bid = count_spades/2
        
        # remaining_spade_bid = 0
        # if count_all_spades >= 4:
        #     remaining_spade_bid = count_spades/2
        # if count_all_spades == 3 and ('1S' in my_cards or 'KS' in my_cards or 'QS' in my_cards):
        #     remaining_spade_bid = count_spades/2
        
        # if count_all_spades == 2 and ('1S' in my_cards or 'KS' in my_cards):
        #     remaining_spade_bid = count_spades/2

        # if count_all_spades == 1 and '1S' in my_cards:
        #     remaining_spade_bid = count_spades/2

        print("Remaining spade bid -------------------------------> ", remaining_spade_bid)
        bid_value += remaining_spade_bid

        if len(uncertain_spades) <= 7 and len(uncertain_spades) >= 5:
            spade_sum = sum([find_max_card([spade]) for spade in uncertain_spades])
            spade_average = spade_sum/len(uncertain_spades)
            if debug:
                print('spade_average ', spade_average)
            if spade_average <= 5.5:
                bid_value -= 0.5
            elif spade_average >= 9:
                bid_value += 0.5
            # if len(uncertain_spades) >= 6:  # scored 5069
            uncertain_less_than_8 = [spade for spade in uncertain_spades if find_max_card([spade]) <= 8]
            if len(uncertain_less_than_8) == len(uncertain_spades):
                all_less_than_8 = True
            else:
                all_less_than_8 = False
            if len(uncertain_spades) >= 6 and not all_less_than_8:
                bid_value += 0.5  # increase for high spade count

        elif len(uncertain_spades) == 4:
            spade_sum = sum([find_max_card([spade]) for spade in uncertain_spades])
            spade_average = spade_sum/len(uncertain_spades)
            if debug:
                print('spade_average ', spade_average)
            if spade_average <= 6:
                bid_value -= 0.5
            elif spade_average >= 9:
                bid_value += 0.5

        # decrease bid by 0.5 if I only have low value spades in uncertain_spades
        elif len(uncertain_spades) <= 3 and len(uncertain_spades) >= 2:
            spade_sum = sum([find_max_card([spade]) for spade in uncertain_spades])
            spade_average = spade_sum/len(uncertain_spades)
            if debug:
                print('spade_average ', spade_average)
            if spade_average <= 6:
                bid_value -= 0.5
            elif spade_average >= 10.5:
                bid_value += 0.5
            my_spade_count = sum([1 for card in my_cards if 'S' in card])
            if my_spade_count <= 2 and spade_average <= 5:
                bid_value -= 0.5  # decrease for low spade count
        
        my_spade_count = sum([1 for card in my_cards if 'S' in card])
        # decrease bid value when low spade count and no winning spade or next winning spade present in my_cards
        if my_spade_count == 2 and '1S' not in my_cards and 'KS' not in my_cards and 'QS' not in my_cards:
            bid_value -= 0.5

        # decrease bid value when low spade count of only one and no winning spade or KS or QS
        if my_spade_count == 1 and '1S' not in my_cards and 'KS' not in my_cards and 'QS' not in my_cards:
            bid_value -= 0.5



    if high_spade_count_used:
        # check if i have high value spade cards like Aces and Kings
        extra_certain_bid = 0
        if '1S' in my_cards and 'KS' in my_cards and 'QS' in my_cards and 'JS' in my_cards:
            extra_certain_bid += 4
        elif '1S' in my_cards and 'KS' in my_cards and 'QS' in my_cards:
            extra_certain_bid += 3
        elif '1S' in my_cards and 'KS' in my_cards:
            extra_certain_bid += 2
        elif '1S' in my_cards:
            extra_certain_bid += 1
        elif 'KS' in my_cards and 'QS' in my_cards and 'JS' in my_cards and 'TS' in my_cards:
            extra_certain_bid += 3
        elif 'KS' in my_cards and 'QS' in my_cards and 'JS' in my_cards:
            extra_certain_bid += 2
        elif 'KS' in my_cards and 'QS' in my_cards:
            extra_certain_bid += 1
        elif 'QS' in my_cards and 'JS' in my_cards and 'TS' in my_cards:
            extra_certain_bid += 1
        certain_bid += extra_certain_bid
        bid_value += extra_certain_bid


    if debug:
        print("bid value after high spade count is ", bid_value)


    if debug:
        print("bid_value at first point ", bid_value)

    # # add total remaining spades to bid, but later subtract the low value bids
    # bid_value += (count_spades * 0.6)
    
    # low_value_spades = [card for card in my_cards if 'S' in card and find_max_card([card]) <= 9]

    # count_low_value_spades = len(low_value_spades)
    # bid_value -= (count_low_value_spades * 0.6)
    my_club_options = [card for card in my_cards if 'C' in card]
    my_heart_options = [card for card in my_cards if 'H' in card]
    my_diamond_options = [card for card in my_cards if 'D' in card]

    my_spade_count = sum([1 for card in my_cards if 'S' in card])

    non_spade_ace_count = 0
    # consider winning Ace cards
    if '1C' in my_cards and len(my_club_options) <= 6:
        bid_value += 1
        non_spade_ace_count += 1
    if '1D' in my_cards and len(my_diamond_options) <= 6:
        bid_value += 1
        non_spade_ace_count += 1
    if '1H' in my_cards and len(my_heart_options) <= 6:
        bid_value += 1
        non_spade_ace_count += 1

    if non_spade_ace_count >= 3:
        bid_value -= 0.5

    if debug:
        print("Bid after Aces is: ", bid_value)

    if my_spade_count == 1 and '1S' in my_cards:
        single_spade_ace_present = True
    else:
        single_spade_ace_present = False

    # consider Ace and King combo
    ace_and_king_combo_used = False
    if my_spade_count >= 2 or single_spade_ace_present:
        if '1C' in my_cards and 'KC' in my_cards and len(my_club_options) <= 4:
            bid_value += 1
            ace_and_king_combo_used = True
        elif '1C' in my_cards and 'KC' in my_cards and 'QC' in my_cards and 'JC' in my_cards and len(my_club_options) <= 6:
            bid_value += 1
            ace_and_king_combo_used = True
        if '1H' in my_cards and 'KH' in my_cards and len(my_heart_options) <= 4:
            bid_value += 1
            ace_and_king_combo_used = True
        elif '1H' in my_cards and 'KH' in my_cards and 'QH' in my_cards and 'JH' in my_cards and len(my_club_options) <= 6:
            bid_value += 1
            ace_and_king_combo_used = True
        if '1D' in my_cards and 'KD' in my_cards and len(my_diamond_options) <= 4:
            bid_value += 1
            ace_and_king_combo_used = True
        elif '1D' in my_cards and 'KD' in my_cards and 'QD' in my_cards and 'JD' in my_cards and len(my_club_options) <= 6:
            bid_value += 1
            ace_and_king_combo_used = True

    if debug:
        print("Ace and King used: ", ace_and_king_combo_used)
        print("bid value after ace and king ", bid_value)

    king_and_queen_combo_used = False
    number_of_king_and_queen_combos = 0
    # if not high_spade_count_used:
    # if 1C not in cards, but KC and QC are in cards and number of C cards in my cards <= 4
    # bid += 1
    if my_spade_count >= 2:
        if '1C' not in my_cards and 'KC' in my_cards and 'QC' in my_cards and len(my_club_options) <= 4:
            bid_value += 1
            number_of_king_and_queen_combos += 1
            king_and_queen_combo_used = True
        if '1H' not in my_cards and 'KH' in my_cards and 'QH' in my_cards and len(my_heart_options) <= 4:
            bid_value += 1
            number_of_king_and_queen_combos += 1
            king_and_queen_combo_used = True
        if '1D' not in my_cards and 'KD' in my_cards and 'QD' in my_cards and len(my_diamond_options) <= 4:
            bid_value += 1
            number_of_king_and_queen_combos += 1
            king_and_queen_combo_used = True
        
        if number_of_king_and_queen_combos >= 3:
            bid_value -= 1
        
        # if not king_and_queen_combo_used and not high_spade_count_used:
        if not king_and_queen_combo_used:
            # if 1C not in cards, but KC and JC are in cards and number of C cards in my cards <= 3
            # bid += 1
            if '1C' not in my_cards and 'KC' in my_cards and 'JC' in my_cards and len(my_club_options) <= 3:
                bid_value += 0.8
                number_of_king_and_queen_combos += 1
                king_and_queen_combo_used = True
            if '1H' not in my_cards and 'KH' in my_cards and 'JH' in my_cards and len(my_heart_options) <= 3:
                bid_value += 0.8
                number_of_king_and_queen_combos += 1
                king_and_queen_combo_used = True
            if '1D' not in my_cards and 'KD' in my_cards and 'JD' in my_cards and len(my_diamond_options) <= 3:
                bid_value += 0.8
                number_of_king_and_queen_combos += 1
                king_and_queen_combo_used = True

            if number_of_king_and_queen_combos >= 3:
                bid_value -= 0.8

        if not king_and_queen_combo_used and not high_spade_count_used and not ace_and_king_combo_used:
            # check if i have a single king and a low face card
            if '1C' not in my_cards and 'KC' in my_cards and len(my_club_options) <= 5 and len(my_club_options) >= 3:
                bid_value += 0.5
                number_of_king_and_queen_combos += 1
                king_and_queen_combo_used = True
            elif '1H' not in my_cards and 'KH' in my_cards and len(my_heart_options) <= 5 and len(my_heart_options) >= 3:
                bid_value += 0.5
                number_of_king_and_queen_combos += 1
                king_and_queen_combo_used = True
            elif '1D' not in my_cards and 'KD' in my_cards and len(my_diamond_options) <= 5 and len(my_diamond_options) >= 3:
                bid_value += 0.5
                number_of_king_and_queen_combos += 1
                king_and_queen_combo_used = True
            else:
                # if 2 or more non-spade kings in my cards
                # increase bid by 0.5
                king_cards = [card for card in my_cards if 'S' not in card]
                king_cards = [card for card in king_cards if 'K' in card]
                if len(king_cards) >= 2:
                    bid_value += 0.4
            if number_of_king_and_queen_combos >= 3:
                bid_value -= 0.6


    # if not king_and_queen_combo_used:
    #     # if king queen combo is not used
    #     # consider king and low face card
    #     # but here the suit length should be exactly 2
    #     if '1C' not in my_cards and 'KC' in my_cards and my_spade_count >= 4 and len(my_club_options) == 2:
    #         bid_value += 1
    #         number_of_king_and_queen_combos += 1
    #         king_and_queen_combo_used = True
    #     if '1H' not in my_cards and 'KH' in my_cards and my_spade_count >= 4 and len(my_heart_options) == 2:
    #         bid_value += 1
    #         number_of_king_and_queen_combos += 1
    #         king_and_queen_combo_used = True
    #     if '1D' not in my_cards and 'KD' in my_cards and my_spade_count >= 4 and len(my_diamond_options) == 2:
    #         bid_value += 1
    #         number_of_king_and_queen_combos += 1
    #         king_and_queen_combo_used = True

    #     if number_of_king_and_queen_combos >= 3:
    #         bid_value -= 0.5

    # commented out as king and queen are already considered above
    # consider 2 kings and 1 queen
    # king_and_queen_used = False
    # king_and_queen = [card for card in my_cards if 'K' in card or 'Q' in card]
    # king_and_queen = [card for card in king_and_queen if 'S' not in card]
    # only_king = [card for card in king_and_queen if 'S' not in card and 'K' in card]
    # if len(king_and_queen) >= 3 and non_spade_ace_count == 0:
    #     bid_value += 1
    #     king_and_queen_used = True
    #     if debug:
    #         print("king and queen found")
    # elif len(king_and_queen) >= 3 and count_spades >= 4:
    #     bid_value += 1
    #     king_and_queen_used = True
    #     if debug:
    #         print("king and queen found")
    # elif len(only_king) >= 2 and count_spades >= 3:
    #     bid_value += 0.5
    #     king_and_queen_used = True
    #     if debug:
    #         print("dual king found")

    # decrease bid if multiple aces are present. check if aces more than equals to 2
    # non_spade_aces = [card for card in my_cards if '1' in card and 'S' not in card]
    # if len(non_spade_aces) >= 2 and count_all_spades <=4 and count_all_spades >= 1:
    #     bid_value -= 0.4

    ## if my spade count >=2 and count of one of my suit is 0, I should increase by 1 as I can callbreak
    my_club_count = sum([1 for card in my_cards if 'C' in card])
    my_heart_count = sum([1 for card in my_cards if 'H' in card])
    my_diamond_count = sum([1 for card in my_cards if 'D' in card])
    my_spade_count = sum([1 for card in my_cards if 'S' in card])

    single_suit_used = False
    # if my_spade_count >= 4 and non_spade_ace_count <= 1:
    #     if my_club_count == 0 and not single_suit_used and not king_combo_used:
    #         bid_value += 1
    #         single_suit_used = True
    #     elif True and my_club_count == 1 and my_spade_count >= 6 and not single_suit_used and not king_combo_used:
    #         bid_value += 1
    #         single_suit_used = True
    #         print('single suit used')

    #     if my_heart_count == 0 and not single_suit_used and not king_combo_used:
    #         bid_value += 1
    #         single_suit_used = True
    #     elif True and my_heart_count == 1 and my_spade_count >= 6 and not single_suit_used and not king_combo_used:
    #         bid_value += 1
    #         single_suit_used = True
    #         print('single suit used')

    #     if my_diamond_count == 0 and not single_suit_used and not king_combo_used:
    #         bid_value += 1
    #         single_suit_used = True
    #     elif True and my_diamond_count == 1 and my_spade_count >= 6 and not single_suit_used and not king_combo_used:
    #         bid_value += 1
    #         single_suit_used = True
    #         print('single suit used')

    # Use High Spade count in combination with zero count suits
    number_of_zero_counts = 0
    if my_club_count == 0:
        number_of_zero_counts += 1
    if my_heart_count == 0:
        number_of_zero_counts += 1
    if my_diamond_count == 0:
        number_of_zero_counts += 1

    # if debug:
    #     print('king_combo_used ', king_combo_used)
    zero_suit_used = False
    if len(uncertain_spades) >= 5:
        bid_value += number_of_zero_counts
        zero_suit_used = True
    elif len(uncertain_spades) >= 4:
        if number_of_zero_counts > 0:
            bid_value += 1
            zero_suit_used = True
    elif my_spade_count >= 4 and len(uncertain_spades) >= 1:
        if number_of_zero_counts > 0:
            bid_value += 1
            zero_suit_used = True
    if debug:
        print("zero count used: ", zero_suit_used)
    if debug:
        print("bid_value at zero point ", bid_value)

    # if many_spade_and_zero_count_combo_used not used, then check for 1 count suits as well
    one_count_used = False
    number_of_one_counts = 0
    if my_club_count == 1:
        number_of_one_counts += 1
    if my_heart_count == 1:
        number_of_one_counts += 1
    if my_diamond_count == 1:
        number_of_one_counts += 1

    # if len(uncertain_spades) >= 5 and not ace_and_king_combo_used and not king_and_queen_combo_used and (number_of_zero_counts == 0) and not high_spade_count_used:
    if debug:
        print("uncertain spades is -------------------------------> ", uncertain_spades)
    # if len(uncertain_spades) >= 4 and (number_of_zero_counts == 0):
    #     if number_of_one_counts > 0:
    #         bid_value += 1
    #         one_count_used = True
    # elif my_spade_count >= 6 and (number_of_zero_counts == 0) and len(uncertain_spades) >= 2:
    #     if number_of_one_counts > 0:
    #         bid_value += 1
    #         one_count_used = True
    # elif my_spade_count >= 3 and (number_of_zero_counts == 0) and len(uncertain_spades) >= 2 and bid_value <= 3:
    #     if number_of_one_counts > 0:
    #         bid_value += 1
    #         one_count_used = True

    if debug:
        print('---------------------')
        print('number of zero counts: ', number_of_zero_counts)
        print('my spade count: ', my_spade_count)
        print('number of one counts: ', number_of_one_counts)
        print('high spade count used: ', high_spade_count_used)
        print("one count used: ", one_count_used)

    # if my suit count is equals to 2 and that suit is a king and a ace
    # i should increase my bid value by 1
    # if my_club_count == 2 and not king_and_queen_used and not one_count_used:
    #     if '1C' in my_cards and 'KC' in my_cards and my_spade_count >= 3:
    #         bid_value += 1
    # elif my_heart_count == 2 and not king_and_queen_used and not one_count_used:
    #     if '1H' in my_cards and 'KH' in my_cards and my_spade_count >= 3:
    #         bid_value += 1
    # elif my_diamond_count == 2 and not king_and_queen_used and not one_count_used:
    #     if '1D' in my_cards and 'KD' in my_cards and my_spade_count >= 3:
    #         bid_value += 1

    # 2 kings = +0.4
    # king_count_not_spade = sum([1 for card in my_cards if 'S' not in card and 'K' in card])
    # if king_count_not_spade >= 2:
    #     bid_value += 0.2
    # # 2 queens = +0.2
    # queen_count_not_spade = sum([1 for card in my_cards if 'S' not in card and 'Q' in card])
    # if queen_count_not_spade >= 2:
    #     bid_value += 0.1
    # # 2 jacks = +0.1
    # jack_count_not_spade = sum([1 for card in my_cards if 'S' not in card and 'J' in card])
    # if jack_count_not_spade >= 2:
    #     bid_value += 0.05

    # do card sum, but do not consider winning Aces - ['1C', '1D', '1H']
    card_sum = find_sum_of_card_numbers([card for card in my_cards if 'S' not in card and '1' not in card])
    # print('count_all_spades ', count_all_spades)
    if debug:
        print('bid_value ', bid_value)
        print('card_sum ', card_sum)
        print('count_spades ', count_spades)
        print('certain bid ', certain_bid)
        print('single suit used', single_suit_used)
        print('ace_and_king_combo_used ', ace_and_king_combo_used)
        print('king_and_queen_combo_used', king_and_queen_combo_used)
    # if card_sum <= 45 and count_spades <= 4:
    #     # reduction because of really bad card
    #     bid_value -= 0.9
        # print("low card sum decrease - Activated")

    # if card_sum >= 90 and count_all_spades >= 3 and not single_suit_used and not king_and_queen_used:
    #     bid_value += 0.7
    #     if debug:
    #         print("high card sum increase - Activated")

    # reduce bid for bad cards
    # if len(uncertain_spades) >= 1:
    #     spade_sum = sum([find_max_card([spade]) for spade in uncertain_spades])
    #     spade_average = spade_sum/len(uncertain_spades)
    #     if spade_average <= 6 and not king_and_queen_combo_used and not king_combo_used and not high_spade_count_used and not ace_and_king_combo_used and not single_suit_used and not zero_suit_used and len(uncertain_spades) <= 4:
    #         bid_value -= 0.5

    if debug:
        print('---------------------------------------------------> final bid ', bid_value)

    # additional bid to consider Kings when bid value <= 2
    ignored_kings_used = False
    # if bid_value <= 1 and not zero_suit_used and not one_count_used and not ace_and_king_combo_used:
    #     # consider ignored Kings
    #     if not high_spade_count_used:
    #         if '1C' not in my_cards and 'KC' in my_cards and len(my_club_options) <= 4 and len(my_club_options) >= 3:
    #             bid_value += 0.5
    #             ignored_kings_used = True
    #         elif '1H' not in my_cards and 'KH' in my_cards and len(my_heart_options) <= 4 and len(my_heart_options) >= 3:
    #             bid_value += 0.5
    #             ignored_kings_used = True
    #         elif '1D' not in my_cards and 'KD' in my_cards and len(my_diamond_options) <= 4 and len(my_diamond_options) >= 3:
    #             bid_value += 0.5
    #             ignored_kings_used = True
    # if ignored_kings_used:
    #     # add boost to ignored kings when len(uncertain_spades) >= 2:
    #     if len(uncertain_spades) >= 2:
    #         bid_value += 0.5
    if debug:
        print('Ignored Kings used: ', ignored_kings_used)



    # limit highest bid
    # if bid_value >= 7:
    #     bid_value -= 1

    # # play more conservatively on the second last and last round
    # if round == 4:
    #     logger.critical("Playing semi-conservatively at Round: " + str(round))
    #     bid_value -= 0.2
    # if round == 5:
    #     logger.critical("Playing conservatively at Round " + str(round))
    #     bid_value -= 0.5

    # use confidence level required for higher jumps
    # if expected bid is much greater than certain bid, it requires a higher confidence level threshold
    confidence_required = 0.6
    jump = bid_value - certain_bid
    if jump >= 6:
        confidence_required = 0.96
    elif jump >= 5:
        confidence_required = 0.9
    elif jump >= 4:
        confidence_required = 0.8
    elif jump >= 3:
        confidence_required = 0.75
    elif jump >= 2:
        confidence_required = 0.7
    else:
        confidence_required = 0.6
    if debug:
        print('jump ', jump)
        print('confidence_required ', confidence_required)
    decimal_value = bid_value - math.floor(bid_value)
    if debug:
        print('decimal_value ', decimal_value)
    if decimal_value >= confidence_required:
        bid_value = math.floor(bid_value) + 1
    else:
        bid_value = math.floor(bid_value)

    # bid_value = math.floor(bid_value)  # convert 2.6 to 2
    if high_spade_count_used:
        return bid_value, certain_bid
    else:
        return bid_value, bid_value - 1

def find_count_of_spades(my_cards):
    count_spades = sum([1 for card in my_cards if 'S' in card])
    return count_spades

# winning_club = '1C'
# winning_heart = '1H'
# winning_diamond = '1D'
# winning_spade = '1S'

def next_winning_card(winning_card):
    # if found AC, should return KC
    # if found KC, should return QC

    suit = winning_card[1]
    number = winning_card[0]
    if number == '1':
        next_number = 'K' + str(suit)
    elif number == 'K':
        next_number = 'Q' + str(suit)
    elif number == 'Q':
        next_number = 'J' + str(suit)
    elif number == 'J':
        next_number = 'T' + str(suit)
    elif number == 'T':
        next_number = '9' + str(suit)
    elif number != '2':
        next_number = int(number) - 1
        next_number = str(next_number) + str(suit)
    else:
        next_number = '2' + str(suit)
    return next_number

@app.route("/bid", methods=["POST"])
def bid(request):
    """
    Bid is called at the starting phase of the game in callbreak.
    You will be provided with the following data:
    {
        "matchId": "M1",
        "playerId": "P3",
        "cards": ["1S", "TS", "8S", "7S", "6S", "4S", "3S", "9H", "6H", "5H", "1C", "1D", "JD"],
        "context": {
            "round": 1,
            "players": {
            "P3": {
                "totalPoints": 0,
                "bid": 0
            },
            "P0": {
                "totalPoints": 0,
                "bid": 3
            },
            "P2": {
                "totalPoints": 0,
                "bid": 3
            },
            "P1": {
                "totalPoints": 0,
                "bid": 3
            }
            }
        }
    }

    This is all the data that you will require for the bidding phase.
    """
    global debug
    if debug:
        t1 = time.time()
    if debug:
        logger.warning('Let the bidding begin')
    body = request.json
    if debug:
        logger.warning(json.dumps(body, indent=2))

    round = body['context']['round']
    if debug:
        logger.critical("Playing Round: " + str(round))

    # search for honest signaling,
    # i.e. if the 1st, 2nd or 3rd ranking players bid a high bid >= 7,
    # it is an honest signal
    # for an honest signal, I should decrease my bid value by 1 or only return the certain bid
    my_player_id = body['playerId']
    players_info = body['context']['players']
    my_total = players_info[my_player_id]['totalPoints']

    # store player info as list of tuples (playerid, playerTotal, playerBid)
    player_info_list = []
    for player in players_info:
        player_total = players_info[player]['totalPoints']
        player_bid = players_info[player]['bid']
        player_tuple = (player, player_total, player_bid)
        player_info_list.append(player_tuple)

    if debug:
        logger.warning(player_info_list)

    # sort players by totalpoints to create 1st, 2nd, 3rd rankings
    player_info_list = sorted(player_info_list, key = lambda x: x[1], reverse=True)
    # sorted players
    if debug:
        logger.critical("Sorted Players by Rank")
        logger.warning(player_info_list)
    
    # find first three
    player_rankings = [player_info[0] for player_info in player_info_list]
    first_three = player_rankings[:3]
    first_two = player_rankings[:2]
    first = player_rankings[:1]
    if debug:
        logger.critical("First Three Ranks")
        logger.warning(first_three)

    # find highest bidder and see if the highest bidder is in first_three or not
    highest_bidder = None
    highest_bid = 0
    bids = []
    for player in players_info:
        player_bid = players_info[player]['bid']
        bids.append(player_bid)
        if player_bid > highest_bid:
            highest_bid = player_bid
            highest_bidder = player
    if debug:
        logger.warning("Highest Bidder is: " + str(highest_bidder))
        logger.warning("Highest Bid is: " + str(highest_bid))

    bids_greater_than_0 = [bid for bid in bids if bid > 0]

    first_position = player_rankings[0]
    second_position = player_rankings[1]
    third_position = player_rankings[2]
    fourth_position = player_rankings[3]

    first_total = players_info[first_position]['totalPoints']
    second_total = players_info[second_position]['totalPoints']
    third_total = players_info[third_position]['totalPoints']
    fourth_total = players_info[fourth_position]['totalPoints']

    take_risk = False
    if round == 5 and fourth_position == my_player_id and (third_total - fourth_total) >= 6:
    # if round == 5 and fourth_position == my_player_id and (third_total - fourth_total) >= 4:
    # if round == 5 and fourth_position == my_player_id and (third_total - fourth_total) >= 4:  # scored 5179
    # if round == 5 and fourth_position == my_player_id and (third_total - fourth_total) >= 5.5:  # scored 5113
    # if round == 5 and fourth_position == my_player_id and (third_total - fourth_total) >= 3.5:  # original
    # if round == 5 and fourth_position == my_player_id and (third_total - fourth_total) >= 3: # 5173 with new combo
    # if round == 5 and fourth_position == my_player_id and (third_total - fourth_total) >= 2: # scored 4975 and 4772
    # if round == 5 and fourth_position == my_player_id and (third_total - fourth_total) >= 3: # scored 4757
        take_risk = True

    # if round == 4 and fourth_position == my_player_id and (third_total - fourth_total) >= 4:  # scored 5043, 5146
    #     take_risk = True

    # if round == 4 and fourth_position == my_player_id and (third_total - fourth_total) >= 6:
    #     take_risk = True

    # if round == 5 and third_position == my_player_id and (second_total - third_total) >= 4 and (third_total - fourth_total) <= 2:  # 4989
    # if round == 5 and third_position == my_player_id and (second_total - third_total) >= 3 and (third_total - fourth_total) <= 1:  # 4936
    # if round == 5 and third_position == my_player_id and (second_total - third_total) >= 3 and (third_total - fourth_total) <= 2:  # 5167 when using this combo
    # # if round == 5 and third_position == my_player_id and (second_total - third_total) >= 3 and (third_total - fourth_total) <= 3:  # 4999
    #     take_risk = True
    #     take_risk = False

    # take_risk = False

    # evaluate if honest high signal is present or not
    # if highest_bidder in first_two and highest_bid >= 7 and not take_risk:
    # # if highest_bidder in first and highest_bid >= 7:
    #     honest_high_bid_signal = True
    # else:
    #     honest_high_bid_signal = False

    # if second and third and fourth within 3 points of first position, consider all
    # if (first_total - fourth_total) <= 1:
    #     if highest_bidder in player_rankings and highest_bid >= 7 and not take_risk:
    #     # if highest_bidder in first and highest_bid >= 7:
    #         honest_high_bid_signal = True
    #     else:
    #         honest_high_bid_signal = False
    honest_high_bid_signal = False
    if round >= 3:  # scored 5173
        if (first_total - third_total) <= 1:
            if highest_bidder in first_three and highest_bid >= 7 and not take_risk:
            # if highest_bidder in first and highest_bid >= 7:
                honest_high_bid_signal = True
            else:
                honest_high_bid_signal = False
        elif (first_total - second_total) <= 1:
            if highest_bidder in first_two and highest_bid >= 7 and not take_risk:
            # if highest_bidder in first and highest_bid >= 7:
                honest_high_bid_signal = True
            else:
                honest_high_bid_signal = False
        else:
            if highest_bidder in first and highest_bid >= 7 and not take_risk:
            # if highest_bidder in first and highest_bid >= 7:
                honest_high_bid_signal = True
            else:
                honest_high_bid_signal = False

    # Evaluate bid here
    my_cards = body['cards']
    # bid_value, certain_bid = find_bid_winning_version_1(my_cards, round=round)

    bid_value = mlp_bid_predict(my_cards)
    certain_bid = bid_value - 1  # june 10

    # Evaluate expected bid from others bid
    if len(bids_greater_than_0) == 3:
        # only adjust bid when i am certain that 3 players have bid
        # i should be the last bidder
        if sum(bids_greater_than_0) >= 11:
            ## decrease bid by 1 when others have very high bids
            bid_value -= 1

    # bid_value = find_bid_from_model(my_cards)

    # if take_risk and bid_value >= 3:
    if take_risk and bid_value >= 6:  # score 5066
        bid_value = 8

    # Use Honest high bid signal
    # if true, it means someone else has a really good card and they're in 1st 2nd or 3rd rank
    # so I should decrease my bid to avoid going to negative
    if honest_high_bid_signal:
        # if bid_value >= 3:
        #     bid_value -= 1
        # bid_value = certain_bid
        # avoid honest signal
        print("avoid honest signal")

    # play more carefully when i'm in the first rank
    my_player_id = body['playerId']
    players_info = body['context']['players']
    my_total = players_info[my_player_id]['totalPoints']
    highest_total = my_total
    
    other_total_points = []
    for player in players_info:
        if player != my_player_id:
            player_total = players_info[player]['totalPoints']
            other_total_points.append(player_total)
            if highest_total < player_total:
                highest_total = player_total
    if (highest_total == my_total) and (round != 1) and not honest_high_bid_signal:
        # I have the highest score
        # so I should be more conservative when playing
        second_highest_total = max(other_total_points)
        if (my_total - second_highest_total) >= 4:
            # if certain_bid >= 3:
            bid_value = certain_bid
            # else:
            #     bid_value -= 2
        # elif (my_total - second_highest_total) >= 3:
        #     if certain_bid >= 3:
        #         bid_value = certain_bid
            # else:
            #     bid_value -= 1

        # if (my_total - second_highest_total) >= 6:
        #     bid_value -= 2
        # elif (my_total - second_highest_total) >= 4:
        #     bid_value -= 1

    # play more riskily when i'm in last place and it is last round
    # lowest_total = my_total
    # other_total_points = []
    # for player in players_info:
    #     if player != my_player_id:
    #         player_total = players_info[player]['totalPoints']
    #         other_total_points.append(player_total)
    #         if lowest_total > player_total:
    #             lowest_total = player_total
    # if (lowest_total == my_total) and (round == 5):
    #     # I have the lowest score
    #     # so I should be more risky when playing
    #     second_lowest_total = min(other_total_points)
    #     if (second_lowest_total - my_total) >= 5:
    #         bid_value += 2
    #     elif (second_lowest_total - my_total) >= 3:
    #         bid_value += 1

    # bid 0 not allowed, so add bid 1 if less
    if bid_value < 1:
        bid_value = 1

    # limit highest bid to 8
    if bid_value > 8:
        bid_value = 8


    if debug:
        logger.info('bid value is ' + str(int(bid_value)))
        t2 = time.time()
        time_taken = (t2 - t1) * 1000
    if debug:
        logger.critical("Time taken for Bid is " + str(time_taken) + " milliseconds")

    ####################################
    #     Input your code here.        #
    ####################################

    # return should have a single field value which should be an int reprsenting the bid value
    # return jsonify({"value": 2})
    return response.json({"value": int(bid_value)})


def is_my_card_higher(my_card, other_card):
    map_cards = {
        '1': '14',
        'T': '10',
        'J': '11',
        'Q': '12',
        'K': '13',
    }
    for key in map_cards:
        if key in my_card[:1]:
            my_card = my_card.replace(key, map_cards[key])
        if key in other_card[:1]:
            other_card = other_card.replace(key, map_cards[key])
    if '1' in my_card:
        rank_my_card = int(my_card[:2])
    else:
        rank_my_card = int(my_card[:1])
    if '1' in other_card:
        rank_other_card = int(other_card[:2])
    else:
        rank_other_card = int(other_card[:1])
    return rank_my_card > rank_other_card

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

# sum of the average card [2, 3, 4, ...., K, A] is 104
# if sum of my card is less than average, it means i've got a bad card
# so i need to be more careful, i.e. bid 1 point less

def find_sum_of_card_numbers(my_cards):
    card_numbers = [find_max_card([card]) for card in my_cards]
    return sum(card_numbers)


@app.route("/play", methods=["POST"])
def play(request):
    """
    Play is called at every hand of the game where the user should throw a card.
    Request data format:
    {
        "timeBudget": 1488,
        "playerId": "P0",
        "playerIds": [
            "P0",
            "Bot-1",
            "Bot-2",
            "Bot-3"
        ],
        "cards": [
            "KS",
            "9S",
            "7S",
            "4S",
            "3S",
            "2S",
            "1H",
            "8H",
            "TC",
            "5C",
            "2C",
            "TD",
            "2D"
        ],
        "played": [
            "TH",
            "4H"
        ],
        "history": [],
        "context": {
            "round": 1,
            "players": {
            "P0": {
                "totalPoints": 0,
                "bid": 4,
                "won": 0
            },
            "Bot-1": {
                "totalPoints": 0,
                "bid": 2,
                "won": 0
            },
            "Bot-2": {
                "totalPoints": 0,
                "bid": 3,
                "won": 0
            },
            "Bot-3": {
                "totalPoints": 0,
                "bid": 1,
                "won": 0
            }
            }
        }
        }

    """
    global debug
    if debug:
        t1 = time.time()
    body = request.json
    if debug:
        logger.info(json.dumps(body, indent=2))

    if debug:
        logger.critical('Play move calculation completed')

    ####################################
    #     Input your code here.        #
    ####################################

    time_budget = body['timeBudget']
    my_cards = body['cards']
    my_player = body['playerId']

    # chose time limit non-linearly
    # lot of time ahead, little time later
    # for now using simple linear calculator
    card_count = len(my_cards)
    time_limit = time_budget / card_count  - 5 ## subtract extra 5 seconds just in case

    if len(my_cards) >= 3:
        # time_limit = 1 * (time_budget / (card_count - 1))  - 5  ## subtract extra 5 seconds just in case
        time_limit = 2 * (time_budget / (card_count - 1)) - 5  ## subtract extra 5 seconds just in case
        if (time_budget - time_limit) < (card_count - 1) * 60:
            time_limit = (time_budget / (card_count - 1)) - 5
    # elif len(my_cards) == 3:
    #     time_limit = (time_budget / (card_count - 1))
    else:
        time_limit = time_budget - 10  # time lag for last end game

    # time_limit = (time_budget) / (card_count - 1) - 20

    if debug:
        logger.warning("Time Budget is: " + str(time_budget))
        logger.warning("Time Limit is : " + str(time_limit))
        logger.warning("Length of cards: " + str(len(my_cards)))

    my_score = body['context']['players'][my_player]['won']
    my_bid = body['context']['players'][my_player]['bid']
    context = body['context']

    # if my_score >= my_bid:
    #     my_bid += 1
    # if my_score >= my_bid:
    #     my_bid += 1

    if debug:
        logger.warning("My Score: " + str(my_score))
        logger.warning("My Bid: " + str(my_bid))

    history_cards = body['history']
    player_list = body['playerIds']
    current_player = body['playerId']
    round = body['context']['round']
    played_cards = body['played']
    current_player_index = player_list.index(current_player)

    player_bids = [1,1,1,1]
    player_scores = [0,0,0,0]

    for i in range(4):
        player_id = player_list[i]
        player_bid = context['players'][player_id]['bid']
        player_score = context['players'][player_id]['won']
        player_bids[i] = player_bid
        player_scores[i] = player_score

    activate_king_crimson = False
    # if card_count >= 10:  # got 3632 score
    # if card_count >= 5:  # got 4603 score
    # if card_count >= 7 or (len(played_cards) == 3 and card_count >= 5):  # got 4258 score


    # if card_count >= 7 and len(played_cards) == 0:
    #     activate_king_crimson = True
    # if card_count >= 7 and len(played_cards) == 3:
    #     activate_king_crimson = True

    # if card_count >= 4 and len(played_cards) == 0:
    #     activate_king_crimson = True
    # if card_count >= 4 and len(played_cards) == 3:
    #     activate_king_crimson = True

    # if card_count >= 3 and len(played_cards) == 0:
    #     activate_king_crimson = True
    # if card_count >= 3 and len(played_cards) == 3:
    #     activate_king_crimson = True

    activate_king_crimson = True

    # if card_count <= 3:
    #     activate_king_crimson = False

    # activate_king_crimson = True  # check how accurate bidding is
    # activate_king_crimson = False  # check how well monte carlo plays

    #######################################################################
    # start MCTS algorithm here
    #######################################################################

    activate_100_simulation = False

    if len(played_cards) == 0 and time_budget >= 300 and len(my_cards) <= 6:
        activate_100_simulation = True

    activate_100_simulation = False

    # if len(played_cards) == 0:
    #     activate_100_simulation = True

    if activate_100_simulation:
        # card_scores = find_average_points_from_simulation(my_cards, history=history_cards, num_iterations=100, my_player_index=current_player_index, start_index=current_player_index, playerIds=player_list)
        card_scores = find_average_points_from_simulation(my_cards, history=history_cards, num_iterations=100, my_player_index=0, start_index=0, playerIds=[my_player] + ['1', '2', '3'])
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
        return response.json({"value": best_card})

    # if number of available options to play is only 1, play that card directly instead of wasting precious time for MCTS
    # available_card_options = find_available_options_of_cards_that_can_be_played(my_cards, played_cards)

    # if len(available_card_options) == 1:
    #     logger.warning("------------------------------------> Only One Option")
    #     logger.warning("------------------------------------> Playing: " + str(available_card_options[0]))
    #     return response.json({"value": available_card_options[0]})

    # time_limit = 150
    time_limit = (time_budget / (card_count - 0)) - 20
    if time_budget < time_limit:
        time_limit = time_budget - 30

    my_player_index = player_list.index(current_player)

    ## player constraints assigned by going through history and played cards
    ## to limit what possible cards are there for each player
    ## exclude constraint for my player as my cards are already known
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

    ## adjust current winning_card that is different than spades
    ## correct values for next winning cards
    history_cards_set = set()  # creates empty set
    history_list = body['history']
    for history in history_list:
        previous_cards = history[1]
        for prev_card in previous_cards:
            prev_card = prev_card[0:2]
            history_cards_set.add(prev_card)
    
    # corect values for winning card as well
    # winning spade
    winning_spade = '1S'
    while winning_spade in history_cards_set:
        winning_spade = next_winning_card(winning_spade)
        if '2' in winning_spade:
            break

    # winning club
    winning_club = '1C'
    while winning_club in history_cards_set:
        winning_club = next_winning_card(winning_club)
        if '2' in winning_club:
            break

    # winning heart
    winning_heart = '1H'
    while winning_heart in history_cards_set:
        winning_heart = next_winning_card(winning_heart)
        if '2' in winning_heart:
            break

    # winning diamond
    winning_diamond = '1D'
    while winning_diamond in history_cards_set:
        winning_diamond = next_winning_card(winning_diamond)
        if '2' in winning_diamond:
            break

    ###################################################################################################

    # find next winning spade
    # second winning spade
    second_winning_spade = next_winning_card(winning_spade)

    while second_winning_spade in history_cards_set:
        second_winning_spade = next_winning_card(second_winning_spade)
        if '2' in second_winning_spade:
            break

    # second winning club
    second_winning_club = next_winning_card(winning_club)

    while second_winning_club in history_cards_set:
        second_winning_club = next_winning_card(second_winning_club)
        if '2' in second_winning_club:
            break

    # second winning heart
    second_winning_heart = next_winning_card(winning_heart)

    while second_winning_heart in history_cards_set:
        second_winning_heart = next_winning_card(second_winning_heart)
        if '2' in second_winning_heart:
            break

    # second winning diamond
    second_winning_diamond = next_winning_card(winning_diamond)

    while second_winning_diamond in history_cards_set:
        second_winning_diamond = next_winning_card(second_winning_diamond)
        if '2' in second_winning_diamond:
            break


    ###################################################################################################

    # third winning spade
    third_winning_spade = next_winning_card(second_winning_spade)

    while third_winning_spade in history_cards_set:
        third_winning_spade = next_winning_card(third_winning_spade)
        if '2' in third_winning_spade:
            break

    ###################################################################################################
    
    # assign to True in those constraints that have been found
    ###################################################################################################
    for history in history_cards:
        
        previous_cards = history[1]
        first_player_index = history[0]
        winner_index = history[2]
        
        # 2S, 5H, 2H
        # history list shows that the first player's card is always on index 0
        first_played_card = previous_cards[0]
        first_played_suit = first_played_card[1]
        
        # clockwise rotation for first, second, third and 4th players
        first_player = player_list[first_player_index]

        second_player_index = (first_player_index + 1) % 4
        third_player_index = (first_player_index + 2) % 4
        fourth_player_index = (first_player_index + 3) % 4
        
        second_player = player_list[second_player_index]
        third_player = player_list[third_player_index]
        fourth_player = player_list[fourth_player_index]

        first_card = previous_cards[0]
        second_card = previous_cards[1]
        third_card = previous_cards[2]
        fourth_card = previous_cards[3]

        winner_player = player_list[winner_index]
        if winner_player == first_player:
            winner_played_card = previous_cards[0]
        elif winner_player == second_player:
            winner_played_card = previous_cards[1]
        elif winner_player == third_player:
            winner_played_card = previous_cards[2]
        else:
            winner_played_card = previous_cards[3]

        winner_played_suit = winner_played_card[1]

        # Check if Spade eliminated
        if 'S' in first_played_card:
            if 'S' not in second_card:
                ## spade is eliminated for the second player
                player_constraints[second_player_index]['spade_eliminated'] = True
            if 'S' not in third_card:
                ## spade is eliminated for the third player
                player_constraints[third_player_index]['spade_eliminated'] = True
            if 'S' not in fourth_card:
                ## spade is eliminated for the fourth player
                player_constraints[fourth_player_index]['spade_eliminated'] = True
        
        # Check if Club eliminated
        if 'C' in first_played_card:
            if 'C' not in second_card:
                player_constraints[second_player_index]['club_eliminated'] = True
            if 'C' not in third_card:
                player_constraints[third_player_index]['club_eliminated'] = True
            if 'C' not in fourth_card:
                player_constraints[fourth_player_index]['club_eliminated'] = True

        # Check if Heart eliminated
        if 'H' in first_played_card:
            if 'H' not in second_card:
                player_constraints[second_player_index]['heart_eliminated'] = True
            if 'H' not in third_card:
                player_constraints[third_player_index]['heart_eliminated'] = True
            if 'H' not in fourth_card:
                player_constraints[fourth_player_index]['heart_eliminated'] = True

        # Check if Diamond eliminated
        if 'D' in first_played_card:
            if 'D' not in second_card:
                player_constraints[second_player_index]['diamond_eliminated'] = True
            if 'D' not in third_card:
                player_constraints[third_player_index]['diamond_eliminated'] = True
            if 'D' not in fourth_card:
                player_constraints[fourth_player_index]['diamond_eliminated'] = True


        # Check the ranks of second, third and fourth players
        first_card_rank = find_card_rank(first_played_card)
        second_card_rank = find_card_rank(second_card)
        third_card_rank = find_card_rank(third_card)
        fourth_card_rank = find_card_rank(fourth_card)
        
        if 'S' in first_played_card:
            if 'S' in second_card:
                # the rank of second card has to be bigger than the first card rank
                # if not, it means the second card rank is the least rank of the second player
                # i.e. the value of the constraint for the second player that we want in our constraints
                if second_card_rank < first_card_rank:
                    player_constraints[second_player_index]['spade_greater_than_rank'] = second_card_rank
                if second_card == second_winning_spade and first_card == winning_spade:
                    player_constraints[second_player_index]['spade_eliminated'] = True
            if 'S' in third_card:
                if third_card_rank < first_card_rank:
                    player_constraints[third_player_index]['spade_greater_than_rank'] = third_card_rank
                if third_card == second_winning_spade and (first_card == winning_spade or second_card == winning_spade):
                    player_constraints[third_player_index]['spade_eliminated'] = True
            if 'S' in fourth_card:
                if fourth_card_rank < first_card_rank:
                    player_constraints[fourth_player_index]['spade_greater_than_rank'] = fourth_card_rank
                if fourth_card == second_winning_spade and (first_card == winning_spade or second_card == winning_spade or third_card == winning_spade):
                    player_constraints[fourth_player_index]['spade_eliminated'] = True

        if 'C' in first_played_card:
            if 'C' in second_card:
                if second_card_rank < first_card_rank:
                    player_constraints[second_player_index]['club_greater_than_rank'] = second_card_rank
                if second_card == second_winning_club and first_card == winning_club:
                    player_constraints[second_player_index]['club_eliminated'] = True
            if 'C' in third_card:
                if third_card_rank < first_card_rank:
                    player_constraints[third_player_index]['club_greater_than_rank'] = third_card_rank
                if third_card == second_winning_club and (first_card == winning_club or second_card == winning_club):
                    player_constraints[third_player_index]['club_eliminated'] = True
            if 'C' in fourth_card:
                if fourth_card_rank < first_card_rank:
                    player_constraints[fourth_player_index]['club_greater_than_rank'] = fourth_card_rank
                if fourth_card == second_winning_club and (first_card == winning_club or second_card == winning_club or third_card == winning_club):
                    player_constraints[fourth_player_index]['club_eliminated'] = True

        if 'H' in first_played_card:
            if 'H' in second_card:
                if second_card_rank < first_card_rank:
                    player_constraints[second_player_index]['heart_greater_than_rank'] = second_card_rank
                if second_card == second_winning_heart and first_card == winning_heart:
                    player_constraints[second_player_index]['heart_eliminated'] = True
            if 'H' in third_card:
                if third_card_rank < first_card_rank:
                    player_constraints[third_player_index]['heart_greater_than_rank'] = third_card_rank
                if third_card == second_winning_heart and (first_card == winning_heart or second_card == winning_heart):
                    player_constraints[third_player_index]['heart_eliminated'] = True
            if 'H' in fourth_card:
                if fourth_card_rank < first_card_rank:
                    player_constraints[fourth_player_index]['heart_greater_than_rank'] = fourth_card_rank
                if fourth_card == second_winning_heart and (first_card == winning_heart or second_card == winning_heart or third_card == winning_heart):
                    player_constraints[fourth_player_index]['heart_eliminated'] = True

        if 'D' in first_played_card:
            if 'D' in second_card:
                if second_card_rank < first_card_rank:
                    player_constraints[second_player_index]['diamond_greater_than_rank'] = second_card_rank
                if second_card == second_winning_diamond and first_card == winning_diamond:
                    player_constraints[second_player_index]['diamond_eliminated'] = True
            if 'D' in third_card:
                if third_card_rank < first_card_rank:
                    player_constraints[third_player_index]['diamond_greater_than_rank'] = third_card_rank
                if third_card == second_winning_diamond and (first_card == winning_diamond or second_card == winning_diamond):
                    player_constraints[third_player_index]['diamond_eliminated'] = True
            if 'D' in fourth_card:
                if fourth_card_rank < first_card_rank:
                    player_constraints[fourth_player_index]['diamond_greater_than_rank'] = fourth_card_rank
                if fourth_card == second_winning_diamond and (first_card == winning_diamond or second_card == winning_diamond or third_card == winning_diamond):
                    player_constraints[fourth_player_index]['diamond_eliminated'] = True

        # end of history loop
    
    ###################################################################################################

    # if len(my_cards) <= 3:  # when to use MCTS instead of king crimson
    #     activate_king_crimson = False

    activate_king_crimson = True

    if activate_king_crimson:
        king_crimson_value = king_crimson_heuristic(body, player_constraints)
        if debug:
            t2 = time.time()
            time_taken = (t2 - t1) * 1000
            logger.warning("----------------------")
            logger.critical("King Crimson")
            logger.warning("----------------------")
            logger.critical("Time taken for Play: " + str(time_taken) + " milliseconds")
        # logger.warning("King Crimson -----------------------------------------------------", king_crimson_value)
        return king_crimson_value

    initialState = Callbreak(
        my_cards=set(my_cards), history_cards=history_cards, 
        player_list=tuple(player_list), my_player=my_player, current_player=current_player,
        round=round, played_cards=played_cards, current_player_index=current_player_index,
        player_bids=player_bids, player_scores=player_scores, context=context, player_constraints=player_constraints
    )
    # searcher = mcts(timeLimit=1000)  # 1000 milliseconds
    # searcher = mcts(timeLimit=100)  # 100 milliseconds
    searcher = mcts(timeLimit=time_limit)
    try:
        action = searcher.search(initialState=initialState)
        print("Action is: ")
        print(action.card)
        best_option = action.card
        if debug:
            t2 = time.time()
            time_taken = (t2 - t1) * 1000
            logger.warning("----------------------")
            logger.warning("Monty Carlo")
            logger.warning("----------------------")
            logger.critical("Time taken for Play: " + str(time_taken) + " milliseconds")
        return response.json({"value": best_option})
    except Exception as e:
        logger.warning("Exception Triggered")
        logger.info(str(e))
        logger.critical("King Crimson")
        logger.warning("---------------------------")
        ## use normal heuristic to play the card from here on out
        king_crimson_value = king_crimson_heuristic(body, player_constraints)
        if debug:
            t2 = time.time()
            time_taken = (t2 - t1) * 1000
            logger.critical("Time taken for Play: " + str(time_taken) + " milliseconds")
        # logger.warning("King Crimson -----------------------------------------------------", king_crimson_value)
        return king_crimson_value

# do not change this port; the sandbox server hits this port on localhost
if __name__ == '__main__':
    app.run(port=7000, debug=False)