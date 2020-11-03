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
module PE(input clk,
      input rst,
      input [`DATA_WIDTH-1:0] q,
      input [`DATA_WIDTH-1:0] r,
      
      input activate,      
      input [`DATA_WIDTH-1:0] top,
      input [`DATA_WIDTH-1:0] left,
      input [`DATA_WIDTH-1:0] diag,
      input [`DATA_WIDTH-1:0] top_rst,              
      output logic[`DATA_WIDTH-1:0] buff_op, output logic[`DATA_WIDTH-1:0] curr_op,     
      output done
    
       );
  

 

  
     
  wire [`DATA_WIDTH-1:0] diag_tmp, top_tmp, left_tmp, score_wire,diff;

  //tmp wires
  assign diag_tmp = diag;
  assign top_tmp = top ;
  assign left_tmp = left ;
   

  //score computation
  assign diff= q-r;
  assign score_wire= diff*diff + (diag_tmp<top_tmp?(diag_tmp<left_tmp?diag_tmp:left_tmp):(top_tmp<left_tmp?top_tmp:left_tmp));

    always_ff @(posedge clk or posedge rst) begin //{}
        
       if(rst) begin //{
          curr_op<=top_rst;
          buff_op<=0;

       end //}
       else if(activate) begin //{
          //update sequentially
          curr_op<=score_wire;
          buff_op<=curr_op;

       end //}
       else begin //{
          curr_op<=curr_op;
          buff_op<=buff_op;
       end//}

        
        
        
    end //}
        
endmodule : PE


