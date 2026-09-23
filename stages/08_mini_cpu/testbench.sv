`include "../../rtl/alu.sv"
`include "../../rtl/register_file.sv"
`include "../../rtl/decoder.sv"
`include "../../rtl/ai_accelerator.sv"
module tb;
    logic clk=0,reset=1; logic [31:0] instr; logic [31:0] pc; logic signed [31:0] last_result;
    always #5 clk=~clk;
    cpu dut(.clk(clk),.reset(reset),.instr(instr),.pc(pc),.last_result(last_result));
    initial begin
        instr=32'h00000013; #6; reset=0;
        instr=32'h00a00093; #10; // ADDI x1,x0,10
        instr=32'h01400113; #10; // ADDI x2,x0,20
        instr=32'h002081b3; #10; // ADD x3,x1,x2
        if (dut.rf.regs[3] !== 32'd30) $error("FAIL CPU x3=%0d", dut.rf.regs[3]); else $display("PASS CPU x3=30");
        $finish;
    end
endmodule
