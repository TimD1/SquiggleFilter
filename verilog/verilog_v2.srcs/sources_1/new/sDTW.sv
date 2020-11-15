 //////////////////////////////////////////////////////////////////////////////////
// Company: UofM
// Engineer: Harisankar Sadasivan
// 
// Create Date: 11/01/2020 10:45:14 PM
// Design Name: SquAl
// Module Name: sDTW
// Project Name: SquAl
// Target Devices: FPGA
// Tool Versions: 
// Description: systolic array top for connecting, initializing and firing the PE's.
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
module sDTW(input clk,
                     input rst, 
                     input start,
                     input [`DATA_WIDTH-1:0] query ,
                     input [`DATA_WIDTH-1:0] reference ,
                     input init_sig,                    
                     output logic result,
                     output logic done                     
                    );
	
	//query initialization
	logic [`QUERY_LEN-1:0] tmp_d; //pipeline registers for 2 clock init signal delay.
	logic [`QUERY_LEN-1:0] init; //resgiter the init signal in each PE input
	//PE firing
	logic activate		[`QUERY_LEN-1:0];
	logic [`CNTR_BITS-1:0] counter;
    //PE interconnects
	wire [`QUERY_LEN-1:0] stop_bits;
    wire [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_op;   
    wire [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_prev_op;      
    wire [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] op_reference;  
    wire [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] query_o;
  


    //First PE
	PE first_col(	.activate(activate[0]),
					.clk(clk),
					.rst(rst),
					.init(init[0]),					
					.left      (0),
					.top       (pe_op[0]),					
					.diag      (0),
					.ip_reference (reference),
					.query     (query),
					.curr_op(pe_op[0]),
					.prev_op   (pe_prev_op[0]),
					.stop_bit(stop_bits[0]),					
					.op_reference(op_reference[0]),
					.query_o(query_o[0])
					
					
				);

	// All other PE's

	genvar i;
	generate
		for (i=1; i<`QUERY_LEN; i++) begin : pe_systolic
			PE col(	.activate(activate[i]),
					.clk(clk),
					.rst(rst),
					.init(init[i]),
					.left(pe_op[i-1]),
					.top(pe_op[i]),
					.diag(pe_prev_op[i-1]),
					.ip_reference(op_reference[i-1]),
					.query(query_o[i-1]),
					.curr_op(pe_op[i]),
					.prev_op(pe_prev_op[i]),
					.stop_bit(stop_bits[i]),				
					.op_reference(op_reference[i]),
					.query_o(query_o[i])				
					
				);
		end
	endgenerate



	//on completion of the array
    always@(done) begin
     for(integer i=0; i<`QUERY_LEN; i++) begin //{
			activate[i] <= 0;
			
     end //}
     
     
     
    end
	// logic for sDTW early abandon
	always_ff @(posedge clk)
	begin

			
			//comparing wrt threshold
			 if(counter>`QUERY_LEN) begin //{
			        
                     //AND-ing to do early stop
                     if(&stop_bits[`QUERY_LEN-1:0]==1) begin//{
                         done<=1;
                         //stop_sig<=1;
                         result<=0;
                     end //}
			 end //}
			
			     			 
	end
	
	//logic for normal sDTW thresholding
	always_ff @(posedge clk)
	begin
	        if (counter==`QUERY_LEN+`REF_MAX_LEN) begin
			     done<=1;
			   
			    
			 	 //OR-ing to check normal stop
			 	 if(|stop_bits[`QUERY_LEN-1:0]==1) begin//{
			    
			     result<=1;
			     end //}
			end
			
			
			
    end
    
    
	// control logic
	always_ff @(posedge clk)
	begin

	    //sync reset
		if(rst)
		begin
			for(integer j=0; j<`QUERY_LEN; j++)
			begin
				activate[j] <= 0;	           
	            tmp_d[j]<=0;
			end
			done<=0;
			result<=0;
			counter<=0;
			tmp_d<=0;
					
		end
		//firing the array
		else if(start==1 && init_sig==0)
		begin
            
			if(init[`QUERY_LEN-1]==1) begin //{
				init[0]<=0;	
				for(int i=1;i<`QUERY_LEN;i++) begin //{
				
				init[i]<=0;
				end //}
			end //}
            //start first PE
            if(counter<`REF_MAX_LEN) begin
                activate[0] <= 1;
    
                //fire consecutive PE's in consecutive cycles
                for(integer j=1; j<`QUERY_LEN; j++) begin //{
                    activate[j] <= activate[j-1];
                
                end //}
			end 
			//inactivate PE's at the end of computation
			else begin
                activate[0] <= 0;
    
                //fire consecutive PE's in consecutive cycles
                for(integer j=1; j<`QUERY_LEN; j++) begin //{
                    activate[j] <= activate[j-1];
                
                end //}
			end

            counter<=counter+1;    
				// propogate active high and active low to other PEs with one cycle delay
		end
		//intializing the PE's with query values in PE number of cycles.
		else if(init_sig) begin
			
			
			init[0]<=1;
			

			for(int i=1;i<`QUERY_LEN;i++) begin //{
				tmp_d[i-1]<=init[i-1];
				init[i]<=tmp_d[i-1];
			end //}
		 
		end 


		
	end
	
endmodule