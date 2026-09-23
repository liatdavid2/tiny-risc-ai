from pathlib import Path
import json, subprocess, re, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
GEN = ROOT / 'generated'
OUT.mkdir(exist_ok=True)
GEN.mkdir(exist_ok=True)

MODELS = ['logistic_regression','decision_tree','random_forest','mlp_classifier']

# ----- Tiny RISC instruction encoders -----
def r_type(rd, rs1, rs2, funct3=0, funct7=0):
    return ((funct7 & 0x7f)<<25)|((rs2&31)<<20)|((rs1&31)<<15)|((funct3&7)<<12)|((rd&31)<<7)|0b0110011

def i_type(rd, rs1, imm, funct3=0):
    imm &= 0xfff
    return (imm<<20)|((rs1&31)<<15)|((funct3&7)<<12)|((rd&31)<<7)|0b0010011

def b_type(rs1, rs2, offset, funct3):
    if offset % 2:
        raise ValueError(f'branch offset must be even: {offset}')
    imm = offset & 0x1fff
    b12 = (imm >> 12) & 1
    b11 = (imm >> 11) & 1
    b10_5 = (imm >> 5) & 0x3f
    b4_1 = (imm >> 1) & 0xf
    return (b12<<31)|(b10_5<<25)|((rs2&31)<<20)|((rs1&31)<<15)|((funct3&7)<<12)|(b4_1<<8)|(b11<<7)|0b1100011

def j_type(rd, offset):
    if offset % 2:
        raise ValueError(f'jump offset must be even: {offset}')
    imm = offset & 0x1fffff
    b20 = (imm >> 20) & 1
    b10_1 = (imm >> 1) & 0x3ff
    b11 = (imm >> 11) & 1
    b19_12 = (imm >> 12) & 0xff
    return (b20<<31)|(b10_1<<21)|(b11<<20)|(b19_12<<12)|((rd&31)<<7)|0b1101111

ADD=lambda rd,a,b:r_type(rd,a,b,0,0)
MUL=lambda rd,a,b:r_type(rd,a,b,0,1)
SLT=lambda rd,a,b:r_type(rd,a,b,2,0)
ADDI=lambda rd,a,imm:i_type(rd,a,imm,0)
SLTI=lambda rd,a,imm:i_type(rd,a,imm,2)
SRAI=lambda rd,a,sh:i_type(rd,a,sh,5)
BEQ=lambda a,b,off:b_type(a,b,off,0)
BNE=lambda a,b,off:b_type(a,b,off,1)
JUMP=lambda off:j_type(0,off)
HALT=0xFFFFFFFF

class Program:
    """Tiny assembler with labels. All control flow is resolved into BEQ/BNE/JAL instructions."""
    def __init__(self):
        self.items=[]
        self.labels={}
        self._counter=0

    def unique(self, prefix):
        self._counter += 1
        return f'{prefix}_{self._counter}'

    def label(self, name):
        self.labels[name]=len(self.items)

    def emit(self, word):
        self.items.append(('word', int(word)))

    def bne(self, rs1, rs2, label):
        self.items.append(('bne', rs1, rs2, label))

    def beq(self, rs1, rs2, label):
        self.items.append(('beq', rs1, rs2, label))

    def jump(self, label):
        self.items.append(('jump', label))

    def finish(self):
        words=[]
        for i,item in enumerate(self.items):
            pc=i*4
            kind=item[0]
            if kind=='word': words.append(item[1])
            elif kind in ('bne','beq'):
                _,a,b,label=item
                target=self.labels[label]*4
                off=target-pc
                words.append(BNE(a,b,off) if kind=='bne' else BEQ(a,b,off))
            elif kind=='jump':
                target=self.labels[item[1]]*4
                words.append(JUMP(target-pc))
            else: raise ValueError(item)
        return words


def ensure_imm12(v, what='immediate'):
    if not -2048 <= int(v) <= 2047:
        raise ValueError(f'{what}={v} does not fit TinyRISC 12-bit immediate')
    return int(v)



def emit_load_const(p, rd, value):
    """Load an arbitrary teaching-scale integer using one or more ADDI instructions."""
    value=int(value)
    if value == 0:
        p.emit(ADDI(rd,0,0)); return
    remaining=value; first=True
    while remaining != 0:
        chunk=max(-2048,min(2047,remaining))
        p.emit(ADDI(rd,0 if first else rd,chunk))
        remaining -= chunk; first=False

def load_inputs(p, values):
    for i,v in enumerate(values):
        p.emit(ADDI(1+i,0,ensure_imm12(v,'input')))


def emit_binary_sign_prediction(p, score_reg=10, pred_reg=31):
    neg=p.unique('negative')
    done=p.unique('prediction_done')
    p.emit(SLTI(30,score_reg,0))
    p.bne(30,0,neg)
    p.emit(ADDI(pred_reg,0,1))
    p.jump(done)
    p.label(neg)
    p.emit(ADDI(pred_reg,0,0))
    p.label(done)


