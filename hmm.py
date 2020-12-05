"""HMM_Algorithms.py

by Ben Yu, Kevin Zhu

date: 12/5/2020

for CSE 473 Project Option 2, Autumn 2020
University of Washington

Provide your own implementations of the Forward algorithm and the Viterbi
algorithm in the provided function templates.

Your Forward algorithm should compute the belief vector B_t at each point t in
time. Here B_t(s) = P(S_t=s | E_1=e_1, E_2=e_2, ..., E_t=e_t). Here E_t
represents the emission at time step t. When show is True, it should display 
the belief values next to each of the nodes.

Your Viterbi algorithm should for each node compute the probability of reaching
that node from the start along the most probable path. When show is True, it
should display this probability next to each of the nodes, and it should
highlight the (or a) most probable path.
"""

import json

import hmm_vis as hv


class HMM:
    """ class that represents an HMM model with functions for the Forward and
        Viterbi algorithms """

    def __init__(self, filename=None):
        """ initialize parameters and other helper variables """
        self.S = None
        self.O = None
        self.P_trans = None
        self.P_emission = None
        if filename is not None:
            self.load_parameters(filename)
        # Add other instance variables you might need below.

    def load_parameters(self, filename):
        """ load HMM model parameters from JSON file """
        with open(filename, 'r') as f:
            parameters = json.load(f)
        self.S = parameters['S']
        self.O = parameters['O']
        self.P_trans = parameters['P_trans']
        self.P_emission = parameters['P_emission']

    def forward_algorithm(self, obs_sequence, show=False):
        if show:
            hv.show_entire_trellis(self.S, obs_sequence,
                                   has_initial_state=True)
            # Demo of node highlighting.
            hv.highlight_node(0, '<S>', highlight=True)
            # highlight/unhighlight other nodes as appropriate
            # to show progress.

        # Put your code implementing the Forward algorithm here. When 
        # debugging, use calls to highlight_node and show_node_label to 
        # illustrate the progress of your algorithm.
        beliefs = []
        prev_dist = {'<S>': 1}
        layer = 1
        for obs in obs_sequence:
            dist_map = {}
            dist = []
            total = 0
            for s in self.S:
                if s != '<S>' and s != '<E>':
                    p_s = 0
                    if obs in self.P_emission[s]:
                        e = self.P_emission[s][obs]
                    else:
                        e = 0
                    for s_prime in prev_dist:
                        p_s += prev_dist[s_prime] * self.P_trans[s_prime][s]
                    p_s *= e if obs in self.O else 0
                    dist_map[s] = p_s
                    dist.append(p_s)
                    total += p_s
            # normalizing beliefs to sum to 1
            for s in dist_map:
                if total > 0:
                    dist_map[s] /= total
                if show:
                    hv.show_label_at_node(layer, s, str(dist_map[s]), dy=30)
            if total > 0:
                for i in range(len(dist)):
                    dist[i] /= total
            beliefs.append(dist)
            prev_dist = dist_map
            layer += 1
        return beliefs

    def viterbi_algorithm(self, obs_sequence, show=False):
        if show:
            hv.show_entire_trellis(self.S, obs_sequence,
                                   has_initial_state=True)
            hv.highlight_node(0, '<S>')         # Demo of node highlighting.
            # hv.highlight_edge(0, '<S>', 'M')    # Demo of edge highlighting.
            # highlight other nodes and edges as appropriate
            # to show progress and results.

        # Put your code implementing the Viterbi algorithm here. When 
        # debugging, use calls to highlight_node and show_node_label to 
        # illustrate the progress of your algorithm.
        state_seq = [None] * len(obs_sequence)
        viterbi = [{}]
        back_ptrs = [{}]
        states = [s for s in self.S if s != '<S>' and s != '<E>']
        for s in states:
            viterbi[0][s] = self.P_trans['<S>'][s] *\
                            (self.P_emission[s][obs_sequence[0]] if obs_sequence[0]
                             in self.P_emission[s] else 0)
            back_ptrs[0][s] = '<S>'
        for t in range(1, len(obs_sequence)):
            viterbi_dict = {}
            back_ptrs_dict = {}
            for s in states:
                argmax = None
                mx = None
                for k in states:
                    value = viterbi[t - 1][k] * self.P_trans[k][s] *\
                            (self.P_emission[s][obs_sequence[t]] if obs_sequence[t]
                             in self.P_emission[s] else 0)
                    if mx is None or value > mx:
                        mx = value
                        argmax = k
                viterbi_dict[s] = mx
                back_ptrs_dict[s] = argmax
            viterbi.append(viterbi_dict)
            back_ptrs.append(back_ptrs_dict)
        mx = None
        for s in states:
            if mx is None or viterbi[-1][s] > mx:
                mx = viterbi[-1][s]
                state_seq[-1] = s
        for t in reversed(range(1, len(obs_sequence))):
            state_seq[t - 1] = back_ptrs[t][state_seq[t]]
        if show:
            prev_state = '<S>'
            for t in range(len(obs_sequence)):
                hv.show_label_at_node(t + 1, state_seq[t], str(viterbi[t][state_seq[t]]), dy=30)
                hv.highlight_node(t + 1, state_seq[t])
                hv.highlight_edge(t, prev_state, state_seq[t])
                prev_state = state_seq[t]
            hv.highlight_node(len(obs_sequence), '<E>')
            hv.highlight_edge(len(obs_sequence), prev_state, '<E>')
        return state_seq


if __name__ == '__main__':
    sample_obs_seq = ['Jane', 'Will', 'Spot', 'Will']
    model = HMM('toy_pos_tagger.json')
    beliefs = model.forward_algorithm(sample_obs_seq, show=True)
    hv.hold()
    state_seq = model.viterbi_algorithm(sample_obs_seq, show=True)
    hv.hold()

