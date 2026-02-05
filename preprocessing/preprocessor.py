import os
import argparse

import yaml


def main(bindings: dict, data: list):

    out = []


    for line in data:
        out.append([])


        if not line.startswith('!'):
            out[-1] = list(line)
            continue


        for char in line[1:]:  # Skip the '!' character

            if char in bindings:
                out[-1].append(bindings[char])
            else:
                out[-1].append(char)


    for i in range(len(out)):
        out[i] = ''.join(out[i])
    out = '\n'.join(out)


    return out


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--filename')
    args = parser.parse_args()


    with open('./preprocessing/keybindings.yml', 'r', encoding='utf-8') as file:
        keybindings = yaml.safe_load(file)
    bindings = {value: key for key, value in keybindings['bindings'].items()}


    data = []
    with open(f'./scouting/{args.filename}', 'r', encoding='utf-8') as file:
        for line in file:
            data.append(line.strip())


    processed_file = main(bindings = bindings, data = data)


    with open(f'./scouting/{args.filename}', 'w', encoding='utf-8') as file:
        file.write(processed_file)