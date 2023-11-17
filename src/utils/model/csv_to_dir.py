from numpy.random import RandomState
import pandas as pd
import os
df = pd.read_csv('full_dataset/labeled.csv')
#print(df)
rng = RandomState()

train = df.sample(frac=0.7, random_state=rng)
test = df.loc[~df.index.isin(train.index)]

train.to_csv("full_dataset/train.csv",index=False)
test.to_csv("full_dataset/test.csv",index=False)

train_df = pd.read_csv('full_dataset/train.csv')
test_df = pd.read_csv('full_dataset/test.csv')

for index, row in train_df.iterrows():
    print(row.name)
    if not(os.path.isdir("full_dataset/train/"+str(row["label"]))):
        os.makedirs("full_dataset/train/"+str(row["label"]))
    with open("full_dataset/train/" +str(row["label"])+  "/" +str(index)+".txt", "w+") as f:
        f.write(str(row["text"]))

for index, row in test_df.iterrows():
    if not(os.path.isdir("full_dataset/test/"+str(row["label"]))):
        os.makedirs("full_dataset/test/"+str(row["label"]))
    with open("full_dataset/test/" +str(row["label"])+  "/" +str(index)+".txt", "w+") as f:
        f.write(str(row["text"]))