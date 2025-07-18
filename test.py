import os
fls = []

for root, folders, files in os.walk('./data/lib'):
    for file in files:
        tmp = os.path.join(root, file)
        if '__pycache__' not in tmp:
            fls.append(tmp.replace('\\', '/'))
            print(tmp)

print(fls)