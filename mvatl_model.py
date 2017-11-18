import atl_model
import mvatl_parser
import copy
import time


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

    def __init__(self, top, bottom, order):
        self.top = top
        self.bottom = bottom
        self.order = order
        self.diff = self.get_different()
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
            if self.compare(e, m) == -1:
                m = e
        return m


    def get_different(self):
        lat = self.upward_closure(self.bottom)
        diff = set()
        for x in lat:
            for y in lat:
                if (y not in self.upward_closure(x).union(self.downward_closure(x))) and \
                        (x not in self.upward_closure(y).union(self.downward_closure(y)))\
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


class MvATLModel(atl_model.ATLModel):
    lattice = None

    def __init__(self, number_of_agents, number_of_states, lattice):
        super(MvATLModel, self).__init__(number_of_agents, number_of_states)
        self.lattice = lattice

    def compute(self, formula, state):
        print(formula)
        if len(formula) == 4: # Ability Formula
            agent_set = formula[1]
            print("Ability not implemented")
            return self.lattice.bottom
        if len(formula) == 3: # Binary Formula
            res1 = self.compute(formula[0], state)
            res2 = self.compute(formula[2], state)
            if formula[1] == '<=': # Order Formula
                print("Order not implemented")
                return self.lattice.bottom
            elif formula[1] == '|': # Or
                return self.lattice.join(res1, res2)
            elif formula[1] == '&': # And
                return self.lattice.meet(res1, res2)
            elif formula[1] == 'U': # Until
                print("Until not implemented")
                return self.lattice.bottom
            elif formula[1] == 'W': # Weak until
                print("Weak until not implemented")
                return self.lattice.bottom
        elif len(formula) == 2: # Unary Formula
            if formula[0] == '!' or formula[0] == '~': # Negation
                #return self.lattice.neg(self.compute(formula[1])
                print("Negation not implemented")
                return self.lattice.bottom
            elif formula[0] == 'X' or formula[0] == '()': # Next
                print("Next not implemented")
                return self.lattice.bottom
            elif formula[0] == 'F' or formula[0] == '<>': # Eventually
                print("Eventually not implemented")
                return self.lattice.bottom
            elif formula[0] == 'G' or formula[0] == '[]': # Always
                print("Always not implemented")
                return self.lattice.bottom
        elif len(formula) == 1: # Zeroary Formula or Atomic Formula
            print("Zeroary or Atomic not implemented")
            return self.lattice.bottom
        else:
            print("Not Handled Formula")
            return self.lattice.bottom



    # @return: translation of the model w.r.t. l in JI(lattice)
    def make_translation(self, l):
        states_t = copy.deepcopy(self.states)
        i = 0
        j = 0
        for state in states_t:
            # TODO: Are they all prop ?
            for prop in state:
                for val in state[prop]:
                    if self.lattice.compare(val, l) > -1:
                        states_t[i][prop][j] = True
                    else:
                        states_t[i][prop][j] = False
                    j += 1
                j = 0
            i += 1
        # TODO: Does it requires a copy ?
        model_t = atl_model.ATLModel(self.number_of_agents, self.number_of_states)
        model_t.transitions = self.transitions
        model_t.reverse_transitions = self.reverse_transitions
        model_t.pre_states = self.pre_states
        model_t.imperfect_information = self.imperfect_information
        model_t.agents_actions = self.agents_actions
        model_t.states = states_t
        model_t.epistemic_class_disjoint = self.epistemic_class_disjoint
        model_t.epistemic_class_membership = self.epistemic_class_membership
        model_t.can_go_there = self.can_go_there
        return model_t


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


def generate_driving(mv_atl):
    state_o = {'Out': ['i', 'i'], 'In': ['i', 'i'], 'Penalty': ['b', 'b'], 'Collision': ['b']}
    state_i = {'Out': ['b', 'b'], 'In': ['t', 't'], 'Penalty': ['b', 'b'], 'Collision': ['b']}
    state_c = {'Out': ['b', 'b'], 'In': ['t', 't'], 'Penalty': ['u', 'u'], 'Collision': ['t']}

    for driver in range(0, mv_atl.number_of_agents):
        mv_atl.add_action(driver, 'in')
        mv_atl.add_action(driver, 'out')

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


# l2p4 = QBAlgebra('t', 'b', [('b', 'n'), ('n', 'i'), ('n', 'u'), ('i', 's'), ('u', 's'), ('s', 't')])
# test = MvATLModel(2, 3, l2p4)
# generate_driving(test)
# res = []


# props = "In Out Penalty Collision"
# const = "b n i u s t"
# atlparser = mvatl_parser.AlternatingTimeTemporalLogicParser(const, props)
# txt = "(<<1>> F In_1 <= u)"
# print(atlparser.parse(txt))
# test.compute(atlparser.parse(txt), test.states[0])