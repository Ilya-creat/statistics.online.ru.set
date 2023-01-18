a = int(input())
for i in range(a):
    k = int(input())
    c = list(map(int, input().split()))
    o = 0
    c.sort()
    m = ''
    for j in c:
        if c.count(j) > 1 and m != j and j != 0:
            o += 2
            m = j
        elif c.count(j) == 1 and j != m:
            o += 1
            m = j
    print(o)
