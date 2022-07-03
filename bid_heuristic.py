import math

debug = False

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
        # print("Searching for Winning: ", winning)
        if winning in my_spades:
            if searching_next == True:
                ## since it was set to true, it meant a card was skipped and cards were spent to find that card
                ## so set search_found to true
                searching_found = True
                spent_spade_count += spend_if_found_count
                spend_if_found_count = 0
            # print('Matched: ', winning)
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
            # print("skipping ", winning)
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
            # print("early stopping ...............................")
            break
        # print("spend_if_found_count: ", spend_if_found_count)
        # print("previous matched: ", previous_matched)
        i += 1
    # print('-----------------')
    # print("matched winning spades is: ", matched_winning_spades)
    # print('certain bid is: ', certain_bid)
    # print('spent spade count is: ', spent_spade_count)
    # print("searching_next ", searching_next)
    # print("searching found ", searching_found)
    # print("previous matched: ", previous_matched)
    # print("spend_if_found_count = ", spend_if_found_count)
    if searching_found:
        # donot use remaining cards to calculate cards
        # i.e. set uncertain spades to empty list
        # print("original spades count: ", original_my_spade_count)
        if certain_bid + spent_spade_count == original_my_spade_count:
            # print('exactly equal so no more remaining spades')
            uncertain_spades = []
        else:
            # print('certain bid and spend spade count not equal, so there are remaining spades')
            uncertain_spades = my_spades_copy[(certain_bid + spent_spade_count - 1):]
    else:
        # search was not found, so use the remaining spades
        # after subtracting the spent spade count
        # uncertain_spades = [card for card in my_spades_copy if card not in matched_winning_spades][spent_spade_count:]
        uncertain_spades = [card for card in my_spades_copy if card not in matched_winning_spades]
        uncertain_spades = uncertain_spades[::-1][spent_spade_count:]
    if certain_bid < len(my_spades)/2 and len(uncertain_spades) == 0:
        # print("calling bid resettter here -------------------------------------> ")
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
    certain_bid, uncertain_spades = find_certain_bid(my_spades)
    if debug:
        print("Result Certain Bid: ", certain_bid)
        print("Result Uncertain Spades: ", uncertain_spades)
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
    elif count_all_spades >= 6:
        if certain_bid < 3:
            certain_bid = 3
            bid_value = 3
            high_spade_count_used = True

    else:
        # use only half of the total remaining spade count
        count_spades = len(uncertain_spades)
        remaining_spade_bid = count_spades/2
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
    elif my_spade_count >= 4:
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
    if len(uncertain_spades) >= 4 and (number_of_zero_counts == 0):
        if number_of_one_counts > 0:
            bid_value += 1
            one_count_used = True
    elif my_spade_count >= 4 and (number_of_zero_counts == 0) and len(uncertain_spades) >= 1:
        if number_of_one_counts > 0:
            bid_value += 1
            one_count_used = True
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

    # print('count_all_spades ', count_all_spades)
    if debug:
        print('bid_value ', bid_value)
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
    if bid_value <= 1 and not zero_suit_used and not one_count_used and not ace_and_king_combo_used:
        # consider ignored Kings
        if not high_spade_count_used:
            if '1C' not in my_cards and 'KC' in my_cards and len(my_club_options) <= 4 and len(my_club_options) >= 3:
                bid_value += 0.5
                ignored_kings_used = True
            elif '1H' not in my_cards and 'KH' in my_cards and len(my_heart_options) <= 4 and len(my_heart_options) >= 3:
                bid_value += 0.5
                ignored_kings_used = True
            elif '1D' not in my_cards and 'KD' in my_cards and len(my_diamond_options) <= 4 and len(my_diamond_options) >= 3:
                bid_value += 0.5
                ignored_kings_used = True
    if ignored_kings_used:
        # add boost to ignored kings when len(uncertain_spades) >= 2:
        if len(uncertain_spades) >= 2:
            bid_value += 0.5
    if debug:
        print('Ignored Kings used: ', ignored_kings_used)



    # limit highest bid
    # if bid_value >= 7:
    #     bid_value -= 1

    # # play more conservatively on the second last and last round
    # if round == 4:
    #     app.logger.critical("Playing semi-conservatively at Round: " + str(round))
    #     bid_value -= 0.2
    # if round == 5:
    #     app.logger.critical("Playing conservatively at Round " + str(round))
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