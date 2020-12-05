import json
import operator

data = []
transition_model = {}
emission_model = {}
S = ['<S>', 'N', 'O', 'S', '^', 'Z', 'L', 'M', 'V', 'A', 'R', '!', 'D',
     'P', '&', 'T', 'X', 'Y', '#', '@', '~', 'U', 'E', '$', ',', 'G', '<E>']
O = []

def setup():
    transition_model['<S>'] = {}
    for s in S:
        if s != '<S>':
            transition_model['<S>'][s] = 0
        if s != '<E>' and s != '<S>':
            transition_model[s] = {}
            emission_model[s] = {}
            for s2 in S:
                if s != '<S>':
                    transition_model[s][s2] = 0
        
def process(filename):
    with open(filename, 'r') as f:
        for line in f:
            twt = json.loads(line)
            process_twt(twt)
    create_probs()
    write_models()
    
def process_twt(twt):
    prev = '<S>'
    for item in twt:
        o = item[0]
        s = item[1]
        if o not in O:
            O.append(o)
        if o not in emission_model[s]:
            emission_model[s][o] = 0
        transition_model[prev][s] += 1
        emission_model[s][o] += 1
        prev = s
    transition_model[prev]['<E>'] += 1

def create_probs():
    for s in transition_model:
        total = 0
        for s2 in transition_model[s]:
            total += transition_model[s][s2]
        if total != 0:
            for s2 in transition_model[s]:
                transition_model[s][s2] /= total
    for s in emission_model:
        total = 0
        for o in emission_model[s]:
            total += emission_model[s][o]
        if total != 0:
            for o in emission_model[s]:
                emission_model[s][o] /= total
        

def write_models():
    with open('twitter_pos_hmm.json', 'w') as f:
        f.write(json.dumps({'S': S, 'O': O, 'P_trans': transition_model, 'P_emission': emission_model}, indent=4))

if __name__ == '__main__':
    setup()
    process('twt.train.json')
