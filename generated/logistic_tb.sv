module tb;
  logic signed [7:0] x0,x1,x2,x3;
  logic prediction;
  logistic_inference dut(.x0(x0),.x1(x1),.x2(x2),.x3(x3),.prediction(prediction));
  initial begin
    x0 = 8'sd9;
    x1 = -8'sd62;
    x2 = -8'sd18;
    x3 = 8'sd57;
    #1;
    $display("RESULT prediction=%0d expected=0", prediction);
    if (prediction !== 1'b0) $error("Prediction mismatch");
    $finish;
  end
endmodule
