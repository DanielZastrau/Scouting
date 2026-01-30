class ServePositions():

    def __init__(self):

        self.serve_positions = {}


    # Modifiers

    def add_player(self, player: int, position: int):
        """Position 1 is the left sideline when standing at the net and looking towards the endline,
        Position 5 is the right sideline, the rest aligns in between
        """

        assert 1 <= position <= 5

        self.serve_positions[player] = position

    
    def extract_serve_positions(self, data: str):
        """e.g. '>  20 3  7 3  10 2  24 5  4 2  14 2'
        """

        print(data)

        positions = data.split('  ')[1:]
        for position in positions:
            player, position = tuple(map(int, position.split(' ')))

            self.add_player(player, position)


    # Save

    def save(self, filepath: str):
        import json
        import os

        with open(os.path.join(filepath, 'serve_positions.json'), 'w', encoding='utf-8') as outfile:
            outfile.write(json.dumps(self.serve_positions, indent=4))