def emit_argmax(p, score_regs, pred_reg=31):
    """Argmax with deterministic lowest-class tie breaking."""
    if len(score_regs) == 1:
        emit_binary_sign_prediction(p, score_regs[0], pred_reg)
        return
    best_reg = 28
    cmp_reg = 30
    p.emit(ADD(best_reg, score_regs[0], 0))
    p.emit(ADDI(pred_reg, 0, 0))
    for cls, reg in enumerate(score_regs[1:], start=1):
        skip = p.unique(f'argmax_skip_{cls}')
        p.emit(SLT(cmp_reg, best_reg, reg))  # 1 only if new score is strictly greater
        p.beq(cmp_reg, 0, skip)
        p.emit(ADD(best_reg, reg, 0))
        p.emit(ADDI(pred_reg, 0, cls))
        p.label(skip)


def build_logistic(meta):
    p=Program(); x=meta['sample_int8']; W=meta['exported']['weights_int8']; B=meta['exported']['bias_int32']
    load_inputs(p,x)
    score_regs=[]
    for c, row in enumerate(W):
        score=21+c; score_regs.append(score)
        p.emit(ADDI(score,0,0))
        for i,w in enumerate(row):
            p.emit(ADDI(5,0,ensure_imm12(w,'weight')))
            p.emit(MUL(11,1+i,5))
            p.emit(ADD(score,score,11))
        emit_load_const(p,20,B[c])
        p.emit(ADD(score,score,20))
    emit_argmax(p,score_regs)
    p.emit(HALT)
    return p.finish()


def emit_tree_control_flow(p, nodes, node, done_label, prefix='tree'):
    """Compile a sklearn tree into actual TinyRISC branches and jumps."""
    n=nodes[node]
    if n['leaf']:
        p.emit(ADDI(31,0,int(n['class'])))
        p.jump(done_label)
        return
    feat=int(n['feature']); thr=int(n['threshold_int8'])
    left_label=p.unique(f'{prefix}_left'); right_label=p.unique(f'{prefix}_right')
    p.emit(SLTI(30,1+feat,ensure_imm12(thr+1,'tree threshold+1')))
    p.bne(30,0,left_label)
    p.jump(right_label)
    p.label(left_label)
    emit_tree_control_flow(p,nodes,int(n['left']),done_label,prefix)
    p.label(right_label)
    emit_tree_control_flow(p,nodes,int(n['right']),done_label,prefix)


def build_decision_tree(meta):
    p=Program(); load_inputs(p,meta['sample_int8'])
    done='tree_done'
    emit_tree_control_flow(p,meta['exported']['nodes'],0,done,'dt')
    p.label(done); p.emit(HALT)
    return p.finish()


def build_random_forest(meta):
    p=Program(); load_inputs(p,meta['sample_int8'])
    trees=meta['exported'].get('trees',[]); n_classes=int(meta.get('n_classes',2))
    if not trees: raise RuntimeError('RandomForest export has no trees')
    vote_regs=[24+i for i in range(n_classes)]
    for r in vote_regs: p.emit(ADDI(r,0,0))
    for ti,t in enumerate(trees):
        done=f'tree_{ti}_done'; after=f'tree_{ti}_vote_done'
        emit_tree_control_flow(p,t['nodes'],0,done,f'rf{ti}')
        p.label(done)
        # x31 contains this tree's class. Increment exactly one vote register.
        for cls,r in enumerate(vote_regs):
            hit=p.unique(f'tree{ti}_class{cls}')
            p.emit(ADDI(29,0,cls))
            p.beq(31,29,hit)
            if cls == n_classes-1:
                p.jump(after)
            else:
                nxt=p.unique(f'tree{ti}_nextclass')
                p.jump(nxt); p.label(hit); p.emit(ADDI(r,r,1)); p.jump(after); p.label(nxt)
                continue
            p.label(hit); p.emit(ADDI(r,r,1)); p.jump(after)
        p.label(after)
    emit_argmax(p,vote_regs)
    p.emit(HALT)
    return p.finish()


def build_mlp(meta):
    ex=meta['exported']; x=meta['sample_int8']; W1=ex['w1_int8']; b1=ex['b1_int32']; W2=ex['w2_int8']; b2=ex['b2_int32']; sh=int(ex['hidden_shift'])
    p=Program(); load_inputs(p,x)
    hidden=len(b1); out_dim=len(b2)
    for j in range(hidden):
        p.emit(ADDI(10,0,0))
        for i in range(4):
            p.emit(ADDI(5,0,ensure_imm12(W1[i][j],'MLP weight')))
            p.emit(MUL(11,1+i,5)); p.emit(ADD(10,10,11))
        emit_load_const(p,20,b1[j]); p.emit(ADD(10,10,20))
        zero=p.unique(f'relu{j}_zero'); after=p.unique(f'relu{j}_after')
        p.emit(SLTI(30,10,0)); p.bne(30,0,zero)
        p.emit(ADD(12+j,10,0)); p.jump(after)
        p.label(zero); p.emit(ADDI(12+j,0,0)); p.label(after)
        if sh>0: p.emit(SRAI(12+j,12+j,sh))
    score_regs=[]
    for c in range(out_dim):
        score=21+c; score_regs.append(score); p.emit(ADDI(score,0,0))
        for j in range(hidden):
            p.emit(ADDI(5,0,ensure_imm12(W2[j][c],'MLP output weight')))
            p.emit(MUL(11,12+j,5)); p.emit(ADD(score,score,11))
        emit_load_const(p,20,b2[c]); p.emit(ADD(score,score,20))
    emit_argmax(p,score_regs)
    p.emit(HALT)
    return p.finish()

