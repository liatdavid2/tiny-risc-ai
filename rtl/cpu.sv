module cpu(
    input  logic clk,
    input  logic reset,
    input  logic [31:0] instr,
    output logic [31:0] pc,
    output logic signed [31:0] last_result
);
    logic [4:0] rs1,rs2,rd;
    logic [3:0] alu_op;
    logic use_imm,reg_write,is_dot;
    logic signed [31:0] imm;
    logic [31:0] rv1_u, rv2_u;
    logic signed [31:0] rv1,rv2,alu_b,alu_result,dot_result;
    logic zero, dot_pred;
    logic [31:0] write_data;

    decoder dec(.instr(instr),.rs1(rs1),.rs2(rs2),.rd(rd),.alu_op(alu_op),.use_imm(use_imm),.reg_write(reg_write),.is_dot(is_dot),.imm(imm));
    register_file rf(.clk(clk),.we(reg_write),.rs1(rs1),.rs2(rs2),.rd(rd),.wd(write_data),.rv1(rv1_u),.rv2(rv2_u));
    assign rv1 = $signed(rv1_u);
    assign rv2 = $signed(rv2_u);
    assign alu_b = use_imm ? imm : rv2;
    alu alu0(.a(rv1),.b(alu_b),.op(alu_op),.result(alu_result),.zero(zero));
    ai_accelerator acc(.packed_x(rv1_u),.packed_w(rv2_u),.bias(32'sd0),.dot(dot_result),.prediction(dot_pred));
    assign write_data = is_dot ? dot_result : alu_result;
    assign last_result = $signed(write_data);

    always_ff @(posedge clk) begin
        if (reset) pc <= 32'd0;
        else       pc <= pc + 32'd4;
    end
endmodule
