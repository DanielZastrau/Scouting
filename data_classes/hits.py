class Hits():
    """
    middles:  1 quickset,  2 quickset behind,  3 shoot,  4 push
    outsides/dia:  1 shoot,  2 normal,  3 high
    setter:  1 always
    
    zones:  1 - 5 from leftmost to rightmost,  just divide the court equally
    zone:  6 - the zone for short tips
    zone:  7 - not attributable
    outcomes:  1 point,  2 defended,  3 block out,  4 blocked,  5 error
    """

    def __init__(self):

        self.hits = {}


    # Modifiers

    def add_player(self, player: int):

        self.hits[player] = {}


    def add_position_to_player(self, player: int, position: int):

        self.hits[player][position] = {
            set_type: {hitting_zone: {hitting_outcome: 0 
                for hitting_outcome in range(1, 6)} 
                for hitting_zone in range(1, 8)} 
                for set_type in range(1, 5)
        }


    def add_hit_to_player(self, player: int, hitting_position: int,set_type: int, hitting_zone: int, hitting_outcome: int):

        if not player in self.hits:
            self.add_player(player)

        if not hitting_position in self.hits[player]:
            self.add_position_to_player(player, hitting_position)

        self.hits[player][hitting_position][set_type][hitting_zone][hitting_outcome] += 1

    

    # Save

    def save(self, filepath: str):
        import json
        import os
        
        with open(os.path.join(filepath, 'hits.json'), 'w', encoding='utf-8') as outfile:
            outfile.write(json.dumps(self.hits, indent=4))