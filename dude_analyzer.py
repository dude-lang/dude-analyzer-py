from dude_ast import *


class Error(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class Warning(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class UseBeforeDefinition(Error):
    def __init__(self, var):
        super().__init__(f'Variable "{var}" used before definition.')


class ShadowingOuterScope(Warning):
    def __init__(self, var):
        super().__init__(f'Variable "{var}" shadows variable from outer scope.')
        

class Scope:
    def __init__(self):
        self.vars = []


def analyze_expression(expression: Statement, scope: Scope):
    def analyze_identifier(e):
        if e.name not in scope.vars:
            raise UseBeforeDefinition(e.name)

    def analyze_condition(e):
        analyze_expression(e.left, scope)
        analyze_expression(e.right, scope)

    def analyze_nested_expression(e):
        analyze_expression(e.expression, scope)

    def analyze_list(e):
        for el in e.elements:
            analyze_expression(el, scope)

    def analyze_sequence(e):
        analyze_expression(e.start, scope)
        analyze_expression(e.stop, scope)
        analyze_expression(e.step, scope)

    lookup = {
        EmptyStatement:   lambda x: x,
        Null:             lambda x: x,
        Number:           lambda x: x,
        Identifier:       analyze_identifier,
        Boolean:          lambda x: x,
        String:           lambda x: x,
        Character:        lambda x: x,
        Operator:         lambda x: x,
        Condition:        analyze_condition,
        NestedExpression: analyze_nested_expression,
        List:             analyze_list,
        Sequence:         analyze_sequence
    }

    t = type(expression)
    if t in lookup:
        lookup[t](expression)
    
    
def analyze_statement(statement: Statement, scope: Scope):
    def analyze_assignment_statement(s: AssignmentStatement):
        scope.vars.append(s.var.name)
        analyze_expression(s.expression, scope)

    def analyze_return_statement(s: ReturnStatement):
        analyze_expression(s.expression, scope)

    def analyze_structure_statement(s: StructureStatement):
        return 

    def analyze_while_statement(s: WhileLoopStatement):
        analyze_expression(s.condition, scope)

        for st in s.body:
            analyze_statement(st, scope)

    def analyze_for_statement(s: ForLoopStatement):
        if s.index.name in scope.vars:
            raise ShadowingOuterScope(s.index.name)

        scope.vars.append(s.index.name)
        analyze_expression(s.sequence, scope)

        for st in s.body:
            analyze_statement(st, scope)

    def analyze_function_statement(s: FunctionStatement):
        for var in s.arguments:
            if var.name in scope.vars:
                raise ShadowingOuterScope(var.name)
            scope.vars.append(var.name)

        for st in s.body:
            analyze_statement(st, scope)

    def analyze_condition_statement(s: ConditionalStatement):
        analyze_expression(s.if_condition, scope)
        analyze_expression(s.elif_condition, scope)

        for if_st in s.if_body:
            analyze_statement(if_st, scope)

        for elif_st in s.elif_body:
            analyze_statement(elif_st, scope)

        for else_st in s.else_body:
            analyze_statement(else_st, scope)

    lookup = {
        AssignmentStatement:  analyze_assignment_statement,
        ReturnStatement:      analyze_return_statement,
        StructureStatement:   analyze_structure_statement,
        WhileLoopStatement:   analyze_while_statement,
        ForLoopStatement:     analyze_for_statement,
        FunctionStatement:    analyze_function_statement,
        ConditionalStatement: analyze_condition_statement,
    }

    t = type(statement)
    if t in lookup:
        lookup[t](statement)


def analyze(ast: Program):
    scope = Scope()
    
    try:
        for statement in ast.statements:
            analyze_statement(statement, scope)
            
    except Error as e:
        print(e)
        return False
    
    except Warning as e:
        print(e)
        return True

    return True
