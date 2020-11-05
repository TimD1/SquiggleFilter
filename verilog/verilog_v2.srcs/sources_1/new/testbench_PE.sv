`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/02/2020 11:18:27 PM
// Design Name: 
// Module Name: testbench_PE
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
`include "constants.vh"

module testbench_PE();
   logic clk;
   logic rst,top_rst;

   logic [`DATA_WIDTH-1:0] q;
   logic [`DATA_WIDTH-1:0] r;     
   
   logic                   start,activate;
   logic                   done = 0;
   logic [`REF_SIZE_BITS-1:0]             reference_length; 
   logic [`DATA_OUT_WIDTH-1:0] result, top,left,diag;
   logic [`DATA_OUT_WIDTH-1:0] buff_op,curr_op;
      logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] diff;
      logic [`DATA_OUT_WIDTH-1:0] rst_val;
       //logic signed [`DATA_OUT_WIDTH-1:0] P;
       logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0] score_wire;
PE pe(.clk(clk),
      .rst_val(rst_val),
      .rst(rst),
      .query(q),
      .reference(r),
      
      .activate(activate),      
      .top(top),
      .left(left),
      .diag(diag),
      .rst_value(0),              
      .prev_op(buff_op), .curr_op(curr_op),     
      .diff(diff[0]),
	  //.P(P),
	  .score_wire(score_wire[0])
      
    );
    
     always begin
      #5
        clk = ~clk;
     end
     initial begin

      
      
      // initialize constants
      start = 1'b0;
      
      // init control signals
      clk = 1'b0;
      rst = 1'b1;
      
      #10
         
        // reset for two clock cycles
      @(posedge clk)
      @(posedge clk)

      rst = 1'b0;
      start = 1'b1;
      activate=1'b1;
      top=11;
      left=22;
      diag=33;
      r=15;
      q=4;
      
      @(posedge clk)
     
      top=10;
      left=20;
      diag=30;
      r=13;
      q=6;
       @(posedge clk)
       top=11;
      left=22;
      diag=33;
      r=15;
      q=4;
      #1000;
       $finish;
     end

     
endmodule
