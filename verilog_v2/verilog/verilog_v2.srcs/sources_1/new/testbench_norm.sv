`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/17/2020 12:46:39 PM
// Design Name: 
// Module Name: testbench_norm
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

module testbench_norm(

    );

    logic clk;
    logic rst;
    logic [`IP_DATA_WIDTH-1:0] in_sample;
    logic in_sample_valid;
    logic last_sample_in;
    logic [`IP_DATA_WIDTH-1:0] out_mean,mean;
    logic out_mean_valid ;
    logic start,rd_done;
    int rd_file;
    logic mean_valid,mad_valid;
    logic [`IP_DATA_WIDTH-1:0] mad;

    // normalizer_top ntop(
    // .rst(rst),
    // .clk(clk),
    // .rd_done(rd_done),
    // .in_sample(in_sample),
    // .in_sample_valid(in_sample_valid),
    // .last_sample_in(last_sample_in),
    // .out_mean(out_mean),
    // .out_mean_valid(out_mean_valid)
    // );
    normalizer_top ntop(
    .rst(rst),
    .clk(clk),
    .rd_done(rd_done),
    .in_sample(in_sample),
    .in_sample_valid(in_sample_valid),
    .last_sample_in(last_sample_in),
    .mean(mean),
    .mean_valid(mean_valid),
    .mad(mad),
    .mad_valid(mad_valid)
    );
  
    task read_from_rd();   
      //read input normalized squiggle from file
      automatic int i=0;
      rd_file=$fopen("G:/My Drive/SquAl/raw.signal","r");
      if (rd_file) $display("file opened succesfully: %0d",rd_file);
      else $display("file NOT opened succesfully: %0d",rd_file);
      last_sample_in=0;
      while(!$feof(rd_file)) begin
        i+=1;
        @(posedge clk)
        mean_valid=1;
        mean=477;     
        mad_valid=1;
        mad=477;    
        $fscanf(rd_file,"%d\n",in_sample);
        in_sample_valid=1; 
        if(i==`QUERY_LEN) break;    
      end
      mean_valid=0;
      mad_valid=0;
      $fclose(rd_file);    
   endtask : read_from_rd

   always begin
      #5
        clk = ~clk;
   end
   initial begin

     
      
      // initialize constants
      start = 1'b0;
      
      // init control signals
      clk = 1'b0;
      
      #10
         
        // reset for two clock cycles
      @(posedge clk);
      @(posedge clk);
      rst = 1'b1;
      last_sample_in=0;
      in_sample_valid=0;
      rd_done=0;
      @(posedge clk);
      @(posedge clk);
      rst=0;

      //drive in_sample_valid=1;
      read_from_rd();
      // @(posedge clk);
      last_sample_in=1;
      @(posedge clk);
      last_sample_in=0;
      in_sample_valid=0;
      rd_done=1;
      @(posedge clk);
      rd_done=0;
      #10000;
      //while(out_mean==0);
      
   end
endmodule: testbench_norm
