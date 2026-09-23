module instruction_memory #(
    parameter DEPTH = 1024
)(
    input  logic [31:0] addr,
    output logic [31:0] instr
);
    localparam INDEX_BITS = $clog2(DEPTH);
    logic [31:0] mem [0:DEPTH-1];
    integer i;

    initial begin
        for (i = 0; i < DEPTH; i = i + 1)
            mem[i] = 32'h00000013; // NOP = ADDI x0,x0,0
    end

    assign instr = mem[addr[INDEX_BITS+1:2]];
endmodule
