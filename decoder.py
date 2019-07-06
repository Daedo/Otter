import base64

def decodeData():
    for i in range(1,6):
        with open("data/test_"+str(i)+".csv","r") as f:
            with open("data/table_"+str(i)+".txt","w") as g:
                for line in f:
                    fun_id = line.split(", ")[2]
                    if fun_id.startswith("b'"):
                        fun_id = fun_id[2:-2]
                        dec = base64.b64decode(fun_id.encode('ascii'))
                        dec = str(dec)[2:-1]
                        g.write(dec+"\n")