import json
import os


def validate_no_outcome_34_in_zones_234(data: dict):

    for player_num, player_data in data.items():

        for position, position_data in player_data.items():

            if position in ['3', '6']:
                continue

            for set_type, set_data in position_data.items():

                for zone, zone_data in set_data.items():

                    if zone in ['1', '5']:
                        continue

                    for outcome_key, outcome_count in zone_data.items():
                        
                        if outcome_key in ['1', '2', '5']:
                            continue

                        assert outcome_count == 0, f'ERROR -- zones 2, 3, 4 cant have outcomes "block out" or "blocked", for non middle or pipe attacks \
                            position: {position}  --  zone: {zone}  --  outcome: {outcome_key}  --  count: {outcome_count}'


if __name__=='__main__':
    
    with open(os.path.join(os.getcwd(), 'analysis', 'hits.json'), 'r', encoding='utf-8') as infile:
        data = json.load(infile)
    
    validate_no_outcome_34_in_zones_234(data)

    print('Successfully validated data.')