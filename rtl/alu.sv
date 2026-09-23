module alu(
    input  logic signed [31:0] a,
    input  logic signed [31:0] b,
    input  logic [3:0]         op,
    output logic signed [31:0] result,
    output logic               zero
);
    localparam ALU_ADD = 4'd0;
    localparam ALU_SUB = 4'd1;
    localparam ALU_AND = 4'd2;
    localparam ALU_OR  = 4'd3;
    localparam ALU_XOR = 4'd4;
    localparam ALU_MUL = 4'd5;
    localparam ALU_SLT = 4'd6;
    localparam ALU_SRA = 4'd7;

    always_comb begin
        case (op)
            ALU_ADD: result = a + b;
            ALU_SUB: result = a - b;
            ALU_AND: result = a & b;
            ALU_OR : result = a | b;
            ALU_XOR: result = a ^ b;
            ALU_MUL: result = a * b;
            ALU_SLT: result = (a < b) ? 32'sd1 : 32'sd0;
            ALU_SRA: result = a >>> b[4:0];
            default: result = 32'sd0;
        endcase
    end
    assign zero = (result == 0);
endmodule
