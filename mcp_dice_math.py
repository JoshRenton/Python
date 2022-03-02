from cgitb import text
from math import factorial
import tkinter as tk
from turtle import width

from numpy import arange

class Dice:
    # The dices sides along with the probability of that side being rolled.
    hit_proba = 0.25
    block_proba = 0.125
    wild_proba = 0.125
    crit_proba = 0.125
    blank_proba = 0.25
    failure_proba = 0.125

    # Store probabilities in array to reduce need for for loops to find probabilities.
    face_probas = [hit_proba, block_proba, wild_proba,
                   crit_proba, blank_proba, failure_proba]

    # Stores the faces of the dice considered to be a success.
    successful_faces = []

    def __init__(self, successful_faces):
        self.successful_faces = successful_faces

    def remove_successful_face(self, face):
        if face in self.successful_faces:
            self.successful_faces.remove(face)

    def add_successful_face(self, face):
        if face not in self.successful_faces:
            self.successful_faces.append(face)

    # Converts input face string to it's index in face_probas.
    def face_to_index(self, face):
        if(face == 'hit'):
            return 0
        if(face == 'block'):
            return 1
        if(face == 'wild'):
            return 2
        if(face == 'crit'):
            return 3
        if(face == 'blank'):
            return 4
        if(face == 'failure'):
            return 5

    # Sets a new probability for the given dice face.
    def change_dice_proba(self, face, new_proba):
        index = self.face_to_index(face)
        self.face_probas[index] = new_proba

    # Takes a dice faces index as an argument and outputs the probability of rolling that face off of one die.
    def get_face_proba(self, index):
        return self.face_probas[index]

    # Takes in a list of unique faces and returns the probability of any of those faces being rolled.
    def total_expected_proba(self):
        proba = 0.0
        for face in self.successful_faces:
            index = self.face_to_index(face)
            proba += self.get_face_proba(index)
        return proba


# Returns value of n choose k formula.
def n_choose_k(n, k):
    return factorial(n) / (factorial(k) * factorial(n - k))

# Takes the number of desired crits and number of successes rolled as input and outputs the probability of getting that many crits from that many successes.
def initial_crits(dice, num_successes, num_crits):
    total_success_proba = dice.total_expected_proba()
    crit_proba_given_success = (dice.face_probas[3] / total_success_proba)
    return n_choose_k(num_successes, num_crits) * pow(crit_proba_given_success, num_crits) * pow(1 - crit_proba_given_success, (num_successes - num_crits))

def initial_roll(dice, n, k):
    expected = dice.total_expected_proba()
    proba = n_choose_k(n, k) * pow(expected, k) * pow(1 - expected, n - k)

    return proba

# Returns probability of rolling k successes in n dice.
# Loops through each permutation of initial_successes, possible crits from those successes and successes from those crits
# and sums all permutations that sum to k.
def roll_proba(dice, n, k):
    proba = 0.0
    for i in range(n, -1, -1):
        initial_proba = initial_roll(dice, n, i)
        for j in range(0, i + 1):
            crits_proba = initial_crits(dice, i, j)
            for l in range(0, j + 1):
                crits_success_proba = initial_roll(dice, j, l)
                if (i + l) == k:
                    proba += initial_proba * crits_proba * crits_success_proba

    return proba


# Returns probability of rolling k or more successes from n dice.
def gt_cumulative_proba(dice, n, k):
    cumulative_proba = 0.0
    for i in range(0, k):
        cumulative_proba += roll_proba(dice, n, i)

    return 1 - cumulative_proba


def lt_cumulative_proba(dice, n, k):
    cumulative_proba = 0.0
    for i in range(0, k + 1):
        cumulative_proba += roll_proba(dice, n, i)
    
    return cumulative_proba 


def print_all_cumulative_proba(n):
    for i in range(0, 2 * n + 1):
        print(str(i) + '+ : ' + str(gt_cumulative_proba(n, i)))


def create_default_atk_dice():
    return Dice(['hit', 'wild', 'crit'])


def create_default_def_dice():
    return Dice(['block', 'wild', 'crit'])


def all_damage_probabilities():
    output.delete('1.0', tk.END)
    num_atk_dice = dice_nums[0]
    num_def_dice = dice_nums[1]
    
    atk_dice = create_default_atk_dice()
    def_dice = create_default_def_dice()
    
    for damage in range(0, num_atk_dice * 2 + 1):
        gt_damage_proba = gt_cumulative_damage_proba(atk_dice, def_dice, num_atk_dice, num_def_dice, damage)
        output.insert(tk.INSERT, (str(damage) + '+: ' + str(gt_damage_proba) + '\n'))
        
    
def damage_probabilities(atk_dice, def_dice, num_atk_dice, num_def_dice, damage):
    proba = 0.0
    if damage > 0:
        for defense in range(0, num_def_dice * 2 + 1):
            if (defense + damage) <= num_atk_dice * 2:
                proba += roll_proba(atk_dice, num_atk_dice, defense + damage) * roll_proba(def_dice, num_def_dice, defense)
                
    else:
        for defense in range(0, num_def_dice * 2 + 1):
            for attack in range(0, defense + 1):
                proba += roll_proba(atk_dice, num_atk_dice, attack) * roll_proba(def_dice, num_def_dice, defense)
            
    return proba

def gt_cumulative_damage_proba(atk_dice, def_dice, num_atk_dice, num_def_dice, damage):
    cumulative_proba = 0.0
    for i in range(0, damage):
        cumulative_proba += damage_probabilities(atk_dice, def_dice, num_atk_dice, num_def_dice, i)
        
    return 1 - cumulative_proba

def store_current_atk_dice_num(num):
    dice_nums[0] = num
    
def store_current_def_dice_num(num):
    dice_nums[1] = num

dice_nums = [1] * 2

# Window setup.
window = tk.Tk()
window.title('MCP Dice Math')

tk.Label(window, text='Attack').grid(row=0, column=1)
tk.Label(window, text='Defense').grid(row=0, column=3)

num_dice_array = arange(1, 13, 1)

atk_dice = tk.IntVar(window)
atk_dice.set(num_dice_array[0])
atk_dice_dd = tk.OptionMenu(window, atk_dice, *num_dice_array, command=store_current_atk_dice_num)
atk_dice_dd.grid(row=1, column=1)

def_dice = tk.IntVar(window)
def_dice.set(num_dice_array[0])
def_dice_dd = tk.OptionMenu(window, def_dice, *arange(1, 9, 1), command=store_current_def_dice_num)
def_dice_dd.grid(row=1, column=3)

tk.Button(window, text='Calculate', command=all_damage_probabilities).grid(row=3, column=2)

output = tk.Text(window)
output.grid(row=4, column=2)

for i in range(0, 5):
    window.grid_columnconfigure(i, minsize=50)
    
for i in range(0, 5):
    window.grid_rowconfigure(i, minsize=25)
    
window.mainloop()
