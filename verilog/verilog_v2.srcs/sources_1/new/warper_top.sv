//////////////////////////////////////////////////////////////////////////////////
// Company: UofM
// Engineer: Harisankar Sadasivan
// 
// Create Date: 11/01/2020 10:45:14 PM
// Design Name: SquAl
// Module Name: warper_top
// Project Name: SquAl
// Target Devices: FPGA
// Tool Versions: 
// Description: warper top for connecting sDTW to BRAM
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
module warper_top(input clk,
                     input rst, 
                     input start,                     
                     input init_sig,                       
                     input q_ena,
                     input q_wea,
                     input [`QUERY_SIZE_BITS-1 : 0] q_addra,                     
                     input [`DATA_WIDTH-1 : 0] q_dina,
                     input [`QUERY_SIZE_BITS-1 : 0] q_addrb,
                     input q_enb,
                     input r_ena,
                     input r_wea,   
                     input [`REF_SIZE_BITS-1:0] r_addra,
                     input [`DATA_WIDTH-1:0] r_dina,
                     output [`DATA_WIDTH-1:0] r_douta,                                                                             
                     output logic result,
                     output logic done  );



  wire [`DATA_WIDTH-1:0] query;
  wire [`DATA_WIDTH-1:0] reference;

  // instantiate warper
  sDTW ed(.clk(clk),
                    .rst(rst),                    
                    .query(query),
                    .reference(reference),
                    //.reference_length(reference_length),
                    .start(start),
                    .result(result),
                    .done(done),
                    .init_sig(init_sig)              
                    );   


  //vivado std lib
  //dual port
  bram_wA_rB q_bram(
   .clk(clk),
   .wea(q_wea),
   .ena(q_ena),
   .addra(q_addra),
   .da(q_dina),
   .enb(q_enb),
   .addrb(q_addrb),
   .qb(query)
   );


  //single port
  bram_rw ref_bram (
  .clk(clk),    // input wire clka
  .ena(r_ena),      // input wire ena
  .wea(r_wea),      // input wire [0 : 0] wea
  .addra(r_addra),  // input wire [15 : 0] addra
  .da(r_dina),    // input wire [7 : 0] dina
  .qa(reference)  // output wire [7 : 0] douta
  );


endmodule : warper_top