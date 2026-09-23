module tb;
    logic clk=0,reset=1;
    logic [31:0] pc,current_instr;
    logic signed [31:0] last_result;
    logic halted;
    integer cycles=0;

    cpu dut(.clk(clk),.reset(reset),.pc(pc),.current_instr(current_instr),.last_result(last_result),.halted(halted));

    task tick;
      begin #1; clk=1; #1; clk=0; #1; cycles=cycles+1; end
    endtask

    initial begin
        // Program in instruction memory:
        // 0: ADDI x1,x0,10
        // 1: ADDI x2,x0,10
        // 2: BEQ  x1,x2,+8 -> skip next ADDI
        // 3: ADDI x3,x0,99  (must be skipped)
        // 4: ADD  x3,x1,x2  (x3=20)
        // 5: JAL  x0,+8     -> skip next ADDI
        // 6: ADDI x3,x0,77  (must be skipped)
        // 7: HALT
        dut.imem.mem[0]=32'h00a00093;
        dut.imem.mem[1]=32'h00a00113;
        dut.imem.mem[2]=32'h00208463;
        dut.imem.mem[3]=32'h06300193;
        dut.imem.mem[4]=32'h002081b3;
        dut.imem.mem[5]=32'h0080006f;
        dut.imem.mem[6]=32'h04d00193;
        dut.imem.mem[7]=32'hffff_ffff;

        tick(); reset=0;
        while(!halted && cycles<20) tick();

        if (!halted) $error("FAIL CPU did not halt");
        else if (dut.rf.regs[3] !== 32'd20) $error("FAIL CPU branch/jump x3=%0d", dut.rf.regs[3]);
        else $display("PASS CPU instruction memory + BEQ + JUMP x3=20 cycles=%0d", cycles);
        $finish;
    end
endmodule
