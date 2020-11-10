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
      input [`DATA_WIDTH-1:0] ip_reference,
      
      input activate,      
      input [`DATA_OUT_WIDTH-1:0] top,
      input [`DATA_OUT_WIDTH-1:0] left,
      input [`DATA_OUT_WIDTH-1:0] diag,                  
      output logic[`DATA_OUT_WIDTH-1:0] prev_op, output logic[`DATA_OUT_WIDTH-1:0] curr_op,
      output logic stop_bit,
         
      output [`DATA_OUT_WIDTH-1:0] diff,      
      output logic [`DATA_OUT_WIDTH-1:0] score_wire
//      output [2:0] min_state
       );
  


  
     

//      wire [`DATA_OUT_WIDTH-1:0] diff;
//      logic [`DATA_OUT_WIDTH-1:0] score_wire;
      wire [2:0] min_state;
      wire stop_wire;
   

   

  //absolute delta score computation between reference and query
  assign diff= (query>ip_reference)?(query-ip_reference):(ip_reference-query);
  

  //state calculations for finding minimum among neighbors.
  assign min_state[2]=diag<top;
  assign min_state[1]=diag<left;
  assign min_state[0]=top<left;
  
  //find minimum among neighboring cells
  always @(*) begin
  casex (min_state)
              3'b11x: 
                score_wire=diff+diag;
              3'b10x: 
                score_wire=diff+left;
              3'b0x1: 
                score_wire=diff+top;
              3'b0x0: 
                score_wire=diff+left;
  endcase 
  end 

 assign stop_wire= (score_wire>=`DTW_THRESHOLD);
 
    always_ff @(posedge clk) begin //{}
       //sync reset
       if(rst) begin //{
          curr_op<=`MAX_VAL;
          prev_op<=curr_op;
          stop_bit<=0;
          

       end //}
       else if(activate) begin //{
          //update sequentially
          curr_op<=score_wire;
          stop_bit<=stop_wire;
          prev_op<=curr_op;
          
       end //}

        
        
        
 end //}

endmodule : PE