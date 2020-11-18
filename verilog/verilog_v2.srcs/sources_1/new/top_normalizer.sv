`include "constants.vh"

module top_normalizer(
    input clk,
    input rst,

    input [`DATA_WIDTH-1:0] in_sample,
    input in_sample_valid,
    output logic ready,

    output logic [`DATA_WIDTH-1:0] out_sample,
    output logic out_sample_valid,
     //exposed memory lines
    input logic mc_IN_MEM_wea,
    input logic mc_IN_MEM_ena,
    input logic [`QUERY_SIZE_BITS-1:0] mc_IN_MEM_addr,
    input logic [`DATA_OUT_WIDTH-1:0] mc_IN_MEM_da,
    input logic [`DATA_OUT_WIDTH-1:0] mc_IN_MEM_qa,
    input logic [`DATA_WIDTH-1:0] IN_MEM_qa,
    output logic [`DATA_OUT_WIDTH-1:0] norm_val_q2,
    output logic norm_val_q2_valid
);

    logic out_mean_valid; //to be taken care of

    logic [`DATA_OUT_WIDTH-1:0] mean_val;
    
    
    logic [`DATA_WIDTH-1:0] mean_sample;
    logic mean_sample_valid;
    logic last_sample_sent;

    logic mad_ready;
    
    
   
   
    mean_calculator MEAN_CALCULATOR(
        .rst(rst),
        .clk(clk),

        .in_sample(in_sample),
        .in_sample_valid(in_sample_valid),
        .IN_MEM_qa(IN_MEM_qa),
        .out_mean(mean_val),
        .out_mean_valid(out_mean_valid),
        .last_sample_sent(last_sample_sent),
        .ready(ready),
        .out_sample(mean_sample),
        .out_sample_valid(mean_sample_valid),
        .next_stage_ready(mad_ready)
    );

    logic [`DATA_WIDTH-1:0] mad_sample;
    logic mad_sample_valid;
    logic [`DATA_OUT_WIDTH-1:0] out_mad;

    mad_calculator MAD_CALCULATOR(
        .clk(clk),
        .rst(rst),

        .in_sample(mean_sample),
        .in_sample_valid(mean_sample_valid),
        .last_sample_sent(last_sample_sent),

        .in_mean(mean_val),

        .ready(mad_ready),
        .out_sample(mad_sample),
        .out_sample_valid(mad_sample_valid),

        .out_mad(out_mad),
        .IN_MEM_wea(mc_IN_MEM_wea),
        .IN_MEM_ena(mc_IN_MEM_ena),
        .IN_MEM_addr(mc_IN_MEM_addr),
        .IN_MEM_da(mc_IN_MEM_da),
        .IN_MEM_qa(mc_IN_MEM_qa)

    );
logic [`DATA_OUT_WIDTH-1:0] norm_val_q1;//HARI
logic norm_val_q1_valid; //HARI
mad_normalizer MAD_NORMALIZER(
    .clk(clk),
    .rst(rst),
    .mad(out_mad),
    .norm_val_q1(norm_val_q1),
    .in_sample({mad_sample}),
    .in_sample_valid(mad_sample_valid),
    .norm_val_q1_valid(norm_val_q1_valid),
    .norm_val(out_sample),
    .norm_val_valid(out_sample_valid),
    .norm_val_q2(norm_val_q2),
    .norm_val_q2_valid(norm_val_q2_valid)
);


endmodule
