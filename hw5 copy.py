# CIS 473/573
# Homework #5
# Daniel Lowd
# May 2017
#
# TEMPLATE CODE 
#
import sys
import tokenize
import operator
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

class Factor:

    # Initialize a new factor object.
    def __init__(self, scope_, vals_):
        self.scope = scope_
        self.vals = vals_
        # Create dictionary from variable -> stride,
        # which will help when iterating through factor entries.
        self.stride = {}
        curr_stride = 1
        for v in scope_:
            self.stride[v] = curr_stride
            curr_stride *= var_ranges[v]
        # DEBUG
        #print "Scope:  ",self.scope
        #print "Stride: ",self.stride
        #print "Values: ",self.vals

    # Factor multiplication
    def __mul__(self, other):
        global var_ranges

        # New factor scope is union of the scopes of the old factors
        new_scope = list(set.union(set(self.scope), set(other.scope)))

        # Initialize helper variables for iterating through factor
        # tables.  First factor is "self", second is "other".
        phi1, stride1, index1 = self.vals, self.stride, 0
        phi2, stride2, index2 = other.vals, other.stride, 0

        # assignment keeps track of the current state of all
        # variables, which determines which factor entries to
        # multiply.
        assignment = {}
        for v in new_scope:
            assignment[v] = 0

        # Iterate through all variable assignments in the scope of the
        # new factor.  For each assignment, create the entry in the
        # new factor by multiplying the corresponding entries in the
        # original factors.  Use indices into each original factor,
        # and use variable strides to update them as we go.
        new_vals  = [];
        num_vals = reduce(operator.mul, [var_ranges[v] for v in new_scope], 1)
        for i in xrange(num_vals):
            # Add new value to the factor
            new_vals.append(phi1[index1] * phi2[index2])

            # Update indices
            # If incrementing the first variable would go past its range,
            # set it to zero and try to increment the next one, etc.
            #   e.g., (0,0,1,1) -> (0,1,0,0) 
            # Once we succeed in incrementing a variable, stop.
            for v in new_scope:
                if assignment[v] == var_ranges[v] - 1:
                    if v in stride1:
                        index1 -= stride1[v] * assignment[v]
                    if v in stride2:
                        index2 -= stride2[v] * assignment[v]
                    assignment[v] = 0

                # If we can increment this variable, do so and stop
                else:
                    assignment[v] += 1
                    if v in stride1:
                        index1 += stride1[v]
                    if v in stride2:
                        index2 += stride2[v]
                    break

        return Factor(new_scope, new_vals)

    def sumout(self, v):
        # You don't have to keep this code -- it's just one way of solving the problem.
        # This creates a new scope and a new set of values, initially zero, for the new
        # factor. You'll need to figure out how to compute the correct values.
        new_scope = self.scope[:]
        new_scope.remove(v)
        new_vals = []
        used_var = [False for i in range(len(self.vals))]

        for i in range(len(self.vals)/var_ranges[v]):
            new_vals.append(0)
            start = 0
            for k in range(len(self.vals)):
                if used_var[k] == False:
                    start = k
                    break

            for j in range(var_ranges[v]):
                new_vals[i] += self.vals[start + self.stride[v] * j]
                used_var[start + self.stride[v] * j] = True
        #### YOUR CODE GOES HERE ####
        new_factor = Factor(new_scope, new_vals)
        #debug
        #print("variable", v)
        #print("old table")
        #print(self)
        #print("new table")
        #print(new_factor)

        return new_factor
        #return Factor(new_scope, new_vals)

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
        scope.reverse()
        factor_scopes.append(scope)

    # Read in all factor values
    factor_vals = []
    for i in range(num_factors):
        factor_vals.append([next_float() for i in range(next_int())])

    # DEBUG
    #print "Num vars: ",num_vars
    #print "Ranges: ",var_ranges
    #print "Scopes: ",factor_scopes
    #print "Values: ",factor_vals
    return [Factor(s,v) for (s,v) in zip(factor_scopes,factor_vals)]


#
# MAIN PROGRAM
#

#def compute_z_varelim(factors):
def generate_mn_graph(factors):
    mn_graph = dict()
    for i in range(len(var_ranges)):
        mn_graph[i] = set()
        for j in factors:
            if i in j.scope:
                mn_graph[i] = mn_graph[i] | set(j.scope)
                #print "mn_graph[i]",i,mn_graph[i]
                #print "j.scope",j.scope
    return mn_graph

def find_min(mn_graph):
    min_node = -1
    for i in mn_graph:
        if min_node == -1:
            min_node = i
        else:
            if len(mn_graph[i]) < len(mn_graph[min_node]):
                min_node = i
    return min_node
        

def compute_z_varelim(factors):        
    ### YOUR CODE GOES HERE ####
    eliminate_factors = []

    mn_graph = generate_mn_graph(factors)

    for i in range(len(var_ranges)):
        min_node = find_min(mn_graph)
        #print "min_ndoe", min_node
        for j in factors:
           # print"whole factors",factors
            #print"iterate",j
            if min_node in j.scope:
                eliminate_factors.append(j)
                #print"eliminate_factors", eliminate_factors
            #else:
             #   print "do not exist",j.scope

        f = reduce(Factor.__mul__,eliminate_factors)
        z = f.sumout(min_node)
        factors = [x for x in factors if x not in eliminate_factors]
        factors.append(z)
        del mn_graph[min_node]
        for i in mn_graph:
            if min_node in mn_graph[i]:
                mn_graph[i].remove(min_node)
        #print "mn_graph", mn_graph
        #print "factors", factors

        del eliminate_factors[:]
    f = reduce(Factor.__mul__,factors)
    return sum(f.vals)


if __name__ == "__main__":
    factors = read_model()
    # Compute Z by variable elimination]
    #mn_graph = generate_mn_graph(factors)
    #min = find_min(mn_graph)
    #print "min", min
    z = compute_z_varelim(factors)
    print "Z = ",z
