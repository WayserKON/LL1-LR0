# 文法文件路径
productionsFilePath = "E:/编译原理/实验二/LL1/LR0Test.txt"
# 要分析的句子
Sentence = "abc"

# 终结符
VT = set()
# 非终结符
VN = set()

# 头符号集
First = dict()
# 后继符号集
Follow = dict()

# 从txt文件读出字符串
with open(productionsFilePath, "r", encoding='utf-8') as f:
    initialString = f.read()

# 字符的提取、分类
string = initialString
string = string.replace("->", "")
string = string.replace("ε", "")
string = string.replace("\n", "")
string = string.replace("|", "")
for ch in string:
    if 'A' <= ch <= 'Z':
        VN.add(ch)
    else:
        VT.add(ch)
print("终结符：")
print(VT)
print("非终结符：")
print(VN)

# 分行
strings = initialString.split("\n")
# 删除空行
while "" in strings:
    strings.remove("")

# 开始符号取第一个产生式的前部
S = strings[0][0]
# S*为添加产生式后的开始符号
print("开始符号：")
print("S'")

print("文法产生式：")
# 产生式前部、后部用字典存放
productions = dict()
i = 1
for production in strings:
    print(i, ": ", production)
    production = production.split("->")
    rears = set(production[1].split("|"))
    if productions.get(production[0]):
        productions[production[0]] = productions[production[0]].union(rears)
    else:
        productions[production[0]] = rears
    i += 1
# 添加产生式
productions["S'"] = {S}
print(i, ": ", "S'->" + S)

# 求Ix的闭包
# Ix 为一字典，键为Vt，值为set
def getClosure(Ix):
    flag = 1
    vs = set()
    while flag:
        flag = 0
        # 遍历Ix中的产生式
        for head in list(Ix):
            # 遍历产生式的每一个后部
            for rear in list(Ix[head]):
                # 获得"·"的位置
                dotPos = rear.index("·")
                # "·"为最后一个符号时
                if dotPos + 1 == len(rear):
                    continue
                vs.add(rear[dotPos+1])
                # "·"的后一个符号为非终结符时
                if rear[dotPos+1] in VN:
                    # "·"后的终结符
                    vt = rear[dotPos+1]
                    if not Ix.get(vt):
                        Ix[vt] = set()
                    # 记录length前后变化
                    length = len(Ix[vt])
                    # 添加产生式
                    for tail in productions[vt]:
                        Ix[vt].add("·" + tail)
                    if len(Ix[vt]) != length:
                        flag = 1
    # 返回"·"后的所有符号的集合，留作以后优化
    return vs

# 构造I0，初始化 I
I = {0: {"S'": {"·" + S}}}
# 求闭包
getClosure(I[0])
# 符号全集
V = VT.union(VN)
# 转换关系
GO = dict()
# 可以规约的项目集
rSet = set()
i = 0
while I.get(i):
    # GO初始化
    GO[i] = dict()
    # 对每一个"·"后的符号
    for v in V:
        # Ix的临时容器
        tmpDict = dict()
        # 对每个产生式
        for head in I[i]:
            # 对每个后部
            for rear in I[i][head]:
                dotPos = rear.index("·")
                if len(rear) - 1 != dotPos:
                    if rear[dotPos+1] == v:
                        if not tmpDict.get(head):
                            tmpDict[head] = set()
                        # “·”与其后边的字符交换位置
                        string = rear[:dotPos] + rear[dotPos+1] + "·"
                        if len(rear) - 1 != dotPos + 1:
                            tmpDict[head].add(string + rear[dotPos+2:])
                        else:
                            tmpDict[head].add(string)
                # "·"在产生式末尾时
                else:
                    rSet.add((i, head + "->" + rear))
        if len(tmpDict) == 0:
            continue
        getClosure(tmpDict)
        flag = 1
        # 与已存在的Ix比较
        for x in range(len(I)):
            if tmpDict == I[x]:
                GO[i][v] = {x}
                flag = 0
        # 若都不相等
        if flag:
            I[len(I)] = tmpDict
            GO[i][v] = {len(I) - 1}
    i = i + 1
# 重复项检测
flag = 1
# 将规约情况加入表中
for (i, pdt) in rSet:
    if "S'" in pdt:
        GO[i]["#"] = {"Acc"}
        continue
    for front in VT.union({"#"}):
        if not GO[i].get(front):
            GO[i][front] = set()
        else:
            flag = 0
        GO[i][front].add(pdt[:-1])

print("LR0项目集规范组：")
for i in range(len(I)):
    print("I"+str(i), ":", I[i])
print("LR0分析表:")
for i in range(len(GO)):
    print(i, ":", GO[i])

def analyseSentence(sentence):
    sentence = sentence + "#"
    # 状态栈
    stackS = [0]
    # 符号栈
    stackT = ["#"]
    print("初始状态")
    print("S栈 :", stackS)
    print("T栈 :", stackT)
    count = 1
    i = 0
    # 对句子逐个字符分析
    while i < len(sentence):
        # 输入符号压栈
        print("No." + str(count), ":")
        print("输入符号：", sentence[i])
        # 取栈顶
        status = stackS[-1]
        if not GO[status].get(sentence[i]):
            print("\n\033[1;31;40m" + "句子出现语法错误！" + "\033[0m")
            exit(-1)
        if list(GO[status][sentence[i]])[0] == "Acc":
            print("分析成功！句子符合语法")
            break
        operation = list(GO[status][sentence[i]])[0]
        if type(operation) is int:
            stackS.append(operation)
            stackT.append(sentence[i])
            print("状态、输入符号压栈")
            print("S栈 :", stackS)
            print("T栈 :", stackT)
        else:
            i -= 1
            operation = operation.split("->")
            # 规约产生式的后部
            head = operation[0]
            rear = operation[1]
            for x in range(len(rear)):
                stackS.pop()
                stackT.pop()
            print("规约")
            print("(1)产生式后部出栈")
            print("S栈 :", stackS)
            print("T栈 :", stackT)
            stackT.append(head)
            print("(2)产生式前部入符号栈")
            print("S栈 :", stackS)
            print("T栈 :", stackT)
            status = stackS[-1]
            sign = stackT[-1]
            if not GO[status].get(sign):
                print("\n\033[1;31;40m" + "句子出现语法错误！" + "\033[0m")
                exit(-1)
            operation = list(GO[status][sign])[0]
            stackS.append(operation)
            print("(3)状态压栈")
            print("S栈 :", stackS)
            print("T栈 :", stackT)
        i += 1
        count += 1

# 文法为LR0文法时
if flag:
    print("分析过程：")
    analyseSentence(Sentence)
else:
    print("\n\033[1;31;40m" + "非LR0文法！" + "\033[0m")