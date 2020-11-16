//////////////////////////////////////////////////////////////////////////////////
// Company: UofM
// Engineer: Harisankar Sadasivan
// 
// Create Date: 11/01/2020 10:45:14 PM
// Design Name: SquAl
// Module Name: testbench
// Project Name: SquAl
// Target Devices: FPGA
// Tool Versions: 
// Description: top testbench for SquAl
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
module testbench();


   /////////////////////////
   //  Global Decls
   /////////////////////////
   
   //-------common vars-------------//
   logic clk;
   logic rst;

   logic [`DATA_WIDTH-1:0] query ;
   logic [`DATA_WIDTH-1:0] reference ;     
   
   logic                   start;
   logic                   done = 0;

   logic  result;
   logic[`DATA_OUT_WIDTH-1:0] expected_result=0;
   //additional signals
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_op;
   logic activate		[`QUERY_LEN-1:0];
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_prev_op;  
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0] diff;
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0] score_wire;
   int ref_file,rd_file;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] ip_reference;
   logic [`CNTR_BITS-1:0] counter;
   logic [`QUERY_LEN-1:0] stop_bits;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] l_query;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] op_reference;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] l_query_r;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] query_o;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] ip_ref ;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] ip_reference_r;
   logic init_sig;
   //-------------------------//

   //-----------------BRAM specific vars-------------//
   logic q_ena=0;
   logic q_wea=0;
   logic [`QUERY_SIZE_BITS-1 : 0] q_addra=0;
   logic [`DATA_WIDTH-1 : 0] q_dina=0,tmp=0,tmp1=0,q_doutb=0; //tmp variables store values read from file
   logic q_enb=0;
   logic [`QUERY_SIZE_BITS-1 : 0] q_addrb=0;   
   logic r_ena=0;      
   logic r_wea=0;
   logic [`REF_SIZE_BITS-1:0] r_addra=0;
   logic [`DATA_WIDTH-1:0] r_dina=0;   
   logic [`DATA_WIDTH-1:0] r_douta=0;  
   //-------------------------------//

   //warper top instantiation
   warper_top w_t(   .clk(clk),
                     .rst(rst), 
                     .start(start),                     
                     .init_sig(init_sig),                       
                     .q_ena(q_ena),
                     .q_wea(q_wea),
                     .q_addra(q_addra),                     
                     .q_dina(q_dina),
                     .q_enb(q_enb),
                     .r_ena(r_ena),
                     .r_wea(r_wea),   
                     .r_addra(r_addra),
                     .r_dina(r_dina),
                     .r_douta(r_douta),                 
                     .q_addrb(q_addrb),                                       
                     .result(result),
                     .done(done)  );
   
  
// vivado std IP                    
//   //connect BRAMs to warper
//   blk_mem_gen_0 query_bram (
//  .clka(clk),    // input wire clka
//  .ena(q_ena),      // input wire ena
//  .wea(q_wea),      // input wire [0 : 0] wea
//  .addra(q_addra),  // input wire [13 : 0] addra
//  .dina(q_dina),    // input wire [7 : 0] dina
//  .clkb(clk),    // input wire clkb
//  .enb(q_enb),      // input wire enb
//  .addrb(q_addrb),  // input wire [13 : 0] addrb
//  .doutb(q_doutb)  // output wire [7 : 0] doutb
//   );

//  blk_mem_gen_1 ref_bram (
//  .clka(clk),    // input wire clka
//  .ena(r_ena),      // input wire ena
//  .wea(r_wea),      // input wire [0 : 0] wea
//  .addra(r_addra),  // input wire [15 : 0] addra
//  .dina(r_dina),    // input wire [7 : 0] dina
//  .douta(reference)  // output wire [7 : 0] douta
//  );
   
   

   
   //-----------read query and reference from file directly instead of from BRAM ----------------//
//    task read_from_ref();
//      //read reference from file
//       automatic int i=0;
//       ref_file=$fopen("G:/My Drive/SquiggAlign/data/covid/reference.signal","r");
//       if (ref_file) $display("file opened succesfully: %0d",ref_file);
//       else $display("file NOT opened succesfully: %0d",ref_file);
//       $display("ptr=%d",ref_file);
//       while(!$feof(ref_file)) begin
//         i+=1;
//         @(posedge clk)
//         $fscanf(ref_file,"%d\n",reference);
//         if(i==`REF_MAX_LEN) break;
//       end
//       $fclose(ref_file);
//    endtask : read_from_ref

