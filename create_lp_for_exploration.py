from ortools.linear_solver import pywraplp
import json


def create_solver_and_player_assignment_variable(word_stats_dict):
    """
    Creates a dictionary with boolean variables in it. Each variable represents if word x is in the solution

    Parameters
    ----------
    word_stats_dict: dict
        Has information about the frequency of each word and its letters

    Returns
    -------
    x_var_dict: dict
        Boolean variables of the model
    solver: ortools.linear_solver.pywraplp.Solver
        MIP solver
    """
    # We create the solver
    solver = pywraplp.Solver('simple_mip_program',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    # We create the variables
    x_var_dict = {}
    for word in word_stats_dict:
        if word_stats_dict[word]['frequency'] > 1:
            x_var_dict[word] = solver.BoolVar(f'x_{word}')
    return x_var_dict, solver


def total_words_constraint(x_var_dict, solver):
    """
    We add a constraint that limits the number of words that will be used to 2. Mathematically this can be
    expressed in the following way

    sum{x_i} = 2

    Parameters
    ----------
    x_var_dict: dict
        Boolean variables of the model
    solver: ortools.linear_solver.pywraplp.Solver
        MIP solver

    Returns
    -------
    solver: ortools.linear_solver.pywraplp.Solver
        MIP solver
    """
    ct = solver.Constraint(2, 2, 'Words')
    for x in x_var_dict.keys():
        ct.SetCoefficient(x_var_dict[x], 1)
    return solver


def add_letter_constraint(x_var_dict, solver, letter):
    """
    We limit the number of wards that contain a particular letter to 1.
    If A is the set of words that contain the letter "a", and n_i is the number of times a specific letter
    (in this case, a, appears), we can express this in the following way

    sum{x \\in A} x_i*n_i <= 1

    Parameters
    ----------
    x_var_dict: dict
        Boolean variables of the model
    solver: ortools.linear_solver.pywraplp.Solver
        MIP solver
    letter: str
        Letter we are considering

    Returns
    -------
    solver: ortools.linear_solver.pywraplp.Solver
        MIP solver
    """
    ct = solver.Constraint(0, 1, letter)
    for x in x_var_dict.keys():
        # We check if the letter is in the word, and as a coefficient, we check the frequency of that letter in the word
        if letter in x:
            ct.SetCoefficient(x_var_dict[x], x.count(letter))
    return solver


def add_constraint_matrix(x_var_dict, solver, count_letters_dict):
    """
    Function that adds all the constraints of the model

    Parameters
    ----------
    x_var_dict: dict
        Boolean variables of the model
    solver: ortools.linear_solver.pywraplp.Solver
        MIP solver
    count_letters_dict: dict
        Has information about the frequency of each letter

    Returns
    -------
    x_var_dict: dict
        Boolean variables of the model
    solver: ortools.linear_solver.pywraplp.Solver
        MIP solver
    """
    solver = total_words_constraint(x_var_dict, solver)
    for letter in count_letters_dict.keys():
        solver = add_letter_constraint(x_var_dict, solver, letter)
    return solver


def set_obj_function(x_var_dict, solver, word_stats_dict):
    """
    We create the objective function of the problem, which will try to maximize the "letter_score" of the selected words
    Mathematically, this can be expressed in the following way:
    max sum{letter_score_i * x_i}

    Parameters
    ----------
    x_var_dict: dict
        Boolean variables of the model
    solver: ortools.linear_solver.pywraplp.Solver
        MIP solver
    word_stats_dict: dict
        Has information about the frequency of each word and its letters

    Returns
    -------
    x_var_dict: dict
        Boolean variables of the model
    solver: ortools.linear_solver.pywraplp.Solver
        MIP solver
    objective: ortools.linear_solver.pywraplp.Objective
        Objective of the MIP
    """
    objective = solver.Objective()
    for x in x_var_dict.keys():
        objective.SetCoefficient(x_var_dict[x], word_stats_dict[x]['letter_score'])
    objective.SetMaximization()
    solver.Solve()
    return x_var_dict, solver, objective


if __name__ == '__main__':
    # Read data
    with open('./processed_data/words_stats.json', 'r') as fp:
        word_stats_dict = json.load(fp)
    with open('./processed_data/letters_data.json', 'r') as fp:
        count_letters_dict = json.load(fp)

    # We create our variables and add it to a dictionary
    x_var_dict, solver = create_solver_and_player_assignment_variable(word_stats_dict)

    # Add constraints
    solver = add_constraint_matrix(x_var_dict, solver, count_letters_dict)

    # Add objective function and solve
    x_var_dict, solver, objective = set_obj_function(x_var_dict, solver, word_stats_dict)

    # We print the results of the selected words
    for word in x_var_dict:
        if round(x_var_dict[word].solution_value()) == 1:
            print(word, word_stats_dict[word])
