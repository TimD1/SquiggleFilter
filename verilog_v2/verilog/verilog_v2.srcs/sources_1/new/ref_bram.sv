//---------------------------------------------------------------------------------------
// Amazon FPGA Hardware Development Kit
//
// Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
//
// Licensed under the Amazon Software License (the "License"). You may not use
// this file except in compliance with the License. A copy of the License is
// located at
//
//    http://aws.amazon.com/asl/
//
// or in the "license" file accompanying this file. This file is distributed on
// an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or
// implied. See the License for the specific language governing permissions and
// limitations under the License.
//---------------------------------------------------------------------------------------
//----------------------------------------------------
// This is a dual ported BRAM
//----------------------------------------------------
`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  
`timescale 1ns / 1ns
module bram_rw #(parameter WIDTH=`DATA_WIDTH, parameter ADDR_WIDTH=`REF_SIZE_BITS, parameter DEPTH=`REF_MAX_LEN, parameter PIPELINE=0, parameter MEMORY_TYPE = "auto") 
(
   input clk,
   input wea,
   input ena,
   input[ADDR_WIDTH-1:0] addra,
   input[WIDTH-1:0] da,
   output logic[WIDTH-1:0] qa

   );

`ifndef NO_XILINX_XPM_RAM 

   xpm_memory_spram # (
   // Common module parameters
   .MEMORY_SIZE (WIDTH*DEPTH), //positive integer
   .MEMORY_PRIMITIVE (MEMORY_TYPE), //string; "auto", "distributed", "block" or "ultra";
   .MEMORY_INIT_FILE ("none"), //string; "none" or "<filename>.mem"
   .MEMORY_INIT_PARAM ("" ), //string;
   .USE_MEM_INIT (1), //integer; 0,1
   .WAKEUP_TIME ("disable_sleep"), //string; "disable_sleep" or "use_sleep_pin"
   .MESSAGE_CONTROL (0), //integer; 0,1

   // Port A module parameters
   .WRITE_DATA_WIDTH_A (WIDTH), //positive integer
   .READ_DATA_WIDTH_A (WIDTH), //positive integer
   .BYTE_WRITE_WIDTH_A (WIDTH), //integer; 8, 9, or WRITE_DATA_WIDTH_A value
   .ADDR_WIDTH_A (ADDR_WIDTH), //positive integer
   .READ_RESET_VALUE_A ("0"), //string
   .READ_LATENCY_A (PIPELINE+1), //non-negative integer
   .WRITE_MODE_A ("read_first") //string; "write_first", "read_first", "no_change"

   ) xpm_memory_spram_inst (
   // Common module ports
   .sleep (1'b0),
   // Port A module ports
   .clka (clk),
   .rsta (1'b0),
   .ena (ena),
   .regcea (1'b1),
   .wea (wea),
   .addra (addra),
   .dina (da),
   .injectsbiterra (1'b0), //do not change
   .injectdbiterra (1'b0), //do not change
   .douta (qa),
   .sbiterra (), //do not change
   .dbiterra () //do not change

   );
   // End of xpm_memory_tdpram instance declaration

`else

   logic[WIDTH-1:0] ram[DEPTH-1:0];
   
   logic[WIDTH-1:0] rddata_a, rddata_a_q;
   
   always @(posedge clk)
      if (ena)
      begin
         if (wea)
            ram[addra] <= da;
         else
            rddata_a <= ram[addra];
      end
   
   always @(posedge clk)
      rddata_a_q <= rddata_a;
   
   assign qa = (PIPELINE)? rddata_a_q: rddata_a;
   
`endif


   
endmodule  
