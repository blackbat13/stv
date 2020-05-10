from stv.logics.atl import Transition
import unittest


class TransitionTestSuite(unittest.TestCase):
    def test_should_not_allow_empty_actions(self):
        with self.assertRaises(ValueError):
            Transition(1, [])

    def test_should_not_allow_negative_state(self):
        with self.assertRaises(ValueError):
            Transition(-1, ["action"])

    def test_should_create_transition(self):
        next_state = 1
        actions = ["action"]
        transition = Transition(next_state, actions)
        self.assertEqual(next_state, transition.next_state)
        self.assertEqual(actions, transition.actions)
