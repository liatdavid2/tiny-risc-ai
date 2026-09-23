module ai_accelerator(
    input  logic [31:0] packed_x,
    input  logic [31:0] packed_w,
    input  logic signed [31:0] bias,
    output logic signed [31:0] dot,
    output logic prediction
);
    logic signed [7:0] x0,x1,x2,x3,w0,w1,w2,w3;
    always_comb begin
        x0 = packed_x[7:0];   x1 = packed_x[15:8];
        x2 = packed_x[23:16]; x3 = packed_x[31:24];
        w0 = packed_w[7:0];   w1 = packed_w[15:8];
        w2 = packed_w[23:16]; w3 = packed_w[31:24];
        dot = x0*w0 + x1*w1 + x2*w2 + x3*w3 + bias;
        prediction = (dot >= 0);
    end
endmodule
