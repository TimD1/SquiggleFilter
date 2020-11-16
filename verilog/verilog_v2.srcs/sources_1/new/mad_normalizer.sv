`include "constants.vh"


module mad_normalizer(
    input clk,
    input rst,
    input [`DATA_WIDTH-1:0] mad,

    input [`DATA_WIDTH-1:0] in_sample,
    input in_sample_valid,

    output logic [`DATA_WIDTH-1:0] out_norm_val,
    output logic out_norm_valid
);

    

    logic [23:0] norm_val;
    logic norm_val_valid;

    logic [23:0] norm_val_q1;
    logic norm_val_q1_valid;

    logic [23:0] norm_val_q2;
    logic norm_val_q2_valid;

    div_gen_0 MEAN_DIV1 (
      .aclk(clk),                                       // input wire aclk
      .s_axis_divisor_tvalid(in_sample_valid),          // input wire s_axis_divisor_tvalid
      .s_axis_divisor_tdata(mad),                       // input wire [15 : 0] s_axis_divisor_tdata
      .s_axis_dividend_tvalid(in_sample_valid),         // input wire s_axis_dividend_tvalid
      .s_axis_dividend_tdata(in_sample),                // input wire [23 : 0] s_axis_dividend_tdata
      .m_axis_dout_tvalid(norm_val_valid),              // output wire m_axis_dout_tvalid
      .m_axis_dout_tdata(norm_val)                      // output wire [23 : 0] m_axis_dout_tdata
    );
    

    always_ff @(posedge clk) begin
        if(rst) begin
            norm_val_q1 <= 'h0;
            norm_val_q1_valid <= 1'b0;
        end
        else begin
            norm_val_q1 <= norm_val;
            norm_val_q1_valid <= norm_val_valid;
        end
    end

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            norm_val_q2 <= 'h0;
            norm_val_q2_valid <= 1'b0;
        end
        else begin
            if(norm_val_q1_valid) begin
                if(!norm_val_q1[23])
                    if(norm_val_q1[3:0] > `MAX_VAL) begin
                        norm_val_q2[3:0] <= `MAX_VAL;
                        norm_val_q2[23:4] <= 20'h0;
                    end
                    else begin
                        norm_val_q2 <= norm_val_q1;
                    end
                end

                if(norm_val_q1[23])
                    if(norm_val_q1[3:0] < `MAX_VAL) begin
                        norm_val_q2[3:0] <= `MIN_VAL;
                        norm_val_q2[23:4] <= ~0;
                    end
                    else begin
                        norm_val_q2 <= norm_val_q1;
                    end
                end
                
                norm_val_q2_valid <= 1'b1;
            end
        end
    end


endmodule
