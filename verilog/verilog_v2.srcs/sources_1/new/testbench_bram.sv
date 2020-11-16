`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/09/2020 10:46:45 AM
// Design Name: 
// Module Name: testbench_bram
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



module testbench_bram();

logic clk=0;
logic q_ena=0;
logic q_wea=0;
logic [13 : 0] q_addra=0;
logic [7 : 0] q_dina=0,tmp=0,tmp1=0; //tmp variables store values read from file
logic q_enb=0;
logic [13 : 0] q_addrb=0;
logic [7 : 0] q_doutb=0;


logic r_ena=0;      
logic r_wea=0;
logic [15:0] r_addra=0;
logic [7:0] r_dina=0;   
logic [7:0] r_douta=0;  
int ref_file,rd_file;
bit stop;
blk_mem_gen_0 query_bram (
  .clka(clk),    // input wire clka
  .ena(q_ena),      // input wire ena
  .wea(q_wea),      // input wire [0 : 0] wea
  .addra(q_addra),  // input wire [13 : 0] addra
  .dina(q_dina),    // input wire [7 : 0] dina
  .clkb(clk),    // input wire clkb
  .enb(q_enb),      // input wire enb
  .addrb(q_addrb),  // input wire [13 : 0] addrb
  .doutb(q_doutb)  // output wire [7 : 0] doutb
);

blk_mem_gen_1 ref_bram (
  .clka(clk),    // input wire clka
  .ena(r_ena),      // input wire ena
  .wea(r_wea),      // input wire [0 : 0] wea
  .addra(r_addra),  // input wire [15 : 0] addra
  .dina(r_dina),    // input wire [7 : 0] dina
  .douta(r_douta)  // output wire [7 : 0] douta
);
always begin
      #5
        clk = ~clk;
end
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
          
          q_dina=tmp1;
        
         @(posedge clk)
         i+=1;
         
         if(i==`QUERY_LEN) begin
       
          q_ena=0;
          q_wea=0;
          q_addra=0;

          i=0;
          
          break;
        end
        else q_addra+=1;
      end
      $fclose(rd_file);
endtask : write_query

task read_from_query();
 //read reference from bram
  q_enb=1;
  
  q_addrb=1;
  @(posedge clk)
  for(int i=0;q_enb!=0;i++) begin
    
    

    
    
    
    @(posedge clk);
    
    if(i==`QUERY_LEN) begin
            
            q_enb=0;  
            i=0;
                   
            break;
            
    end 
    if(i<`QUERY_LEN-1) q_addrb+=1; 
    
  end  
endtask : read_from_query

task read_from_reference();
 //read reference from bram
  r_ena=1;
  r_wea=0;
  r_addra=0;
  
  for(int i=0;r_ena!=0;i++) begin
    
    

    
    
    
    @(posedge clk);
    if(i==`REF_MAX_LEN) begin
           
            @(posedge clk)
            r_ena=0;  
            i=1;
            stop=1;            
            break;
            
    
    end 
    if(i<`REF_MAX_LEN-1) r_addra+=1; 
    
  end  
endtask : read_from_reference
   
initial begin

  @(posedge clk)
  fork
  begin
  write_reference();  
  read_from_reference();
  end
  begin 
  

  write_query();
  end
  begin

  @(posedge clk);
  @(posedge clk);
  read_from_query();
  end
  join_none
  
  while(stop==0) begin
     @(posedge clk);
  end
$finish;
end
  
endmodule
