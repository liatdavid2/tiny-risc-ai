module counter #(parameter WIDTH = 32, parameter STEP = 1)(
    input  logic             clk,
    input  logic             reset,
    output logic [WIDTH-1:0] count
);
    always_ff @(posedge clk) begin
        if (reset) count <= '0;
        else       count <= count + STEP;
    end
endmodule
