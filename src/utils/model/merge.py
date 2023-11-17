import pandas as pd
import os

#merges the go emotions csv files into one, taking goemotions_2 and goemotions_3 and adding the rows from them to goemtions_1

with open("full_dataset/goemotions_2.csv", 'r') as f2:
    two = f2.read()
with open("full_dataset/goemotions_3.csv", 'r') as f3:
    three = f3.read()
with open('full_dataset/goemotions_1.csv', 'a') as f1:
    f1.write('\n')
    f1.write(two)
    f1.write('\n')
    f1.write(three)