module tb;
    logic a, b, y;
    and_gate dut(.a(a), .b(b), .y(y));
    initial begin
        a=0; b=0; #1; if (y !== 0) $error("FAIL 0&0"); else $display("PASS 0&0");
        a=0; b=1; #1; if (y !== 0) $error("FAIL 0&1"); else $display("PASS 0&1");
        a=1; b=0; #1; if (y !== 0) $error("FAIL 1&0"); else $display("PASS 1&0");
        a=1; b=1; #1; if (y !== 1) $error("FAIL 1&1"); else $display("PASS 1&1");
        $finish;
    end
endmodule
