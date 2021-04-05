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
                     input [`MAX_BONUS_WIDTH-1:0] ip_bonus,
                     input init_sig,       
                     input  [`DATA_OUT_WIDTH-1:0] loop_score_i,              
                     output logic result,
                     output logic done,
                     output  [`DATA_OUT_WIDTH-1:0] loop_score_o,
                     output loop_score_val  ,
                     output logic loop_finish                 
                    );
	
	//query initialization
	logic [`QUERY_LEN-1:0] tmp_d; //pipeline registers for 2 clock init signal delay.
	logic [`DATA_OUT_WIDTH-1:0] tmp1_d;
	logic [`QUERY_LEN-1:0] init; //resgiter the init signal in each PE input
	//PE firing
	logic [`QUERY_LEN-1:0] activate;
	logic [`CNTR_BITS-1:0] counter;
    //PE interconnects
	logic [`REF_MAX_LEN-1:0] stop_bits;
    wire [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_op;   
    wire [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_prev_op;      
    wire [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] op_reference;  
    wire [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] query_o;
    logic [`LOOP_CNTR_BITS-1:0] loop_ctr;
    logic [`DATA_OUT_WIDTH-1:0] loop_score_pe;

    wire [`QUERY_LEN-1:0][`MAX_BONUS_WIDTH-1:0]		pe_prev_bonus; 
    //First PE
    
	PE_v2 first_col(	.activate(activate[0]),
					.clk(clk),
					.rst(rst),
					.init(init[0]),		
					.ip_bonus(ip_bonus)	,		
					.left      (loop_score_i),
					//.top       (pe_op[0]),					
					.diag      (loop_score_pe),
					.ip_reference (reference),
					.query     (query),
					.curr_op(pe_op[0]),
					.prev_op   (pe_prev_op[0]),
					.prev_bonus(pe_prev_bonus[0]),
					//.stop_bit(stop_bits[0]),					
					//.prev_bonus(prev_bonus),
					.op_reference(op_reference[0]),
					.query_o(query_o[0])
					
					
					
				);

	// All other PE's
    `ifndef SYNTH 
	genvar i;
	generate
		for (i=1; i<`QUERY_LEN-1; i++) begin : pe_systolic
			PE_v2 col(	.activate(activate[i]),
					.clk(clk),
					.rst(rst),
					.init(init[i]),
					.ip_bonus(pe_prev_bonus[i-1])	,	
					.left(pe_op[i-1]),
					//.top(pe_op[i]),
					.diag(pe_prev_op[i-1]),
					.ip_reference(op_reference[i-1]),
					.query(query_o[i-1]),
					.curr_op(pe_op[i]),
					.prev_op(pe_prev_op[i]),
					.prev_bonus(pe_prev_bonus[i]),
					//.stop_bit(stop_bits[i]),
					//.prev_bonus(prev_bonus),				
					.op_reference(op_reference[i]),
					.query_o(query_o[i])													
		);
		end
	endgenerate
	
			 PE_last_col_v2 PE_lc(	.activate(activate[`QUERY_LEN-1]),
					.clk(clk),
					.rst(rst),
					.init(init[`QUERY_LEN-1]),
					.ip_bonus(pe_prev_bonus[`QUERY_LEN-2])	,	
					.left(pe_op[`QUERY_LEN-2]),
					//.top(pe_op[`QUERY_LEN-1]),
					.diag(pe_prev_op[`QUERY_LEN-2]),
					.ip_reference(op_reference[`QUERY_LEN-2]),
					.query(query_o[`QUERY_LEN-2]),					
					.curr_op(pe_op[`QUERY_LEN-1]),
					.prev_op(pe_prev_op[`QUERY_LEN-1]),
					.prev_bonus(pe_prev_bonus[`QUERY_LEN-1]),
					.stop_bit(stop_bits[`QUERY_LEN-1]),				
					.op_reference(op_reference[`QUERY_LEN-1]),
					.query_o(query_o[`QUERY_LEN-1]),
					//.prev_bonus(prev_bonus),
					.loop_score_o(loop_score_o)	,
					.loop_score_val(loop_score_val)								
			);
		
	
	`else
	genvar i;
	generate
		for (i=1; i<`QUERY_LEN-1; i++) begin : pe_systolic
			PE_v2 col(	.activate(activate[i]),
					.clk(clk),
					.rst(rst),
					.init(init[i]),
					.ip_bonus(pe_prev_bonus[i-1])	,	
					.left(pe_op[i-1]),
					//.top(pe_op[i]),
					.diag(pe_prev_op[i-1]),
					.ip_reference(op_reference[i-1]),
					.query(query_o[i-1]),
					.curr_op(pe_op[i]),
					.prev_op(pe_prev_op[i]),
					.prev_bonus(pe_prev_bonus[i]),
					//.stop_bit(stop_bits[i]),	
					//.prev_bonus(prev_bonus),			
					.op_reference(op_reference[i]),
					.query_o(query_o[i])				
					
				);
				
		end
		endgenerate
		 PE_last_col_v2 PE_lc(	.activate(activate[`QUERY_LEN-1]),
					.clk(clk),
					.rst(rst),
					.init(init[`QUERY_LEN-1]),
					.ip_bonus(pe_prev_bonus[`QUERY_LEN-2])	,	
					.left(pe_op[`QUERY_LEN-2]),
					//.top(pe_op[`QUERY_LEN-1]),
					.diag(pe_prev_op[`QUERY_LEN-2]),
					.ip_reference(op_reference[`QUERY_LEN-2]),
					.query(query_o[`QUERY_LEN-2]),					
					.curr_op(pe_op[`QUERY_LEN-1]),
					.prev_op(pe_prev_op[`QUERY_LEN-1]),
					.prev_bonus(pe_prev_bonus[`QUERY_LEN-1]),
					.stop_bit(stop_bits[`QUERY_LEN-1]),				
					.op_reference(op_reference[`QUERY_LEN-1]),
					.query_o(query_o[`QUERY_LEN-1]),
					//.prev_bonus(prev_bonus),
					.loop_score_o(loop_score_o)	,
					.loop_score_val(loop_score_val)								
	     );
		
	
	
    `endif



	// control logic
	always_ff @(posedge clk)
	begin
        	
			//comparing wrt threshold
			
			        
                     
            if(counter==`CNTR_STOP-2) begin
			      loop_finish<=1;
			end
			
	        else if (counter==`CNTR_STOP) begin //12
			     //done<=1;
			     if(loop_ctr<`MAX_LOOP_CNT) begin //2
			       counter<=0;
			       loop_ctr<=loop_ctr+1;
			       activate<={activate[`QUERY_LEN-2:0],1'b1};
			     end 
			     
			   
			end
			if(counter==`QUERY_LEN && loop_ctr==`MAX_LOOP_CNT) begin			     			     			     
			       done<=1;  
			       //counter<=0;  
			       activate<=0; 
			       //OR-ing to check normal stop           
			       if(|stop_bits[`REF_MAX_LEN-1:0]==1) begin//{
			         result<=1;
			       end
			end
			
			
        if(init) begin
		  if(counter<`QUERY_LEN) begin//{
		      counter<=counter+1;
		      
		  end //}
		  else begin
		      counter<=0;
		      init<=0;
		  end 
		end
		
	    //sync reset
		if(rst)
		begin
			activate<=0;
			done<=0;
			result<=0;
			counter<=0;
			tmp_d<=0;
			loop_ctr<=1;
		    init<=0;	
		    loop_finish<=0;
		    loop_score_pe<=0;
		    tmp1_d<=0;
		    stop_bits<=0;
		end
		//firing the array
		else if(start==1 && init_sig==0)
		begin
            
			//if(init[`QUERY_LEN-1]==1) begin //{

            //    init <=0;
			//end //}
            //start first PE
           
            tmp1_d<=loop_score_i;
            loop_score_pe<=tmp1_d;
            if(loop_ctr!=`MAX_LOOP_CNT+1 && counter<`CNTR_STOP) begin
                if(counter<`REF_MAX_LEN) begin
    
                    activate<={activate[`QUERY_LEN-2:0],1'b1};
                    
                end 
                //inactivate PE's at the end of computation
                else begin
    
                    activate<={activate[`QUERY_LEN-2:0],1'b0};
                    
                end
                counter<=counter+1;
            end  
				// propogate active high and active low to other PEs with one cycle delay
		end
		//intializing the PE's with query values in PE number of cycles.
		else if(init_sig) begin
            
            

            
              tmp_d<=init;
              init<={tmp_d[`QUERY_LEN-2:0],1'b1};             
            
		 
		end 
		
		

		
	end
	
endmodule