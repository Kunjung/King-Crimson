# from flask import jsonify
from sanic.response import json as jsonify

debug = True

def find_available_options_of_cards_that_can_be_played(my_cards, played_cards):
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

    # logic for when it is my turn
    # there is certainty of what cards i can choose from
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
    options_greater_than_max_played_card = [option for option in options if find_max_card([option]) > max_played_card]
    options_greater_than_max_played_card = [option for option in options_greater_than_max_played_card if first_played_suit in option or 'S' in option]

    options_less_than_max_played_card = [option for option in options if find_max_card([option]) < max_played_card]
    options_less_than_max_played_card = [option for option in options_less_than_max_played_card if first_played_suit in option or 'S' in option]

    if len(options_greater_than_max_played_card) > 0:
        options = options_greater_than_max_played_card
        options_rankings = [find_max_card([option]) for option in options_greater_than_max_played_card]
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
                options_rankings = [find_max_card([option]) for option in new_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = new_options[best_index]
                options = [best_option]

    elif len(options_less_than_max_played_card) > 0:
        options = options_less_than_max_played_card
        options_rankings = [find_max_card([option]) for option in options_less_than_max_played_card]
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
                options_rankings = [find_max_card([option]) for option in new_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = new_options[best_index]
                options = [best_option]

    return options

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

def king_crimson_heuristic(body, player_constraints):
    global debug
    winning_club = '1C'
    winning_heart = '1H'
    winning_diamond = '1D'
    winning_spade = '1S'

    ## adjust current winning_card that is different than spades
    ## correct values for next winning cards
    history_cards = set()  # creates empty set
    history_list = body['history']
    for history in history_list:
        previous_cards = history[1]
        for prev_card in previous_cards:
            prev_card = prev_card[0:2]
            history_cards.add(prev_card)
            # if winning_club == prev_card:
            #     ## winning card was played, so find out next winning card
            #     winning_club = next_winning_card(winning_club)
            # if winning_heart == prev_card:
            #     ## winning card was played, so find out next winning card
            #     winning_heart = next_winning_card(winning_heart)
            # if winning_diamond == prev_card:
            #     ## winning card was played, so find out next winning card
            #     winning_diamond = next_winning_card(winning_diamond)
            # if winning_spade == prev_card:
            #     ## winning card was played, so find out next winning card
            #     winning_spade = next_winning_card(winning_spade)
    
    # corect values for winning card as well
    # winning spade
    winning_spade = '1S'
    while winning_spade in history_cards:
        winning_spade = next_winning_card(winning_spade)
        if '2' in winning_spade:
            break

    # winning club
    winning_club = '1C'
    while winning_club in history_cards:
        winning_club = next_winning_card(winning_club)
        if '2' in winning_club:
            break

    # winning heart
    winning_heart = '1H'
    while winning_heart in history_cards:
        winning_heart = next_winning_card(winning_heart)
        if '2' in winning_heart:
            break

    # winning diamond
    winning_diamond = '1D'
    while winning_diamond in history_cards:
        winning_diamond = next_winning_card(winning_diamond)
        if '2' in winning_diamond:
            break

    ###################################################################################################

    # find next winning spade
    # second winning spade
    second_winning_spade = next_winning_card(winning_spade)

    while second_winning_spade in history_cards:
        second_winning_spade = next_winning_card(second_winning_spade)
        if '2' in second_winning_spade:
            break

    # second winning club
    second_winning_club = next_winning_card(winning_club)

    while second_winning_club in history_cards:
        second_winning_club = next_winning_card(second_winning_club)
        if '2' in second_winning_club:
            break

    # second winning heart
    second_winning_heart = next_winning_card(winning_heart)

    while second_winning_heart in history_cards:
        second_winning_heart = next_winning_card(second_winning_heart)
        if '2' in second_winning_heart:
            break

    # second winning diamond
    second_winning_diamond = next_winning_card(winning_diamond)

    while second_winning_diamond in history_cards:
        second_winning_diamond = next_winning_card(second_winning_diamond)
        if '2' in second_winning_diamond:
            break


    ###################################################################################################

    # third winning spade
    third_winning_spade = next_winning_card(second_winning_spade)

    while third_winning_spade in history_cards:
        third_winning_spade = next_winning_card(third_winning_spade)
        if '2' in third_winning_spade:
            break

    ###################################################################################################


    cards = body['cards']
    # convert cards from list to set to speed up play calculation
    # cards = set(cards)
    ## adjust other's remaining number of club, heart, diamond
    others_remaining_club_count = 13 - sum([1 for card in cards if 'C' in card])
    others_remaining_heart_count = 13 - sum([1 for card in cards if 'H' in card])
    others_remaining_diamond_count = 13 - sum([1 for card in cards if 'D' in card])
    ## adjust other's remaining number of spade
    others_remaining_spade_count = 13 - sum([1 for card in cards if 'S' in card])
    for history in history_list:
        previous_cards = history[1]

        for prev_card in previous_cards:
            prev_card = prev_card[0:2]
            if 'C' in prev_card:
                others_remaining_club_count -= 1
            if 'H' in prev_card:
                others_remaining_heart_count -= 1
            if 'D' in prev_card:
                others_remaining_diamond_count -= 1
            if 'S' in prev_card:
                others_remaining_spade_count -= 1

    ## adjust suit eliminated for club, heart and diamond
    ## only adjust it if it doesn't involve when I played a spade and won
    my_player = body['playerId']
    player_ids = body['playerIds']
    player_my_index = player_ids.index(my_player)
    club_eliminated = False
    heart_eliminated = False
    diamond_eliminated = False

    spade_eliminated = False

    if others_remaining_club_count <= 2:
        club_eliminated = True
    if others_remaining_heart_count <= 2:
        heart_eliminated = True
    if others_remaining_diamond_count <= 2:
        diamond_eliminated = True

    for history in history_list:
        previous_cards = history[1]
        first_player_index = history[0]
        winner_index = history[2]
        
        # history list shows that the first player's card is always on index 0
        first_played_card = previous_cards[0]
        first_played_suit = first_played_card[1]
        
        # clockwise rotation for first, second, third and 4th players
        first_player = player_ids[first_player_index]

        second_player_index = (first_player_index + 1) % 4
        third_player_index = (first_player_index + 2) % 4
        fourth_player_index = (first_player_index + 3) % 4
        
        second_player = player_ids[second_player_index]
        third_player = player_ids[third_player_index]
        fourth_player = player_ids[fourth_player_index]

        winner_player = player_ids[winner_index]
        # winner_played_card = find_winner_card(previous_cards)  # find the winner out of 4 previous played cards
        if winner_player == first_player:
            winner_played_card = previous_cards[0]
        elif winner_player == second_player:
            winner_played_card = previous_cards[1]
        elif winner_player == third_player:
            winner_played_card = previous_cards[2]
        else:
            winner_played_card = previous_cards[3]
        winner_played_suit = winner_played_card[1]


        # only consider non-spade cards
        if 'S' not in first_played_card:
            # only consider suit elimination when I was not the winner
            if winner_player != my_player:
                if winner_played_suit != first_played_suit:
                    ## a suit has been eliminated
                    if first_played_suit == 'C':
                        club_eliminated = True
                    elif first_played_suit == 'H':
                        heart_eliminated = True
                    elif first_played_suit == 'D':
                        diamond_eliminated = True
            # check if suits have been reset
            # this time should consider when i was the winner as well
            if winner_played_suit == first_played_suit:
                ## a suit has been reset as someone won with that suit
                if first_played_suit == 'C':
                    club_eliminated = False
                elif first_played_suit == 'H':
                    heart_eliminated = False
                elif first_played_suit == 'D':
                    diamond_eliminated = False

        # search if any player's spade is eliminated
        if 'S' in first_played_card:
            # only consider cards that are not mine
            if my_player == first_player:
                my_previous_card = previous_cards[0]
            elif my_player == second_player:
                my_previous_card = previous_cards[1]
            elif my_player == third_player:
                my_previous_card = previous_cards[2]
            else:
                my_previous_card = previous_cards[3]
            previous_cards_without_my_card = [card for card in previous_cards if card != my_previous_card]
            previous_cards_without_my_card_and_spade = [card for card in previous_cards_without_my_card if 'S' in card]
            if len(previous_cards_without_my_card) != len(previous_cards_without_my_card_and_spade):
                # spade eliminated for other player
                spade_eliminated = True
            
    
    if others_remaining_spade_count == 0:
        club_eliminated = False
        heart_eliminated = False
        diamond_eliminated = False

    if debug:
        print('club eliminated ', club_eliminated)
        print('heart eliminated ', heart_eliminated)
        print('diamond_eliminated ', diamond_eliminated)

    played = body['played']
    if len(played) > 0:
        suit = played[0][1:2]
    else:
        suit = ''  # should be able to pick any suit as len(player) means it's my turn now

    my_spade_options = [card for card in cards if 'S' in card]
    my_spade_count = len(my_spade_options)

    # always check if others spade count has fallen to 0
    # if len(played) == 0:
    #     my_spade_options = [card for card in cards if 'S' in card]
    #     if others_remaining_spade_count == 0 and len(my_spade_options) >= 1:
    #         return jsonify({"value": my_spade_options[-1]})
    #     if others_remaining_spade_count == 0:
    #         if winning_club in cards:
    #             return jsonify({"value": winning_club})
    #         if winning_heart in cards:
    #             return jsonify({"value": winning_heart})
    #         if winning_diamond in cards:
    #             return jsonify({"value": winning_diamond})

    #         # check if the other players have 0 count suits
    #         # if found, play that suit
    #         if others_remaining_club_count == 0:
    #             # play least club
    #             my_club_options = [card for card in cards if 'C' in card]
    #             if len(my_club_options) >= 1:
    #                 return jsonify({"value": my_club_options[-1]})
    #         if others_remaining_heart_count == 0:
    #             # play least heart
    #             my_heart_options = [card for card in cards if 'H' in card]
    #             if len(my_heart_options) >= 1:
    #                 return jsonify({"value": my_heart_options[-1]})
    #         if others_remaining_diamond_count == 0:
    #             # play least diamond
    #             my_diamond_options = [card for card in cards if 'D' in card]
    #             if len(my_diamond_options) >= 1:
    #                 return jsonify({"value": my_diamond_options[-1]})

    # Heuristic: 8
    if len(played) == 0 and others_remaining_spade_count <= 0:
        if winning_club in cards:
            return jsonify({"value": winning_club})
        if winning_heart in cards:
            return jsonify({"value": winning_heart})
        if winning_diamond in cards:
            return jsonify({"value": winning_diamond})
        my_club_options = [card for card in cards if 'C' in card]
        my_heart_options = [card for card in cards if 'H' in card]
        my_diamond_options = [card for card in cards if 'D' in card]
        if len(my_club_options) > 0 and others_remaining_club_count <= 0:
            return jsonify({"value": my_club_options[-1]})
        if len(my_heart_options) > 0 and others_remaining_heart_count <= 0:
            return jsonify({"value": my_heart_options[-1]})
        if len(my_diamond_options) > 0 and others_remaining_diamond_count <= 0:
            return jsonify({"value": my_diamond_options[-1]})

    # Heuristic: 6
    # if len(played) == 0:
    #     # When I am the first player search for 2 call breakable players
    #     # search for 2 players with suit eliminated who also have their spade not eliminated

    #     # 1. search for 2 club eliminated and 2 spade not eliminated
    #     if winning_spade not in cards and winning_club not in cards and others_remaining_spade_count >= 3:
    #         num_players_who_can_break_suit = 0
    #         ###
    #         player_2_index = (player_my_index + 1) % 4
    #         player_2_suit_eliminated = player_constraints[player_2_index]['club_eliminated']
    #         player_2_spade_eliminated = player_constraints[player_2_index]['spade_eliminated']
    #         if player_2_suit_eliminated and not player_2_spade_eliminated:
    #             num_players_who_can_break_suit += 1
    #         ###
    #         player_3_index = (player_my_index + 2) % 4
    #         player_3_suit_eliminated = player_constraints[player_3_index]['club_eliminated']
    #         player_3_spade_eliminated = player_constraints[player_3_index]['spade_eliminated']
    #         if player_3_suit_eliminated and not player_3_spade_eliminated:
    #             num_players_who_can_break_suit += 1
    #         ###
    #         player_4_index = (player_my_index + 3) % 4
    #         player_4_suit_eliminated = player_constraints[player_4_index]['club_eliminated']
    #         player_4_spade_eliminated = player_constraints[player_4_index]['spade_eliminated']
    #         if player_4_suit_eliminated and not player_4_spade_eliminated:
    #             num_players_who_can_break_suit += 1
    #         ###
    #         if num_players_who_can_break_suit == 3:
    #             my_options = [card for card in cards if 'C' in card]
    #             if len(my_options) > 0:
    #                 options_rankings = [find_max_card([option]) for option in my_options]
    #                 min_option_rank = min(options_rankings)
    #                 best_index = options_rankings.index(min_option_rank)
    #                 best_option = my_options[best_index]
    #                 return jsonify({"value": best_option})

    #     # 2. search for 2 heart eliminated and 2 spade not eliminated
    #     if winning_spade not in cards and winning_heart not in cards and others_remaining_spade_count >= 3:
    #         num_players_who_can_break_suit = 0
    #         ###
    #         player_2_index = (player_my_index + 1) % 4
    #         player_2_suit_eliminated = player_constraints[player_2_index]['heart_eliminated']
    #         player_2_spade_eliminated = player_constraints[player_2_index]['spade_eliminated']
    #         if player_2_suit_eliminated and not player_2_spade_eliminated:
    #             num_players_who_can_break_suit += 1
    #         ###
    #         player_3_index = (player_my_index + 2) % 4
    #         player_3_suit_eliminated = player_constraints[player_3_index]['heart_eliminated']
    #         player_3_spade_eliminated = player_constraints[player_3_index]['spade_eliminated']
    #         if player_3_suit_eliminated and not player_3_spade_eliminated:
    #             num_players_who_can_break_suit += 1
    #         ###
    #         player_4_index = (player_my_index + 3) % 4
    #         player_4_suit_eliminated = player_constraints[player_4_index]['heart_eliminated']
    #         player_4_spade_eliminated = player_constraints[player_4_index]['spade_eliminated']
    #         if player_4_suit_eliminated and not player_4_spade_eliminated:
    #             num_players_who_can_break_suit += 1
    #         ###
    #         if num_players_who_can_break_suit == 3:
    #             my_options = [card for card in cards if 'H' in card]
    #             if len(my_options) > 0:
    #                 options_rankings = [find_max_card([option]) for option in my_options]
    #                 min_option_rank = min(options_rankings)
    #                 best_index = options_rankings.index(min_option_rank)
    #                 best_option = my_options[best_index]
    #                 return jsonify({"value": best_option})

    #     # 3. search for 2 diamond eliminated and 2 spade not eliminated
    #     if winning_spade not in cards and winning_diamond not in cards and others_remaining_spade_count >= 3:
    #         num_players_who_can_break_suit = 0
    #         ###
    #         player_2_index = (player_my_index + 1) % 4
    #         player_2_suit_eliminated = player_constraints[player_2_index]['diamond_eliminated']
    #         player_2_spade_eliminated = player_constraints[player_2_index]['spade_eliminated']
    #         if player_2_suit_eliminated and not player_2_spade_eliminated:
    #             num_players_who_can_break_suit += 1
    #         ###
    #         player_3_index = (player_my_index + 2) % 4
    #         player_3_suit_eliminated = player_constraints[player_3_index]['diamond_eliminated']
    #         player_3_spade_eliminated = player_constraints[player_3_index]['spade_eliminated']
    #         if player_3_suit_eliminated and not player_3_spade_eliminated:
    #             num_players_who_can_break_suit += 1
    #         ###
    #         player_4_index = (player_my_index + 3) % 4
    #         player_4_suit_eliminated = player_constraints[player_4_index]['diamond_eliminated']
    #         player_4_spade_eliminated = player_constraints[player_4_index]['spade_eliminated']
    #         if player_4_suit_eliminated and not player_4_spade_eliminated:
    #             num_players_who_can_break_suit += 1
    #         ###
    #         if num_players_who_can_break_suit == 3:
    #             my_options = [card for card in cards if 'D' in card]
    #             if len(my_options) > 0:
    #                 options_rankings = [find_max_card([option]) for option in my_options]
    #                 min_option_rank = min(options_rankings)
    #                 best_index = options_rankings.index(min_option_rank)
    #                 best_option = my_options[best_index]
    #                 return jsonify({"value": best_option})

    if len(played) == 0 and (my_spade_count == len(cards)):
        # when I only have spades remaining
        # If I have the winning spade, I should play the winning spade
        if winning_spade in cards:
            return jsonify({"value": winning_spade})
        elif second_winning_spade in cards and my_spade_count >= 2:
            # if i have the next winning spade, I should preserve it for later
            my_spade_options_copy = my_spade_options[:]
            my_spade_options_copy.remove(second_winning_spade)
            # play the maximum spade value after removing the next winning spade
            options_rankings = [find_max_card([option]) for option in my_spade_options_copy]
            max_option_rank = max(options_rankings)
            best_index = options_rankings.index(max_option_rank)
            best_option = my_spade_options_copy[best_index]
            return jsonify({"value": best_option})
        else:
            # play the least card
            options_rankings = [find_max_card([option]) for option in my_spade_options]
            max_option_rank = min(options_rankings)
            best_index = options_rankings.index(max_option_rank)
            best_option = my_spade_options[best_index]
            return jsonify({"value": best_option})

    # if len(played) == 0 and others_remaining_spade_count == 0 and my_spade_count > 0:
    #     # check if i have any suit that is zeroed in others
    #     my_club_options = [card for card in cards if 'C' in card]
    #     my_heart_options = [card for card in cards if 'H' in card]
    #     my_diamond_options = [card for card in cards if 'D' in card]
    #     if others_remaining_club_count == 0:
    #         if len(my_club_options) > 0:
    #             ## play spade
    #             return jsonify({"value": my_spade_options[0]})
    #     if others_remaining_heart_count == 0:
    #         if len(my_heart_options) > 0:
    #             ## play spade
    #             return jsonify({"value": my_spade_options[0]})
    #     if others_remaining_diamond_count == 0:
    #         if len(my_diamond_options) > 0:
    #             ## play spade
    #             return jsonify({"value": my_spade_options[0]})

    if len(played) == 0 and others_remaining_spade_count == 1 and winning_spade in cards:
        return jsonify({"value": winning_spade})

    # Heuristic: 7
    if len(played) == 0 and others_remaining_spade_count == 1 and (my_spade_count >= others_remaining_spade_count):
        # TODO: in the future check the player who has that final spade by looking at the spade eliminated of other players
        # that way it should be able to pinpoint the player with spade 
        # next by comparing the number of points that player has acquired, decide whether to defeat his spade or leave his spade alone
        # if his won >= bid, leave him be
        # if his won < bid, defeat him
        if winning_spade in cards:
            return jsonify({"value": winning_spade})

    # Heuristic: 9
    if len(played) == 0 and others_remaining_spade_count == 2 and (my_spade_count >= others_remaining_spade_count):
        if winning_spade in cards and second_winning_spade in cards:
            return jsonify({"value": winning_spade})

    # Heuristic: 10
    if len(played) == 0 and others_remaining_spade_count == 3 and (my_spade_count >= others_remaining_spade_count):
        if winning_spade in cards and second_winning_spade in cards and third_winning_spade in cards:
            return jsonify({"value": winning_spade})

    # as long as i have more or equal to the spade count of all the others,
    # i should play spades
    if len(played) == 0 and (my_spade_count >= others_remaining_spade_count or my_spade_count >= 6):
        # if others_remaining_spade_count >= 2:
        #     if my_spade_count >= 7 or (my_spade_count >= 6 and others_remaining_spade_count <= 3) or (my_spade_count >= 5 and others_remaining_spade_count <= 2):
        #         if winning_spade in cards:
        #             return jsonify({"value": winning_spade})

        # make sure that there are 3 spades at least while playing
        if others_remaining_spade_count >= 3:
            # others should still have at least 3 spade cards
            # if i have winning spade, i should play it to force others to lose their spade card
            # but i should only do this when i still have a non-spade ace or a non-spade king to do this
            # otherwise i'm just wasting my spades unnecessarily
            non_spade_aces = [card for card in cards if 'S' not in card and '1' in card]
            ace_count = len(non_spade_aces)
            my_club_options = [card for card in cards if 'C' in card]
            my_heart_options = [card for card in cards if 'H' in card]
            my_diamond_options = [card for card in cards if 'D' in card]
            king_count = 0
            if 'KC' in my_club_options and len(my_club_options) >= 2:
                king_count += 1
            if 'KH' in my_heart_options and len(my_heart_options) >= 2:
                king_count += 1
            if 'KD' in my_diamond_options and len(my_diamond_options) >= 2:
                king_count += 1
            
            # check if the other players have 0 count suits
            # if found, play that suit
            zero_count_suit = None
            zero_count_found = False
            if others_remaining_club_count == 0:
                my_club_options = [card for card in cards if 'C' in card]
                if len(my_club_options) >= 1:
                    zero_count_found = True
                    zero_count_suit = my_club_options[-1]
            if others_remaining_heart_count == 0:
                my_heart_options = [card for card in cards if 'H' in card]
                if len(my_heart_options) >= 1:
                    zero_count_found = True
                    zero_count_suit = my_heart_options[-1]
            if others_remaining_diamond_count == 0:
                my_diamond_options = [card for card in cards if 'D' in card]
                if len(my_diamond_options) >= 1:
                    zero_count_found = True
                    zero_count_suit = my_diamond_options[-1]

            # check if winning non spade is present
            winning_non_spade_present = False
            if winning_club in cards or winning_heart in cards or winning_diamond in cards:
                winning_non_spade_present = True
            
            # if winning_spade in cards and ace_count > 0 and king_count > 0:
            # if (ace_count > 0 or zero_count_found or winning_non_spade_present):
            # if (ace_count > 0 or zero_count_found or winning_non_spade_present or second_winning_spade in cards):  # scored 4692 with this
            
            # ora ora attack rush
            spade_options = [card for card in cards if 'S' in card]
            if len(spade_options) >= 1:
                # if (winning_non_spade_present or my_spade_count >= 7 or (my_spade_count >= 5 and others_remaining_spade_count <= 3)):  # scored 5121
                if (winning_non_spade_present or my_spade_count >= 7 or (my_spade_count >= 6 and others_remaining_spade_count <= 3)):
                # if (winning_non_spade_present or my_spade_count >= 6 or (my_spade_count >= 5 and others_remaining_spade_count <= 3)):
                    # play spade
                    # return jsonify({"value": spade_options[-1]})  # only using this scored 4813
                    # if winning_spade in cards and second_winning_spade in cards:
                    if winning_spade in cards:
                        return jsonify({"value": winning_spade})
                    # elif second_winning_spade in cards:
                    #     # if i have the next winning spade, I should preserve it for later
                    #     my_spade_options.remove(second_winning_spade)
                    #     # play the maximum spade value after removing the next winning spade
                    #     options_rankings = [find_max_card([option]) for option in my_spade_options]
                    #     max_option_rank = max(options_rankings)
                    #     best_index = options_rankings.index(max_option_rank)
                    #     best_option = my_spade_options[best_index]
                    # if True and not spade_eliminated:
                    if True:
                        options_rankings = [find_max_card([option]) for option in my_spade_options]
                        min_option_rank = min(options_rankings)
                        best_index = options_rankings.index(min_option_rank)
                        best_option = my_spade_options[best_index]
                        return jsonify({"value": best_option})

            # ora ora attack # scored 4647
            # if winning_spade in cards and second_winning_spade in cards:
            #     return jsonify({"value": winning_spade})
            # elif second_winning_spade in cards:
            #     # if i have the next winning spade, I should preserve it for later
            #     my_spade_options.remove(second_winning_spade)
            #     # play the maximum spade value after removing the next winning spade
            #     options_rankings = [find_max_card([option]) for option in my_spade_options]
            #     max_option_rank = max(options_rankings)
            #     best_index = options_rankings.index(max_option_rank)
            #     best_option = my_spade_options[best_index]
            # else:
            #     options_rankings = [find_max_card([option]) for option in my_spade_options]
            #     min_option_rank = min(options_rankings)
            #     best_index = options_rankings.index(min_option_rank)
            #     best_option = my_spade_options[best_index]
            #     return jsonify({"value": best_option})

            # scored 4761 using this
            # if winning_spade in cards and (ace_count > 0 or zero_count_found or winning_non_spade_present or second_winning_spade in cards):
            #     return jsonify({"value": winning_spade})
            # elif second_winning_spade in cards and winning_spade not in cards:
            #     # if i have the next winning spade, I should preserve it for later
            #     my_spade_options.remove(second_winning_spade)
            #     # play the maximum spade value after removing the next winning spade
            #     options_rankings = [find_max_card([option]) for option in my_spade_options]
            #     max_option_rank = max(options_rankings)
            #     best_index = options_rankings.index(max_option_rank)
            #     best_option = my_spade_options[best_index]
            # else:
            #     options_rankings = [find_max_card([option]) for option in my_spade_options]
            #     min_option_rank = min(options_rankings)
            #     best_index = options_rankings.index(min_option_rank)
            #     best_option = my_spade_options[best_index]
            #     return jsonify({"value": best_option})

            # scored 4847 using this
            # if winning_spade in cards and (ace_count > 0 or zero_count_found or winning_non_spade_present or second_winning_spade in cards):
            #     if winning_spade in cards:
            #         return jsonify({"value": winning_spade})
            #     elif second_winning_spade in cards and winning_spade not in cards:
            #         # if i have the next winning spade, I should preserve it for later
            #         my_spade_options.remove(second_winning_spade)
            #         # play the maximum spade value after removing the next winning spade
            #         options_rankings = [find_max_card([option]) for option in my_spade_options]
            #         max_option_rank = max(options_rankings)
            #         best_index = options_rankings.index(max_option_rank)
            #         best_option = my_spade_options[best_index]
            #     else:
            #         options_rankings = [find_max_card([option]) for option in my_spade_options]
            #         min_option_rank = min(options_rankings)
            #         best_index = options_rankings.index(min_option_rank)
            #         best_option = my_spade_options[best_index]
            #         return jsonify({"value": best_option})


    # last end game
    # last 3 cards and I'm the first player
    # end game modification
    if len(cards) <= 3 and len(played) == 0:
        if others_remaining_spade_count >= 1:
            # others still have a spade card
            # if i have winning spade, i should play it to force others to lose their spade card
            # but i should only do this when i have a winning non-spade card as well
            # check if the other players have 0 count suits
            # if found, play that suit
            zero_count_suit = None
            zero_count_found = False
            if others_remaining_club_count == 0:
                my_club_options = [card for card in cards if 'C' in card]
                if len(my_club_options) >= 1:
                    zero_count_found = True
                    zero_count_suit = my_club_options[-1]
            if others_remaining_heart_count == 0:
                my_heart_options = [card for card in cards if 'H' in card]
                if len(my_heart_options) >= 1:
                    zero_count_found = True
                    zero_count_suit = my_heart_options[-1]
            if others_remaining_diamond_count == 0:
                my_diamond_options = [card for card in cards if 'D' in card]
                if len(my_diamond_options) >= 1:
                    zero_count_found = True
                    zero_count_suit = my_diamond_options[-1]

            # check if winning non spade is present
            winning_non_spade_present = False
            if winning_club in cards or winning_heart in cards or winning_diamond in cards:
                winning_non_spade_present = True
            
            # if winning_spade in cards and ace_count > 0 and king_count > 0:
            # if (ace_count > 0 or zero_count_found or winning_non_spade_present):
            if winning_spade in cards and (zero_count_found or winning_non_spade_present):  # scored 4947 using this
            # if winning_spade in cards and (zero_count_found or winning_non_spade_present or second_winning_spade in cards):  # scored 4737 using this
                return jsonify({"value": winning_spade})
            # if winning_spade in cards: # scored 4803 when using this
                # return jsonify({"value": winning_spade})
            else:
                # play lowest face card
                # means someone else has the winning spade card, so I'll definitely lose if i play spade
                # So to save my spade I should play a non-spade card
                # First try to play a non-spade card that has not been eliminated
                if winning_club in cards and others_remaining_club_count >= 4:
                    return jsonify({"value": winning_club})
                if winning_heart in cards and others_remaining_heart_count >= 4:
                    return jsonify({"value": winning_heart})
                if winning_diamond in cards and others_remaining_diamond_count >= 4:
                    return jsonify({"value": winning_diamond})

                if winning_club in cards and not club_eliminated:
                    return jsonify({"value": winning_club})
                if winning_heart in cards and not heart_eliminated:
                    return jsonify({"value": winning_heart})
                if winning_diamond in cards and not diamond_eliminated:
                    return jsonify({"value": winning_diamond})

                # if all suits have been eliminated, play the least face card
                non_spade_options = [card for card in cards if 'S' not in card]
                if len(non_spade_options) >= 1:
                    options_rankings = [find_max_card([option]) for option in non_spade_options]
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = non_spade_options[best_index]
                    return jsonify({"value": best_option})
                else:
                    # i don't have any non-spade options, so i only have spade options
                    # since i don't have the winning spade
                    # i should play the least spade i have
                    spade_options = [card for card in cards if 'S' in card]
                    options_rankings = [find_max_card([option]) for option in spade_options]
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = spade_options[best_index]
                    return jsonify({"value": best_option})

    # always check if others spade count has fallen to 0
    if len(cards) <= 3 and len(played) == 0:
        my_spade_options = [card for card in cards if 'S' in card]
        if others_remaining_spade_count == 0 and len(my_spade_options) >= 1:
            return jsonify({"value": my_spade_options[-1]})
        if others_remaining_spade_count == 0:
            if winning_club in cards:
                return jsonify({"value": winning_club})
            if winning_heart in cards:
                return jsonify({"value": winning_heart})
            if winning_diamond in cards:
                return jsonify({"value": winning_diamond})

            # check if the other players have 0 count suits
            # if found, play that suit
            if others_remaining_club_count == 0:
                # play least club
                my_club_options = [card for card in cards if 'C' in card]
                if len(my_club_options) >= 1:
                    return jsonify({"value": my_club_options[-1]})
            if others_remaining_heart_count == 0:
                # play least heart
                my_heart_options = [card for card in cards if 'H' in card]
                if len(my_heart_options) >= 1:
                    return jsonify({"value": my_heart_options[-1]})
            if others_remaining_diamond_count == 0:
                # play least diamond
                my_diamond_options = [card for card in cards if 'D' in card]
                if len(my_diamond_options) >= 1:
                    return jsonify({"value": my_diamond_options[-1]})

            # when i don't have any spade and others also don't have any spade
            # it means that noone can play spade card
            # but since the winning suit was not returned ahead,
            # it means that someone else has winning card,
            # so try to find a card that might become the next winning card
            my_club_options = [card for card in cards if 'C' in card]
            my_heart_options = [card for card in cards if 'H' in card]
            my_diamond_options = [card for card in cards if 'D' in card]
            if second_winning_club in cards and len(my_club_options) >= 2:
                my_club_options.remove(second_winning_club)
                return jsonify({"value": my_club_options[0]})
            if second_winning_heart in cards and len(my_heart_options) >= 2:
                my_heart_options.remove(second_winning_heart)
                return jsonify({"value": my_heart_options[0]})
            if second_winning_diamond in cards and len(my_diamond_options) >= 2:
                my_diamond_options.remove(second_winning_diamond)
                return jsonify({"value": my_diamond_options[0]})
            # so i should play the least card i have
            options_rankings = [find_max_card([option]) for option in cards]
            min_option_rank = min(options_rankings)
            best_index = options_rankings.index(min_option_rank)
            best_option = cards[best_index]
            return jsonify({"value": best_option})


    # my_spade_options = [card for card in cards if 'S' in card]
    # if False and len(played) == 0 and len(my_spade_options) == 1 and others_remaining_spade_count >= 2 and others_remaining_spade_count <= 7 and my_spade_options[0] != winning_spade:
    #     if winning_club in cards:
    #         return jsonify({"value": my_spade_options[0]})
    #     if winning_heart in cards:
    #         return jsonify({"value": my_spade_options[0]})
    #     if winning_diamond in cards:
    #         return jsonify({"value": my_spade_options[0]})

    # If the remaining spade count for other players has dropped to 0 and it's my first turn,
    # play a card whose suit is not present for other players
    # if len(played) == 0 and others_remaining_spade_count == 0:
    #     # i should play a non-spade card that is not present in any of my competitors
    #     # i.e. play a non-spade card that has zero value for others_remaining_suit
    #     if others_remaining_club_count == 0:
    #         # play club
    #         my_clubs = [card for card in cards if 'C' in card]
    #         if len(my_clubs) >= 1:
    #             return jsonify({"value": my_clubs[0]})
    #     if others_remaining_heart_count == 0:
    #         # play heart
    #         my_hearts = [card for card in cards if 'H' in card]
    #         if len(my_hearts) >= 1:
    #             return jsonify({"value": my_hearts[0]})
    #     if others_remaining_diamond_count == 0:
    #         # play diamond
    #         my_diamonds = [card for card in cards if 'D' in card]
    #         if len(my_diamonds) >= 1:
    #             return jsonify({"value": my_diamonds[0]})
    #     # non-spade card not found
    #     # so throw a spade card if it is present in my card
    #     my_spades = [card for card in cards if 'S' in card]
    #     if len(my_spades) >= 1:
    #         return jsonify({"value": my_spades[0]})

    # If the remaining spade count for other players is less than or equal to 4, 
    # and it's my first turn
    # if len(played) == 0 and others_remaining_spade_count <= 6 and others_remaining_spade_count >= 3:
    #     # if I have the winning spade card
    #     # I should play the winning spade card
    #     if winning_spade in cards:
    #         return jsonify({"value": winning_spade})

    aim_for_zero_suit = False
    # my_spade_count
    # scored 5030 with below certain spades
    # certain_spades = [spade for spade in my_spade_options if spade == winning_spade or spade == second_winning_spade or spade == third_winning_spade]

    # scored 5092
    certain_spades = [spade for spade in my_spade_options if spade == winning_spade or spade == second_winning_spade]

    # new certain spades finder
    # if winning_spade in my_spade_options and second_winning_spade in my_spade_options and third_winning_spade in my_spade_options:
    #     certain_spades = [winning_spade, second_winning_spade, third_winning_spade]
    # elif winning_spade in my_spade_options and second_winning_spade in my_spade_options:
    #     certain_spades = [winning_spade, second_winning_spade]
    # elif winning_spade in my_spade_options and third_winning_spade in my_spade_options and my_spade_count >= 3:
    #     certain_spades = [winning_spade, third_winning_spade]
    # elif winning_spade in my_spade_options:
    #     certain_spades = [winning_spade]
    # elif second_winning_spade in my_spade_options and third_winning_spade in my_spade_options:
    #     certain_spades = [second_winning_spade]
    # else:
    #     certain_spades = []  # no certain spades

    certain_spade_count = len(certain_spades)
    if my_spade_count > certain_spade_count:
        # there are extra uncertain spades
        # so need to aim for zero suit
        aim_for_zero_suit = True
    else:
        aim_for_zero_suit = False

    # aim_for_zero_suit = True
    # if my_spade_count == 3 and winning_spade in my_spade_options and second_winning_spade in my_spade_options and third_winning_spade in my_spade_options:
    #     aim_for_zero_suit = False
    # elif my_spade_count == 2 and winning_spade in my_spade_options and second_winning_spade in my_spade_options:
    #     aim_for_zero_suit = False
    # elif my_spade_count == 1 and winning_spade in my_spade_options:
    #     aim_for_zero_suit = False

    # when I'm the first player, I can choose any suit
    # if len(cards) >= 4 and len(played) == 0:
    if len(cards) >= 4 and len(played) == 0:
        if winning_club in cards and others_remaining_club_count >= 5 and not club_eliminated:
            return jsonify({"value": winning_club})
        if winning_heart in cards and others_remaining_heart_count >= 5 and not heart_eliminated:
            return jsonify({"value": winning_heart})
        if winning_diamond in cards and others_remaining_diamond_count >= 5 and not diamond_eliminated:
            return jsonify({"value": winning_diamond})
        
        # I should throw a 1 remaining suit if I don't have winning card,
        # but have enough spades in my cards
        spades_in_my_card = [card for card in cards if 'S' in card]
        my_spade_count = len(spades_in_my_card)
        my_club_options = [card for card in cards if 'C' in card]
        my_heart_options = [card for card in cards if 'H' in card]
        my_diamond_options = [card for card in cards if 'D' in card]

        # if len(spades_in_my_card) >= 1:  # 1 is better than 2
        if aim_for_zero_suit == True:
            
            if len(my_club_options) == 1:
                my_club_option = my_club_options[0]
                # before playing single suit card, check if it is a high value card
                # don't play high value card unnecessarily
                # better to save the high value card for later
                # only play the single remaining card if it is not the winning suit card
                if my_club_option != winning_club and aim_for_zero_suit:
                    return jsonify({"value": my_club_option})
                # if my_club_option[0] in ('2','3','4','5','6') and (club_eliminated):
                #     ## eliminate others cards
                #     return jsonify({"value": my_club_option})
            if len(my_heart_options) == 1:
                my_heart_option = my_heart_options[0]
                if my_heart_option != winning_heart and aim_for_zero_suit:
                    return jsonify({"value": my_heart_option})
                # if my_heart_option[0] in ('2','3','4','5','6') and (heart_eliminated):
                #     return jsonify({"value": my_heart_option})
            if len(my_diamond_options) == 1:
                my_diamond_option = my_diamond_options[0]
                if my_diamond_option != winning_diamond and aim_for_zero_suit:
                    return jsonify({"value": my_diamond_option})
                # if my_diamond_option[0] in ('2','3','4','5','6') and (diamond_eliminated):
                #     return jsonify({"value": my_diamond_option})
            # handle suit case == 2, by selecting least suit
            if len(my_club_options) == 2 and not club_eliminated:
                first_club = my_club_options[0]
                second_club = my_club_options[1]
                if find_max_card([first_club]) < find_max_card([second_club]):
                    best_option = first_club
                else:
                    best_option = second_club
                if best_option != second_winning_club and aim_for_zero_suit:
                    return jsonify({"value": best_option})
            if len(my_heart_options) == 2 and not heart_eliminated:
                first_heart = my_heart_options[0]
                second_heart = my_heart_options[1]
                if find_max_card([first_heart]) < find_max_card([second_heart]):
                    best_option = first_heart
                else:
                    best_option = second_heart
                if best_option != second_winning_heart and aim_for_zero_suit:
                    return jsonify({"value": best_option})
            if len(my_diamond_options) == 2 and not diamond_eliminated:
                first_diamond = my_diamond_options[0]
                second_diamond = my_diamond_options[1]
                if find_max_card([first_diamond]) < find_max_card([second_diamond]):
                    best_option = first_diamond
                else:
                    best_option = second_diamond
                if best_option != second_winning_diamond and aim_for_zero_suit:
                    return jsonify({"value": best_option})

        # Heuristic: Save Next Winning Card
        # handle suit case >= 3, by selecting 2nd highest suit
        # in case i have the next winning card
        if winning_club not in cards and len(my_club_options) >= 3 and others_remaining_club_count >= 6:
            next_winning_club = second_winning_club
            if next_winning_club in cards:
                # play highest club that is not the next winning card
                # this way the winning club will go away in this round
                # and I'll have the winning club in the next round
                my_club_options.remove(next_winning_club)
                options_rankings = [find_max_card([option]) for option in my_club_options]
                max_option_rank = max(options_rankings)
                best_index = options_rankings.index(max_option_rank)
                best_option = my_club_options[best_index]
                return jsonify({"value": best_option})
        if winning_heart not in cards and len(my_heart_options) >= 3 and others_remaining_heart_count >= 6:
            next_winning_heart = second_winning_heart
            if next_winning_heart in cards:
                my_heart_options.remove(next_winning_heart)
                options_rankings = [find_max_card([option]) for option in my_heart_options]
                max_option_rank = max(options_rankings)
                best_index = options_rankings.index(max_option_rank)
                best_option = my_heart_options[best_index]
                return jsonify({"value": best_option})
        if winning_diamond not in cards and len(my_diamond_options) >= 3 and others_remaining_diamond_count >= 6:
            next_winning_diamond = second_winning_diamond
            if next_winning_diamond in cards:
                my_diamond_options.remove(next_winning_diamond)
                options_rankings = [find_max_card([option]) for option in my_diamond_options]
                max_option_rank = max(options_rankings)
                best_index = options_rankings.index(max_option_rank)
                best_option = my_diamond_options[best_index]
                return jsonify({"value": best_option})

        # case 2
        if winning_club not in cards and len(my_club_options) >= 2 and others_remaining_club_count >= 7:
            next_winning_club = second_winning_club
            if next_winning_club in cards:
                # play highest club that is not the next winning card
                # this way the winning club will go away in this round
                # and I'll have the winning club in the next round
                my_club_options.remove(next_winning_club)
                options_rankings = [find_max_card([option]) for option in my_club_options]
                max_option_rank = max(options_rankings)
                best_index = options_rankings.index(max_option_rank)
                best_option = my_club_options[best_index]
                return jsonify({"value": best_option})
        if winning_heart not in cards and len(my_heart_options) >= 2 and others_remaining_heart_count >= 7:
            next_winning_heart = second_winning_heart
            if next_winning_heart in cards:
                my_heart_options.remove(next_winning_heart)
                options_rankings = [find_max_card([option]) for option in my_heart_options]
                max_option_rank = max(options_rankings)
                best_index = options_rankings.index(max_option_rank)
                best_option = my_heart_options[best_index]
                return jsonify({"value": best_option})
        if winning_diamond not in cards and len(my_diamond_options) >= 2 and others_remaining_diamond_count >= 7:
            next_winning_diamond = second_winning_diamond
            if next_winning_diamond in cards:
                my_diamond_options.remove(next_winning_diamond)
                options_rankings = [find_max_card([option]) for option in my_diamond_options]
                max_option_rank = max(options_rankings)
                best_index = options_rankings.index(max_option_rank)
                best_option = my_diamond_options[best_index]
                return jsonify({"value": best_option})

        # case 3 - play least card of max count that is not eliminated
        if winning_club not in cards and len(my_club_options) >= 3 and others_remaining_club_count >= 6 and not club_eliminated:
            options_rankings = [find_max_card([option]) for option in my_club_options]
            max_option_rank = min(options_rankings)
            best_index = options_rankings.index(max_option_rank)
            best_option = my_club_options[best_index]
            return jsonify({"value": best_option})
        if winning_heart not in cards and len(my_heart_options) >= 3 and others_remaining_heart_count >= 6 and not heart_eliminated:
            options_rankings = [find_max_card([option]) for option in my_heart_options]
            max_option_rank = min(options_rankings)
            best_index = options_rankings.index(max_option_rank)
            best_option = my_heart_options[best_index]
            return jsonify({"value": best_option})
        if winning_diamond not in cards and len(my_diamond_options) >= 3 and others_remaining_diamond_count >= 6 and not diamond_eliminated:
            options_rankings = [find_max_card([option]) for option in my_diamond_options]
            max_option_rank = min(options_rankings)
            best_index = options_rankings.index(max_option_rank)
            best_option = my_diamond_options[best_index]
            return jsonify({"value": best_option})

        # case 3 - play least card of max count. no need to consider if suit is eiminated or not
        if winning_club not in cards and len(my_club_options) >= 3 and others_remaining_club_count >= 6:
            options_rankings = [find_max_card([option]) for option in my_club_options]
            max_option_rank = min(options_rankings)
            best_index = options_rankings.index(max_option_rank)
            best_option = my_club_options[best_index]
            return jsonify({"value": best_option})
        if winning_heart not in cards and len(my_heart_options) >= 3 and others_remaining_heart_count >= 6:
            options_rankings = [find_max_card([option]) for option in my_heart_options]
            max_option_rank = min(options_rankings)
            best_index = options_rankings.index(max_option_rank)
            best_option = my_heart_options[best_index]
            return jsonify({"value": best_option})
        if winning_diamond not in cards and len(my_diamond_options) >= 3 and others_remaining_diamond_count >= 6:
            options_rankings = [find_max_card([option]) for option in my_diamond_options]
            max_option_rank = min(options_rankings)
            best_index = options_rankings.index(max_option_rank)
            best_option = my_diamond_options[best_index]
            return jsonify({"value": best_option})

    # Heuristic 1

    # 2 player played for S
    if len(played) == 2 and 'S' in played[0]:
        max_spade_ranking = find_max_card(played)
        my_spade_options = [card for card in cards if 'S' in card and find_max_card([card]) > max_spade_ranking]
        if len(my_spade_options) >= 2 and winning_spade in cards:
            # check 4th player spade constraints
            # find next player
            player_4_index = (player_my_index + 1) % 4
            player_4_spade_eliminated = player_constraints[player_4_index]['spade_eliminated']
            if player_4_spade_eliminated:
                # can play least number spade
                # my_spade_options.remove(winning_spade)
                options_rankings = [find_max_card([option]) for option in my_spade_options]
                max_option_rank = min(options_rankings)
                best_index = options_rankings.index(max_option_rank)
                best_option = my_spade_options[best_index]
                return jsonify({"value": best_option})
            else:
                # since spade for 4th not eliminated, so must play winning spade
                return jsonify({"value": winning_spade})
        if len(my_spade_options) >= 2 and winning_spade not in cards and second_winning_spade in cards:
            # check 4th player spade constraints
            # find next player
            player_4_index = (player_my_index + 1) % 4
            player_4_spade_eliminated = player_constraints[player_4_index]['spade_eliminated']
            if player_4_spade_eliminated:
                # can play least number spade
                # my_spade_options.remove(winning_spade)
                options_rankings = [find_max_card([option]) for option in my_spade_options]
                max_option_rank = min(options_rankings)
                best_index = options_rankings.index(max_option_rank)
                best_option = my_spade_options[best_index]
                return jsonify({"value": best_option})
            if not player_4_spade_eliminated:
                # depends on how high card 4th player has
                # if 4th player has winning_spade, I should play least spade card
                # but winning spade can be with the 1st and 2nd player as well,
                # so maybe playing higher card here might be a good decision
                # since next_winning_spade cannot beat winning spade anyway
                # this might be the only chance where KS has a chance to beat 1S by avoiding it entirely
                # with a 2/3 chance of winning
                return jsonify({"value": second_winning_spade})

    # 2 player played for C
    if len(played) == 2 and 'C' in played[0] and 'C' in played[1]:
        max_club_ranking = find_max_card(played)
        my_club_options = [card for card in cards if 'C' in card and find_max_card([card]) > max_club_ranking]
        if len(my_club_options) >= 2 and winning_club in cards:
            # check 4th player spade constraints
            # find next player
            player_4_index = (player_my_index + 1) % 4
            player_4_club_eliminated = player_constraints[player_4_index]['club_eliminated']
            player_4_spade_eliminated = player_constraints[player_4_index]['spade_eliminated']
            if player_4_club_eliminated and not player_4_spade_eliminated:
                # there is a possibility player 4 can cut the club
                # so play the least ranking club
                options_rankings = [find_max_card([option]) for option in my_club_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = my_club_options[best_index]
                return jsonify({"value": best_option})
            elif player_4_spade_eliminated:
                # player 4 cannot cut club, so it will definitely have to play club if it has it
                # so i'll play my winning club here in case a second winning club is present with player 4
                return jsonify({"value": winning_club})

    # 2 player played for H
    if len(played) == 2 and 'H' in played[0] and 'H' in played[1]:
        max_heart_ranking = find_max_card(played)
        my_heart_options = [card for card in cards if 'H' in card and find_max_card([card]) > max_heart_ranking]
        if len(my_heart_options) >= 2 and winning_heart in cards:
            player_4_index = (player_my_index + 1) % 4
            player_4_heart_eliminated = player_constraints[player_4_index]['heart_eliminated']
            player_4_spade_eliminated = player_constraints[player_4_index]['spade_eliminated']
            if player_4_heart_eliminated and not player_4_spade_eliminated:
                options_rankings = [find_max_card([option]) for option in my_heart_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = my_heart_options[best_index]
                return jsonify({"value": best_option})
            elif player_4_spade_eliminated:
                return jsonify({"value": winning_heart})

    # 2 player played for D
    if len(played) == 2 and 'D' in played[0] and 'D' in played[1]:
        max_diamond_ranking = find_max_card(played)
        my_diamond_options = [card for card in cards if 'D' in card and find_max_card([card]) > max_diamond_ranking]
        if len(my_diamond_options) >= 2 and winning_diamond in cards:
            player_4_index = (player_my_index + 1) % 4
            player_4_diamond_eliminated = player_constraints[player_4_index]['diamond_eliminated']
            player_4_spade_eliminated = player_constraints[player_4_index]['spade_eliminated']
            if player_4_diamond_eliminated and not player_4_spade_eliminated:
                options_rankings = [find_max_card([option]) for option in my_diamond_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = my_diamond_options[best_index]
                return jsonify({"value": best_option})
            elif player_4_spade_eliminated:
                return jsonify({"value": winning_diamond})

    # 1 player played for S
    if len(played) == 1 and 'S' in played[0]:
        max_ranking = find_max_card(played)
        my_options = [card for card in cards if 'S' in card and find_max_card([card]) > max_ranking]
        if len(my_options) >= 2 and winning_spade in cards:
            ###
            player_3_index = (player_my_index + 1) % 4
            player_3_spade_eliminated = player_constraints[player_3_index]['spade_eliminated']
            ###
            player_4_index = (player_my_index + 2) % 4
            player_4_spade_eliminated = player_constraints[player_4_index]['spade_eliminated']
            ###
            if player_3_spade_eliminated and player_4_spade_eliminated:
                options_rankings = [find_max_card([option]) for option in my_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = my_options[best_index]
                return jsonify({"value": best_option})
            else:
                return jsonify({"value": winning_spade})

    # 1 player played for C
    if len(played) == 1 and 'C' in played[0]:
        max_ranking = find_max_card(played)
        my_options = [card for card in cards if 'C' in card and find_max_card([card]) > max_ranking]
        if len(my_options) >= 2:
            ###
            player_3_index = (player_my_index + 1) % 4
            player_3_club_eliminated = player_constraints[player_3_index]['club_eliminated']
            ###
            player_4_index = (player_my_index + 2) % 4
            player_4_club_eliminated = player_constraints[player_4_index]['club_eliminated']
            ###
            if player_3_club_eliminated and player_4_club_eliminated:
                options_rankings = [find_max_card([option]) for option in my_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = my_options[best_index]
                return jsonify({"value": best_option})

    # 1 player played for H
    if len(played) == 1 and 'H' in played[0]:
        max_ranking = find_max_card(played)
        my_options = [card for card in cards if 'H' in card and find_max_card([card]) > max_ranking]
        if len(my_options) >= 2:
            ###
            player_3_index = (player_my_index + 1) % 4
            player_3_heart_eliminated = player_constraints[player_3_index]['heart_eliminated']
            ###
            player_4_index = (player_my_index + 2) % 4
            player_4_heart_eliminated = player_constraints[player_4_index]['heart_eliminated']
            ###
            if player_3_heart_eliminated and player_4_heart_eliminated:
                options_rankings = [find_max_card([option]) for option in my_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = my_options[best_index]
                return jsonify({"value": best_option})

    # 1 player played for D
    if len(played) == 1 and 'D' in played[0]:
        max_ranking = find_max_card(played)
        my_options = [card for card in cards if 'D' in card and find_max_card([card]) > max_ranking]
        if len(my_options) >= 2:
            ###
            player_3_index = (player_my_index + 1) % 4
            player_3_diamond_eliminated = player_constraints[player_3_index]['diamond_eliminated']
            ###
            player_4_index = (player_my_index + 2) % 4
            player_4_diamond_eliminated = player_constraints[player_4_index]['diamond_eliminated']
            ###
            if player_3_diamond_eliminated and player_4_diamond_eliminated:
                options_rankings = [find_max_card([option]) for option in my_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = my_options[best_index]
                return jsonify({"value": best_option})


    # when I'm the not the first player, I have to choose the given suit
    spades_in_played = [card for card in played if 'S' in played]
    if len(spades_in_played) == 0 and len(played) >= 1 and len(played) != 3:
        # no spades in played means all played cards are of same suit as first,
        # so can decrease remaining count of that suit by the number of played
        if suit == 'C':
            others_remaining_club_count -= len(played)
        elif suit == 'H':
            others_remaining_heart_count -= len(played)
        elif suit == 'D':
            others_remaining_diamond_count -= len(played)
        if winning_club in cards and suit in winning_club and others_remaining_club_count >= 2 and not club_eliminated:
            return jsonify({"value": winning_club})
        if winning_heart in cards and suit in winning_heart and others_remaining_heart_count >= 2 and not heart_eliminated:
            return jsonify({"value": winning_heart})
        if winning_diamond in cards and suit in winning_diamond and others_remaining_diamond_count >= 2 and not diamond_eliminated:
            return jsonify({"value": winning_diamond})

    # find max_other_card played
    if len(played) > 0:
        new_played = [card for card in played if suit in card[0:2]]
        max_played_card = int(find_max_card(new_played))
    else:
        max_played_card = 0

    # check if suit played is present in current cards
    options = [card for card in cards if suit in card]

    if len(options) == 0:
        # include spade if no suit found
        options = [card for card in cards if 'S' in card]
        # reset max_played_card rank
        # but this time use the played cards that are only spade
        new_played = [card for card in played if 'S' in card[0:2]]
        max_played_card = int(find_max_card(new_played))

    if len(options) == 0:
        # if options is still 0, include all cards as options
        options = [card for card in cards]
        # reset max_played_card rank
        # but this time use the least ranked card by setting max_played_card to 0
        max_played_card = 0

    # use options based on whether you can win or not
    # case when 3 bots have played i.e. len(played) == 3
    options_greater_than_max_played_card = [option for option in options if find_max_card([option]) > max_played_card]
    # make sure the options greater than max played card are actually in the suit or have spades
    options_greater_than_max_played_card = [option for option in options_greater_than_max_played_card if suit in option or 'S' in option]
    
    options_less_than_max_played_card = [option for option in options if find_max_card([option]) < max_played_card]
    # make sure the options less than max played card are actually in the suit or have spades
    options_less_than_max_played_card = [option for option in options_less_than_max_played_card if suit in option or 'S' in option]


    ## todo: 1
    ## add suit distribution computation based on history
    ## so that you only send low number cards when the suit is low in probability
    ## and you send high number cards when the suit is high in probability
    ## high in probability is at the beginning to middle of the game


    ## todo: 2
    ## add current winning_suit for diamonds, hearts, clubs, and spade
    ## this is to ensure a win whenever you have the winning suit and play it as quickly as possible
    ## as there is 100% chance of winning if current winning suit is for spades
    ## high to low probability for current winning suits on diamonds, hearts, and clubs
    ## p(diamonds) = 1 - seen_diamonds, p(hearts) = 1 - seen_hearts, p(clubs) = 1 - seen_clubs
    
    if len(options_greater_than_max_played_card) > 0:
        # greater than 0 means that I have a better hand than the cards others played
        # so I should choose the least higher card to win
        # select best option
        best_index = 0
        options_rankings = [find_max_card([option]) for option in options_greater_than_max_played_card]
        min_option_rank = min(options_rankings)
        best_index = options_rankings.index(min_option_rank)
        best_option = options_greater_than_max_played_card[best_index]

        # Don't waste high ranking non-spade cards if one player has already played a spade
        # e.g. if 9D is the first card and 2nd card is 2S, if i have ['TD', '5D'] I shouldn't play TD
        # as i would lose to 2S, so instead I should play 5D here
        new_played = [card for card in played if 'S' in card[0:2]]
        if len(new_played) >= 1 and 'S' not in best_option and suit != 'S':
            new_options = [card for card in cards if suit in card]
            if len(new_options) >= 1:
                # confirm that i actually have a non-spade card
                # only choose new best option if my non-spade card count is greater than 0
                options_rankings = [find_max_card([option]) for option in new_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = new_options[best_index]

                return jsonify({"value": best_option})
            
        # special case when i have winning spade and third winning spade and someone else has second winning spade
        # if len(new_played) >= 1 and 'S' in best_option and best_option == third_winning_spade and winning_spade in cards and second_winning_spade not in history_cards and others_remaining_spade_count <= 2 and not spade_eliminated:
            # # play winning spade
            # return jsonify({"value": winning_spade})
        if len(new_played) >= 1 and 'S' in best_option and best_option == third_winning_spade and winning_spade in cards and second_winning_spade not in history_cards and others_remaining_spade_count <= 1:
            # play winning spade
            return jsonify({"value": winning_spade})

    elif len(options_less_than_max_played_card) > 0:
        # less than 0 options means that I don't have a better hand than the cards others played
        # so I should chooose a valid option that is of the least ranking in my available option

        # same logic as above except that rankings are chosen less than the max_played_card
        best_index = 0
        options_rankings = [find_max_card([option]) for option in options_less_than_max_played_card]
        min_option_rank = min(options_rankings)
        best_index = options_rankings.index(min_option_rank)
        best_option = options_less_than_max_played_card[best_index]

        # Don't throw away spade needlessly
        # When the first player played a non-spade card and someone else played a spade card
        # If I don't have that first player played suit and also dont' have a spade card that can with the 2nd, 3rd players spade card
        # I don't have to play spade and instead can play any other card
        new_played = [card for card in played if 'S' in card[0:2]]
        if len(new_played) >= 1 and 'S' in best_option and suit != 'S':

            # i'm already checking for options with spades less than 2nd, 3rd player
            # so my current spade card will not win,
            # so i have to play a non-spade card of least rank
            new_options = [card for card in cards if 'S' not in card]
            if len(new_options) >= 1:
                # confirm that i actually have a non-spade card
                # only choose new best option if my non-spade card count is greater than 0
                options_rankings = [find_max_card([option]) for option in new_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = new_options[best_index]

                return jsonify({"value": best_option})

    else:
        # use the least number card if remaining card count is the same for all clubs, heart and heart
        to_play_suit = None
        play_highest_remaining_suit = True
        max_remaining_suit_found = False
        if play_highest_remaining_suit == True:
            # if no options, use the least value card of the most remaining suit
            most_remaining_suit = max([others_remaining_club_count, others_remaining_heart_count, others_remaining_diamond_count])
            # my_current_space_count = find_count_of_spades(cards)
            if most_remaining_suit == others_remaining_club_count:
                to_play_suit = 'C'
                club_options = [option for option in options if 'C' in option]
                if len(club_options) >= 1 and not club_eliminated:
                    max_remaining_suit_found = True  # set max remaining suit found to True
                    options_rankings = [find_max_card([option]) for option in club_options]
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = club_options[best_index]
                else:
                    # no club found, so choose the next highest suit
                    most_remaining_suit = max([others_remaining_heart_count, others_remaining_diamond_count])
            if most_remaining_suit == others_remaining_heart_count:
                to_play_suit == 'H'
                heart_options = [option for option in options if 'H' in option]
                if len(heart_options) >= 1 and not heart_eliminated:
                    max_remaining_suit_found = True  # set max remaining suit found to True
                    options_rankings = [find_max_card([option]) for option in heart_options]
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = heart_options[best_index]
                else:
                    # no club or heart found, so choose the next highest suit
                    most_remaining_suit = others_remaining_diamond_count
            if most_remaining_suit == others_remaining_diamond_count:
                to_play_suit == 'D'
                diamond_options = [option for option in options if 'D' in option]
                if len(diamond_options) >= 1 and not diamond_eliminated:
                    options_rankings = [find_max_card([option]) for option in diamond_options]
                    max_remaining_suit_found = True  # set max remaining suit found to True
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = diamond_options[best_index]
                else:
                    # no club or heart or diamond found, so set max remaining suit found to False
                    max_remaining_suit_found = False

        if max_remaining_suit_found == False:
            non_spade_options = [option for option in options if 'S' not in option]
            if club_eliminated:
                non_spade_options = [option for option in non_spade_options if 'C' not in option]
            if heart_eliminated:
                non_spade_options = [option for option in non_spade_options if 'H' not in option]
            if diamond_eliminated:
                non_spade_options = [option for option in non_spade_options if 'D' not in option]
            if len(non_spade_options) >= 1:
                options_rankings = [find_max_card([option]) for option in non_spade_options]
                min_option_rank = min(options_rankings)
                best_index = options_rankings.index(min_option_rank)
                best_option = non_spade_options[best_index]
            else:
                # no non-spade found
                to_play_suit = 'S'

                spade_options = [option for option in options if 'S' in option]
                if len(spade_options) >= 1:
                    options_rankings = [find_max_card([option]) for option in spade_options]
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = spade_options[best_index]

                else:
                    # play the least card
                    options = [option for option in options]
                    options_rankings = [find_max_card([option]) for option in options]
                    min_option_rank = min(options_rankings)
                    best_index = options_rankings.index(min_option_rank)
                    best_option = options[best_index]

    return jsonify({"value": best_option})