module tb;
    logic clk=0,we; logic [4:0] rs1,rs2,rd; logic [31:0] wd,rv1,rv2;
    always #5 clk=~clk;
    register_file dut(.clk(clk),.we(we),.rs1(rs1),.rs2(rs2),.rd(rd),.wd(wd),.rv1(rv1),.rv2(rv2));
    initial begin
        we=1; rd=5'd1; wd=32'd10; rs1=1; rs2=0; #6;
        we=0; #1; if(rv1!==10) $error("FAIL write/read"); else $display("PASS R1=10");
        we=1; rd=0; wd=99; #10; we=0; rs1=0; #1;
        if(rv1!==0) $error("FAIL x0"); else $display("PASS x0 always zero");
        $finish;
    end
endmodule
