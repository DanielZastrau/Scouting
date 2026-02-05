class Serves():
    """
    zones 1 - 9, all the relevant zones in the backcourt + 2 frontcourt zones
    zone 10,  not attributable in case of error
    """

    def __init__(self):

        self.serves = {}

    
    # Modifier

    def add_player(self, player: int) -> None:

        self.serves[player] = {
            type_: {zone: {outcome: 0 
                for outcome in range(1, 5)} 
                for zone in range(1, 11)}
                for type_ in range(1, 5)        
        }


    def add_serve_to_player(self, player: int, type_: int, zone: int, outcome: int) -> None:

        if not player in self.serves:
            self.add_player(player)

        self.serves[player][type_][zone][outcome] += 1


    # Save

    def save(self, filepath: str):
        import json
        import os
        
        with open(os.path.join(filepath, 'serves.json'), 'w', encoding='utf-8') as outfile:
            outfile.write(json.dumps(self.serves, indent=4))