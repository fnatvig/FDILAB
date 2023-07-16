string1 = "hej vanja!"
index = [i for i in range(len(string1))]
new_string = []
new_index = []
for i in range(1, len(string1)+1):
    new_string += string1[-i]
    new_index.append(f"{index[-i]}")
# new_string = [new_string[i] for i in range()]
print(string1)
print(''.join(new_string))
print(''.join(new_index))
# print(type(str(new_string)))