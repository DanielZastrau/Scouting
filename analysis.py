import argparse
import os
import json

from data_classes.lineup import Lineup

from data_classes.serve_types import ServeTypes
from data_classes.serves import Serves

from data_classes.receptions import Receptions

from data_classes.sets import Sets

from data_classes.hits import Hits


##############################    Main    ##############################

def main(filename: str):

    analysis_dir_path = os.path.join(os.getcwd(), 'analysis')


    # get the scouting file    
    with open(os.path.join(os.getcwd(), 'scouting', filename), 'r', encoding='utf-8') as file:
        data = file.read()


    # filter out irrelevant lines
    data = data.split('\n')
    data = [line for line in data if (not line.startswith('#')) and (len(line) != 0)]


    # remove serve pos line and serve type line
    data = [line for line in data if not line.startswith('>')]


    # define information dataclasses to be filled
    serves = Serves()

    receptions = Receptions()
    
    sets_c1 = Sets(complex=1)
    sets_c2 = Sets(complex=2)
    sets_special_case1 = Sets(complex=3)

    hits = Hits()

    c = 1
    amount_of_serves = 0
    for i, line in enumerate(data):
        print(f'set: {i + 1}')


        # index gives back the first occurrence
        first_occurence = line.index('>')
        lineup_, actions = line[:first_occurence], line[first_occurence + 1:]


        # Determine lineup
        lineup = Lineup()
        lineup.determine_lineup(lineup_)


        # currently want to fill serving dicts
        mode = 'looking for action'
        team_mode = 'none'
        

        # 1 for reception, 2 for defense,
        # only interesting for set distribution, therefore we only care if K1 or K2
        complex = 0    


        # pauses vanish
        # breaks become empty strings ''
        actions = actions.split(' ')
        for ii, action in enumerate(actions):
            
            print(mode, f'action {ii}', action)


            if action == '':
                mode = 'looking for action'


            # indicates a substituion
            elif action.startswith('<'):
                lineup.modify_lineup(substitution=action)


            # then it should only find . or ..
            # also the only mode in which the team mode can change and therefore the rotation
            elif mode == 'looking for action':    
                
                assert action in ['.', '..'], f'action {action} not eligible. Only serve or reception can be expected here.'

                # .  --  indicates a serve
                if action == '.':
                    mode = 'looking for type of serve next'

                    if team_mode == 'receiving':
                        lineup.rotate_lineup()

                    team_mode = 'serving'

                    serves_player = lineup.get_server()
                    serves_type = 0
                    serves_zone = 0
                    serves_outcome = 0

                    # to reiterate  --  1 for K1,  2 for K2
                    complex = 2

                # ..  --  indicates a reception
                elif action == '..':

                    mode = 'looking for reception type next'
                    
                    team_mode = 'receiving'

                    receptions_player = 0
                    receptions_type = ''
                    receptions_position = 0
                    receptions_outcome = 0

                    # to reiterate  --  1 for K1  --  2 for K2
                    complex = 1


            #--------------------------------------------------------------------------------------


            # . float,  .. jumper,  ... jumper after float toss,  .... float after jump toss
            elif mode == 'looking for type of serve next':
                
                assert 1 <= len(action) <= 4, f'ERR:  action {action} not eligible. Only 4 serve types defined.'

                serves_type = len(action)

                mode = 'looking for serve zone next'


            # this should be a group of . of lengths 1 - 10, 1 - 9 zones, 10 not attributable
            elif mode == 'looking for serve zone next':
                
                assert 1 <= len(action) <= 10, f'ERR:  action {action} not eligible. Only 10 service zones are defined.'

                mode = 'looking for serve outcome next'
                
                serves_zone = len(action)


            # . ace, .. overpass, ... received,  .... error
            elif mode == 'looking for serve outcome next':

                assert 1 <= len(action) <= 4, f'ERR:  action {action} not eligible. Only 4 service outcomes are defined.' 
                
                serves_outcome = len(action)

                serves.add_serve_to_player(serves_player, serves_type, serves_zone, serves_outcome)
                

                # ..  --  came back over,  ...  --  received
                if len(action) in [2, 3]:
                    mode = 'looking for set destination next'


            #--------------------------------------------------------------------------------------


            # . float, .. jumper
            elif mode == 'looking for reception type next':

                assert 1 <= len(action) <= 2, f'ERR: action {action} not eligible. Only 2 reception types are defined.'

                mode = 'looking for receiving position next'

                receptions_type = len(action)


            # ... pos 3, ..... pos 5, ...... pos 6, . pos 1
            elif mode == 'looking for receiving position next':

                assert len(action) in [0, 1, 3, 5, 6], f'ERR: action {action} not eligible. Only 5 receiving positions are defined.'

                # opposing team missed their serve
                if len(action) == 0:
                    mode = 'looking for action'
                    continue

                receptions_position = len(action)

                receptions_player = lineup.get_receiving_player_on_position(receptions_position)

                mode = 'looking for reception outcome next'


            # . perfect, .. okay, ... bad, ... error (aced / back over the net)
            elif mode == 'looking for reception outcome next':

                assert 1 <= len(action) <= 4, f'ERR: action {action} not eligible. Only 4 reception outcomes are defined. '
                
                receptions_outcome = len(action)

                receptions.add_reception_to_player(receptions_player, receptions_type, receptions_outcome)

                mode = 'looking for set destination next'
            
                if len(action) == 4:
                    complex = 2    # potentially if the ball comes back

                # if it was an ace,  then the next action is an empty string
                # if it came back over the next,  then the next action of the team being scouted
                #     is technically a defense,  which is not being taken into account,
                #     thus the next action would be a set


            #--------------------------------------------------------------------------------------


            # 1 - 7,  7 is for setter dump
            elif mode == 'looking for set destination next':

                assert 1 <= len(action) <= 7, f'ERR: action {action} not eligible. Only 7 set destinations are defined.'

                mode = 'looking for type of set next'

                sets_destination = len(action)
                
                # check if set destination is possible
                if lineup.is_in_frontcourt(lineup.setter) and sets_destination == 2:
                    sets_destination = 1
                    print(f'\\033[31m Faulty scouting there is no opposite in the frontcourt, current lineup: {lineup.lineup}. Will assume opposite in the backcourt')

                if lineup.is_in_backcourt(lineup.setter) and sets_destination == 1:
                    sets_destination = 2
                    print(f'\\033[31m Faulty scouting there is no opposite in the backcourt, current lineup: {lineup.lineup}. Will assume opposite in the frontcourt')

                # careful the set destination is given as 1 - 6,  the lineup positions are stored as 0 - 5
                hits_player = lineup.get_hitting_player_on_position(sets_destination)

            # 1 - 4
            elif mode == 'looking for type of set next':

                assert 1 <= len(action) <= 4, f'ERR: action {action} not eligible. Only 4 set types are defined.'

                sets_type = len(action)
                rotation = lineup.get_rotation()

                if complex == 1:
                    sets_c1.add_set_to_player(lineup.setter, rotation, sets_destination, sets_type)

                    if receptions_position == 1:
                        sets_special_case1.add_set_to_player(lineup.setter, rotation, sets_destination, sets_type)

                elif complex == 2:
                    sets_c2.add_set_to_player(lineup.setter, rotation, sets_destination, sets_type)

                mode = 'looking for type of hit next'


            #--------------------------------------------------------------------------------------


            # . hit,  .. tip,  ... rebound
            elif mode == 'looking for type of hit next':

                assert 1 <= len(action) <= 3, f'ERR: action {action} not eligible. Only 3 types of hits are defined.'

                type_of_hit = len(action)

                mode = 'looking for zone of hit next'


            # 1 - 5,  from leftmost to rightmost,  just divide the court equally
            # 6 - zone for short tips
            # 7 - zone for not attributable blocked hits and errors
            elif mode == 'looking for zone of hit next':

                assert 1 <= len(action) <= 7, f'ERR: action {action} not eligible. Only 7 hitting zones are defined.'

                mode = 'looking for outcome of hit next'

                hits_zone = len(action)


            # . point,  .. defended,  ... block out,  .... blocked,  ..... error
            elif mode == 'looking for outcome of hit next':

                assert 1 <= len(action) <= 5, f'ERR: action {action} not eligible. Only 5 hitting outcomes are defined.'

                hits_outcome = len(action)

                hits.add_hit_to_player(hits_player, sets_destination, sets_type, hits_zone, hits_outcome)


                # ..  --  defended  --  that includes a defense which comes straight back over and rebound off the block
                if action == '..':
                    mode = 'looking for set destination next'

                    complex = 2    # potential return of ball
            

    serves.save(analysis_dir_path)

    receptions.save(analysis_dir_path)
    
    sets_c1.save(analysis_dir_path)
    sets_c2.save(analysis_dir_path)
    sets_special_case1.save(analysis_dir_path)
    
    hits.save(analysis_dir_path)
    

if __name__ == '__main__': 

    parser = argparse.ArgumentParser()
    parser.add_argument('--filename',)

    args = parser.parse_args()

    main(filename = args.filename)


####################################################################################################