BUILDERS={
    'logistic_regression':build_logistic,
    'decision_tree':build_decision_tree,
    'random_forest':build_random_forest,
    'mlp_classifier':build_mlp,
}


def make_tb(name, words, expected):
    loads='\n'.join(f"    dut.imem.mem[{i}] = 32'h{w:08x};" for i,w in enumerate(words))
    return f'''// AUTO-GENERATED: {name}\n// Full instruction stream lives in TinyRISC Instruction Memory.\n// Tree/forest decisions are executed with BEQ/BNE/JAL inside the CPU.\nmodule tb;\n  logic clk=0, reset=1;\n  logic [31:0] pc,current_instr;\n  logic signed [31:0] last_result;\n  logic halted;\n  integer cycles=0;\n  cpu dut(.clk(clk),.reset(reset),.pc(pc),.current_instr(current_instr),.last_result(last_result),.halted(halted));\n\n  task tick;\n    begin #1; clk=1; #1; clk=0; #1; cycles=cycles+1; end\n  endtask\n\n  initial begin\n{loads}\n    tick();\n    reset=0; cycles=0;\n    while(!halted && cycles < 5000) tick();\n    $display("CPU_RESULT prediction=%0d expected={int(expected)} cycles=%0d halted=%0d pc=%0d", dut.rf.regs[31], cycles, halted, pc);\n    if(!halted) $error("TinyRISC program did not halt");\n    if(dut.rf.regs[31] !== 32'd{int(expected)}) $error("TinyRISC CPU prediction mismatch");\n    $finish;\n  end\nendmodule\n'''


def run_one(name):
    meta=json.loads((OUT/f'{name}.json').read_text())
    words=BUILDERS[name](meta)
    expected=int(meta['sklearn_prediction'])

    # Save a human-inspectable instruction-memory image too.
    (GEN/f'{name}.mem').write_text('\n'.join(f'{w:08x}' for w in words)+'\n')
    tb=make_tb(name,words,expected)
    tb_path=GEN/f'cpu_{name}_tb.sv'; tb_path.write_text(tb)
    exe=OUT/f'cpu_{name}.out'
    rtl=[
        ROOT/'rtl'/'alu.sv', ROOT/'rtl'/'register.sv', ROOT/'rtl'/'counter.sv',
        ROOT/'rtl'/'register_file.sv', ROOT/'rtl'/'decoder.sv',
        ROOT/'rtl'/'ai_accelerator.sv', ROOT/'rtl'/'instruction_memory.sv', ROOT/'rtl'/'cpu.sv'
    ]
    cp=subprocess.run(['iverilog','-g2012','-o',str(exe),*map(str,rtl),str(tb_path)],cwd=ROOT,capture_output=True,text=True)
    if cp.returncode:
        return {'ok':False,'model':name,'output':cp.stdout+cp.stderr,'program_instructions':len(words)}
    rp=subprocess.run(['vvp',str(exe)],cwd=ROOT,capture_output=True,text=True)
    text=(rp.stdout or '')+(rp.stderr or '')
    m=re.search(r'CPU_RESULT prediction=(\d+) expected=(\d+) cycles=(\d+) halted=(\d+) pc=(\d+)',text)
    pred=int(m.group(1)) if m else None; exp=int(m.group(2)) if m else None; cyc=int(m.group(3)) if m else None
    halted=int(m.group(4)) if m else 0; pc=int(m.group(5)) if m else None
    return {
        'ok':rp.returncode==0 and pred==exp and halted==1,
        'model':name,'prediction':pred,'expected':exp,'cycles':cyc,
        'program_instructions':len(words),'final_pc':pc,
        'instruction_memory':f'generated/{name}.mem',
        'control_flow':'Executed inside TinyRISC with BEQ/BNE/JAL',
        'sv_output':text.strip()
    }

def main():
    if not (OUT/'models_summary.json').exists():
        subprocess.run([sys.executable,str(ROOT/'python'/'train_models.py')],cwd=ROOT,check=True)
    res=[run_one(n) for n in MODELS]
    (OUT/'cpu_inference_summary.json').write_text(json.dumps(res,indent=2))
    print(json.dumps(res,indent=2))
    return 0 if all(x['ok'] for x in res) else 1

if __name__ == '__main__':
    raise SystemExit(main())
