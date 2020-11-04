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

   logic [`DATA_WIDTH-1:0] query [`QUERY_LEN-1:0];
   logic [`DATA_WIDTH-1:0] reference [`REF_MAX_LEN-1:0];     
   
   logic                   start;
   logic                   done = 0;
   logic [9:0]             reference_length; 
   logic [`DATA_WIDTH-1:0] result;
   
   // instantiate accelerator
   sDTW ed(.clk(clk),
                    .rst(rst),
                    .query(query),
                    .reference(reference),
                    .reference_length(reference_length),
                    .start(start),
                    .result(result),
                    .done(done)
                    );   
   

   /////////////////////////
   //  Helper Tasks
   /////////////////////////


    task software_edit_distance(input clk,
                                input rst,
                                input start,
                                input [`DATA_WIDTH-1:0] query [`QUERY_LEN-1:0],
                                input [`DATA_WIDTH-1:0] reference [`REF_MAX_LEN-1:0],
                                input [9:0] reference_length,
                                output done,
                                output [`DATA_WIDTH-1:0] result);

      int i,j,t,c;
      int edit_distance[`QUERY_LEN+1][`REF_MAX_LEN+1];

      for (i=0; i<=`QUERY_LEN; i++) 
      begin
        edit_distance[i][0] = i;
      end

      for(j=0; j<=reference_length; j++)
      begin
        edit_distance[0][j] = j;
      end

      for (i=1; i<=`QUERY_LEN; i++)
      begin
        for(j=1; j <= reference_length; j++)
        begin
          // $display("Query %0d", query[i-1]);
          // $display("Reference %0d", reference[j-1]);
          if(query[i-1] == reference[j-1])
            c = 0;
          else
            c = 1;
          t = (edit_distance[i-1][j] < edit_distance[i][j-1]) ? edit_distance[i-1][j] + 1 : edit_distance[i][j-1] + 1;
          edit_distance[i][j] = (edit_distance[i-1][j-1]+c) < t ? (edit_distance[i-1][j-1] + c) : t;
          // $display("i %0d j %0d Value %0d", i, j, edit_distance[i][j]);
        end
      end

      result = edit_distance[`QUERY_LEN][reference_length];
      $display("Edit Distance Value: %0d", result);
      done = 1'b1;

    endtask

    task run_test(string test_id,
                 input [`DATA_WIDTH-1:0] test_query [`QUERY_LEN-1:0], 
                 input [`DATA_WIDTH-1:0] test_reference [`REF_MAX_LEN-1:0],
                 input [`REF_SIZE_BITS:0]             test_reference_len,
                 input [`DATA_WIDTH-1:0] expected_result);
      
      query = test_query;
      reference = test_reference;
      reference_length = test_reference_len;
      
      // reset edit distance accelerator
      rst = 1'b1;
      @(posedge clk)
      @(posedge clk)
      rst = 1'b0;
      
      // start the accelerator!
      start = 1'b1;

      
      // Call your own verification task here if you please
      
       // software_edit_distance(.clk(clk),
       // .rst(rst),
       // .start(start),
       // .query(query),
       // .reference(reference),
       // .reference_length(reference_length),
       // .done(done),
       // .result(result));
       
      
      // wait for test to finish
      while(done == 1'b0) begin
         @(posedge clk);
      end
      
      // check to see if the score matches the expectation
      if(result == expected_result) begin
         $display("Test\t%d\t\tPASSED!", test_id);
      end else begin
         $display("Test\t%d\t\tFAILED! result = %d expected = %d", test_id, result, expected_result);
      end
      
   endtask
   
   
   always begin
      #5
        clk = ~clk;
   end
   

   initial begin

      
      
      // initialize constants
      start = 1'b0;
      
      // init control signals
      clk = 1'b0;
      rst = 1'b1;
      
      #10
         
        // reset for two clock cycles
      @(posedge clk)
      @(posedge clk)

      rst = 1'b0;
      start = 1'b1;
      
      @(posedge clk)
      @(posedge clk)
      
      
      $display("////////////////////////////////////////////////");
      $display("//          Running HW2 Testbench             //");
      $display("////////////////////////////////////////////////");
      // run_test("Substitution", 
      //          "ATGC", 
      //          "ATGG", 
      //          4, 
      //          1);

      run_test("Exact Match", 
               "123456789", 
               "56", 
               10, 
               0);

//      run_test("Substitution", 
//               "TTACATCTTGAAAATCTAGTCGTCTCTCTCAGTTCCAGGCGGTAAGCCGAGTACGGATAAAACTTCTCGAACAATCCGCCGGAGCGACAGATAGCCTCTAA", 
//               "TTACATCTTGAAAATCTAGTCGTCTCTCTCAGTTCCAGGCGGTAAGCCGAGAACGGATAAAACTTCTCGAACAATCCGCCGGAGCGACAGATAGCCTCTAA", 
//               101, 
//               1);
      
//      run_test("Insertion", 
//               "TTACATCTTGAAAATCTAGTCGTCTCTCTCAGTTCCAGGCGGTAAGCCGAGTACGGATAAAACTTCTCGAACAATCCGCCGGAGCGACAGATAGCCTCTAA", 
//               "TTACATCTTGAAAATCTAGTCGTCTCTCTCAGTTCCAGGCGGTAAGCCGAGGTACGGATAAAACTTCTCGAACAATCCGCCGGAGCGACAGATAGCCTCTAA", 
//               102, 
//               1);
      
//      run_test("Deletion", 
//               "CTGGTCCAACTGTATTAAGATAAATTAAGCGACGGGGCCGTCTCTGCTGAAGTCGCCCTGTGGTTGGTCAAGGTAGCTAACTTACGGTCGGCAGGAGTCTG", 
//               "CTGGTCCAACTGTATTAAGATAAATTAAGCGACGGGGCCGTCTCTGCTGAAGTCGCCCTGTGGTTGGTCAAGTAGCTAACTTACGGTCGGCAGGAGTCTG", 
//               100, 
//               1);

//      run_test("2 Substitutions", 
//               "CTGGTCCAACTGTATTAAGATAAATTAAGGGACGGGGCCGTCTCTGCTGAAGTCGCCCTGTGGTTGGACAAGGTAGCTAACTTACGGTCGGCAGGAGTCTG", 
//               "CTGGTCCAACTGTATTAAGATAAATTAAGCGACGGGGCCGTCTCTGCTGAAGTCGCCCTGTGGTTGGTCAAGGTAGCTAACTTACGGTCGGCAGGAGTCTG", 
//               101, 
//               2);

//      run_test("2 Insertions", 
//               "CTGGTCCAACTGTATTAAGATAAATTAAGCGACGGGGCCGTCTCTGCTGAAGTCGCCCTGTGGTTGGTCAAGGTAGCTAACTTACGGTCGGCAGGAGTCTG", 
//               "CTGGTCCAACTGTATTAAGATAAATTGAAGCGACGGGGCCGTCTCTGCTGAAGTCGCCCTGTGGTTGGTGCAAGGTAGCTAACTTACGGTCGGCAGGAGTCTG", 
//               103, 
//               2);

//      run_test("2 Deletions", 
//               "CTGGTCCAACTGTATTAAGATAAATTAAGCGACGGGGCCGTCTCTGCTGAAGTCGCCCTGTGGTTGGTCAAGGTAGCTAACTTACGGTCGGCAGGAGTCTG", 
//               "CTGGTCCAACTGTATTAAGATAAATTAAGCACGGGGCCGTCTCTGCTGAAGTCGCCCTGTGGTTGGTCAGGTAGCTAACTTACGGTCGGCAGGAGTCTG", 
//               99, 
//               2);
      
//      run_test("1 Insertion 1 Deletion", 
//               "CTGGTCCAACTGTATTAAGATAAATTAAGCGACGGGGCCGTCTCTGCTGAAGTCGCCCTGTGGTTGGTCAAGGTAGCTAACTTACGGTCGGCAGGAGTCTG", 
//               "CTGGTCCAACTGTATTAAGATGAAATTAAGCGACGGGGCCGTCTCTGCTGAAGTCGCCCTGTGGTTGGTCAAGGTAGCTAACTTACGGTCGGCGGAGTCTG", 
//               101, 
//               2);

//      run_test("1 Random Same Length ", 
//               "GTTTAATTCGACAAACGGGACTTGTCACCTGTCCTCATAGCTTGCAAACTACTCTATTGGTACCGTCTTGGTCATGTGCTAAGGACCGGGCGCGTCTGGAT", 
//               "GGCCGTGACAAGCTTCGACGTGCAGTTGCCTTTTTGAGCCACAATCCGGGCCTCTTGGACAAGCCGCTGTGTAACGCCGAGTAGCCCGTGTCGAGACAATC", 
//               101, 
//               53);

//      run_test("2 Random Same Length ", 
//               "TGATGATCCAGGGGGCTGCATAATTAACTCAGGCTCTTATTTTATAAGTGATAAGTGCTGGTATCCTAGATAGGCCTGGTCCCAATATCTCTTCGCGCAGC", 
//               "TTAAACACTACCAGTACTGAGCGGATTGTAACGAGACAGGGAGCATTGCCAGAGACAGATCCCGGCTTCGAGCGATCTATCGTCTATTGCAATAGATAGAC", 
//               101, 
//               58); 
      
//      run_test("1 Long Reference ", 
//               "TGATGATCCAGGGGGCTGCATAATTAACTCAGGCTCTTATTTTATAAGTGATAAGTGCTGGTATCCTAGATAGGCCTGGTCCCAATATCTCTTCGCGCAGC", 
//               "TGATGATCCAGGGGGCTGCATAATTAACTCAGGCTCTTATTTTATAAGTGATAAGTGCTGGTATCCTAGATAGGCCTGGTCCCAATATCTCTTCGCGCAGCTGATGATCCAGGGGGCTGCATAATTAACTCAGGCTCTTATTTTATAAGTGATAAGTGCTGGTATCCTAGATAGGCCTGGTCCCAATATCTCTTCGCGCAGC", 
//               202, 
//               101); 
      
//      run_test("2 Long Reference ", 
//               "TTAAACACTACCAGTACTGAGCGGATTGTAACGAGACAGGGAGCATTGCCAGAGACAGATCCCGGCTTCGAGCGATCTATCGTCTATTGCAATAGATAGAC", 
//               "TGATGATCCAGGGGGCTGCATAATTAACTCAGGCTCTTATTTTATAAGTGATAAGTGCTGGTATCCTAGATAGGCCTGGTCCCAATATCTCTTCGCGCAGCTGATGATCCAGGGGGCTGCATAATTAACTCAGGCTCTTATTTTATAAGTGATAAGTGCTGGTATCCTAGATAGGCCTGGTCCCAATATCTCTTCGCGCAGC", 
//               202, 
//               121);              
      

      $finish;
      
   end

endmodule
