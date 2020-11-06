/*
 *
 * Starter Testbench for EECS 498/598 HW2
 * 
 * You can use this testbench to test your Edit-Distance systolic array
 * accelerator. Your design must at least pass these tests in order to
 * be considered for grading. Grading will use an expanded set of test 
 * cases that are secret.
 * 
 */

`include "constants.vh"

module testbench();


   /////////////////////////
   //  Global Decls
   /////////////////////////
   
   logic clk;
   logic rst;
   logic [`DATA_OUT_WIDTH-1:0] rst_val;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] query ;
   logic [`REF_MAX_LEN-1:0][`DATA_WIDTH-1:0] reference ;     
   
   logic                   start;
   logic                   done = 0;
   logic [`REF_SIZE_BITS:0]   reference_length; 
   logic [`DATA_OUT_WIDTH-1:0] result;
   logic[`DATA_OUT_WIDTH-1:0] expected_result=0;
   //additional signals
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_op;
   logic activate		[`QUERY_LEN-1:0];
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_prev_op;
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		counter;
   logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] diff;
       //logic signed [`DATA_OUT_WIDTH-1:0] P;
   logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0] score_wire;
   int ref_file,rd_file;
   // instantiate accelerator
   sDTW ed(.clk(clk),
                    .rst(rst),
                    .rst_val(rst_val),
                    .query(query),
                    .reference(reference),
                    .reference_length(reference_length),
                    .start(start),
                    .result(result),
                    .done(done),
                    .pe_op(pe_op),
                    .activate(activate),
                    .counter(counter),
                    .pe_prev_op(pe_prev_op),
                    .diff(diff),
                    //.P(P),
                    .score_wire(score_wire)
                    );   
   
   task read_from_file();
     //read reference from file
      ref_file=$fopen("G:/My Drive/SquiggAlign/data/covid/reference.signal","r");
      if (ref_file) $display("file opened succesfully: %0d",ref_file);
      else $display("file NOT opened succesfully: %0d",ref_file);
      $display("ptr=%d",ref_file);
      for(int i =1;i<=`REF_MAX_LEN;i++) begin
        $fscanf(ref_file,"%d",reference[i-1]);
      end
      $fclose(ref_file);
      
      //read input normalized squiggle from file
      rd_file=$fopen("G:/My Drive/SquiggAlign/data/covid/trimmed_read.signal","r");
      if (rd_file) $display("file opened succesfully: %0d",rd_file);
      else $display("file NOT opened succesfully: %0d",rd_file);
      for(int i =1;i<=`QUERY_LEN;i++) begin
        $fscanf(rd_file,"%d",query[i-1]);
      end
      $fclose(rd_file);
      $display("%d\t%d",query[5],reference[10]);
   endtask : read_from_file


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
      rst_val = `MAX_VAL ;  
      read_from_file();    
      //start = 1'b1;
      
      @(posedge clk)
      @(posedge clk)
      rst = 1'b0;
      start = 1'b1;
      reference_length=`REF_MAX_LEN;
      //query[`QUERY_LEN-1:0]={4'd5,4'd6};
      //query[`QUERY_LEN-1:0]={4'd8,4'd7,4'd5,4'd1,4'd17};
      //reference[`REF_MAX_LEN-1:0]={4'd1,4'd2,4'd3,4'd4,4'd5,4'd6,4'd7,4'd8,4'd9,4'd10};
      
      //reference[`REF_MAX_LEN-1:0]={4'd10,4'd9,4'd8,4'd7,4'd6,4'd5,4'd15,4'd15,4'd5,4'd1,4'd17};
      
     
      
      
      $display("////////////////////////////////////////////////");
      $display("//          Running Squal Testbench             //");
      $display("////////////////////////////////////////////////");
      
      
      while(done == 1'b0) begin
         @(posedge clk);
      end
      
      // check to see if the score matches the expectation
      if(result == expected_result) begin
         $display("Test\t\t\tPASSED!");
      end else begin
         $display("Test\t\t\tFAILED! result = %d expected = %d", result, expected_result);
      end
        $display("%d",`MAX_VAL);
      #10000000;

      $finish;
      
   end

endmodule
