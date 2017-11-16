from atl_model import *
import time
import pickle
import gc
import resource
import random
from sys import getsizeof


class SeleneModel:
    model = None
    states_dictionary = {}
    epistemic_states_dictionary = {}
    state_number = 0
    beginning_states_count = 0
    no_voters = 0
    no_candidates = 0
    coercer_number = 0
    defense_number = 0
    first_voter_number = 1
    first_state = {}
    environment_number = 0

    # Agents: 0 - coercer, 1..n - voters, n+1 - defense, n+2 - environment

    def __init__(self, no_voters, no_candidates):
        self.clear_variables()
        self.no_voters = no_voters
        self.no_candidates = no_candidates
        self.defense_number = no_voters + 1
        self.coercer_number = 0
        self.environment_number = no_voters + 2
        self.create_atl_model()
        self.create_actions()
        self.create_first_state()
        self.generate_rest_of_model()

    def clear_variables(self):
        self.model = None
        self.states_dictionary = {}
        self.epistemic_states_dictionary = {}
        self.no_voters = 0
        self.no_candidates = 0
        self.state_number = 0
        self.beginning_states_count = 0
        self.defense_number = 0
        self.coercer_number = 0
        self.first_state = {}
        self.environment_number = 0

    def create_atl_model(self):
        if self.no_voters == 1:
            self.model = ATLModel(self.no_voters + 2, 100)
        elif self.no_voters == 2:
            self.model = ATLModel(self.no_voters + 2, 1000)
        elif self.no_voters == 3:
            self.model = ATLModel(self.no_voters + 2, 100000)
        elif self.no_voters == 4:
            self.model = ATLModel(self.no_voters + 2, 3000000)
        else:
            self.model = ATLModel(self.no_voters + 2, 10000000)

        self.model.states = []

    def create_actions(self):
        for voter_number in range(1, self.no_voters + 1):
            self.model.add_action(voter_number, "FetchGoodTracker")
            self.model.add_action(voter_number, "CopyRealTracker")
            self.model.add_action(voter_number, "Wait")
            for candidate_number in range(1, self.no_candidates + 1):
                self.model.add_action(self.coercer_number,
                                      'RequestVote' + str(candidate_number) + "FromVoter" + str(voter_number))
                self.model.add_action(voter_number, "Vote" + str(candidate_number))
                self.model.add_action(voter_number, "HelpINeedVote" + str(candidate_number))
                self.model.add_action(self.defense_number,
                                      "SetFalseTrackerForVoter" + str(voter_number) + "To" + str(candidate_number))

            for voter_number2 in range(1, self.no_voters + 1):
                self.model.add_action(self.environment_number,
                                      'SetTracker' + str(voter_number) + 'To' + str(voter_number2))

        self.model.add_action(self.coercer_number, "Wait")
        self.model.add_action(self.defense_number, "Wait")
        self.model.add_action(self.environment_number, 'PublishVotes')
        self.model.add_action(self.environment_number, 'StartVoting')
        self.model.add_action(self.environment_number, 'Wait')

    def create_first_state(self):
        votes = []
        demanded_votes = []
        true_trackers_copied = []
        help_requests_sent = []
        public_votes = []
        trackers = []
        voters_votes = []
        voters_trackers_set = []
        voters_owned_trackers = []
        environment_demanded_votes = []
        false_or_copied_trackers_for_voters = []
        coercer_demanded_votes = []
        false_trackers_sent = []
        for i in range(1, self.no_voters + 1):
            votes.append(0)
            demanded_votes.append(0)
            true_trackers_copied.append(False)
            help_requests_sent.append(False)
            public_votes.append(0)
            trackers.append(0)
            voters_votes.append(0)
            voters_trackers_set.append(False)
            voters_owned_trackers.append(0)
            environment_demanded_votes.append(0)
            false_or_copied_trackers_for_voters.append(0)
            coercer_demanded_votes.append(0)
            false_trackers_sent.append(False)

        votes_published = False
        voting_started = False
        coerced_voters = 0
        max_coerced = 2

        self.first_state = {
            'Voter': {'Votes': votes, 'DemandedVotes': demanded_votes, 'TrueTrackersCopied': true_trackers_copied,
                      'HelpRequestSent': help_requests_sent},
            'Environment': {'PublicVotes': public_votes, 'Trackers': trackers,
                            'VotersVotes': voters_votes, 'VotersTrackersSet': voters_trackers_set,
                            'VotersOwnedTrackers': voters_owned_trackers,
                            'DemandedVotes': environment_demanded_votes,
                            'FalseOrCopiedTrackersForVoters': false_or_copied_trackers_for_voters,
                            'VotingStarted': voting_started, 'FalseTrackersSent': false_trackers_sent,
                            'VotesPublished': votes_published},
            'Coercer': {'DemandedVotes': coercer_demanded_votes, 'CoercedVoters': coerced_voters,
                        'MaxCoerced': max_coerced}}

        self.add_state(self.first_state)

    def generate_rest_of_model(self):
        current_state_number = -1
        for state in self.model.states:
            current_state_number += 1
            environment = state['Environment']
            voter = state['Voter']
            coercer = state['Coercer']
            if environment['VotingStarted'] == False:
                any_tracker_set = False
                for tracker_number in range(0, self.no_voters):
                    tracker = environment['Trackers'][tracker_number]
                    if tracker == 0:
                        for set_tracker_number in range(0, self.no_voters):
                            tracker_set = environment['VotersTrackersSet'][set_tracker_number]
                            if tracker_set == False:
                                new_state = copy.deepcopy(state)
                                new_state['Environment']['Trackers'][tracker_number] = set_tracker_number + 1
                                new_state['Environment']['VotersTrackersSet'][set_tracker_number] = True
                                new_state_number= self.add_state(new_state)
                                action = {0: 'Wait'}
                                for voter_number in range(1, self.no_voters + 1):
                                    action[voter_number] = 'Wait'
                                action[self.defense_number] = 'Wait'
                                action[self.environment_number] = 'SetTracker' + str(tracker_number + 1) + 'To' + str(set_tracker_number + 1)
                                self.model.add_transition(current_state_number, new_state_number, action)
                                any_tracker_set = True

                if any_tracker_set == False:
                    # start voting

                continue

            if environment['StartVoting'] == True and environment['PublishVotes'] = False:
                # Voters vote in any order
                # if everyone votes then publish votes?

    def add_state(self, state):
        new_state_number = self.get_state_number(state)
        epistemic_state = self.get_epistemic_state(state)
        self.add_to_epistemic_dictionary(epistemic_state, new_state_number)
        return new_state_number

    def get_state_number(self, state):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.states_dictionary:
            self.states_dictionary[state_str] = self.state_number
            new_state_number = self.state_number
            self.model.states.append(state)
            self.state_number += 1
        else:
            new_state_number = self.states_dictionary[state_str]

        return new_state_number

    def add_to_epistemic_dictionary(self, state, new_state_number):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.epistemic_states_dictionary:
            self.epistemic_states_dictionary[state_str] = {new_state_number}
        else:
            self.epistemic_states_dictionary[state_str].add(new_state_number)

    def get_epistemic_state(self, state):
        # epistemic_hands = state['hands'][:]
        # epistemic_hands[1] = self.keep_values_in_list(epistemic_hands[1], -1)
        # epistemic_hands[3] = self.keep_values_in_list(epistemic_hands[3], -1)
        # epistemic_state = {'hands': epistemic_hands, 'lefts': state['lefts'], 'next': state['next'],
        #                    'board': state['board'], 'beginning': state['beginning'], 'history': state['history'],
        #                    'clock': state['clock'], 'suit': state['suit']}
        # return epistemic_state
