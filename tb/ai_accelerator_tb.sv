module tb;
    logic [31:0] packed_x,packed_w; logic signed [31:0] bias,dot; logic prediction;
    ai_accelerator dut(.*);
    initial begin
        // x=[1,2,3,4], w=[2,-1,1,3], bias=-5 => 2-2+3+12-5 = 10
        packed_x = {8'sd4,8'sd3,8'sd2,8'sd1};
        packed_w = {8'sd3,8'sd1,-8'sd1,8'sd2};
        bias=-5; #1;
        if(dot!==10 || prediction!==1) $error("FAIL dot=%0d pred=%0d",dot,prediction); else $display("PASS accelerator dot=10 pred=1");
        $finish;
    end
endmodule
