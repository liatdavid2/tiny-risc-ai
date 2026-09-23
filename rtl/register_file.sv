module register_file(
    input  logic        clk,
    input  logic        we,
    input  logic [4:0]  rs1,
    input  logic [4:0]  rs2,
    input  logic [4:0]  rd,
    input  logic [31:0] wd,
    output logic [31:0] rv1,
    output logic [31:0] rv2
);
    logic [31:0] regs [0:31];
    integer i;
    initial begin
        for (i=0; i<32; i=i+1) regs[i] = 32'd0;
    end
    assign rv1 = (rs1 == 0) ? 32'd0 : regs[rs1];
    assign rv2 = (rs2 == 0) ? 32'd0 : regs[rs2];
    always_ff @(posedge clk) begin
        if (we && rd != 0) regs[rd] <= wd;
        regs[0] <= 32'd0;
    end
endmodule
