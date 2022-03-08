from cgitb import text
from math import factorial
import tkinter as tk
from tkinter import ttk
from turtle import width
from typing_extensions import IntVar

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

    # Removes the input face from the array of successful faces.
    def remove_successful_face(self, face):
        if face in self.successful_faces:
            self.successful_faces.remove(face)

    # Adds the input face to the array of successful faces.
    def add_successful_face(self, face):
        if face not in self.successful_faces:
            self.successful_faces.append(face)
            
    # Sets the dices successful faces array.
    def set_successful_faces(self, new_successful_faces):
        self.successful_faces = new_successful_faces

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
            l = k - i
            if l <= j and l >= 0:
                crits_success_proba = initial_roll(dice, j, l)
                proba += initial_proba * crits_proba * crits_success_proba

    return proba


# Returns probability of rolling k or more successes from n dice.
def gt_cumulative_proba(dice, n, k):
    cumulative_proba = 0.0
    for i in range(0, k):
        cumulative_proba += roll_proba(dice, n, i)

    return 1 - cumulative_proba

# Returns probability of rolling k or less successes from n dice.
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
    
    for damage in range(1, num_atk_dice * 2 + 1):
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
    all_damage_probabilities()
    
def store_current_def_dice_num(num):
    dice_nums[1] = num
    all_damage_probabilities()
    
# Creates the options window.
def create_options_window():
    options_window = tk.Toplevel(window)
    
    tk.Label(options_window, text='Successful Faces (Attack)').grid(row=0, column=0)
    tk.Label(options_window, text='Successful Faces (Defense)').grid(row=0,column=2)
    
    tk.Checkbutton(options_window, text='Hit', variable=atk_cb_hit).grid(row=1, column=0)
    
    tk.Checkbutton(options_window, text='Block', variable=atk_cb_block).grid(row=2, column=0)

    tk.Checkbutton(options_window, text='Wild', variable=atk_cb_wild).grid(row=3, column=0)
    
    tk.Checkbutton(options_window, text='Crit', variable=atk_cb_crit).grid(row=4, column=0)
    
    tk.Checkbutton(options_window, text='Blank', variable=atk_cb_blank).grid(row=5, column=0)
    
    tk.Checkbutton(options_window, text='Fail', variable=atk_cb_fail).grid(row=6, column=0)
    
    tk.Checkbutton(options_window, text='Hit', variable=def_cb_hit).grid(row=1, column=2)
    
    tk.Checkbutton(options_window, text='Block', variable=def_cb_block).grid(row=2, column=2)
    
    tk.Checkbutton(options_window, text='Wild', variable=def_cb_wild).grid(row=3, column=2)
    
    tk.Checkbutton(options_window, text='Crit', variable=def_cb_crit).grid(row=4, column=2)
    
    tk.Checkbutton(options_window, text='Blank', variable=def_cb_blank).grid(row=5, column=2)
    
    tk.Checkbutton(options_window, text='Fail', variable=def_cb_fail).grid(row=6, column=2)
    
    tk.Button(options_window, text='Update Dice', command=update_dice).grid(row=7, column=1)
    
    options_window.grid_columnconfigure(1, minsize=50)
    
    options_window.transient(window)
    options_window.grab_set()
    window.wait_window(options_window)

def update_dice():
    updated_atk_dice = []
    updated_def_dice = []
    
    if atk_cb_hit.get() == 1:
        updated_atk_dice.append('hit')
    if atk_cb_block.get() == 1:
        updated_atk_dice.append('block')
    if atk_cb_wild.get() == 1:
        updated_atk_dice.append('wild')
    if atk_cb_crit.get() == 1:
        updated_atk_dice.append('crit')
    if atk_cb_blank.get() == 1:
        updated_atk_dice.append('blank')
    if atk_cb_fail.get() == 1:
        updated_atk_dice.append('fail')
        
    if def_cb_hit.get() == 1:
        updated_def_dice.append('hit')
    if def_cb_block.get() == 1:
        updated_def_dice.append('block')
    if def_cb_wild.get() == 1:
        updated_def_dice.append('wild')
    if def_cb_crit.get() == 1:
        updated_def_dice.append('crit')
    if def_cb_blank.get() == 1:
        updated_def_dice.append('blank')
    if def_cb_fail.get() == 1:
        updated_def_dice.append('fail')
        
    atk_dice.set_successful_faces(updated_atk_dice)
    def_dice.set_successful_faces(updated_def_dice)
    

window = tk.Tk()

atk_dice = create_default_atk_dice()
def_dice = create_default_def_dice()

# Initialize checkbox variables.
atk_cb_hit = tk.IntVar()
atk_cb_block = tk.IntVar()
atk_cb_wild = tk.IntVar()
atk_cb_crit = tk.IntVar()
atk_cb_blank = tk.IntVar()
atk_cb_fail = tk.IntVar()
def_cb_hit = tk.IntVar()
def_cb_block = tk.IntVar()
def_cb_wild = tk.IntVar()
def_cb_crit = tk.IntVar()
def_cb_blank = tk.IntVar()
def_cb_fail = tk.IntVar()

dice_nums = [1] * 2

# Window setup.
window.title('MCP Dice Math')

tk.Label(window, text='Attack').grid(row=0, column=1)
tk.Label(window, text='Defense').grid(row=0, column=3)

num_atk_dice = tk.IntVar(window)
num_atk_dice.set(1)
atk_dice_dd = tk.OptionMenu(window, num_atk_dice, *arange(1, 13, 1), command=store_current_atk_dice_num)
atk_dice_dd.grid(row=1, column=1)

num_def_dice = tk.IntVar(window)
num_def_dice.set(1)
def_dice_dd = tk.OptionMenu(window, num_def_dice, *arange(1, 9, 1), command=store_current_def_dice_num)
def_dice_dd.grid(row=1, column=3)

output = tk.Text(window)
output.bindtags((str(output), str(window), 'all'))
output.grid(row=4, column=2)

tk.Button(window, text='Options', command=create_options_window).grid(row=3, column=2)

# Set the columns and rows of the window to a minimum size.
for i in range(0, 5):
    window.grid_columnconfigure(i, minsize=50)
    
for i in range(0, 5):
    window.grid_rowconfigure(i, minsize=25)
    
window.mainloop()
