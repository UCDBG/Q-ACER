

class operators:

    def apply_operator_bruteForce(self, row_value, condition_value, operator):
        # Define a dictionary mapping operators to their respective lambda functions
        ops = {
            '<': lambda x, y: x < y,
            '<=': lambda x, y: x <= y,
            '>': lambda x, y: x > y,
            '>=': lambda x, y: x >= y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
        }
        
        # Check if the operator is valid and apply the operation
        if operator in ops:
            return ops[operator](row_value, condition_value)
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    @classmethod
    def smaller(cls, x, y):
        try:
            return x < y
        except TypeError as e:
            print(f"x: {x} of type {type(x)}, y: {y} of type {type(y)}")
            raise e

    @classmethod
    def larger(cls, x, y):
        try:
            return x > y
        except TypeError as e:
            print(f"x: {x} of type {type(x)}, y: {y} of type {type(y)}")
            raise e

    @classmethod
    def leq(cls, x, y):
        try:
            return x <= y
        except TypeError as e:
            print(f"x: {x} of type {type(x)}, y: {y} of type {type(y)}")
            raise e

    @classmethod
    def geq(cls, x, y):
        try:
            return x >= y
        except TypeError as e:
            print(f"x: {x} of type {type(x)}, y: {y} of type {type(y)}")
            raise e

    @classmethod
    def eq(cls, x, y, z):
        try:
            return x == y and y == z
        except TypeError as e:
            print(f"x: {x} of type {type(x)}, y: {y} of type {type(y)}, z: {z} of type {type(z)}")
            raise e

    @classmethod
    def neq(cls, x, y, z):
        try:
            return x != y and y != z
        except TypeError as e:
            print(f"x: {x} of type {type(x)}, y: {y} of type {type(y)}, z: {z} of type {type(z)}")
            raise e                             
        
    def apply_operator(self, Min_value, Max_value, condition_value, operator, type):
        # Define a dictionary mapping operators to their respective lambda functions
        ops = {
            '<': operators.smaller, # lambda x, y: x < y,
            '<=': operators.leq, # lambda x, y: x <= y,
            '>': operators.larger, # lambda x, y: x > y,
            '>=': operators.geq, # lambda x, y: x >= y,
            '==': operators.eq, # lambda x, y, z: x == z and y == z, # All points are exactly equal
            '!=': operators.neq, # lambda x, y, z: x != z and y != z # All points are not equal
        }
    
        # Check if the operator is valid and apply the operation
        if operator == '>=' and type == "Full":
            return ops[operator](Min_value, condition_value)
        elif operator == '<=' and type == "Full":
            return ops[operator](Max_value, condition_value)
        elif operator == '>' and type == "Full":
            return ops[operator](Min_value, condition_value)
        elif operator == '<' and type == "Full":
            return ops[operator](Max_value, condition_value)
        elif operator == '==' and type == "Full":
            return ops[operator](Min_value, Max_value, condition_value)
        elif operator == '!=' and type == "Full":
            return ops[operator](Min_value, Max_value, condition_value)

        '''
        operators_partial = {
            '==': lambda x_min, x_max, y: (x_min <= y and x_max > y) or (x_min < y and x_max >= y), #one of min and max is == and the other is not
            '!=': lambda x_min, x_max, y: (x_min != y and x_max == y) or (x_min == y and x_max != y)  #one of min and max is != and the other is ==
        }
        if operator == '>=' and type == "Partial":
            return ops[operator](Max_value, condition_value)
        elif operator == '<=' and type == "Partial":
            return ops[operator](Min_value, condition_value)
        elif operator == '>' and type == "Partial":
            return ops[operator](Max_value, condition_value)
        elif operator == '<' and type == "Partial":
            return ops[operator](Min_value, condition_value)

        elif operator == '==' and type == "Partial":
            return operators_partial[operator](Min_value, Max_value, condition_value)
        elif operator == '!=' and type == "Partial":
            return ops[operator](Min_value, Max_value, condition_value)
        
        else:
            raise ValueError("Unsupported operator")
        '''


    @classmethod
    def eq_range(cls, a, b, x, y):
        try:
            return x == y and y == a and a == b
        except TypeError as e:
            print(f"a: {a} of type {type(a)}, b: {b} of tbpe {type(b)}, x: {x} of type {type(x)}, y: {y} of type {type(y)}")
            raise e

    @classmethod
    def neq_range(cls, a, b, x, y):
        try:
            return (a > y or x > b)
        except TypeError as e:
            print(f"a: {a} of type {type(a)}, b: {b} of tbpe {type(b)}, x: {x} of type {type(x)}, y: {y} of type {type(y)}")
            raise e

    @classmethod
    def eq_range_partial(cls, a, b, x, y):
        try:
            return (a <= y and x <= b)
        except TypeError as e:
            print(f"a: {a} of type {type(a)}, b: {b} of tbpe {type(b)}, x: {x} of type {type(x)}, y: {y} of type {type(y)}")
            raise e

    @classmethod
    def neq_range_partial(cls, a, b, x, y):
        try:
            return (a <= y and x <= b)
        except TypeError as e:
            print(f"a: {a} of type {type(a)}, b: {b} of tbpe {type(b)}, x: {x} of type {type(x)}, y: {y} of type {type(y)}")
            raise e
        
    def apply_operator_ranges(self, Min_value, Max_value, Min_condition, Max_condition, operator, type):
        # Define a dictionary mapping operators to their respective lambda functions
        ops = {
            '<': operators.smaller, # lambda x, y: x < y,
            '<=': operators.leq, # lambda x, y: x <= y,
            '>': operators.larger, # lambda x, y: x > y,
            '>=': operators.geq, # lambda x, y: x >= y,
            '==': operators.eq_range, # lambda x, y, z: x == z and y == z, # All points are exactly equal
            '!=': operators.neq_range, # lambda x, y, z: x != z and y != z # All points are not equal
            # '<': lambda x, y: x < y,
#             '<=': lambda x, y: x <= y,
#             '>': lambda x, y: x > y,
#             '>=': lambda x, y: x >= y,
            # '==': lambda a, b, x, y: a == b == x == y, #all values from cluster fulfill condition for all values from the range
            # '!=': lambda a, b, x, y: (a > y or x > b) #Equivelant to (not(a <= y and x <= b))  
            #no value from the cluster can fulfill the condition for any value from the range

        }
        operators_partial = {
            '==': operators.eq_range_partial, # lambda a, b, x, y: (a <= y and x <= b), #some value from the cluster may fulfill the condition for some value from the range
            '!=': operators.neq_range_partial, # lambda a, b, x, y: (a <= y and x <= b)  #some value from the cluster may not fulfill the condition for some value from the range
        }
    
        # Check if the operator is valid and apply the operation
        if operator == '>=' and type == "Full":
            return ops[operator](Min_value, Max_condition)
        elif operator == '<=' and type == "Full":
            return ops[operator](Max_value, Min_condition)
        elif operator == '>' and type == "Full":
            return ops[operator](Min_value, Max_condition)
        elif operator == '<' and type == "Full":
            return ops[operator](Max_value, Min_condition)
        elif operator == '==' and type == "Full":
            return ops[operator](Min_value, Max_value, Min_condition, Max_condition)
        elif operator == '!=' and type == "Full":
            return ops[operator](Min_value, Max_value, Min_condition, Max_condition)

        if operator == '>=' and type == "Partial":
            return ops[operator](Max_value, Min_condition)
        elif operator == '<=' and type == "Partial":
            return ops[operator](Min_value, Max_condition)
        elif operator == '>' and type == "Partial":
            return ops[operator](Max_value, Min_condition)
        elif operator == '<' and type == "Partial":
            return ops[operator](Min_value, Max_condition)
        elif operator == '==' and type == "Partial":
            return operators_partial[operator](Min_value, Max_value, Min_condition, Max_condition)
        elif operator == '!=' and type == "Partial":
            return ops[operator](Min_value, Max_value, Min_condition, Max_condition)

        else:
            raise ValueError("Unsupported operator")


 
    
    

