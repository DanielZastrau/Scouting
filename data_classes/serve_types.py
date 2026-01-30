class ServeTypes():

    def __init__(self):

        self.serve_types = {}


    # Modifiers

    def add_player(self, player: str, type_: str):
        """Position 1 is the left sideline when standing at the net and looking towards the endline,
        Position 5 is the right sideline, the rest aligns in between
        """

        assert type_ in ['J', 'F', 'H']

        self.serve_types[player] = type_

    
    def extract_serve_types(self, data: str):
        """e.g. '>>  20 J  7 F  10 H  24 J  4 J  14 F'
        """

        types = data[0].split('  ')[2:]
        for tuple_ in types:
            player, type_ = tuple_.split(' ')

            self.add_player(player, type_)


    # Save

    def save(self, filepath: str):
        import json
        import os

        with open(os.path.join(filepath, 'serve_types.txt'), 'w', encoding='utf-8') as outfile:
            outfile.write(json.dumps(self.serve_types, indent=4))