from random import randint, choice
import tkinter as tk
from tkinter import filedialog as fd
from os import getcwd
from tkinter.messagebox import showinfo
from time import time

"""
########################
HELPER FUNCTIONS
########################
"""

# creates number_of_items random items with random weight and random price
def create_random_items(number_of_items):
    items = []
    for _ in range(number_of_items):
        price = randint(1, 50)
        weight = randint(1, 10)
        item = (price, weight)
        items.append(item)
    return items


"""
########################
EVOLUTION ALGORITHM 
########################
"""

# initializes number_of_solutions solutions each of the length of items
def initialize(items, number_of_solutions):
    solutions = []
    for _ in range(number_of_solutions):
        solution = [randint(0, 1) for _ in range(len(items))]
        solutions.append(solution)
    return solutions


# evaluates single solution according to the list of items
def evaluate_single(solution, items, max_weight):
    total_price = sum(item[0] for i, item in enumerate(items) if solution[i])
    total_weight = sum(item[1] for i, item in enumerate(items) if solution[i])
    if total_weight <= max_weight:
        return total_price
    return -(total_price * (total_weight - max_weight))


# evaluates every solution from solutions, according to the list of items and max weight
def evaluate(solutions, items, max_weight):
    return [evaluate_single(solution, items, max_weight) for solution in solutions]


# selects top n solutions from solutions evaluated using their fitnesses
def select(solutions, fitnesses, n):
    solutions_sorted = [i for _, i in sorted(zip(fitnesses, solutions), reverse=True)]
    return solutions_sorted[:int(len(solutions) * n / 100)]


# takes two parent solution and randomly creates one of their children (using half from each parent solution)
def crossover_single(solution_1, solution_2):
    if randint(0, 1):
        return solution_1[:int(len(solution_1) / 2)] + solution_2[int(len(solution_2) / 2):]
    return solution_1[int(len(solution_1) / 2):] + solution_2[:int(len(solution_2) / 2)]


# takes the top solutions and creates number_of_solutions new solutions
def crossover(solutions, number_of_solutions):
    new_solutions = []
    while len(new_solutions) < number_of_solutions:
        new_solutions.append(crossover_single(choice(solutions), choice(solutions)))
    return new_solutions


# takes single solutions and flips number of bits determined by the intensity
def mutate_single(solution, intensity):
    if intensity == 0:
        return solution
    for _ in range(int(len(solution) * intensity / 100)):
        position = randint(0, len(solution) - 1)
        solution[position] = not solution[position]
    return solution


# takes all the solutions and performs mutation
def mutate(solutions, intensity):
    return [mutate_single(solution, intensity) for solution in solutions]


def format_generation(generation, items, solution, max_weight, fitnesses):
    output = f"Generation: {generation}\n"
    output += f"Maximal price: {max(fitnesses)}\n"
    total_weight = sum(item[1] for i, item in enumerate(items) if solution[i])
    output += f"Weight of this solution: {total_weight}/{max_weight}\n"
    output += f"Average price: {sum(fitnesses) / len(fitnesses)}\n"
    output += f"-------------------------------\n"
    return output


def format_best_solution(solution, items, price, max_weight):
    output = f"BEST SOLUTION\n"
    output += f"Price: {price}\n"
    selected_items = [(i, item) for i, item in enumerate(items) if solution[i]]
    total_weight = sum(item[1][1] for item in selected_items)
    output += f"Weight of this solution: {total_weight}/{max_weight}\n"
    selected_items_format = ""
    for item in selected_items:
        selected_items_format += f"#{item[0] + 1} : {item[1]}, "
    output += f"Selected items: {selected_items_format}\n"
    return output


def evolution(length, items, mutation_intensity, selection, max_weight, starting_population, save_to_file):
    if save_to_file:
        f = open("results.txt", "w")
    start = time()
    solutions = initialize(items, starting_population)
    best_solution = [0, []]

    for i in range(length):
        fitnesses = evaluate(solutions, items, max_weight)
        solutions = select(solutions, fitnesses, selection)
        if save_to_file:
            f.write(format_generation(i, items, solutions[0], max_weight, fitnesses))
        if max(fitnesses) > best_solution[0]:
            best_solution[0] = max(fitnesses)
            best_solution[1] = solutions[0]
        solutions = crossover(solutions, starting_population)
        solutions = mutate(solutions, mutation_intensity)
    end = time()
    output = format_best_solution(best_solution[1], items, best_solution[0], max_weight)
    output += f"\nTotal time elapsed: {round(end - start, 4)} seconds"
    if save_to_file:
        f.write(output)
    if save_to_file:
        f.close()
    return output


"""
########################
LOADING ITEMS FROM FILE
########################
"""


def load_items(filename):
    with open(filename, "r") as f:
        content = f.read().splitlines()

    items = []
    for item in content:
        item = item.split(",")
        items.append((int(item[0]), int(item[1])))

    return items


