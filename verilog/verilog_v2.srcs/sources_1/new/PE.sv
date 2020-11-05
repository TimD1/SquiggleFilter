`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: UofM
// Engineer: Harisankar Sadasivan
// 
// Create Date: 11/01/2020 10:45:14 PM
// Design Name: SquAl
// Module Name: PE
// Project Name: SquAl
// Target Devices: FPGA
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
//includ global defines
`include "constants.vh"

//Processing element of the systolic array
module PE(
      
      input clk,
      input rst,
      input [`DATA_WIDTH-1:0] query,
      input [`DATA_WIDTH-1:0] reference,
      
      input activate,      
      input [`DATA_OUT_WIDTH-1:0] top,
      input [`DATA_OUT_WIDTH-1:0] left,
      input [`DATA_OUT_WIDTH-1:0] diag,
      input [`DATA_OUT_WIDTH-1:0] rst_value,              
      output logic[`DATA_OUT_WIDTH-1:0] prev_op, output logic[`DATA_OUT_WIDTH-1:0] curr_op,     
      output [`DATA_WIDTH-1:0] diff,
      //output signed [`DATA_OUT_WIDTH+1:0] P,
      output [`DATA_OUT_WIDTH-1:0] score_wire
       );
  


  
     

  wire [`DATA_OUT_WIDTH-1:0] diag_tmp, top_tmp, left_tmp;
  //wire signed [`DATA_WIDTH:0] diff;
  //wire [`DATA_OUT_WIDTH-1:0] score_wire;
  //wire signed [`DATA_OUT_WIDTH+1:0] P; 

   
 
  //tmp wires
  assign diag_tmp = diag;
  assign top_tmp = top ;
  assign left_tmp = left ;
   

  //score computation
  assign diff= (query>reference)?(query-reference):(reference-query);
//   mult_gen_0 MUL (
//      .CLK(clk),  // input wire CLK
//      .A(diff),      // input wire [10 : 0] A
//      .B(diff),      // input wire [10 : 0] B
//      .P(P)      // output wire [21 : 0] P
//    );
  assign score_wire= diff + (diag_tmp<top_tmp?(diag_tmp<left_tmp?diag_tmp:left_tmp):(top_tmp<left_tmp?top_tmp:left_tmp));

    always_ff @(posedge clk or posedge rst) begin //{}
        
       if(rst) begin //{
          curr_op<=rst_value;
          prev_op<=curr_op;

       end //}
       else if(activate) begin //{
          //update sequentially
          curr_op<=score_wire;
          prev_op<=curr_op;

       end //}
       else begin //{
          curr_op<=curr_op;
          prev_op<=prev_op;
       end//}

        
        
        
    end //}
        
endmodule : PE