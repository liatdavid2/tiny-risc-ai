from pathlib import Path
import argparse, json, pickle, re, subprocess, time
import numpy as np

from run_tinyrisc_cpu_inference import ROOT, OUT, GEN, MODELS, BUILDERS, ADDI


def balanced_indices(y, max_per_class):
    picked=[]
    for cls in sorted(np.unique(y)):
        idx=np.flatnonzero(y==cls)[:max_per_class]
        picked.extend(idx.tolist())
    return np.array(picked, dtype=int)


def make_batch_tb(name, words, q_samples):
    base='\n'.join(f"    dut.imem.mem[{i}] = 32'h{w:08x};" for i,w in enumerate(words))
    blocks=[]
    for idx, q in enumerate(q_samples):
        loads='\n'.join(f"    dut.imem.mem[{i}] = 32'h{ADDI(1+i,0,int(v)):08x};" for i,v in enumerate(q))
        blocks.append(f'''    // sample {idx}\n    for (r=0; r<32; r=r+1) dut.rf.regs[r] = 32'd0;\n{loads}\n    reset=1; tick(); reset=0; cycles=0;\n    while(!halted && cycles < 5000) tick();\n    $display("BATCH_RESULT idx={idx} prediction=%0d cycles=%0d halted=%0d", dut.rf.regs[31], cycles, halted);\n''')
    return f'''module tb;\n  logic clk=0, reset=1;\n  logic [31:0] pc,current_instr;\n  logic signed [31:0] last_result;\n  logic halted;\n  integer cycles=0; integer r;\n  cpu dut(.clk(clk),.reset(reset),.pc(pc),.current_instr(current_instr),.last_result(last_result),.halted(halted));\n  task tick; begin #1; clk=1; #1; clk=0; #1; cycles=cycles+1; end endtask\n  initial begin\n{base}\n{''.join(blocks)}\n    $finish;\n  end\nendmodule\n'''


def run_hardware_batch(name, meta, q_samples):
    tmp=dict(meta)
    tmp['sample_int8']=q_samples[0].tolist()
    words=BUILDERS[name](tmp)
    tb=make_batch_tb(name, words, q_samples)
    tb_path=GEN/f'batch_{name}_tb.sv'; tb_path.write_text(tb)
    exe=OUT/f'batch_{name}.out'
    rtl=[ROOT/'rtl'/'alu.sv', ROOT/'rtl'/'register.sv', ROOT/'rtl'/'counter.sv',
         ROOT/'rtl'/'register_file.sv', ROOT/'rtl'/'decoder.sv', ROOT/'rtl'/'ai_accelerator.sv',
         ROOT/'rtl'/'instruction_memory.sv', ROOT/'rtl'/'cpu.sv']
    t0=time.perf_counter()
    cp=subprocess.run(['iverilog','-g2012','-o',str(exe),*map(str,rtl),str(tb_path)],cwd=ROOT,capture_output=True,text=True)
    if cp.returncode:
        raise RuntimeError(cp.stdout+cp.stderr)
    rp=subprocess.run(['vvp',str(exe)],cwd=ROOT,capture_output=True,text=True)
    sim_wall_ms=(time.perf_counter()-t0)*1000.0
    if rp.returncode:
        raise RuntimeError((rp.stdout or '')+(rp.stderr or ''))
    rows=re.findall(r'BATCH_RESULT idx=(\d+) prediction=(\d+) cycles=(\d+) halted=(\d+)',rp.stdout or '')
    if len(rows)!=len(q_samples):
        raise RuntimeError(f'{name}: expected {len(q_samples)} batch results, got {len(rows)}')
    rows=sorted(rows,key=lambda x:int(x[0]))
    return {
        'predictions':[int(x[1]) for x in rows],
        'cycles':[int(x[2]) for x in rows],
        'halted':[int(x[3]) for x in rows],
        'program_instructions':len(words),
        'simulation_wall_ms':sim_wall_ms,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--max-per-class',type=int,default=25)
    args=ap.parse_args()
    max_per_class=max(1,min(int(args.max_per_class),100))
    artifacts=OUT/'training_artifacts.pkl'
    if not artifacts.exists():
        raise SystemExit('Train models first.')
    with artifacts.open('rb') as f: data=pickle.load(f)
    X,y,QX=data['X'],data['y'],data['QX']; models=data['models']
    idx=balanced_indices(y,max_per_class)
    Xb,yb,Qb=X[idx],y[idx],QX[idx]
    class_counts={str(int(c)):int(np.sum(yb==c)) for c in np.unique(yb)}
    results=[]
    for name in MODELS:
        model=models[name]
        t0=time.perf_counter(); host_pred=model.predict(Xb); host_ms=(time.perf_counter()-t0)*1000.0
        meta=json.loads((OUT/f'{name}.json').read_text())
        hw=run_hardware_batch(name,meta,Qb)
        cpu_pred=np.array(hw['predictions'],dtype=int)
        agreement=float(np.mean(cpu_pred==host_pred))
        host_acc=float(np.mean(host_pred==yb)); cpu_acc=float(np.mean(cpu_pred==yb))
        cycles=np.array(hw['cycles'],dtype=float)
        results.append({
            'model':name,'samples':int(len(idx)),'class_counts':class_counts,
            'host_accuracy':host_acc,'cpu_accuracy':cpu_acc,'agreement':agreement,
            'host_inference_ms':host_ms,'host_avg_us_per_sample':host_ms*1000.0/len(idx),
            'cpu_total_cycles':int(cycles.sum()),'cpu_avg_cycles_per_sample':float(cycles.mean()),
            'cpu_min_cycles':int(cycles.min()),'cpu_max_cycles':int(cycles.max()),
            'program_instructions':hw['program_instructions'],
            'simulator_wall_ms':hw['simulation_wall_ms'],
            'mismatches':int(np.sum(cpu_pred!=host_pred)),
        })
    payload={'max_per_class':max_per_class,'samples':int(len(idx)),'class_counts':class_counts,'models':results,
             'note':'Host time is real sklearn wall-clock inference time. TinyRISC execution is reported in simulated CPU cycles; simulator wall time is not hardware latency.'}
    (OUT/'batch_benchmark.json').write_text(json.dumps(payload,indent=2))
    print(json.dumps(payload,indent=2))

if __name__=='__main__': main()
