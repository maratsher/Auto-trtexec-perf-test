from sys import argv
import argparse
import os
import re

def cartesianProduct(set_a, set_b):
    result =[]
    for i in range(0, len(set_a)):
        for j in range(0, len(set_b)):
 
            if type(set_a[i]) != list:        
                set_a[i] = [set_a[i]]
            temp = [num for num in set_a[i]]  
            temp.append(set_b[j])            
            result.append(temp) 
             
    return result
 
# находим декартова произведение N множеств
def Cartesian(list_a, n):

    temp = list_a[0]
     
    for i in range(1, n):
        temp = cartesianProduct(temp, list_a[i])
         
    return temp

# создаем list из файла
# --flag1 [v1 v2] {path} ->
# [--flag v1, --flag v2]
def make_list(file):
    lst = []
    with open(file) as file:
        lines = file.read().split('\n')
        reg = r"\[(.*?)\]"
        regp = r"\{(.*?)\}"
        for l in lines:
            m = re.findall(reg, l)
            mp = re.findall(regp, l)
            if(len(m) > 1):
                print("Input structure data error.")
                exit()
            elif len(m) == 0:
                if l == "NULL":
                    lst.append("")
                else:
                    lst.append(l)
            elif len(m) == 1:
                for v in m[0].split(" "):
                    l = l.split('[')[0]
                    if(len(mp) == 1):
                        lst.append((l+"="+os.path.join(mp[0], v)).replace(" ", ""))
                    else:
                        lst.append((l+"="+v).replace(" ", ""))
    return lst
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--save-dir', type=str, default='./', help='Save dir')
    parser.add_argument('--param-dir', type=str, default='./params', help='Dir with params for models')
    parser.add_argument('--global-params', type=str, default='./global-params.txt', help='File with global params')
    parser.add_argument('--trtexec-dir', type=str, default='./', help='Trtexec bin dir')

    opt = parser.parse_args()
    print(opt)

    if not os.path.isdir(opt.save_dir):
        print(opt.save_dir + " is not dir")
        exit()

    if not os.path.isdir(opt.param_dir):
        print(opt.param_dir + " is not dir")
        exit()
    
    if not os.path.exists(os.path.join(opt.trtexec_dir, "trtexec")):
        print("Could not find "+os.path.join(opt.trtexec_dir, "trtexec"))
        exit()

    if not os.path.exists(opt.global_params):
        print("Global params file " +opt.global_params+ " dont exist")
        exit()

    params_dir = opt.param_dir
    with open(opt.global_params) as file:
        global_params = file.readline()
    L = [] # список списков параметров

    # разворачиваем файл с параметры в списки
    for file in sorted(os.listdir(params_dir)):
        filename = os.fsdecode(file)
        if filename.endswith(".txt"):
            L.append(make_list(os.path.join(params_dir, filename)))
            continue
        else:
            continue

    # запускаем trtexec для каждого набора параметров
    np = len(L) # кол-во параметров
    sets = Cartesian(L,np)
    nm = len(sets) # кол-во моделей
    print(f"ВСЕГО МОДЕЛЕЙ: {nm}")
    print("\n\n\n\n")
    for i, set in enumerate(Cartesian(L,np)):
        params = ""
        params = " ".join(set)

        # формируем имя для сохроняемого файла name.txt
        name = re.sub(r'\W+', '_', params)
        # скращаем имя
        name = name[name.find("weights"):]

        # если в save_dir уже есть файл с таким именем, пропускаем
        if os.path.exists(os.path.join(opt.save_dir, name+".txt")):
            print(os.path.join(opt.save_dir, name+".txt") + " уже сущесвует! Модель пропущена...")
            continue

        # формируем строку исполняемой комманды
        command = str(opt.trtexec_dir) + "./trtexec "+ params + " "+global_params + " > buff.txt"
        command = " ".join(command.split())
        print(command)
        """
        # выполянем команду
        try:
            #os.system(command) 
            pass
        except Exception as e:
            print("Команда {command} выполнена с ошибкой {e}")
            continue
        os.system("python3 export.py > buff.txt")

        # ищем в выводе trtexec qps
        key_word = 'Throughput'
        qps = 0
        with open('buff.txt', 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                if line.find(key_word) != -1:
                    qps = float(line.split(" ")[3])
                    break
        
        print(f"QPS: {qps}")
        # сранвивам qps, если вышли за рамки, завершаем программу
        if(qps < 10): # <
            print(f"Модель {name} вышла за рамки. Throughput {qps} qps" )
            print("Тестирование завершено!")
            exit()
        else:
            # если все хорошо, перемещаем буффер и save-dir с именем name.txt
            os.rename("buff.txt", os.path.join(opt.save_dir, name+".txt"))

        print()
        print("="*100)
        print(f"Протестированно {i+1} из {nm} моделей")
        print("="*100)
        print()
        """

print("Тестирование завершено!")