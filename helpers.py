from lineup import Lineup

def determine_lineup(lineup: str) -> Lineup:

    lineup = list(map(int, lineup.split(' ')))

    # libero is always the last person noted
    libero = lineup[-1]

    # setter is the second to last person
    setter = lineup[-2]

    # the 6 people before that are the lineup
    lineup = lineup[:-2]

    # determine meta
    meta = ['', '', '', '', '', '']

    setter_index = lineup.index(setter)

    meta[setter_index] = 'S'
    meta[(setter_index + 3) % 6] = 'O'
    meta[(setter_index + 1) % 6] = 'OH'
    meta[(setter_index + 4) % 6] = 'OH'
    meta[(setter_index + 2) % 6] = 'M'
    meta[(setter_index + 5) % 6] = 'M'

    lineup = Lineup(setter, libero, lineup, meta)

    return lineup


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
