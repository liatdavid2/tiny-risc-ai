module decoder(
    input  logic [31:0] instr,
    output logic [4:0]  rs1,
    output logic [4:0]  rs2,
    output logic [4:0]  rd,
    output logic [3:0]  alu_op,
    output logic        use_imm,
    output logic        reg_write,
    output logic        is_dot,
    output logic signed [31:0] imm
);
    logic [6:0] opcode, funct7;
    logic [2:0] funct3;
    always_comb begin
        opcode = instr[6:0];
        rd = instr[11:7];
        funct3 = instr[14:12];
        rs1 = instr[19:15];
        rs2 = instr[24:20];
        funct7 = instr[31:25];
        imm = {{20{instr[31]}}, instr[31:20]};
        alu_op = 4'd0; use_imm=0; reg_write=0; is_dot=0;
        case (opcode)
            7'b0110011: begin // R-type subset
                reg_write = 1;
                case ({funct7,funct3})
                    {7'b0000000,3'b000}: alu_op=4'd0; // ADD
                    {7'b0100000,3'b000}: alu_op=4'd1; // SUB
                    {7'b0000000,3'b111}: alu_op=4'd2; // AND
                    {7'b0000000,3'b110}: alu_op=4'd3; // OR
                    {7'b0000000,3'b100}: alu_op=4'd4; // XOR
                    {7'b0000001,3'b000}: alu_op=4'd5; // MUL (M extension style)
                    default: begin alu_op=4'd0; reg_write=0; end
                endcase
            end
            7'b0010011: begin // ADDI only
                if (funct3==3'b000) begin alu_op=4'd0; use_imm=1; reg_write=1; end
            end
            7'b0001011: begin // custom-0 opcode: packed int8 dot product
                is_dot=1; reg_write=1;
            end
            default: ;
        endcase
    end
endmodule
