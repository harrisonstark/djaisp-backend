#this file takes the merged goemitions_1.csv and does two things to it 
# (Removal of all unnecessary columns (everything except text and the emotions) was done by hand)
#  (Creates a column called 'label', also done by hand)
# - Goes through rows and if value of emotion is 1, adds that column name to label column 
# - Removes all the emotion columns once done, leaving us with only the text and label columns
# Ex: Angry=1 means Label=Angry

import pandas as pd
import os 

file = pd.read_csv("full_dataset/goemotions_1.csv")
df = pd.DataFrame(file)
df_new = pd.DataFrame(columns = ["text","label"])
emotions = dict()
for column in range(0,len(df.columns)):
    emotions[column] = df.columns[column]
print(emotions)
#this has all the column names and the indices so dont have to call df.columns again each time

for index, row in df.iterrows():
    print(row)
    for x in range(0,len(row)):
        #x is column index now
        #row[x] is value of that index
        #df.columns[x] is column name
        if row[x] == 1:
            new_row = {"text":row[0],"label":emotions[x]}
            df_new.loc[len(df_new)]=new_row
            break

df_new.to_csv("full_dataset/labeled.csv")



