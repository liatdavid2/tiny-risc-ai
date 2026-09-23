module tb;
    logic [31:0] instr; logic [4:0] rs1,rs2,rd; logic [3:0] alu_op; logic use_imm,reg_write,is_dot; logic signed [31:0] imm;
    decoder dut(.*);
    initial begin
        // ADD x3,x1,x2 = 0x002081b3
        instr=32'h002081b3; #1;
        if(!(rd==3 && rs1==1 && rs2==2 && alu_op==0 && reg_write)) $error("FAIL ADD decode"); else $display("PASS ADD decode");
        // ADDI x1,x0,10 = 0x00a00093
        instr=32'h00a00093; #1;
        if(!(rd==1 && rs1==0 && use_imm && imm==10 && reg_write)) $error("FAIL ADDI decode"); else $display("PASS ADDI decode");
        $finish;
    end
endmodule
