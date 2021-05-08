# 文法文件路径
productionsFilePath = "E:/编译原理/实验二/LL1/LL1Test.txt"
# 要分析的句子
Sentence = "i+i*i"

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
print("开始符号：")
print(S)

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

print("First集:")
# 求First集
def first(seq):
    global First
    if First.get(seq):
        return First[seq]
    else:
        First[seq] = set()
        # reverse
        seqR = seq[::-1]
        # 1用来分割句型
        stack = [1]
        # 暂存First集的中间数据
        seqFirTmp = set()
        # 逆序压栈
        for char in seqR:
            stack.append(char)
        while len(stack):
            top = stack.pop()
            if top in VT:
                seqFirTmp.add(top)
                # 弹出整个句型
                while stack.pop() != 1:
                    pass
            elif top in VN:
                if "ε" not in productions[top]:
                    # 弹出整个句型
                    while stack.pop() != 1:
                        pass
                elif len(stack) == 1:
                    seqFirTmp = seqFirTmp.union({"ε"})
                if First.get(top):
                    seqFirTmp = seqFirTmp.union(First[top] - {"ε"})
                else:
                    # 将栈顶元素的产生式后部全部逆序压栈
                    for rear in productions[top]:
                        rear = rear[::-1]
                        stack.append(1)
                        for char in rear:
                            stack.append(char)
            elif top == "ε":
                # 弹出分隔符1
                stack.pop()
                if not len(stack):
                    seqFirTmp = seqFirTmp.union({"ε"})
    First[seq] = seqFirTmp
    return First[seq]
for vn in VN:
    print(vn, ": ", first(vn))

# Follow
# 赋初值
for vn in VN:
    Follow[vn] = set()
# 以第一个产生式前部为开始符号
Follow[S].add("#")
flag = 1
while flag:
    flag = 0
    # 对每一个非终结符的Follow集进行扩展
    for vn in VN:
        length = len(Follow[vn])
        # 对每一个产生式
        for front in productions:
            rears = productions[front]
            # 对每一个不含或的后部
            for rear in rears:
                # 对后部的每一个字符
                for i in range(len(rear)):
                    # vn在该符号串中时
                    if rear[i] == vn:
                        # vn不位于末尾时
                        if i+1 != len(rear):
                            Follow[vn] = Follow[vn].union(first(rear[i+1:]) - {"ε"})
                            # 终结符后边能推出空符时
                            if "ε" in first(rear[i+1:]):
                                Follow[vn] = Follow[vn].union(Follow[front])
                        # vn位于末尾时
                        else:
                            Follow[vn] = Follow[vn].union(Follow[front])
        if length != len(Follow[vn]):
            flag = 1
print("FOLLOW集:")
for vn in VN:
    print(vn, ": ", Follow[vn])

# 建表
tableLL1 = dict()
for vn in VN:
    tableLL1[vn] = dict()
for front in productions:
    rears = productions[front]
    # 对每一个不可再分的产生式
    for rear in rears:
        for v in first(rear):
            if v != "ε":
                tableLL1[front][v] = rear
            else:
                for vv in Follow[front]:
                    tableLL1[front][vv] = rear
print("LL1分析表：")
for vn in tableLL1:
    print(vn, ": ", tableLL1[vn])

def analyseSentence(sentence):
    number = 1
    stack = ["#", S]
    sentence = sentence + "#"
    for char in sentence:
        while stack[-1] in VN:
            print(number, ": ")
            print("当前输入符号：" + char)
            print("Stack: ", stack)
            top = stack.pop()
            if not tableLL1[top].get(char):
                print("\n\033[1;31;40m" + "句子语法有误！" + "\033[0m")
                exit(-1)
            print("使用产生式: ", top + "->" + tableLL1[top][char])
            number += 1
            rear = tableLL1[top][char][::-1]
            for c in rear:
                stack.append(c)
            if stack[-1] == "ε":
                stack.pop()
        if char == stack[-1]:
            stack.pop()
        else:
            print("\n\033[1;31;40m" + "句子语法错误！" + "\033[0m")
            exit(-1)

print("分析过程：")
analyseSentence(Sentence)
print("\n分析成功！")
print("句子符合文法")