"""
########################
GUI
########################
"""

ITEMS = []


def get_items():
    global ITEMS
    global item_fields
    for i in range(20):
        price = item_fields[i][0].get()
        weight = item_fields[i][1].get()
        if not price or not weight:
            break
        if not price.isnumeric() or not weight.isnumeric():
            showinfo(title='Error: Not a number', message="Invalid input in one of the item fields. Fix it first")
            break
        ITEMS.append((int(price), int(weight)))


window = tk.Tk()
window.geometry("1000x500")
window.title("Knapsack problem evolution solver")
items_label = tk.Label(text="Items (in format price, weight)")
items_label.pack()
item_fields = []

items_frame = tk.Frame()

for i in range(0, 2):
    for j in range(0, 10):
        item_frame = tk.Frame(highlightbackground="black", highlightthickness=1, master=items_frame)
        price_input = tk.Entry(master=item_frame, width=3)
        weight_input = tk.Entry(master=item_frame, width=3)
        item_fields.append((price_input, weight_input))

        price_input.pack(side=tk.LEFT)
        weight_input.pack(side=tk.LEFT)
        item_frame.grid(padx=5, pady=5, row=i, column=j)

items_frame.pack()


# gets filename from user, if it's too big to display, loads it to ITEMS variable, otherwise diplays it in input fields
def process_file():
    global ITEMS
    global item_fields
    filetypes = (
        ('text files', '*.txt'),
    )
    filename = fd.askopenfilename(
        title='Select file',
        initialdir=getcwd(),
        filetypes=filetypes)
    ITEMS = load_items(filename)
    if len(ITEMS) > len(item_fields):
        showinfo(title='Too many items to display', message="The file was successfully processed but there "
                                                            "to many items to display. You can run the evolution "
                                                            "anyways")
    else:
        for i in range(len(item_fields)):
            item_fields[i][0].delete(0, tk.END)
            item_fields[i][0].insert(0, str(ITEMS[i][0]))
            item_fields[i][1].delete(0, tk.END)
            item_fields[i][1].insert(0, str(ITEMS[i][1]))
        ITEMS = []


tk.Label(text="Load items from file instead").pack()
tk.Button(text="Select file", command=process_file).pack()

parameters_frame = tk.Frame()
tk.Label(master=parameters_frame, text="Maximal weight").grid(row=0, column=0)
max_weight_input = tk.Entry(master=parameters_frame, width=5)
max_weight_input.grid(row=0, column=1)

tk.Label(master=parameters_frame, text="Starting population").grid(row=1, column=0)
starting_population_input = tk.Entry(master=parameters_frame, width=5)
starting_population_input.grid(row=1, column=1)
tk.Label(master=parameters_frame, text="(number of solutions in the start)").grid(row=1, column=2)

tk.Label(master=parameters_frame, text="Mutation intensity").grid(row=2, column=0)
mutation_intensity_input = tk.Entry(master=parameters_frame, width=5)
mutation_intensity_input.grid(row=2, column=1)
tk.Label(master=parameters_frame, text="(how many percent of genes will be mutated)").grid(row=2, column=2)

tk.Label(master=parameters_frame, text="Selection").grid(row=3, column=0)
selection_input = tk.Entry(master=parameters_frame, width=5)
selection_input.grid(row=3, column=1)
tk.Label(master=parameters_frame, text="(how many percent of best solutions will be selected)").grid(row=3, column=2)

tk.Label(master=parameters_frame, text="Length of evolution").grid(row=4, column=0)
length_input = tk.Entry(master=parameters_frame, width=5)
length_input.grid(row=4, column=1)
tk.Label(master=parameters_frame, text="(number of generations)").grid(row=4, column=2)

save_to_file = tk.IntVar()
tk.Checkbutton(parameters_frame, text='Save to file (results.txt)', variable=save_to_file,
                                    onvalue=1, offvalue=0).grid(row=5, column=0)

parameters_frame.pack()


def run_evolution():
    global max_weight_input, starting_population_input, mutation_intensity_input, selection_input, length_input, \
        save_to_file, ITEMS
    try:
        max_weight = int(max_weight_input.get())
        starting_population = int(starting_population_input.get())
        mutation_intensity = int(mutation_intensity_input.get())
        selection = int(selection_input.get())
        length = int(length_input.get())
    except:
        showinfo(title='Error: Not a number', message="Invalid input in one of the parameter fields. Fix it first")
        return
    if not ITEMS:
        get_items()
    output = evolution(length, ITEMS, mutation_intensity, selection, max_weight, starting_population,
                       save_to_file.get())
    results.config(text=output)


tk.Button(text="RUN", command=run_evolution).pack()

result_frame = tk.Frame()
results = tk.Label(master=result_frame, text="")
results.grid(row=0, column=0)
result_frame.pack()

window.mainloop()
