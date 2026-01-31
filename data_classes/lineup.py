class Lineup():
    """positions and rotations are always one down due to indexing in lists
    i.e. position 5 is at index 4 and rotation 5 will be given as 4

    meta positions are: OH, MI, OP, S
    """

    def __init__(self):

        self.setter: int
        self.libero: int

        # lineup is supposed to be the actual lineup with the middle in the backcourt
        # indeces are one down of position, i.e. position 1 is at index 0
        self.lineup: list[int]
        
        # meta has to be correlated with self.lineup
        self.meta: list[str]


    # getters

    def get_frontcourt(self) -> tuple[list]:
        """returns a tuple of lists, the first one is the actual lineup,
        the second one are the actual positions

        e.g. ([1,2,3], [OH, MI, OP])

        the court positions are 2, 3, 4 in that order
        """
        return self.lineup[1:4], self.meta[1:4]


    def get_backcourt(self) -> tuple[list]:
        """returns a tuple of lists, the first one is the actual lineup,
        the second one are the actual positions

        e.g. ([1,2,3], [OH, MI, OP])

        the court positions are 1, 5, 6 in that order
        """
        backcourt_players = [self.lineup[0]]
        backcourt_players.extend(self.lineup[4:])

        backcourt_meta = [self.meta[0]]
        backcourt_meta.extend(self.meta[4:])

        return backcourt_players, backcourt_meta


    def get_rotation(self) -> int:
        """Returns the rotation as values 0 - 5
        """
        return self.lineup.index(self.setter)


    def get_receiving_players(self) -> dict:

        rotation = self.get_rotation()

        receiving_positions = {1: 0, 6: 0, 5: 0, 3: 0}

        frontcourt_players, frontcourt_meta = self.get_frontcourt()
        backcourt_players, backcourt_meta = self.get_backcourt()

        # determine position 3 receiver  --  always the frontcourt middle
        receiving_positions[3] = frontcourt_players[frontcourt_meta.index('MI')]

        # determine position 5 receiver  --  always an OH
        if rotation == 0:
            receiving_positions[5] = backcourt_players[backcourt_meta.index('OH')]
            receiving_positions[1] = frontcourt_players[frontcourt_meta.index('OH')]
        else:
            receiving_positions[5] = frontcourt_players[frontcourt_meta.index('OH')]
            
            # if the backcourt OH is on position 1 he receives there, 
            # else he receives on 6
            player = backcourt_players[backcourt_meta.index('OH')]
            if self.lineup.index(player) == 0:
                receiving_positions[1] = player
            else:
                receiving_positions[6] = player

        empty_key = [key for key in receiving_positions if receiving_positions[key] == 0][0]
        receiving_positions[empty_key] = self.libero

        return receiving_positions


    def get_receiving_player_on_position(self, position: int) -> int:

        receiving_positions = self.get_receiving_players()

        return receiving_positions[position]


    def get_hitting_player_on_position(self, position: int) -> int:
        """Careful! The position passed is given as 1 - 6, but the positions in the lineup are stored as 0 - 5

        hopefully the other cases just don't occur, for example setter in front but set destination 2
        """

        rotation = self.get_rotation()

        frontcourt_players, frontcourt_meta = self.get_frontcourt()
        backcourt_players, backcourt_meta = self.get_backcourt()

        if position == 1:
            try:
                return backcourt_players[backcourt_meta.index('OP')]
            except ValueError:
                print(f'\\033[31m Faulty scouting there is no opposite in the back row, current lineup: {self.lineup}. Will assume opposite in the front row')
                return frontcourt_players[frontcourt_meta.index('OP')]

        if position == 2:
            if rotation == 0:
                return frontcourt_players[frontcourt_meta.index('OH')]
            else:
                try:
                    return frontcourt_players[frontcourt_meta.index('OP')]
                except ValueError:
                    print(f'\\033[31m Faulty scouting there is no opposite in the front row, current lineup: {self.lineup}. Will assume opposite in the back row')
                    return frontcourt_players[frontcourt_meta.index('OP')]

        # middle was set
        if position == 3:
            return frontcourt_players[frontcourt_meta.index('MI')]

        if position == 4:
            if rotation == 0:
                return frontcourt_players[frontcourt_meta.index('OP')]
            else:
                return frontcourt_players[frontcourt_meta.index('OH')]

        if position == 6:
            return backcourt_players[backcourt_meta.index('OH')]

        # special case of setter dump
        if position == 7:
            return self.setter


    def get_server(self) -> int:

        return self.lineup[0]


    # modifiers

    def determine_lineup(self, lineup: str):
        """3 15 8 11 13 12 12 2>.. .. .. 
        """

        lineup = list(map(int, lineup.split(' ')))

        # libero is always the last person noted
        self.libero = lineup[-1]

        # setter is the second to last person
        self.setter = lineup[-2]

        # the 6 people before that are the lineup
        self.lineup = lineup[:-2]

        # determine meta
        self.meta = ['', '', '', '', '', '']

        setter_index = self.lineup.index(self.setter)

        self.meta[setter_index] = 'S'
        self.meta[(setter_index + 3) % 6] = 'OP'
        self.meta[(setter_index + 1) % 6] = 'OH'
        self.meta[(setter_index + 4) % 6] = 'OH'
        self.meta[(setter_index + 2) % 6] = 'MI'
        self.meta[(setter_index + 5) % 6] = 'MI'


    def modify_lineup(self, substitution: str):
        """e.g. <12-13>

        if it is a diagonal substituion it would look like this
        e.g.  <x-y>  <a-b>  <->
        """

        # detect diagonal substitution
        if substitution == '<->':
            
            # then the substitutions already happened, I only need to change the setter value and the meta
            opposite_index = self.meta.index('OP')
            setter_index = self.meta.index('S')

            self.meta[opposite_index] = 'S'
            self.meta[setter_index] = 'OP'

            self.setter = self.lineup[opposite_index]

        else:
            relevant = substitution[1:-1]
            player_out, player_in = list(map(int, relevant.split('-')))

            # libero is special case
            if player_out == self.libero:
                self.modify_libero(player_in)

            else:
                assert player_out in self.lineup, \
                    f'player {player_out} is not in the current lineup {self.lineup}'

                self.lineup[self.lineup.index(player_out)] = player_in

                if player_out == self.setter:
                    self.setter = player_in


    def modify_libero(self, player_in):
        self.libero = player_in


    def rotate_lineup(self):
        self.lineup = self.lineup[1:] + [self.lineup[0]]
        self.meta = self.meta[1:] + [self.meta[0]]