import argparse
import os
import json

def main(filename: str):

    with open(os.path.join(os.getcwd(), filename), 'r', encoding='utf-8') as file:
        data = file.read()

    data = data.split('\n')
    tmp = []
    for line in data:
        if line.startswith('#') or len(line) == 0:
            continue
        tmp.append(line)
    data = tmp

    # each line is a set in the game
    positions = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }
    K1 = {i: positions.copy() for i in range(1, 4)}
    K2 = {i: positions.copy() for i in range(1, 4)}
    serves = {}
    serve_outcomes = {}

    c = 1
    amount_of_serves = 0
    for line in data:
        print(f'set {c}')
        c += 1

        actions = line.split('  ')

        cc = 1
        for action in actions:
            # print(f'action {cc}')
            # print('action: ', action)

            elements = action.split(' ')
            # print('elements: ', elements)

            if elements[0][0] in ['.', ',']:    # this evaluates the set distribution
                quality_of = elements[0]
                position_set_to = elements[1]
                outcome_of_hit = elements[2]

                if action.startswith('.'):    # set out of reception, i.e. K1
                    K1[len(quality_of)][len(position_set_to)] += 1

                if action.startswith(','):    # set out of defense, i.e. K2
                    K2[len(quality_of)][len(position_set_to)] += 1

            else:    # this evaluates the serves
                try:
                    amount_of_serves += 1
                    if len(elements) == 2:
                        number = int(elements[0])
                        served_to = 7
                        outcome = 3

                    elif len(elements) == 3:
                        number = int(elements[0])
                        served_to = len(elements[1])
                        outcome = len(elements[2])

                    # serve distribution
                    if number in serves:
                        if served_to != 7:
                            serves[number][served_to] += 1
                    else:
                        serves[number] = positions.copy()
                        if served_to != 7:
                            serves[number][served_to] += 1

                    # serve outcome
                    if number in serve_outcomes:
                        serve_outcomes[number][outcome] += 1
                    else:
                        serve_outcomes[number] = {1: 0, 2: 0, 3: 0}
                        serve_outcomes[number][outcome] += 1

                except ValueError as err:
                    print(err)
                    print(action)

            cc += 1
        print('K1', K1, sep='---')
        print('K2', K2, sep='---')
        print('serves', serves, sep='---')
        print('serve_outcomes', serve_outcomes, sep='---')
        print('amount_of_serves', amount_of_serves, sep='---')
        print('-'*100)

    dicts_to_write = [K1, K2, serves, serve_outcomes]
    with open(os.path.join(os.getcwd(), f'analysis_{filename}'), 'w', encoding='utf-8') as file:
        for d in dicts_to_write:
            json_string = json.dumps(d)
            file.write(json_string + '\n')

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--filename',)

    args = parser.parse_args()

    main(filename = args.filename)