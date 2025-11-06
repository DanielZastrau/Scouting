import argparse
import os
import json

# need the libero
# need reception stats
# need hitting stats
# need setting stats

def determine_receiving_players(general_information: dict) -> dict:
    
    receiving_players = {1: 0, 6: 0, 5: 0, 3: 0}
    
    rotation = general_information['rotation'].index('S')
    if rotation == 0:
        receiving_players[1] = general_information['lineup'][1]
        receiving_players[6] = general_information['lineup'][5]
        receiving_players[5] = general_information['lineup'][4]
        receiving_players[3] = general_information['lineup'][2]

    elif rotation == 1:
        receiving_players[1] = general_information['lineup'][0]
        receiving_players[6] = general_information['lineup'][5]
        receiving_players[5] = general_information['lineup'][2]
        receiving_players[3] = general_information['lineup'][3]

    elif rotation == 2:
        receiving_players[1] = general_information['lineup'][0]
        receiving_players[6] = general_information['lineup'][4]
        receiving_players[5] = general_information['lineup'][3]
        receiving_players[3] = general_information['lineup'][1]

    elif rotation == 3:
        receiving_players[1] = general_information['lineup'][5]
        receiving_players[6] = general_information['lineup'][4]
        receiving_players[5] = general_information['lineup'][1]
        receiving_players[3] = general_information['lineup'][2]

    elif rotation == 4:
        receiving_players[1] = general_information['lineup'][0]
        receiving_players[6] = general_information['lineup'][5]
        receiving_players[5] = general_information['lineup'][2]
        receiving_players[3] = general_information['lineup'][3]

    elif rotation == 5:
        receiving_players[1] = general_information['lineup'][0]
        receiving_players[6] = general_information['lineup'][4]
        receiving_players[5] = general_information['lineup'][3]
        receiving_players[3] = general_information['lineup'][1]

    general_information['receiving players'] = receiving_players

    return general_information

def determine_additional_information(general_information: dict) -> dict:

    general_information = determine_receiving_players(general_information)

    return general_information

def rotate(general_information: dict) -> dict:

    lineup = general_information['lineup']
    general_information['lineup'] = lineup[1:] + lineup[:1]

    rotation = general_information['rotation']
    general_information['rotation'] = rotation[1:] + rotation[:1]

    general_information = determine_additional_information(general_information)

    return general_information

##############################    Serves    ##############################

def add_player_to_serves_dict(serves: dict, player: int) -> dict:
    # services with the outcome 5 "came back over" are counted as aces.
    # the dict for key 0 stands for the errors 

    serves[player] = {i: {1: 0, 2: 0, 3: 0,} for i in range(10)}

    return serves

def add_serve_to_player(serves: dict, player: int, zone: int, outcome: int) -> dict:

    if outcome == 4:
        serves[player][0][1] += 1
        serves[player][0][2] += 1
        serves[player][0][3] += 1
    else:
        serves[player][zone][outcome] += 1

    return serves

##############################    Reception    ##############################

def add_player_to_reception_dict(reception: dict, player: int) -> dict:
    # receptions which go back to the opponent are counted as aced

    reception[player] = {i: {1: 0, 2: 0, 3: 0, 4: 0} for i in [1, 5, 6]}

    return reception

def add_reception_to_player(reception: dict, player: int, position: int, outcome: int) -> dict:

    reception[player][position][outcome] += 1

    return reception

##############################    K1 / K2    ##############################

def add_player_to_sets(K1: dict, K2: dict, player: int) -> tuple[dict]:
    # pos 4 and 6 is always outside, pos 2 and 1 always opposite, pos 3 always middle 

    K1[player] = {i: {j: {k: {l: 0 for l in range(1, 5)} for k in range(1, 7)} for j in range(1, 4)} for i in range(1, 7)}
    
    K2[player] = {i: {j: {k : 0 for k in range(1, 5)} for j in range(1, 7)} for i in range(1, 7)}

    return K1, K2

