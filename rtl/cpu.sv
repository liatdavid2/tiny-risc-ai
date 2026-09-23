module cpu(
    input  logic clk,
    input  logic reset,
    output logic [31:0] pc,
    output logic [31:0] current_instr,
    output logic signed [31:0] last_result,
    output logic halted
);
    logic [4:0] rs1,rs2,rd;
    logic [3:0] alu_op;
    logic use_imm,reg_write,is_dot,branch_eq,branch_ne,jump,halt_dec;
    logic signed [31:0] imm;
    logic [31:0] rv1_u, rv2_u;
    logic signed [31:0] rv1,rv2,alu_b,alu_result,dot_result;
    logic zero, dot_pred;
    logic [31:0] write_data;
    logic take_branch;
    logic rf_we;

    instruction_memory imem(.addr(pc), .instr(current_instr));

    decoder dec(
        .instr(current_instr),
        .rs1(rs1),.rs2(rs2),.rd(rd),.alu_op(alu_op),
        .use_imm(use_imm),.reg_write(reg_write),.is_dot(is_dot),
        .branch_eq(branch_eq),.branch_ne(branch_ne),.jump(jump),.halt(halt_dec),
        .imm(imm)
    );

    register_file rf(
        .clk(clk),.we(rf_we),.rs1(rs1),.rs2(rs2),.rd(rd),.wd(write_data),
        .rv1(rv1_u),.rv2(rv2_u)
    );

    assign rv1 = $signed(rv1_u);
    assign rv2 = $signed(rv2_u);
    assign alu_b = use_imm ? imm : rv2;

    alu alu0(.a(rv1),.b(alu_b),.op(alu_op),.result(alu_result),.zero(zero));
    ai_accelerator acc(.packed_x(rv1_u),.packed_w(rv2_u),.bias(32'sd0),.dot(dot_result),.prediction(dot_pred));

    assign write_data = jump ? (pc + 32'd4) : (is_dot ? dot_result : alu_result);
    assign last_result = $signed(write_data);
    assign take_branch = (branch_eq && (rv1_u == rv2_u)) || (branch_ne && (rv1_u != rv2_u));
    assign rf_we = reg_write && !reset && !halted && !halt_dec;

    always_ff @(posedge clk) begin
        if (reset) begin
            pc <= 32'd0;
            halted <= 1'b0;
        end else if (!halted) begin
            if (halt_dec) begin
                halted <= 1'b1;
                pc <= pc;
            end else if (jump) begin
                pc <= pc + imm;
            end else if (take_branch) begin
                pc <= pc + imm;
            end else begin
                pc <= pc + 32'd4;
            end
        end
    end
endmodule
