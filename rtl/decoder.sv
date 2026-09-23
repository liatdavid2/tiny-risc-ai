module decoder(
    input  logic [31:0] instr,
    output logic [4:0]  rs1,
    output logic [4:0]  rs2,
    output logic [4:0]  rd,
    output logic [3:0]  alu_op,
    output logic        use_imm,
    output logic        reg_write,
    output logic        is_dot,
    output logic        branch_eq,
    output logic        branch_ne,
    output logic        jump,
    output logic        halt,
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

        alu_op = 4'd0;
        use_imm = 1'b0;
        reg_write = 1'b0;
        is_dot = 1'b0;
        branch_eq = 1'b0;
        branch_ne = 1'b0;
        jump = 1'b0;
        halt = 1'b0;
        imm = 32'sd0;

        if (instr == 32'hFFFF_FFFF) begin
            halt = 1'b1;
        end else begin
            case (opcode)
                7'b0110011: begin // R-type subset
                    reg_write = 1'b1;
                    case ({funct7,funct3})
                        {7'b0000000,3'b000}: alu_op=4'd0; // ADD
                        {7'b0100000,3'b000}: alu_op=4'd1; // SUB
                        {7'b0000000,3'b111}: alu_op=4'd2; // AND
                        {7'b0000000,3'b110}: alu_op=4'd3; // OR
                        {7'b0000000,3'b100}: alu_op=4'd4; // XOR
                        {7'b0000001,3'b000}: alu_op=4'd5; // MUL (M-extension style)
                        {7'b0000000,3'b010}: alu_op=4'd6; // SLT
                        default: begin alu_op=4'd0; reg_write=1'b0; end
                    endcase
                end

                7'b0010011: begin // I-type subset
                    imm = {{20{instr[31]}}, instr[31:20]};
                    case (funct3)
                        3'b000: begin alu_op=4'd0; use_imm=1'b1; reg_write=1'b1; end // ADDI
                        3'b010: begin alu_op=4'd6; use_imm=1'b1; reg_write=1'b1; end // SLTI
                        3'b101: begin // SRAI teaching subset
                            alu_op=4'd7; use_imm=1'b1; reg_write=1'b1;
                            imm = {27'd0, instr[24:20]};
                        end
                        default: ;
                    endcase
                end

                7'b1100011: begin // B-type branches
                    imm = {{19{instr[31]}}, instr[31], instr[7], instr[30:25], instr[11:8], 1'b0};
                    case (funct3)
                        3'b000: branch_eq = 1'b1; // BEQ
                        3'b001: branch_ne = 1'b1; // BNE
                        default: ;
                    endcase
                end

                7'b1101111: begin // JAL
                    imm = {{11{instr[31]}}, instr[31], instr[19:12], instr[20], instr[30:21], 1'b0};
                    jump = 1'b1;
                    reg_write = (rd != 5'd0); // JAL x0,label behaves as JUMP
                end

                7'b0001011: begin // custom-0: packed int8 dot product
                    is_dot = 1'b1;
                    reg_write = 1'b1;
                end

                default: ;
            endcase
        end
    end
endmodule
