
`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  
`timescale 1ns / 1ns

module mad_normalizer(
    input clk,
    input rst,
    input [`DATA_OUT_WIDTH-1:0] mad,

    input [`DATA_OUT_WIDTH-1:0] in_sample,
    input in_sample_valid,
    output logic [`DATA_OUT_WIDTH-1:0] norm_val_q1, //HARI
    output logic norm_val_q1_valid,
//HARI: what are these?
    output logic [`DATA_WIDTH-1:0] norm_val,
    output logic norm_val_valid,
    output logic [`DATA_OUT_WIDTH-1:0] norm_val_q2,
    output logic norm_val_q2_valid
);

        
//    logic [`DATA_OUT_WIDTH-1:0] norm_val;
//    logic norm_val_valid;

    //HARI//logic [`DATA_OUT_WIDTH-1:0] norm_val_q1;
    //logic norm_val_q1_valid;

   

    logic [`NORM_DIV1_DIVIDEND-1:0] in_sample_shifted;
    
    assign in_sample_shifted = in_sample << `MAD_SHIFT_SCALE;
    //HARI
    logic [23:0] wire_out;
    assign norm_val=wire_out[20:8];
    div_gen_3 NORM_DIV1 (
      .aclk(clk),                                       // input wire aclk
      .s_axis_divisor_tvalid(in_sample_valid),    // input wire s_axis_divisor_tvalid
      .s_axis_divisor_tdata(mad[`NORM_DIV1_DIVISOR-1:0]),                 // input wire [15 : 0] s_axis_divisor_tdata
      .s_axis_dividend_tvalid(in_sample_valid),   // input wire s_axis_dividend_tvalid
      .s_axis_dividend_tdata(in_sample_shifted[`NORM_DIV1_DIVIDEND-1:0]),          // input wire [23 : 0] s_axis_dividend_tdata
      .m_axis_dout_tvalid(norm_val_valid),              // output wire m_axis_dout_tvalid
      .m_axis_dout_tdata(wire_out)                      // output wire [23 : 0] m_axis_dout_tdata
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
                if(!norm_val_q1[`DATA_OUT_WIDTH-1]) begin
                    if(norm_val_q1[3:0] > `MAX_TVAL) begin
                        norm_val_q2[3:0] <= `MAX_TVAL;
                        norm_val_q2[`DATA_OUT_WIDTH-1:4] <= 20'h0;
                    end
                    else begin
                        norm_val_q2 <= norm_val_q1;
                    end
                end

                if(norm_val_q1[`DATA_OUT_WIDTH-1]) begin
                    if(norm_val_q1[3:0] < `MAX_TVAL) begin
                        norm_val_q2[3:0] <= `MIN_TVAL;
                        norm_val_q2[`DATA_OUT_WIDTH-1:4] <= ~0;
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
