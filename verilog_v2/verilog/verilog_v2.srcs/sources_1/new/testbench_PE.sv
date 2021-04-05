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
`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  


module testbench_PE();
   logic clk;
   logic rst,top_rst;

   logic [`DATA_WIDTH-1:0] query,query_o;
   logic [`DATA_WIDTH-1:0] ip_reference,op_reference;
   logic [`DATA_WIDTH-1:0] o_r;     
   logic init;
   logic                   start,activate;
   logic                   done = 0;
   logic [`REF_SIZE_BITS-1:0]             reference_length; 
   logic [`DATA_OUT_WIDTH-1:0] result, top,left,diag;
   logic [`DATA_OUT_WIDTH-1:0] prev_op,curr_op;
   logic [`DATA_OUT_WIDTH-1:0] diff;
    logic[`MAX_BONUS_WIDTH-1:0] prev_bonus,ip_bonus;
   logic stop_bit;
    logic [`DATA_OUT_WIDTH-1:0] loop_score_o ;
    logic loop_score_val       ;  
       //logic signed [`DATA_OUT_WIDTH-1:0] P;
      logic [`DATA_OUT_WIDTH-1:0] score_wire;

      PE_last_col_v2 pe(.clk(clk),           
      .rst(rst),
      .query(query),
      .ip_reference(ip_reference),    
      .activate(activate) ,
      //input [`DATA_OUT_WIDTH-1:0] top,
      .ip_bonus(ip_bonus),
      .left(left),
      .diag(diag),     
      .init(init),             
      .prev_op(prev_op), 
      .curr_op(curr_op),
      .prev_bonus(prev_bonus), 
      //output logic stop_bit,   
      .query_o(query_o) , 
      .op_reference(op_reference) ,
      .stop_bit(stop_bit),
      .loop_score_o(loop_score_o),
      .loop_score_val(loop_score_val)            
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
      @(posedge clk)
      @(posedge clk)

      init=1;
      query=4;
       @(posedge clk)
       init=0;
      //start = 1'b1;
      activate=1'b1;
      top=11;
      left=22;
      diag=33;
      ip_reference=10;
      ip_bonus=0;
      
      
      @(posedge clk)
     
      top=30;
      left=20;
      diag=10;
      ip_reference=20;
      ip_bonus=8;
       @(posedge clk)
       top=22;
      left=11;
      diag=33;
      ip_reference=30;
      ip_bonus=16;
      #1000;
       $finish;
     end

     
endmodule
