# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0 {state: value, ...}
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"

        allStates = self.mdp.getStates()
        for count in range(self.iterations):
            newStateValues = self.values.copy()
            for state in allStates:
                if self.mdp.isTerminal(state):
                    continue
                else:
                    value = float('-inf')
                    actions = self.mdp.getPossibleActions(state)
                    for action in actions:
                        value = max(value, self.computeQValueFromValues(state, action))
                    newStateValues[state] = value
            self.values = newStateValues

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        Qvalue = 0
        for transition in self.mdp.getTransitionStatesAndProbs(state, action):
            Qvalue += transition[1] * (self.mdp.getReward(state, action, transition[0]) + self.discount * self.getValue(transition[0]))
        return Qvalue


    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        actions = self.mdp.getPossibleActions(state)
        maxVal = float('-inf')
        chosenAct = None
        if self.mdp.isTerminal(state):
            return None
        for action in actions:
            val = self.computeQValueFromValues(state, action)
            if val > maxVal:
                maxVal = val
                chosenAct = action

        return chosenAct

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        allStates = self.mdp.getStates()
        for count in range(self.iterations):
            state = allStates[count % len(allStates)]
            if not self.mdp.isTerminal(state):
                value = float('-inf')
                actions = self.mdp.getPossibleActions(state)
                for action in actions:
                    value = max(value, self.computeQValueFromValues(state, action))
                self.values[state] = value

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        allStates = self.mdp.getStates()
        predecessor = dict()
        for state in allStates:
            if not self.mdp.isTerminal(state):
                predecessor[state] = set()

        for state in allStates:
            if not self.mdp.isTerminal(state):
                for action in self.mdp.getPossibleActions(state):
                    for transition in self.mdp.getTransitionStatesAndProbs(state, action):
                        if not self.mdp.isTerminal(transition[0]):
                            predecessor[transition[0]].add(state)
        queue = util.PriorityQueue()

        for state in allStates:
            if not self.mdp.isTerminal(state):
                maxQ = float('-inf')
                for action in self.mdp.getPossibleActions(state):
                    Qvalue = self.computeQValueFromValues(state, action)
                    maxQ = max(maxQ, Qvalue)
                diff = abs(self.getValue(state) - maxQ)
                queue.push(state, -diff)

        for count in range(self.iterations):
            if queue.isEmpty():
                return
            else:
                state = queue.pop()
                maxQ = float('-inf')
                for action in self.mdp.getPossibleActions(state):
                    Qvalue = self.computeQValueFromValues(state, action)
                    maxQ = max(maxQ, Qvalue)
                self.values[state] = maxQ
                for predState in predecessor[state]:
                    maxQ = float('-inf')
                    for action in self.mdp.getPossibleActions(predState):
                        Qvalue = self.computeQValueFromValues(predState, action)
                        maxQ = max(maxQ, Qvalue)
                    diff = abs(self.getValue(predState) - maxQ)
                    if (diff > self.theta):
                        queue.update(predState, -diff)