//    task read_from_rd();   
//       //read input normalized squiggle from file
//       automatic int i=0;
//       rd_file=$fopen("G:/My Drive/SquiggAlign/data/covid/trimmed_read.signal","r");
//       if (rd_file) $display("file opened succesfully: %0d",rd_file);
//       else $display("file NOT opened succesfully: %0d",rd_file);
//       while(!$feof(rd_file)) begin
//         i+=1;
//         @(posedge clk)        
//         $fscanf(rd_file,"%d\n",query); 
//         if(i==`QUERY_LEN) break;    
//       end
//       $fclose(rd_file);    
//    endtask : read_from_rd
   //----------------------------------------------//

   //read and write into BRAM from testbench --------------//
   task write_reference();
      
     //from reference from file to bram
      automatic int i=0;
      ref_file=$fopen("G:/My Drive/SquiggAlign/data/covid/reference.signal","r");
      if (ref_file) $display("file opened succesfully: %0d",ref_file);
      else $display("file NOT opened succesfully: %0d",ref_file);
      $display("ptr=%d",ref_file);
      while(!$feof(ref_file)) begin
       
        $fscanf(ref_file,"%d\n",tmp); 
     
          r_ena=1;
          r_wea=1;
          
          r_dina=tmp;
         @(posedge clk)
         i+=1;
        if(i==`REF_MAX_LEN) begin
       
          r_ena=0;
          r_wea=0;
          r_addra=0;
         
          i=0;
          break;
        end
        else r_addra+=1;
      end
      $fclose(ref_file);
   endtask : write_reference

   task write_query();
      
     //write query to bram from file
      automatic int i=0;
      rd_file=$fopen("G:/My Drive/SquiggAlign/data/covid/trimmed_read.signal","r");
      if (rd_file) $display("file opened succesfully: %0d",rd_file);
      else $display("file NOT opened succesfully: %0d",rd_file);
      $display("ptr=%d",rd_file);
      while(!$feof(rd_file)) begin
       
        $fscanf(rd_file,"%d\n",tmp1); 
   
          q_ena=1;
          q_wea=1;
          
          q_addra=i;
          q_dina=tmp1;
        
         @(posedge clk)
        
         i+=1;
         
         if(i==`QUERY_LEN) begin
       
          q_ena=0;
          q_wea=0;
          //q_addra=0;

          i=0;
          
          break;

        end
        
      end
      $fclose(rd_file);
   endtask : write_query

  task read_from_query();
   //read reference from bram
    q_enb=1;
    
   
    
    for(int i=0;q_enb!=0;i++) begin
      q_addrb=i;
      @(negedge clk);
      
      if(i==`QUERY_LEN-1) begin
            // @(posedge clk);
              q_enb=0;  
              //i=0;
                     
              break;
              
      end 
     
      
    end  
  endtask : read_from_query

  task read_from_reference();
   //read reference from bram
    r_ena=1;
    r_wea=0;
    
    
    for(int i=0;r_ena!=0;i++) begin
      r_addra=i;
      @(posedge clk);
      if(i==`REF_MAX_LEN-1) begin
             @(posedge clk);           
              r_ena=0;  
             
          
              break;
              
      
      end 
     
      
    end  
  endtask : read_from_reference


   //-------------common clock -----------//
   always begin
      #5
        clk = ~clk;
   end
   //-------------------------------//

   task latency_h();
    for(int i=0;i<`QUERY_LEN+1;i++)
        @(posedge clk);
    
   endtask: latency_h

   //-----------testbench starts here---------------//
   initial begin

     
      
      // initialize constants
      start = 1'b0;
      
      // init control signals
      clk = 1'b0;
      
      #10
         
        // reset for two clock cycles
      @(posedge clk)
      @(posedge clk)
      rst = 1'b1;
      init_sig=0;
      
      //start = 1'b1;
      
      @(posedge clk)
      @(posedge clk)
      rst = 1'b0;
      @(posedge clk)
      @(posedge clk)
      
      //---tb starter when reading inputs from file----//
//       fork 
//         read_from_ref();
//         read_from_rd();
//         begin
//         @(posedge clk)
//         start = 1'b1;
//         end
//       join_none
      //-----------------------------//

      //--tb started when writing and reading from bram---------------//
      //initialize BRAM with reference, one time config---//
      
      write_reference();
      
      write_query();
      init_sig=1'b1;
      
        read_from_query();
        latency_h();
        init_sig=0;

      fork
      
       begin  

        @(posedge clk);
        read_from_reference();
       end
       begin
        @(posedge clk);
        @(posedge clk);
        @(posedge clk);
         @(posedge clk);
        start=1'b1;
       end 
      join_none
         
       
           //array start
      
          
         
      
      $display("////////////////////////////////////////////////");
      $display("//          Running Squal Testbench             //");
      $display("////////////////////////////////////////////////");
      
      
      while(result == 1'b0) begin
         @(posedge clk);
      end
      rst=1;
      // check to see if the score matches the expectation
      if(result == expected_result) begin
         $display("Test\t\t\tPASSED!");
      end else begin
         $display("Test\t\t\tFAILED! result = %d expected = %d", result, expected_result);
      end
        $display("%d",`MAX_VAL);
      //#10000000;

      $finish;
      
   end

   initial begin
    
   end

endmodule
