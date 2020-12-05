import hmm
import json
import hmm_vis as hv

def get_model(smoothing=False):
    if smoothing:
        return hmm.HMM('twitter_pos_hmm_laplace.json')
    else:
        return hmm.HMM('twitter_pos_hmm.json')

def form_seq(twt):
    seq = []
    for item in twt:
        seq.append(item[0])
    return seq

def get_ans(twt):
    ans = []
    for item in twt:
        ans.append(item[1])
    return ans

if __name__ == '__main__':
    model = get_model(smoothing=True)
    total = 0
    correct = 0
    with open('twt.test.json', 'r') as f:
        for line in f:
            twt = json.loads(line)
            seq = form_seq(twt)
            ans = get_ans(twt)
            beliefs = model.forward_algorithm(seq)
            state_seq = model.viterbi_algorithm(seq)
            total += len(seq)
            for i in range(len(state_seq)):
                if ans[i] == state_seq[i]:
                    correct += 1
    accuracy = correct / total * 100
    print("Total count of correctly-tagged words in the test set: " + str(correct))
    print("Total count of words in the test set: " + str(total))
    print("Test set accuracy: " + str(accuracy))
