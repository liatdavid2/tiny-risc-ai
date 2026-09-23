module tb;
    logic [31:0] instr;
    logic [4:0] rs1,rs2,rd;
    logic [3:0] alu_op;
    logic use_imm,reg_write,is_dot,branch_eq,branch_ne,jump,halt;
    logic signed [31:0] imm;
    decoder dut(.*);

    initial begin
        // ADD x3,x1,x2 = 0x002081b3
        instr=32'h002081b3; #1;
        if(!(rd==3 && rs1==1 && rs2==2 && alu_op==0 && reg_write)) $error("FAIL ADD decode"); else $display("PASS ADD decode");

        // ADDI x1,x0,10 = 0x00a00093
        instr=32'h00a00093; #1;
        if(!(rd==1 && rs1==0 && use_imm && imm==10 && reg_write)) $error("FAIL ADDI decode"); else $display("PASS ADDI decode");

        // BEQ x1,x2,+8 = 0x00208463
        instr=32'h00208463; #1;
        if(!(rs1==1 && rs2==2 && branch_eq && imm==8)) $error("FAIL BEQ decode imm=%0d", imm); else $display("PASS BEQ decode");

        // BNE x1,x2,+8 = 0x00209463
        instr=32'h00209463; #1;
        if(!(rs1==1 && rs2==2 && branch_ne && imm==8)) $error("FAIL BNE decode imm=%0d", imm); else $display("PASS BNE decode");

        // JAL x0,+8 = 0x0080006f
        instr=32'h0080006f; #1;
        if(!(jump && imm==8)) $error("FAIL JAL decode imm=%0d", imm); else $display("PASS JUMP decode");

        instr=32'hffff_ffff; #1;
        if(!halt) $error("FAIL HALT decode"); else $display("PASS HALT decode");

        $finish;
    end
endmodule
