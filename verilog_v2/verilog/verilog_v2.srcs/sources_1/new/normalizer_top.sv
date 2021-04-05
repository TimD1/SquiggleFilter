//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 12/21/2020 10:24:44 AM
// Design Name: 
// Module Name: normalizer_top
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////
`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  
`timescale 1ns / 1ns

module normalizer_top(input clk, 
                      input rst,
                      input rd_done,
                      input [`IP_DATA_WIDTH-1:0] in_sample,
                      input in_sample_valid,
                      input last_sample_in,
                      input logic [`IP_DATA_WIDTH-1:0] mean,
                      input logic mean_valid,
                      input logic [`IP_DATA_WIDTH-1:0] mad,
                      input logic mad_valid
                      // input logic [`IP_DATA_WIDTH-1:0] mad,
                      // input logic mad_valid
                      // output logic [`IP_DATA_WIDTH-1:0] out_mean,
                      // output logic out_d_valid
                     );
    
 // mean_finder mf(
 //    .rst(rst),
 //    .clk(clk),
 //    .rd_done(rd_done),
 //    .in_sample(in_sample),
 //    .in_sample_valid(in_sample_valid),
 //    .last_sample_in(last_sample_in),
 //    .out_mean(out_mean),
 //    .out_mean_valid(out_mean_valid)
 
 //    );
 // mad_finder mf(
 //    .rst(rst),
 //    .clk(clk),
 //    .rd_done(rd_done),
 //    .in_sample(in_sample),
 //    .in_sample_valid(in_sample_valid),
 //    .last_sample_in(last_sample_in),
 //    .mean(mean),
 //    .mean_valid(mean_valid),
 //    .out_mad(out_mad),
 //    .out_mad_valid(out_mad_valid)
 
 //    );

 mean_mad_normalizer mmn(
    .rst(rst),
    .clk(clk),
    .in_sample(in_sample),
    .in_sample_valid(in_sample_valid),
    .last_sample_in(last_sample_in),
    .mean(mean),
    .mean_valid(mean_valid),
    .mad(mad),
    .mad_valid(mad_valid)
    //.scaled_op(scaled_op)
    //output logic scaled_op_valid

);
endmodule : normalizer_top
