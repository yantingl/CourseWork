# CIS 410/510pm
# Homework #4
# Daniel Lowd
# May 2017
#
# TEMPLATE CODE
import sys
import tokenize
import itertools
from collections import Counter

# List of variable cardinalities is global, for convenience.
# NOTE: This is not a good software engineering practice in general.
# However, the autograder code currently uses it to set the variable
# ranges directly without reading in a full model file, so please keep it
# here and use it when you need variable ranges!
var_ranges = []
# var_ranges = dict()


#
# FACTOR CLASS -- EDIT HERE!
#


"""
MARKOV          name of the network
3               number of random variables
2 2 3           cardinalities of variables
3               number of cliques in the problem
1 0
2 0 1           first integer in each line specifies the number of variables in the clique, followed by the actual indexes of the variables.
2 1 2
2               2 entried
 0.436 0.564
4
 0.128 0.872
 0.920 0.080
6
 0.210 0.333 0.457
 0.811 0.000 0.189
"""

class Factor(dict):
    """
    +---+---+---------+
    | Y | Z | P(Y, Z) |
    +---+---+---------+
    | 0 | 0 |   0.210 |
    | 0 | 1 |   0.333 |
    | 0 | 2 |   0.457 |
    | 1 | 0 |   0.811 |
    | 1 | 1 |   0.000 |
    | 1 | 2 |   0.189 |
    +---+---+---------+
    in this case scope will be [2, 3]
    because Y has 2 values and Z has 3 values
    therefore the stride should be [3, 1], because Y advances in 3 steps and Z
    advances in 1 step
    """
    def __init__(self, scope_, vals_):
        self.scope = scope_
        self.vals = vals_
        self.strides = Counter()
        strides_temp = [1]
        offset = min(self.scope)
        self.factor_var_ranges = [ var_ranges[item] for item in self.scope]
        for i in range(len(self.factor_var_ranges)):
            strides_temp.append(self.factor_var_ranges[i] * strides_temp[i])

        strides_temp.pop()

        for i in range(len(strides_temp)):
            self.strides[self.scope[i]] = strides_temp[i]

        print "self.strides",self.strides

    def indexOf(self, assignment):
        index = 0;
        for i in range(len(assignment)):
            index += assignment[i] * self.strides[i]

        return index

    # this function is tested correct
    def phi(self, assignment):
        """
        assignment should be a turple
        """
        if (len(assignment) != len(self.strides) ):
            # implement input error handling
            print ("illegal assignment")

        index = self.indexOf(assignment)
        return self.vals[index]


    def __mul__(self, other):
        def val_len(union):
            return reduce( lambda x, y: x * y, map( lambda x: var_ranges[x], union))


        j, k = 0, 0
        # the new scope of the new table
        new_scope = list(set(self.scope) | set(other.scope))

        # the new values of the new table
        new_vals = [-1] * val_len(new_scope)

        # initialize the assignments to all zeros
        # assignment = [0] * len( new_scope )


        # assignment cannot be an array because variable name might not start from one
        assignment = dict()
        for v in new_scope: assignment[v] = 0

        for i in range(len( new_vals )):
            new_vals[i] = self.vals[j] * other.vals[k]

            # l is all the varibles in the scope not an index
            for l in new_scope:
                assignment[l] = assignment[l] + 1
                if assignment[l] == var_ranges[l]:
                    assignment[l] = 0
                    j = j - (var_ranges[l] - 1) * self.strides[l]
                    k = k - (var_ranges[l] - 1) * other.strides[l]
                else:
                    j = j + self.strides[l]
                    print "self,strides j",self.strides[l]
                    k = k + other.strides[l]
                    print "self,strides k",other.strides[l]
                    break

        return Factor(new_scope, new_vals)

    def __rmul__(self, other):
        return self * other

    def __imul__(self, other):
        return self * other

    def __repr__(self):
        """Return a string representation of a factor."""
        rev_scope = self.scope[::-1]
        val = "x" + ", x".join(str(s) for s in rev_scope) + "\n"
        itervals = [range(var_ranges[i]) for i in rev_scope]
        for i,x in enumerate(itertools.product(*itervals)):
            val = val + str(x) + " " + str(self.vals[i]) + "\n"
        return val


#
# READ IN MODEL FILE
#

# Read in all tokens from stdin.  Save it to a (global) buf that we use
# later.  (Is there a better way to do this? Almost certainly.)
curr_token = 0
token_buf = []

def read_tokens():
    global token_buf
    for line in sys.stdin:
        token_buf.extend(line.strip().split())
    #print "Num tokens:",len(token_buf)

def next_token():
    global curr_token
    global token_buf
    curr_token += 1
    return token_buf[curr_token-1]

def next_int():
    return int(next_token())

def next_float():
    return float(next_token())

def read_model():
    # Read in all tokens and throw away the first (expected to be "MARKOV")
    read_tokens()
    s = next_token()

    # Get number of vars, followed by their ranges
    num_vars = next_int()
    global var_ranges
    global var_ranges
    var_ranges = [next_int() for i in range(num_vars)]

    # Get number and scopes of factors
    num_factors = int(next_token())
    factor_scopes = []
    for i in range(num_factors):
        scope = [next_int() for i in range(next_int())]
        # NOTE:
        #   UAI file format lists variables in the opposite order from what
        #   the pseudocode in Koller and Friedman assumes. By reversing the
        #   list, we switch from the UAI convention to the Koller and
        #   Friedman pseudocode convention.
        scope.reverse()
        factor_scopes.append(scope)

    # Read in all factor values
    factor_vals = []
    for i in range(num_factors):
        factor_vals.append([next_float() for i in range(next_int())])

    global_scope = sorted(reduce(lambda x, y: list(set(x) | set(y)), factor_scopes))

    return [Factor(s,v) for (s,v) in zip(factor_scopes,factor_vals)]


#
# MAIN PROGRAM
#

if __name__ == "__main__":
    factors = read_model()
    # Compute Z by brute force
    f = reduce(Factor.__mul__, factors)
    z = sum(f.vals)
    print "Z = " + str(z)
