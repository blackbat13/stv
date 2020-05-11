from stv.logics.atl.atl_ir_model import ATLirModel
import copy

from stv.logics.atl.mv import mvatl_parser as P

__author__ = 'Arthur Queffelec'


class QBAlgebra:
    # List of couples (x,y), with x <= y
    # i.e. [(b,n),(n,i),(n,u),(i,s),(u,s),(s,t)]
    order = []

    # List of couples (x,y), with x >< y
    # i.e. [(i,u)]
    diff = []

    # List of l, with l in JI(lattice)
    # i.e. [n,i,u,t]
    join_irreducible = []

    # Top of the lattice
    # i.e. t
    top = ''

    # Bottom of the lattice
    # i.e. b
    bottom = ''

    def __init__(self, top, bottom, order, diff=None):
        self.top = top
        self.bottom = bottom
        self.order = order
        if diff == None:
            self.diff = self.get_different()
        else:
            self.diff = diff
        self.join_irreducible = self.get_join_irreducible()

    def upward_closure(self, l):
        closure = set()
        closure.add(l)
        for c in self.order:
            if c[0] == l:
                closure = closure.union(self.upward_closure(c[1]))
        return closure

    def downward_closure(self, l):
        closure = set()
        closure.add(l)
        for c in self.order:
            if c[1] == l:
                closure = closure.union(self.downward_closure(c[0]))
        return closure

    # @return : -1 inf, 0 equ, 1 sup, -2 diff
    def compare(self, l1, l2):
        if l1 is l2:
            return 0
        elif l1 in self.upward_closure(l2):
            return 1
        elif l1 in self.downward_closure(l2):
            return -1
        else:
            return -2

    def join(self, l1, l2):
        up_l1 = self.upward_closure(l1)
        up_l2 = self.upward_closure(l2)
        diff = up_l2.intersection(up_l1)
        m = diff.pop()
        for e in diff:
            if self.compare(e, m) == -1:
                m = e
        return m

    def join_list(self, l):
        if len(l) == 0:
            return self.bottom
        if len(l) > 1:
            return self.join(l[0], self.join_list(l[1:]))
        else:
            return l[0]

    def meet(self, l1, l2):
        down_l1 = self.downward_closure(l1)
        down_l2 = self.downward_closure(l2)
        diff = down_l2.intersection(down_l1)
        m = diff.pop()
        for e in diff:
            if self.compare(e, m) == 1:
                m = e
        return m

    def neg(self, l):
        n = set()
        for (x, y) in self.diff:
            if x == l:
                return y
            if y == l:
                return x

    def get_different(self):
        lat = self.upward_closure(self.bottom)
        diff = set()
        for x in lat:
            for y in lat:
                if (y not in self.upward_closure(x).union(self.downward_closure(x))) and \
                        (x not in self.upward_closure(y).union(self.downward_closure(y))) \
                        and (y, x) not in diff:
                    diff.add((x, y))
        return diff

    def get_join_irreducible(self):
        lat = self.upward_closure(self.bottom)
        ji = set(lat)
        for x in lat:
            for y in lat:
                j = self.join(x, y)
                if j == self.bottom or (j != x and j != y):
                    ji.discard(j)
        return ji


