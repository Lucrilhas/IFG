import numpy as np
from random import sample, randint
import copy

TEMP = 0.5


def sudoku_ann(puzzle_input,maxIterations=5000000,T=TEMP,coolingRate=1.0 - 1e-5,verbose=False):
    """
    Preenche de forma única cada bloco nxn em um quebra-cabeça de n^2xn^2 de maneira aleatória.
    Conta o número de elementos únicos em cada linha e coluna, atribuindo uma pontuação de -1 para cada elemento único.
    Escolhe aleatoriamente um quadrado nxn no quebra-cabeça e troca duas entradas nele para calcular um "estado vizinho".
    Calcula a pontuação para o estado vizinho e aceita/rejeita com uma certa probabilidade de que o novo estado tenha uma pontuação mais baixa.
    Reduz a temperatura por meio de uma taxa de resfriamento (T = 0,99999T).
    Repete a partir do passo 2 até que a pontuação mínima seja alcançada.
    """
    reheat_rate = T/0.3

    sudoku = copy.deepcopy(puzzle_input)
    tam = len(sudoku)
    tam_total = int(np.sqrt(tam))

    lugares_vazios = inicializar(sudoku)


    #Start annealing
    score = calc_custos(sudoku)
    target_score = -2*tam*tam
    best_score = score
    stuck_count=0

    for i in range(maxIterations):
        if(i%10000 ==0 and verbose):
            print("Iteration "+str(i)+", current score:"+str(score)+"  Best score: "+str(best_score))

        # Adjust temperature
        if(score == target_score or T==0):
            break

        #If stuck then reheat the annealer
        if(stuck_count>5000 or T < 1e-4):
            print("Annealer is stuck at T={} and stuck_count={}, so re-initializing...".format(T,stuck_count))
            T=T*reheat_rate
            sudoku=copy.deepcopy(puzzle_input)
            lugares_vazios = inicializar(sudoku)
            stuck_count=0


        neighbor_puzzle = get_vizinho(sudoku,lugares_vazios) # Find neighbouring state
        s2 = calc_custos(neighbor_puzzle) # Energy of neighbouring state
        delta_s = float(score-s2) # Energy difference
        probability = np.exp(delta_s/T) #Acceptance probability

        random_probability = np.random.uniform(low=0,high=1,size=1)

        if(probability > random_probability): #Acceptance condition, ref: accept-reject sampling
            sudoku = copy.deepcopy(neighbor_puzzle)
            score = s2
            if(score<best_score):
                best_score=score
            stuck_count=0

        stuck_count+=1

        T=coolingRate*T

    if(verbose):
        print("Total number of iterations done: ",i+1," to get score:", score)
        #Print solution
        print("Solution:")
        puzzle_maker.Print(sudoku)

    return sudoku


def descobrir_vazios(lugares_vazios,dim,sqcont):

    vazios = []

    for row in range(dim):
        for col in lugares_vazios[row]:
            r= row + dim*(sqcont//dim)
            c= col + dim*(sqcont%dim)
            vazios.append((r,c))
    return vazios


def inicializar(sudoku):
    tam = len(sudoku)
    tam_total = int(np.sqrt(tam))
    i, j = 0, 0
    lugares_vazios=[]
    temp_list=[]
    temp_cont=0
    while(i<tam and j<tam):

        temp_list.append(sudoku[i][j:j+tam_total])

        if ((i+1)%tam_total == 0 and (j+tam_total)%tam_total == 0):
            mudados=[]
            vazios=[]

            values=list(range(1,tam+1))
            #Find empty cells and fixed cells in the block
            for row in range(tam_total):
                vazios.append(np.where(np.array(temp_list)[row]==0)[0].tolist())
                mudados.append(np.where(np.array(temp_list)[row]!=0)[0].tolist())

                #Find fixed values in the block
                for f in mudados[row]:
                    values.remove(temp_list[row][f])

            #Map empty cell to puzzle indices
            index_map = descobrir_vazios(vazios,tam_total,temp_cont)
            lugares_vazios.append(index_map)

            #Fill empty cells in the block uniquely
            for cell in index_map:

                random_val=sample(values,1)[0]

                sudoku[cell[0]][cell[1]] = random_val

                values.remove(random_val)

            temp_cont+=1
            j+=tam_total
            i-=tam_total
            temp_list=[]
            if(j%tam==0):
                i=i+tam_total
                j=0

        i+=1

    return lugares_vazios



def calc_custos(sudoku):
    tam = len(sudoku)
    score = 0

    #Count in the columns
    sudoku_trans =  list(zip(*sudoku))
    for i in range(tam):

        #Score by unique elements
        score -= len(list(set(sudoku[i])))
        score -= len(list(set(sudoku_trans[i])))

    return score



def get_vizinho(sudoku,lugares_vazios):
    tam = len(sudoku)
    tam_total = int(np.sqrt(tam))
    novo_sudoku = copy.deepcopy(sudoku)

    random_pedaco=0
    while(random_pedaco<2 ):
        #Pick a random block
        block = randint(0,tam-1)
        random_pedaco = len(lugares_vazios[block])

    #Randomly find 2 cells in the block to swap
    x, y = sample(range(len(lugares_vazios[block])),2)
    b1, b2 = lugares_vazios[block][x], lugares_vazios[block][y]

    #Swap entries
    novo_sudoku[b1[0]][b1[1]], novo_sudoku[b2[0]][b2[1]] = novo_sudoku[b2[0]][b2[1]], novo_sudoku[b1[0]][b1[1]]

    return novo_sudoku