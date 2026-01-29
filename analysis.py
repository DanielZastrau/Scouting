import argparse
import os
import json

from lineup import Lineup

from helpers import determine_lineup

# want reception stats
# want hitting stats
# want setting stats

##############################    Main    ##############################

def main(filename: str):

    # create a folder for the analysis files
    if not os.path.isdir(os.path.join(os.getcwd(), 'analysis', filename)):
        os.mkdir(os.path.join(os.getcwd(), 'analysis', filename))


    # get the scouting file    
    with open(os.path.join(os.getcwd(), 'scouting', filename), 'r', encoding='utf-8') as file:
        data = file.read()


    # filter out irrelevant lines
    data = data.split('\n')
    data = [line for line in data if (not line.startswith('#')) and (len(line) != 0)]


    # read out serve positions
    serve_positions = {}

    print(data[0])

    positions = data[0].split('  ')[1:]
    for position in positions:
        number, pos = position.split(' ')

        serve_positions[number] = int(pos)

    with open(os.path.join(os.getcwd(), 'analysis', filename, 'serve_positions.txt'), 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(serve_positions, indent=4))


    # read out serve type
    serve_types = {}

    types = data[1].split('  ')[2:]
    for type_ in types:
        number, type__ = type_.split(' ')

        serve_types[number] = type__

    with open(os.path.join(os.getcwd(), 'analysis', filename, 'serve_types.txt'), 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(serve_types))

    # remove serve pos line and serve type line
    data = [line for line in data if not line.startswith('>')]


    positions = {i: 0 for i in range(1, 7)}

    # top level: player nubmer + dict,    second level: setter position + dict,    third level: reception quality + dict,    fourth level: pos + dict,    fifth level: set + count
    K1 = {}

    # top level: player number + dict,    second level: setter position + dict,    third level: pos + dict,    fourth level: set + count
    K2 = {}

    # top level: player number + dict,    second level: pos + dict,    third level: outcome + count
    reception = {}
    
    # top level: player number + dict,    second level: zone + dict,    third level: outcome + count
    serves = {}

    c = 1
    amount_of_serves = 0
    for i, line in enumerate(data):
        print(f'set: {i + 1}')

        lineup, actions = line.split('>')


        # Determine lineup
        lineup = determine_lineup(lineup)


        # currently want to fill serving dicts
        mode = 'looking for action'
        team_mode = 'none'
        
        # 1 for reception, 2 for defense,
        # only interesting for set distribution, therefore we only care if K1 or K2
        complex = 0    

        actions = actions.split(' ')
        for ii, action in enumerate(actions):


            if action == '':
                # print('action ended')
                mode = 'looking for action'


            # then it should only find . or ..
            # also the only mode in which the team mode can change and therefore the rotation
            elif mode == 'looking for action':    
                
                # .  --  indicates a serve
                if action == '.':

                    # print(f'player {curr_server} is serving')
                    mode = 'looking for serve zone next'

                    if team_mode == 'none':
                        team_mode = 'serving'
                    elif team_mode == 'receiving':
                        team_mode = 'serving'

                        lineup.rotate_lineup()

                    curr_server = lineup.get_server()
                    serving_zone = 0
                    serving_outcome = 0

                    # to reiterate  --  1 for K1,  2 for K2
                    complex = 2

                # ..  --  indicates a reception
                elif action == '..':

                    mode = 'looking for receiving position next'
                    
                    team_mode = 'receiving'

                    receiving_player = 0
                    receiving_position = 0
                    reception_outcome = 0

                    # to reiterate  --  1 for K1,  2 for K2
                    complex = 1

                else:
                    raise Exception(f'ERR: this should not happen. Only defined 2 actions.\n current action: {action}')


            # this should be a group of . of lengths 1 - 9
            elif mode == 'looking for serve zone next':    
                
                assert 1 <= len(action) <= 9, \
                    f'ERR:  this should not happen. Only 9 service zones are defined'

                mode = 'looking for serve outcome next'
                
                serving_zone = len(action)


            # this should be a group of . of lengths 1 - 6
            elif mode == 'looking for receiving position next':
                if len(action) == 0:
                    # print('opposing team missed their serve.')
                    mode = 'looking for action'

                elif 1 <= len(action) <= 6:
                    receiving_position = len(action)
                    receiving_player = general_information['receiving players'][receiving_position]

                    mode = 'looking for reception outcome next'

                else:
                    raise Exception('ERR: this should not happen. A position which does not exist, cannot receive.')

            elif mode == 'looking for serve outcome next':    # . ace, .. good reception, ... bad reception, .... err, ..... came back over free ball
                assert 1 <= len(action) <= 5 and action.startswith('.'), 'faulty bit'
                
                serving_outcome = len(action)
                if serving_outcome == 5: 
                    serving_outcome = 1

                if not curr_server in serves:
                    serves = add_player_to_serves_dict(serves, curr_server)
                serves = add_serve_to_player(serves, curr_server, serving_zone, serving_outcome)
                
                if len(action) == 1:
                    mode = 'ace'    # after this I can expect there to be an empty string

                elif len(action) == 2:
                    # print('good reception opposing team')
                    mode = 'looking for possible return of the ball'

                elif len(action) == 3:
                    # print('bad reception opposing team')
                    mode = 'looking for possible return of the ball'

                elif len(action) == 4:
                    mode = 'service was an error'    # after this I can expect there to be an empty string

                elif len(action) == 5:
                    # print('service wasnt an ace, but came straight back.')
                    mode = 'looking for set destination next'

                else:
                    raise Exception('ERR: this should not happen. No other service outcome defined.')

            elif mode == 'looking for reception outcome next':
                assert 1 <= len(action) <= 5 and action.startswith('.'), 'faulty action'
                
                reception_outcome = len(action)
                if reception_outcome == 5:
                    reception_outcome = 4

                if receiving_position in [1, 6, 5]:
                    if not receiving_player in reception:
                        reception = add_player_to_reception_dict(reception, receiving_player)
                    reception = add_reception_to_player(reception, receiving_player, receiving_position, reception_outcome)

                if len(action) == 1:
                    # print('perfect reception.')
                    mode = 'looking for set destination next'

                elif len(action) == 2:
                    # print('mehh reception')
                    mode = 'looking for set destination next'

                elif len(action) == 3:
                    # print('bad reception')
                    mode = 'looking for set destination next'

                elif len(action) == 4:
                    mode = 'aced'    # after this I can expect there to be an empty string

                elif len(action) == 5:
                    # print('ball was directly returned to the opposing team.')
                    mode = 'looking for possible return of the ball'

                else:
                    raise Exception('ERR: this should not happen. Only defined 4 reception outcomes')

            elif mode == 'looking for possible return of the ball':
                complex = 2

                if action == '':
                    # print('action ended')
                    mode = 'looking for action'

                elif action == ',':
                    # print('ball was returned as a hit')
                    mode = 'looking for set destination next'

                elif action == ',,':
                    # print('ball was returned as a free ball')
                    mode = 'looking for set destination next'

            elif mode == 'looking for set destination next':

                if 1 <= len(action) <= 6:
                    # print(f'ball was set to player on position {len(action)}')
                    mode = 'looking for type of set next'

                    set_position = len(action)
                    set_type = 0

                else:
                    raise Exception('ERR: this should not happen. Ball has to be set to a position on the court.')

            elif mode == 'looking for type of set next':
                set_type = len(action)

                if general_information['setter'] not in K1:
                    K1, K2 = add_player_to_sets(K1, K2, general_information['setter'])
                K1, K2 = add_set_to_player(K1, K2, complex, general_information['setter'], general_information['rotation'].index('S') + 1, reception_outcome, set_position, set_type)

                if actions[ii - 1] != '...':    # in this case the action will always be '.', since a non middle was set
                    # print('standard set')
                    mode = 'looking for zone of hit next'

                elif actions[ii - 1] == '...':    # then a middle was set

                    if action == '.':
                        # print('fast ball')
                        mode = 'looking for zone of hit next'

                    elif action == '..':
                        # print('push ball')
                        mode = 'looking for zone of hit next'

                    elif action == '...':
                        # print('shoot ball')
                        mode = 'looking for zone of hit next'

                    elif action == '....':
                        # print('back fast')
                        mode = 'looking for zone of hit next'

                    else:
                        raise Exception('ERR: this should not happen. Only 4 cases defined')
                
                else:
                    raise Exception('ERR: this should not happen. Only 6 positions on the court.')

            elif mode == 'looking for zone of hit next':
                if 1 <= len(action) <= 5:
                    # print(f'ball was hit to zone {len(action)}')
                    mode = 'looking for outcome of hit next'

            elif mode == 'looking for outcome of hit next':
                if action == '.':
                    mode = 'point'

                elif action == '..':
                    # print('defended')
                    mode = 'looking for possible return of the ball'

                elif action == '...':
                    # print('defended, but came back over')
                    mode = 'looking for set destination next'

                elif action == '....':
                    mode = 'error'

                elif action == '.....':
                    # print('rebound')
                    mode = 'looking for set destination next'

                else:
                    raise Exception(f'ERR: this should not happen. This mode is not defined.\n{actions[i-6: i+1]}')

            else:
                raise Exception(f'ERR: this should not happen. This mode is not defined. mode: {mode}\n{actions[i-6: i]}')
            
            # print(mode)
            
    dicts_to_write = [K1, K2, serves, serve_positions, reception]
    with open(os.path.join(os.getcwd(), f'analysis_{filename}'), 'w', encoding='utf-8') as file:
        for d in dicts_to_write:
            json_string = json.dumps(d)
            file.write(json_string + '\n')

if __name__ == '__main__': 

    parser = argparse.ArgumentParser()
    parser.add_argument('--filename',)

    args = parser.parse_args()

    main(filename = args.filename)


####################################################################################################