class MvATLirModel(ATLirModel):
    lattice = None

    def __init__(self, number_of_agents, lattice):
        super(MvATLirModel, self).__init__(number_of_agents)
        self.lattice = lattice

    # translate a single state for local model checking
    def translate_state(self, l, q):
        state = {}
        j = 0
        for prop in self.states[q]:
            if prop in self.props or prop == 'Turn':
                state[prop] = copy.deepcopy(self.states[q][prop])
        for prop in state:
            if prop == 'Turn':
                continue
            for val in state[prop]:
                if self.lattice.compare(val, l) > -1:
                    state[prop][j] = True
                else:
                    state[prop][j] = False
                j += 1
            j = 0
        return state

    # @return: translation of the model w.r.t. l in JI(lattice)
    # not used anymore
    def make_translation(self, l):
        states_t = []
        for i in range(0, len(self.states)):
            states_t.append(self.translate_state(l, i))
        # TODO: Does it requires a copy ?
        model_t = ATLirModel(self.number_of_agents)
        model_t.transitions = self.transitions
        model_t.reverse_transitions = self.reverse_transitions
        model_t.pre_states = self.pre_states
        model_t.imperfect_information = self.imperfect_information
        model_t.agents_actions = self.agents_actions
        model_t.states = states_t
        # model_t.epistemic_class_disjoint = self.epistemic_class_disjoint
        model_t.epistemic_class_membership = self.epistemic_class_membership
        # model_t.can_go_there = self.can_go_there
        return model_t

    def get_children(self, state):
        children = set()
        for tr in self.transitions[state]:
            children.add(tr['nextState'])
        return children

    # Handle every formula else than ability
    # returns true or false
    def simple_interpreter(self, formula, agent, l, n_s, state):
        if P.isBinary(formula):
            if P.isAnd(formula):
                return self.simple_interpreter(formula[0], agent, l, n_s, state) and self.simple_interpreter(formula[2],
                                                                                                             agent, l,
                                                                                                             n_s, state)
            if P.isOr(formula):
                return self.simple_interpreter(formula[0], agent, l, n_s, state) or self.simple_interpreter(formula[2],
                                                                                                            agent, l,
                                                                                                            n_s, state)
            if P.isUntil(formula):
                if self.simple_interpreter(formula[2], agent, l, n_s, state):
                    return True
                if self.simple_interpreter(formula[0], agent, l, n_s, state):
                    val = True
                    for child in self.get_children(n_s):
                        val = val and self.simple_interpreter(formula, agent, l, child, self.translate_state(l, child))
                    return val
                return False
            if P.isWeakUntil(formula):
                return self.simple_interpreter(
                    ('!', (('!', formula[2]), 'U', (('!', formula[0]), '&', ('!', formula[2])))), agent, l, n_s, state)
            if P.isOrder(formula):
                res = self.lattice.compare(self.order_interpreter(formula[0], agent, n_s),
                                           self.order_interpreter(formula[2], agent, n_s))
                return res != -2 and res <= 0
        if P.isUnary(formula):
            if P.isNot(formula):
                return not self.simple_interpreter(formula[1], agent, l, n_s, state)
            if P.isNext(formula):
                if 'Turn' in state:
                    if state['Turn'] != agent:
                        val = True
                        for child in self.get_children(n_s):
                            val = val and self.simple_interpreter(formula[1], agent, l, child,
                                                                  self.translate_state(l, child))
                        return val
                    val = False
                    for child in self.get_children(n_s):
                        val = val or self.simple_interpreter(formula[1], agent, l, child,
                                                             self.translate_state(l, child))
                    return val
            if P.isAlways(formula):
                return self.simple_interpreter((formula[1], 'W', self.lattice.bottom), agent, l, n_s, state)
            if P.isEventually(formula):
                return self.simple_interpreter((self.lattice.top, 'U', formula[1]), agent, l, n_s, state)
        if P.isAbility(formula):  # Not finished, cannot handle embedded ability formula
            return self.interpreter(formula, n_s)
            # winning_states = list()
            # for s in range(0, len(self.states)):
            #    c_s = self.translate_state(l, s)
            #    if self.simple_interpreter(formula[3], int(formula[1][0]), l, s, c_s):
            #        winning_states.append(s)
        if isinstance(formula, str):  # If is atomic proposition
            if '_' in formula:  # If has a subscript
                p = formula[:formula.index('_')]
                n = int(formula[formula.index('_') + 1:])  # - 1
                return state[p][n]
            if formula in self.props:
                return state[formula]
            return self.lattice.compare(formula, l) > -1

    # Handle the required translation for an order formula
    # returns true or false
    def order_interpreter(self, formula, agent, s):
        valid = list()
        for l in self.lattice.get_join_irreducible():
            state = self.translate_state(l, s)
            if self.simple_interpreter(formula, agent, l, s, state):
                valid.append(l)
        return self.lattice.join_list(valid)

    # Can only handle ability formula followed by box or diamond
    # returns true or false
    def interpreter(self, formula, initial_state):
        if P.isAbility(formula):
            if P.isEventually(formula[3]) or P.isAlways(formula[3]):
                valid = list()
                for l in self.lattice.get_join_irreducible():
                    winning_states = list()
                    result = None
                    agents = list(map(int, formula[1]))
                    for s in range(0, len(self.states)):
                        state = self.translate_state(l, s)
                        if self.simple_interpreter(formula[3][1], None, l, s, state):
                            winning_states.append(s)
                    if P.isAlways(formula[3]):
                        if len(formula[1]) == 0:  # E \phi
                            result = self.maximum_formula_no_agents(set(winning_states))
                        elif len(formula[1]) == 1:  # <<a>> \phi
                            result = self.maximum_formula_one_agent(int(agents[0]), set(winning_states))
                        else:  # <<C>> \phi
                            result = self.maximum_formula_many_agents(list(map(lambda a: int(a), agents)),
                                                                      set(winning_states))
                    if P.isEventually(formula[3]):
                        if len(formula[1]) == 0:  # E \phi
                            result = self.minimum_formula_no_agents(set(winning_states))
                        elif len(formula[1]) == 1:  # <<a>> \phi
                            result = self.minimum_formula_one_agent(int(agents[0]), set(winning_states))
                        else:  # <<C>> \phi
                            result = self.minimum_formula_many_agents(list(map(lambda
                                                                                   a: int(a), agents)),
                                                                      set(winning_states))
                    if len(result) > 0 and initial_state in list(result):
                        valid.append(l)
                return self.lattice.join_list(valid)
        elif P.isAnd(formula):
            l1 = self.interpreter(formula[0], initial_state)
            l2 = self.interpreter(formula[2], initial_state)
            return self.lattice.meet(l1, l2)
        elif P.isOr(formula):
            l1 = self.interpreter(formula[0], initial_state)
            l2 = self.interpreter(formula[2], initial_state)
            return self.lattice.join(l1, l2)
        elif P.isNot(formula):
            l = self.interpreter(formula[1], initial_state)
            return self.lattice.neg(l)


