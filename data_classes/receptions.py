class Receptions():

    def __init__(self):

        self.receptions = {}

    
    # Modifier

    def add_player(self, player: int):

        self.receptions[player] = {type_: {outcome: 0 for outcome in range(1, 5)} for type_ in ['F', 'J', 'H']}


    def add_reception_to_player(self, player, type_, outcome):

        if not player in self.receptions:
            self.add_player(player)

        self.receptions[player][type_][outcome] += 1


    # Save

    def save(self, filepath: str):
        import json
        import os
        
        with open(os.path.join(filepath, 'reception'), 'w', encoding='utf-8') as outfile:
            outfile.write(json.dumps(self.receptions, indent=4))