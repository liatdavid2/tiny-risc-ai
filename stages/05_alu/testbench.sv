module tb;
    logic signed [31:0] a,b,result;
    logic [3:0] op;
    logic zero;
    alu dut(.a(a),.b(b),.op(op),.result(result),.zero(zero));
    initial begin
        a=10; b=3;
        op=0; #1; if(result!==13) $error("ADD"); else $display("PASS ADD");
        op=1; #1; if(result!==7)  $error("SUB"); else $display("PASS SUB");
        op=2; #1; if(result!==(10&3)) $error("AND"); else $display("PASS AND");
        op=3; #1; if(result!==(10|3)) $error("OR"); else $display("PASS OR");
        op=4; #1; if(result!==(10^3)) $error("XOR"); else $display("PASS XOR");
        op=5; #1; if(result!==30) $error("MUL"); else $display("PASS MUL");
        $finish;
    end
endmodule
