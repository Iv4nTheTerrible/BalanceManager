import os
import json

print(os.getcwd())

numbers = [1, 2, 3]

with open("numbers.json", "w") as file:
    json.dump(numbers, file)

print("done")