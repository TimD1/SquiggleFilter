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
	logic [`QUERY_LEN-1:0] activate;
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
    `ifndef SYNTH 
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
	`else
	genvar i;
	generate
		for (i=1; i<1000; i++) begin : pe_systolic
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
	
	generate
		for (i=2000; i<3000; i++) begin : pe_systolic1
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
	generate
		for (i=3000; i<4000; i++) begin : pe_systolic2
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
	generate
		for (i=4000; i<`QUERY_LEN; i++) begin : pe_systolic3
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
    `endif


	//on completion of the array
//    always@(done) begin
//     for(integer i=0; i<`QUERY_LEN; i++) begin //{
//			activate[i] <= 0;
			
//     end //}
     
     
     
//    end
//	// logic for sDTW early abandon
//	always_ff @(posedge clk)
//	begin

		
			
			     			 
//	end
	
//	//logic for normal & early sDTW thresholding
//	always_ff @(posedge clk)
//	begin
	
	
	        
			
			
//    end
    
    
	// control logic
	always_ff @(posedge clk)
	begin
        	
			//comparing wrt threshold
			if(counter>`QUERY_LEN && counter!=`QUERY_LEN+`REF_MAX_LEN) begin //{
			        
                     //AND-ing to do early stop
                     if(&stop_bits[`QUERY_LEN-1:0]==1) begin//{
                         done<=1;
                         //stop_sig<=1;
                         result<=0;
                     end //}
			 end //}
	        else if (counter==`QUERY_LEN+`REF_MAX_LEN) begin
			     done<=1;
			   
			    
			 	 //OR-ing to check normal stop
			 	 if(|stop_bits[`QUERY_LEN-1:0]==1) begin//{
			    
			     result<=1;
			     end //}
			end
			
	    //sync reset
		if(rst)
		begin
			activate<=0;
			done<=0;
			result<=0;
			counter<=0;
			tmp_d<=0;
					
		end
		//firing the array
		else if(start==1 && init_sig==0)
		begin
            
			if(init[`QUERY_LEN-1]==1) begin //{
				//init[0]<=0;	
//				for(int i=0;i<`QUERY_LEN;i++) begin //{
				
//				init[i]<=0;
//				end //}
                init <=0;
			end //}
            //start first PE
            if(counter<`REF_MAX_LEN) begin
                //activate[0] <= 1;
    
                //fire consecutive PE's in consecutive cycles
//                for(integer j=1; j<`QUERY_LEN; j++) begin //{
//                    activate[j] <= activate[j-1];
                
//                end //}
                activate<={activate[`QUERY_LEN-2:0],1'b1};
			end 
			//inactivate PE's at the end of computation
			else begin
//                activate[0] <= 0;
    
//                //fire consecutive PE's in consecutive cycles
//                for(integer j=1; j<`QUERY_LEN; j++) begin //{
//                    activate[j] <= activate[j-1];
                
//                end //}
                activate<={activate[`QUERY_LEN-2:0],1'b0};
			end

            counter<=counter+1;    
				// propogate active high and active low to other PEs with one cycle delay
		end
		//intializing the PE's with query values in PE number of cycles.
		else if(init_sig) begin
			
			
//			init[0]<=1;
			

//			for(int i=1;i<`QUERY_LEN;i++) begin //{
//				tmp_d[i-1]<=init[i-1];
//				init[i]<=tmp_d[i-1];
//			end //}
            tmp_d<=init;
            init<={tmp_d[`QUERY_LEN-2:0],1'b1};
		 
		end 
		else if(done) begin//{
//		  for(integer i=0; i<`QUERY_LEN; i++) begin //{
//			activate[i] <= 0;
			
//          end //}
          activate<=0;
		end//}


		
	end
	
endmodule