def print_create_for_state(state_number, state):
    msg = "CREATE (S" + str(state_number) + ":State { "
    i = 1
    # TODO: Are they all prop ?
    for prop in state:
        if len(state[prop]) > 1:
            for val in state[prop]:
                msg += "[" + prop + str(i) + "]" + " = " + str(val) + " "
                i += 1
            i = 1
        else:
            msg += "[" + prop + "]" + " = " + str(state[prop]) + " "
    msg += "]}"
    print(msg)


def generate_driving(mv_atl):  # generate the driving example of MVVSA (Jamroga:2016)
    state_o = {'Out': ['i', 'i'], 'In': ['i', 'i'], 'Penalty': ['b', 'b'], 'Collision': ['b']}
    state_i = {'Out': ['b', 'b'], 'In': ['t', 't'], 'Penalty': ['b', 'b'], 'Collision': ['b']}
    state_c = {'Out': ['b', 'b'], 'In': ['t', 't'], 'Penalty': ['u', 'u'], 'Collision': ['t']}

    for driver in range(0, mv_atl.number_of_agents):
        mv_atl.add_action(driver, 'in')
        mv_atl.add_action(driver, 'out')

    mv_atl.props = ['Out', 'In', 'Penalty', 'Collision']

    print_create_for_state(0, state_o)
    print_create_for_state(1, state_i)
    print_create_for_state(2, state_c)

    mv_atl.add_transition(0, 0, {0: 'in', 1: 'out'})
    mv_atl.add_transition(0, 0, {0: 'out', 1: 'in'})
    mv_atl.add_transition(0, 0, {0: 'out', 1: 'out'})
    mv_atl.add_transition(0, 1, {0: 'in', 1: 'in'})

    mv_atl.add_transition(1, 0, {0: 'in', 1: 'out'})
    mv_atl.add_transition(1, 0, {0: 'out', 1: 'in'})
    mv_atl.add_transition(1, 1, {0: 'in', 1: 'in'})
    mv_atl.add_transition(1, 2, {0: 'out', 1: 'out'})

    mv_atl.add_transition(2, 2, {0: 'out', 1: 'out'})

    mv_atl.states.append(state_o)
    mv_atl.states.append(state_i)
    mv_atl.states.append(state_c)
