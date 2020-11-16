`timescale 1ns / 1ns
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
// Description: defines the PE in the systolic array (warper) for SquAl
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////
//include global defines
`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  

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
      input init,             
      output logic[`DATA_OUT_WIDTH-1:0] prev_op, output logic[`DATA_OUT_WIDTH-1:0] curr_op,
      output logic stop_bit,
      output [`DATA_WIDTH-1:0] query_o , 
      output [`DATA_WIDTH-1:0] op_reference         
       );
  


  
     
     //internal logic and wires
    logic [`DATA_WIDTH-1:0] query_o_r;
    logic [1:0] set_bit=0;
    wire stop_wire;
    wire [`DATA_OUT_WIDTH-1:0] diff;      
    logic [`DATA_OUT_WIDTH-1:0] score_wire;
    wire [`DATA_WIDTH-1:0] l_query;
    logic [`DATA_WIDTH-1:0] l_query_r;       
    wire  [`DATA_WIDTH-1:0] ip_ref ;
    logic [`DATA_WIDTH-1:0] ip_reference_r;
    wire [2:0] min_state;


  //register streaming reference
  always @(posedge clk) begin

    ip_reference_r<=ip_reference;     
  end
  
  
  //wires for registered output from ref and query
  assign ip_ref=ip_reference_r;
  assign op_reference=ip_ref;
  assign op_reference = ip_reference_r;
  
  assign l_query=l_query_r;
  assign query_o=query_o_r;

  //absolute delta score computation between reference and query
  assign diff= (l_query>ip_ref)?(l_query-ip_ref):(ip_ref-l_query);
   

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

  //stopping score line
  assign stop_wire= (score_wire>=`DTW_THRESHOLD);
 
    always_ff @(posedge clk) begin //{}
       
       if(rst) begin //{  //sync reset
          curr_op<=`MAX_VAL;
          prev_op<=curr_op;
          stop_bit<=0;
          set_bit<=0;
          l_query_r<=0;
          query_o_r<=0;
          

       end //}
       else if(init) begin //{ //PE initialization 
          if(set_bit<2'b1) begin
            l_query_r<=query;
            set_bit<=set_bit+1;
          end
          else query_o_r<=query;
       end //}
       else if(activate) begin //{ //Firing the PE
          //update sequentially
          curr_op<=score_wire;
          stop_bit<=stop_wire;
          prev_op<=curr_op;   
                     
       end //}
       
    
        
        
        
     end //}
     

endmodule : PE