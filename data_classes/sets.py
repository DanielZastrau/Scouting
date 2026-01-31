class Sets():
    """
    set destinations:  1-6 = pos 1-6,  7 setter dump

    middles:  1 quickset,  2 quickset behind,  3 shoot,  4 push
    outsides/dia:  1 shoot,  2 normal,  3 high
    setter:  1 always

    complex:  1 for K1,  2 for K2
    """

    def __init__(self, complex: int):

        self.sets = {}
        self.complex = complex

    
    # Modifier

    def add_player(self, player: int):

        self.sets[player] = {rotation: {set_destination: {set_type: 0 for set_type in range(1, 5)} for set_destination in range(1, 8)} for rotation in range(6)}


    def add_set_to_player(self, player: int, rotation: int, set_destination: int, set_type: int):

        if not player in self.sets:
            self.add_player(player)

        self.sets[player][rotation][set_destination][set_type] += 1


    # Save

    def save(self, filepath: str):
        import json
        import os
        
        with open(os.path.join(filepath, f'setsK{self.complex}.json'), 'w', encoding='utf-8') as outfile:
            outfile.write(json.dumps(self.sets, indent=4))