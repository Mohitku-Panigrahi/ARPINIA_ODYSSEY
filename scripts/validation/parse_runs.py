import json

with open('b6_real_golden_output.json', 'r') as f:
    ens = json.load(f)

print("Candidate stabilities keys:")
for cand in ens['candidate_stabilities']:
    if cand['mmsi'] == '123456789':
        print(json.dumps(cand, indent=2))
        break

print("Runs data:")
ranks = {}
for attempt in ens.get('runs', []) or []:
    # Actually wait, where is run by run data stored? 
    pass

