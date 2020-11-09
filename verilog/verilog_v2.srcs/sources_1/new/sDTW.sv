/*
 * 
 * A systolic array implementation to compute the sDTW scores and thereafter find if alignment meets threshold requirements or not
 *
 */
 
`include "constants.vh"

module sDTW(input clk,
                     input rst, 
                     input start,
                     input [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] query ,
                     input [`DATA_WIDTH-1:0] reference ,
                     //input [`REF_SIZE_BITS:0] reference_length,
                     output logic result,
                     output logic done,
                     output [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_op,
                    output logic activate		[`QUERY_LEN-1:0],
                    output                 [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_prev_op,
                     //output logic [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		counter
                    output [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0] diff,
                     //output signed [`DATA_OUT_WIDTH+1:0] P,
                    output [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0] score_wire,
                    output logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] ip_reference,
                    output logic [`CNTR_BITS-1:0] counter,
                    output logic stop_sig,
                    output logic [`QUERY_LEN-1:0] early_stop,
                    output logic [`QUERY_LEN-1:0] normal_stop
                    );
	
//	logic	activate		[`QUERY_LEN-1:0];
//	wire	[`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_op 		;
//	wire	[`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_prev_op 	;
//	wire [`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0] score_wire;
	//logic	[`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		counter		; //TBD: check if width can be reduced 
	
	//wire op_reference[`QUERY_LEN-1:0];
    //logic [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] ip_reference;
	// first PE declared separately since it has nothing on the left; just constants as inputs
	
	//logic [`QUERY_LEN-1:0] early_stop, normal_stop;
	//wire stop_sig; //signal stopping the systolic array, early or normal
	//logic [`CNTR_BITS-1:0] counter;
	PE first_col(	.activate(activate[0]),
					.clk(clk),
					.rst(rst),
					
					.left      (0),
					.top       (pe_op[0]),
					//.top       (pe_op[0]),
					.diag      (0),
					.ip_reference (ip_reference[0]),
					.query     (query[0]),
					.curr_op(pe_op[0]),
					.prev_op   (pe_prev_op[0]),
					.diff(diff[0]),
					.score_wire(score_wire[0])
					//.op_reference(op_reference[0])
				);

	// except for first PE, all other PE's have a uniform connection pattern

	genvar i;
	generate
		for (i=1; i<`QUERY_LEN; i++) begin : pe_systolic
			PE col(	.activate(activate[i]),
					.clk(clk),
					.rst(rst),
					
					.left(pe_op[i-1]),
					.top(pe_op[i]),
					.diag(pe_prev_op[i-1]),
					.ip_reference(ip_reference[i]),
					.query(query[i]),
					.curr_op(pe_op[i]),
					.prev_op(pe_prev_op[i]),
					.diff(diff[i]),					
					.score_wire(score_wire[i])
					//.op_reference(op_reference[i])
				);
		end
	endgenerate



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
			         //comparator signals for early stop
                     for(integer j=0; j<`QUERY_LEN; j++)
                     begin
                        if(pe_op[j]>`DTW_THRESHOLD) begin
                            early_stop[j]<=1;				 					
                        end
                        else
                           early_stop[j]<=0;	
                     end
                     //AND-ing to do early stop
                     if(&early_stop[`QUERY_LEN-1:0]==1) begin//{
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
			     //comparator signals generated for OR-ing
			     for(integer j=0; j<`QUERY_LEN; j++)
			     begin
			 	 if(pe_op[j]<=`DTW_THRESHOLD) begin
			 		normal_stop[j]<=1;				 					
			 	 end
			 	 else
			 	   normal_stop[j]<=0;
			 	 end	
			 	 //OR-ing to check normal stop
			 	 if(|normal_stop[`QUERY_LEN-1:0]==1) begin//{
			    
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
	            early_stop[j]<=0;
	            normal_stop[j]<=1;
	            
			end
			done<=0;
			result<=0;
			counter<=0;
			//stop_sig<=0;
		end

		else if(start)
		begin

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
			//stream reference into the PE's
            ip_reference[0]<=reference;
            for(int i=1;i<`QUERY_LEN;i++)
                ip_reference[i]<=ip_reference[i-1];
            counter<=counter+1;    
				// propogate active high and active low to other PEs with one cycle delay
		end

		
	end
	
endmodule