import os


def generador_archivos(num_replicas, num_files):
    
    if not os.path.exists("../replicas"):
            os.mkdir("../replicas")

    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num_letters = len(letters)
    
    for i in range(num_replicas):  
        next = [""]
        directorio = "replica" + str(i)
        
        if not os.path.exists("../replicas/" + directorio):
            os.mkdir("../replicas/" + directorio)
        
        for i in range(num_files):
            with open("../replicas/" + directorio + "/archivo" + str(i) + ".txt", "w") as file:
                
                if next[-1] == letters[-1]:
                    next.append(letters[0])
                for i in range(len(next)):
                    if letters.index(next[i]) == num_letters - 1:
                        next[i] = "a"
                    else:
                        next[i] = letters[letters.index(next[i]) + 1]
                        break
                
                file.write("".join(next))

generador_archivos(3, 10)   