def add_set_to_player(K1: dict, K2: dict, complex, setter, setter_position, reception_quality, position, set_type) -> tuple[dict]:
    # middles 1 - 4, fast - push - three - back fast
    # outsides and opposites always a one for now

    # print(setter, setter_position, reception_quality, position, set_type, sep='---')

    if complex == 1:
        K1[setter][setter_position][reception_quality][position][set_type] += 1

    elif complex == 2:
        K2[setter][setter_position][position][set_type] += 1

    return K1, K2

##############################    Main    ##############################

def main(filename: str):

    with open(os.path.join(os.getcwd(), filename), 'r', encoding='utf-8') as file:
        data = file.read()

    # filter out irrelevant lines
    data = data.split('\n')
    data = [line for line in data if (not line.startswith('#')) and (len(line) != 0)]

    # read out serve positions
    serve_positions = {}

    positions = data[0].split('  ')[1:]
    for position in positions:
        number, pos = position.split(' ')

        serve_positions[number] = int(pos)

    # read out serve type
    serve_types = {}

    types = data[1].split('  ')[2:]
    for type_ in types:
        number, type__ = type_.split(' ')

        serve_types[number] = type__

    # remove serve pos line
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


        general_information = {
            'lineup': ['0' for _ in range(6)],
            'setter': 0,
            'rotation': ['p', 'p', 'p', 'p', 'p', 'p',]
        }

        lineup, actions = line.split('>')
        for i, e in enumerate(lineup.split(' ')):
            if e == ' ' or e == '': continue

            if e.endswith('S'):
                general_information['setter'] = e[:-1]

                general_information['rotation'][i] = 'S'
                general_information['rotation'][(i + 3) % 6] = 'O'
                general_information['rotation'][(i + 1) % 6] = 'OH'
                general_information['rotation'][(i + 4) % 6] = 'OH'
                general_information['rotation'][(i + 2) % 6] = 'M'
                general_information['rotation'][(i + 5) % 6] = 'M'

                general_information['lineup'][i] = e[:-1]
            
            elif not e.endswith('S'):
                general_information['lineup'][i] = e

        general_information = determine_additional_information(general_information)

        # currently want to fill serving dicts
        mode = 'looking for action'
        team_mode = 'none'
        complex = 0    # 1 for reception, 2 for defense,    only interesting for set distribution, therefore we only care if K1 or K2

        actions = actions.split(' ')
        for ii, action in enumerate(actions):
            print(f'action: {ii + 1}')

            if action == '':
                # print('action ended')
                mode = 'looking for action'

            elif mode == 'looking for action':    # then it should only find . or ..,    also the only mode in which the team mode can change and therefore the rotation
                
                if action == '.':

                    # print(f'player {curr_server} is serving')
                    mode = 'looking for serve zone next'

                    if team_mode == 'none':
                        team_mode = 'serving'
                    elif team_mode == 'receiving':
                        team_mode = 'serving'
                        general_information = rotate(general_information)

                    curr_server = general_information['lineup'][0]
                    serving_zone = 0
                    serving_outcome = 0

                    complex = 2

                elif action == '..':

                    mode = 'looking for receiving position next'
                    
                    if team_mode == 'none' or team_mode == 'serving':
                        team_mode = 'receiving'

                    receiving_player = 0
                    receiving_position = 0
                    reception_outcome = 0

                    complex = 1

                else:
                    raise Exception(f'ERR: this should not happen. Only defined 2 actions.\n current action: {action}')

            elif mode == 'looking for serve zone next':    # this should be a group of . of lengths 1 - 9
                if 1 <= len(action) <= 9:
                    mode = 'looking for serve outcome next'

                    serving_zone = len(action)

                else:
                    raise Exception('ERR: this should not happen. Only defined 9 serve zones.')

            elif mode == 'looking for receiving position next':    # this should be a group of . of lengths 1 - 6
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