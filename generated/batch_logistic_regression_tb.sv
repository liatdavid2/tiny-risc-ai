module tb;
  logic clk=0, reset=1;
  logic [31:0] pc,current_instr;
  logic signed [31:0] last_result;
  logic halted;
  integer cycles=0; integer r;
  cpu dut(.clk(clk),.reset(reset),.pc(pc),.current_instr(current_instr),.last_result(last_result),.halted(halted));
  task tick; begin #1; clk=1; #1; clk=0; #1; cycles=cycles+1; end endtask
  initial begin
    dut.imem.mem[0] = 32'h00900093;
    dut.imem.mem[1] = 32'hfc200113;
    dut.imem.mem[2] = 32'hfee00193;
    dut.imem.mem[3] = 32'h03900213;
    dut.imem.mem[4] = 32'hf9c00293;
    dut.imem.mem[5] = 32'h01400313;
    dut.imem.mem[6] = 32'h01600393;
    dut.imem.mem[7] = 32'h00500413;
    dut.imem.mem[8] = 32'hf0a00a13;
    dut.imem.mem[9] = 32'h00000513;
    dut.imem.mem[10] = 32'h025085b3;
    dut.imem.mem[11] = 32'h00b50533;
    dut.imem.mem[12] = 32'h026105b3;
    dut.imem.mem[13] = 32'h00b50533;
    dut.imem.mem[14] = 32'h027185b3;
    dut.imem.mem[15] = 32'h00b50533;
    dut.imem.mem[16] = 32'h028205b3;
    dut.imem.mem[17] = 32'h00b50533;
    dut.imem.mem[18] = 32'h01450533;
    dut.imem.mem[19] = 32'h00052f13;
    dut.imem.mem[20] = 32'h000f1663;
    dut.imem.mem[21] = 32'h00100f93;
    dut.imem.mem[22] = 32'h0080006f;
    dut.imem.mem[23] = 32'h00000f93;
    dut.imem.mem[24] = 32'hffffffff;
    // sample 0
    for (r=0; r<32; r=r+1) dut.rf.regs[r] = 32'd0;
    dut.imem.mem[0] = 32'h00900093;
    dut.imem.mem[1] = 32'hfc200113;
    dut.imem.mem[2] = 32'hfee00193;
    dut.imem.mem[3] = 32'h03900213;
    reset=1; tick(); reset=0; cycles=0;
    while(!halted && cycles < 5000) tick();
    $display("BATCH_RESULT idx=0 prediction=%0d cycles=%0d halted=%0d", dut.rf.regs[31], cycles, halted);
    // sample 1
    for (r=0; r<32; r=r+1) dut.rf.regs[r] = 32'd0;
    dut.imem.mem[0] = 32'h02600093;
    dut.imem.mem[1] = 32'hfdf00113;
    dut.imem.mem[2] = 32'hfe000193;
    dut.imem.mem[3] = 32'h02300213;
    reset=1; tick(); reset=0; cycles=0;
    while(!halted && cycles < 5000) tick();
    $display("BATCH_RESULT idx=1 prediction=%0d cycles=%0d halted=%0d", dut.rf.regs[31], cycles, halted);
    // sample 2
    for (r=0; r<32; r=r+1) dut.rf.regs[r] = 32'd0;
    dut.imem.mem[0] = 32'h01900093;
    dut.imem.mem[1] = 32'hfd700113;
    dut.imem.mem[2] = 32'hfea00193;
    dut.imem.mem[3] = 32'h02500213;
    reset=1; tick(); reset=0; cycles=0;
    while(!halted && cycles < 5000) tick();
    $display("BATCH_RESULT idx=2 prediction=%0d cycles=%0d halted=%0d", dut.rf.regs[31], cycles, halted);
    // sample 3
    for (r=0; r<32; r=r+1) dut.rf.regs[r] = 32'd0;
    dut.imem.mem[0] = 32'hfee00093;
    dut.imem.mem[1] = 32'h01d00113;
    dut.imem.mem[2] = 32'h02500193;
    dut.imem.mem[3] = 32'hfdd00213;
    reset=1; tick(); reset=0; cycles=0;
    while(!halted && cycles < 5000) tick();
    $display("BATCH_RESULT idx=3 prediction=%0d cycles=%0d halted=%0d", dut.rf.regs[31], cycles, halted);
    // sample 4
    for (r=0; r<32; r=r+1) dut.rf.regs[r] = 32'd0;
    dut.imem.mem[0] = 32'hfda00093;
    dut.imem.mem[1] = 32'h01700113;
    dut.imem.mem[2] = 32'h01500193;
    dut.imem.mem[3] = 32'hfe800213;
    reset=1; tick(); reset=0; cycles=0;
    while(!halted && cycles < 5000) tick();
    $display("BATCH_RESULT idx=4 prediction=%0d cycles=%0d halted=%0d", dut.rf.regs[31], cycles, halted);
    // sample 5
    for (r=0; r<32; r=r+1) dut.rf.regs[r] = 32'd0;
    dut.imem.mem[0] = 32'hfef00093;
    dut.imem.mem[1] = 32'h00f00113;
    dut.imem.mem[2] = 32'h00800193;
    dut.imem.mem[3] = 32'hfd100213;
    reset=1; tick(); reset=0; cycles=0;
    while(!halted && cycles < 5000) tick();
    $display("BATCH_RESULT idx=5 prediction=%0d cycles=%0d halted=%0d", dut.rf.regs[31], cycles, halted);

    $finish;
  end
endmodule
