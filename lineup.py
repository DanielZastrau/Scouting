class Lineup():
    """positions and rotations are always one down due to indexing in lists
    i.e. position 5 is at index 4 and rotation 5 will be given as 4

    meta positions are: OH, MI, OP, S
    """

    def __init__(self, setter: int, libero: int, lineup: list, meta: list):

        self.setter = setter
        self.libero = libero

        # lineup is supposed to be the actual lineup with the middle in the backcourt
        # indeces are one down of position, i.e. position 1 is at index 0
        self.lineup = lineup
        
        # meta has to be correlated with self.lineup
        self.meta = meta


    # getters

    def get_frontcourt(self) -> tuple[list]:
        """returns a tuple of lists, the first one is the actual lineup,
        the second one are the actual positions

        e.g. ([1,2,3], [OH, MI, OP])

        the court positions are 2, 3, 4 in that order
        """
        return [self.lineup[1:4], self.meta[1:4]]


    def get_backcourt(self) -> tuple[list]:
        """returns a tuple of lists, the first one is the actual lineup,
        the second one are the actual positions

        e.g. ([1,2,3], [OH, MI, OP])

        the court positions are 1, 5, 6 in that order
        """
        return [self.lineup[0]].extend(self.lineup[4:], [self.meta[0]].extend(self.meta[4:]))


    def get_rotation(self) -> int:
        return self.lineup.index(self.setter)


    def get_receiving_players(self) -> dict:

        rotation = self.get_rotation()

        receiving_positions = {1: 0, 6: 0, 5: 0, 3: 0}

        frontcourt_players, frontcourt_meta = self.get_frontcourt()
        backcourt_players, backcourt_meta = self.get_backcourt()

        # determine position 3 receiver  --  always the frontcourt middle
        receiving_positions[3] = frontcourt_players[frontcourt_meta.index('MI')]

        # determine where the libero receives
        translation = {0: 1, 1: 5, 2: 6}
        libero_position = translation[backcourt_meta.index('MI')]
        receiving_positions[libero_position] = self.libero

        # determine position 5 receiver  --  always an OH
        if rotation == 0:
            receiving_positions[5] = backcourt_players[backcourt_meta.index('OH')]
            receiving_positions[1] = frontcourt_players[frontcourt_meta.index('OH')]
        else:
            receiving_positions[5] = frontcourt_players[frontcourt_meta.index('OH')]
            
            # find empty slot
            empyt_position = [key_ for key_ in receiving_positions if receiving_positions[key_] == 0][0]
            receiving_positions[empyt_position] = backcourt_players[backcourt_meta.index('OH')]


    def get_server(self) -> int:
        return self.lineup[0]


    # modifiers

    def modify_lineup(self, player_out, player_in):

        if player_out == self.libero:
            self.modify_libero(player_in)

        else:
            assert player_out in self.lineup, \
                f'player {player_out} is not in the current lineup {self.lineup}'

            self.lineup[self.lineup.index(player_out)] = player_in


    def modify_libero(self, player_in):
        self.libero = player_in


    def rotate_lineup(self):
        self.lineup = self.lineup[1:].extend([self.lineup[0]])
        self.meta = self.meta[1:].extend([self.meta[0]])