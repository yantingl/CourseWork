# CIS 410/510pm
# Homework #4
# Daniel Lowd
# May 2017
#
# TEMPLATE CODE

#Modified By Yanting Liu, Guangyun Hou

import sys
import tokenize
import itertools

# List of variable cardinalities is global, for convenience.
# NOTE: This is not a good software engineering practice in general.
# However, the autograder code currently uses it to set the variable 
# ranges directly without reading in a full model file, so please keep it
# here and use it when you need variable ranges!
var_ranges = []


#
# FACTOR CLASS
#

class Factor(dict):
    def __init__(self, scope_, vals_):
        self.scope = scope_
        self.vals = vals_
        self.strides = [0] * len(var_ranges)
        temp_strides = [1]

        self.factor_var_ranges = [var_ranges[item] for item in self.scope]
        

        for i in range(len(self.factor_var_ranges)):
            temp_strides.append(temp_strides[i] * self.factor_var_ranges[i])
        #print "temp",temp_strides

        for i in range(len(temp_strides) - 1):
            self.strides[self.scope[i]] = temp_strides[i]

        #print "self.strides", self.strides
        #print "self.vals",self.vals

        # TODO -- ADD EXTRA INITIALIZATION CODE IF NEEDED
    
    def __mul__(self, other):
        """Returns a new factor representing the product."""
        def vals_len(union):
            val_len = 1
            for i in union:
                val_len = val_len * var_ranges[i]
            return val_len
        j = 0
        k = 0
        assignment = [0]*len(var_ranges)
        new_vals = []
        new_strides = []
        new_scope = list(set(self.scope).union(set(other.scope)))
        factor_num_vals = vals_len(new_scope)
        #print"factor_num_vals",factor_num_vals
        #print "new_scope",new_scope
        
        #for l in new_scope:
         #   assignment[l] = 0

        for i in range(factor_num_vals):
            new_vals.append(self.vals[j] * other.vals[k])
            for l in new_scope:
                assignment[l] = assignment[l] + 1;
                if assignment[l] == var_ranges[l]:
                    assignment[l] = 0;
                    j = j - (var_ranges[l] - 1) * self.strides[l]
                    k = k - (var_ranges[l] - 1) * other.strides[l]
                else:
                    j = j + self.strides[l];
                    k = k + other.strides[l];
                    #print "strides j", self.strides[l]
                    #print "self",self.vals
                    #print "strides k", other.strides[l]
                    #print "other",other.vals
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
    global var_ranges;
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

    # DEBUG
    print "Num vars: ",num_vars
    print "Ranges: ",var_ranges
    print "Scopes: ",factor_scopes
    print "Values: ",factor_vals
    return [Factor(s,v) for (s,v) in zip(factor_scopes,factor_vals)]


#
# MAIN PROGRAM
#

if __name__ == "__main__":
    factors = read_model()
    # Compute Z by brute force
    f = reduce(Factor.__mul__, factors)
    z = sum(f.vals)
    print "Z = ",z
