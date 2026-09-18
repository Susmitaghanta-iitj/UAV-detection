from shield_ahco.bitaccurate.canonical import TPMode, decode_to_canonical, encode_from_canonical
from shield_ahco.bitaccurate.transprecision_mac import TPAccumulator

def relu_code(code,mode):
    v=decode_to_canonical(code,mode)
    if v.is_nar: return code
    return encode_from_canonical(max(v.q16_16,0),mode)

def maxpool1d_codes(x_codes,channels,length,mode,kernel=2,stride=2):
    out=[]; out_len=((length-kernel)//stride)+1
    for c in range(channels):
        base=c*length
        for o in range(out_len):
            vals=[]
            for k in range(kernel):
                code=x_codes[base+o*stride+k]
                cv=decode_to_canonical(code,mode)
                vals.append((cv.value,code))
            out.append(max(vals,key=lambda z:z[0])[1])
    return out

def dense_codes(x_codes,w_codes,b_codes,din,dout,mode,do_relu=True):
    y=[]
    for o in range(dout):
        acc=TPAccumulator(mode)
        for i in range(din):
            acc.mac_codes(x_codes[i],w_codes[o*din+i])
        if b_codes is not None:
            b=decode_to_canonical(b_codes[o],mode)
            if b.is_nar: acc.nar_seen=True
            else: acc.acc_q32_32 += b.q16_16 << 16
        out=acc.output_code()
        y.append(relu_code(out,mode) if do_relu else out)
    return y

def conv1d_codes(x_codes,w_codes,b_codes,cin,cout,length,kernel,mode,stride=1,padding=0,do_relu=True):
    out_len=((length+2*padding-kernel)//stride)+1
    y=[]
    for oc in range(cout):
        for ox in range(out_len):
            acc=TPAccumulator(mode)
            for ic in range(cin):
                for k in range(kernel):
                    ix=ox*stride+k-padding
                    x=x_codes[ic*length+ix] if 0<=ix<length else 0
                    w=w_codes[(oc*cin+ic)*kernel+k]
                    acc.mac_codes(x,w)
            if b_codes is not None:
                b=decode_to_canonical(b_codes[oc],mode)
                if b.is_nar: acc.nar_seen=True
                else: acc.acc_q32_32 += b.q16_16 << 16
            out=acc.output_code()
            y.append(relu_code(out,mode) if do_relu else out)
    return y
