module tb;
    logic clk=0, reset=1;
    logic [7:0] d, q;
    always #5 clk = ~clk;
    register #(.WIDTH(8)) dut(.clk(clk), .reset(reset), .d(d), .q(q));
    initial begin
        d=8'd42; #7;
        reset=0; #3; // next posedge at t=10 captures 42
        #1; if (q !== 8'd42) $error("FAIL register"); else $display("PASS register q=%0d", q);
        d=8'd99; #10; #1; if (q !== 8'd99) $error("FAIL register update"); else $display("PASS register q=%0d", q);
        $finish;
    end
endmodule
