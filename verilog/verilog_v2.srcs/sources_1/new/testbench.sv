/*
 *
 SquAL testbench
 * 
 */

`include "constants.vh"

module testbench();


   /////////////////////////
   //  Global Decls
   /////////////////////////
   
   logic clk;
   logic rst;
   //logic [`DATA_OUT_WIDTH-1:0] rst_val;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] query ;
   logic [`DATA_WIDTH-1:0] reference ;     
   
   logic                   start;
   logic                   done = 0;
   //logic [`REF_SIZE_BITS:0]   reference_length; 
   logic  result;
   logic[`DATA_OUT_WIDTH-1:0] expected_result=0;
   //additional signals
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_op;
   logic activate		[`QUERY_LEN-1:0];
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_prev_op;
  // logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		counter;
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0] diff;
       //logic signed [`DATA_OUT_WIDTH-1:0] P;
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0] score_wire;
   int ref_file,rd_file;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] ip_reference;
   logic [`CNTR_BITS-1:0] counter;
   logic stop_sig;
   logic [`QUERY_LEN-1:0] early_stop;
   logic [`QUERY_LEN-1:0] normal_stop;
   // instantiate accelerator
    
   sDTW ed(.clk(clk),
                    .rst(rst),                    
                    .query(query),
                    .reference(reference),
                    //.reference_length(reference_length),
                    .start(start),
                    .result(result),
                    .done(done),
                    .pe_op(pe_op),
                    .activate(activate),
                    //.counter(counter),
                    .pe_prev_op(pe_prev_op),
                    .diff(diff),
                    //.P(P),
                    .score_wire(score_wire),
                    .ip_reference(ip_reference),
                    .counter(counter),
                    .stop_sig(stop_sig),
                    .early_stop(early_stop),
                    .normal_stop(normal_stop)
                    );   
                    
   //making connections to inner module wires
   
       //logic signed [`DATA_OUT_WIDTH-1:0] P;

   
//    for(integer i=0;i<`QUERY_LEN;i++) begin //{
   
        
         
//   end //}
   
   
   task read_from_ref();
     //read reference from file
      automatic int i=0;
      ref_file=$fopen("G:/My Drive/SquiggAlign/data/covid/reference.signal","r");
      if (ref_file) $display("file opened succesfully: %0d",ref_file);
      else $display("file NOT opened succesfully: %0d",ref_file);
      $display("ptr=%d",ref_file);
      while(!$feof(ref_file)) begin
        i+=1;
        @(posedge clk)
        $fscanf(ref_file,"%d\n",reference);
        if(i==`REF_MAX_LEN) break;
      end
      $fclose(ref_file);
   endtask : read_from_ref

   task read_from_rd();   
      //read input normalized squiggle from file
      rd_file=$fopen("G:/My Drive/SquiggAlign/data/covid/trimmed_read.signal","r");
      if (rd_file) $display("file opened succesfully: %0d",rd_file);
      else $display("file NOT opened succesfully: %0d",rd_file);
      while(!$feof(rd_file)) begin
        //@(posedge clk)
        for(int i=0;i<`QUERY_LEN;i++) begin //{
        $fscanf(rd_file,"%d\n",query[i]); 
        end //}
        break;
      end
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
      @(posedge clk)
      @(posedge clk)
      rst = 1'b1;
      
      //start = 1'b1;
      
      @(posedge clk)
      @(posedge clk)
      rst = 1'b0;
      @(posedge clk)
      @(posedge clk)
      
   
      fork 
        read_from_ref();
        read_from_rd();
        begin
        @(posedge clk)
        start = 1'b1;
        end
      join_none
    
     
      
      
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
