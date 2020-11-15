`include "constants.vh"

module top_normalizer(
    input clk,
    input rst,

    input [`DATA_WIDTH-1:0] in_sample,
    input in_sample_valid,
    output logic ready,

    output logic [`DATA_WIDTH-1:0] out_sample,
    output logic out_sample_valid
);



    logic [23:0] mean_val;
    
    
    logic [7:0] mean_sample;
    logic mean_sample_valid;
    logic last_sample_sent;

    logic mad_ready;
    mean_calculator MEAN_CALCULATOR(
        .rst(rst),
        .clk(clk),

        .in_sample(in_sample),
        .in_sample_valid(in_sample_valid),

        .out_mean(mean_val),

        .ready(ready),
        .out_sample(mean_sample),
        .out_sample_valid(mean_sample_valid),
        .next_stage_ready(mad_ready)
    );

    logic [7:0] mad_sample;
    logic mad_sample_valid;
    logic [23:0] out_mad;

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

        .out_mad(out_mad)

    );

mad_normalizer MAD_NORMALIZER(
    .clk(clk),
    .rst(rst),
    .mad(out_mad),

    .in_sample({16'h0,mad_sample},
    .in_sample_valid(mad_sample_valid),

    .out_norm_val(out_sample),
    .out_norm_valid(out_sample_valid)
);


endmodule
