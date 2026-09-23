module tb;
    logic clk=0, reset=1;
    logic [7:0] count;
    always #5 clk=~clk;
    counter #(.WIDTH(8), .STEP(1)) dut(.clk(clk), .reset(reset), .count(count));
    initial begin
        #6; reset=0;
        #5; if (count !== 1) $error("FAIL count=%0d", count); else $display("PASS count=1");
        #10; if (count !== 2) $error("FAIL count=%0d", count); else $display("PASS count=2");
        #10; if (count !== 3) $error("FAIL count=%0d", count); else $display("PASS count=3");
        $finish;
    end
endmodule
