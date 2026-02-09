class Breaks():
    # Rotation as 0 - 5, since lineup returns rotation as 0 - 5
    # Extra players dict, because it is an interesting stat with whoms serve they scored the most breaks

    def __init__(self):

        self.breaks = {
            rotation : 0 for rotation in range(0, 6)
        }

        self.player_breaks = {}
    

    # Modifiers

    def add_player(self, player: int):

        self.player_breaks[player] = 0


    def won_breakpoint(self, rotation: int = -1, player: int = -1):

        if player != -1:

            if player not in self.player_breaks:
                self.add_player(player)
            self.player_breaks[player] += 1
        
        if rotation != -1:
            self.breaks[rotation] += 1


    def lost_sideout(self, rotation: int):
        self.breaks[rotation] -= 1


    # Save

    def save(self, filepath: str):
        import json
        import os
        
        with open(os.path.join(filepath, 'breakpoints.json'), 'w', encoding='utf-8') as outfile:
            outfile.write(json.dumps(self.breaks, indent=4))

        with open(os.path.join(filepath, 'breakpoints_players.json'), 'w', encoding='utf-8') as outfile:
            outfile.write(json.dumps(self.player_breaks, indent=4))