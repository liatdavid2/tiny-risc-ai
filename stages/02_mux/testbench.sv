module tb;
    logic a, b, sel, y;
    mux2 dut(.a(a), .b(b), .sel(sel), .y(y));
    initial begin
        a=0; b=1; sel=0; #1; if (y !== 0) $error("FAIL"); else $display("PASS sel=0 y=%0d", y);
        sel=1; #1; if (y !== 1) $error("FAIL"); else $display("PASS sel=1 y=%0d", y);
        a=1; b=0; sel=0; #1; if (y !== 1) $error("FAIL"); else $display("PASS sel=0 y=%0d", y);
        sel=1; #1; if (y !== 0) $error("FAIL"); else $display("PASS sel=1 y=%0d", y);
        $finish;
    end
endmodule
