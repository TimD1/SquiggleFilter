/*
 * 
 * A systolic array implementation to compute the Edit Distance string scoring metric
 *
 */
 
`include "constants.vh"

module sDTW(input clk,
                     input rst,
                     input start,
                     input [`QUERY_LEN-1:0][`DATA_WIDTH-1:0] query ,
                     input [`REF_MAX_LEN-1:0][`DATA_WIDTH-1:0] reference ,
                     input [`REF_SIZE_BITS:0] reference_length,
                     output logic [`DATA_OUT_WIDTH-1:0] result,
                     output logic done
                    );
	
	logic							active		[`QUERY_LEN-1:0];
	logic	[`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		counter		; //TBD: check if width can be reduced 
	wire	[`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_op 		;
	wire	[`QUERY_LEN-1:0][`DATA_OUT_WIDTH-1:0]		pe_prev_op 	;
	
	// first PE declared separately since it has nothing on the left; just constants as inputs
	PE first_col(	.activate(active[0]),
					.clk(clk),
					.rst(rst),
					.rst_value (1),
					.left      (0),
					.top       (pe_op[0]),
					.diag      (0),
					.reference (reference[counter[0]]),
					.query     (query[0]),
					.curr_op(pe_op[0]),
					.prev_op   (pe_prev_op[0])
				);

	// except for first PE, all other PE's have a uniform connection pattern
	genvar i;
	generate
		for (i=1; i<`QUERY_LEN; i++) begin : pe_systolic
			PE col(	.activate(active[i]),
					.clk(clk),
					.rst(rst),
					.rst_value (i+1),
					.left(pe_op[i-1]),
					.top(pe_op[i]),
					.diag(pe_prev_op[i-1]),
					.reference(reference[counter[i]]),
					.query(query[i]),
					.curr_op(pe_op[i]),
					.prev_op(pe_prev_op[i])
				);
		end
	endgenerate

	// output logic
	always_ff @(posedge clk)
	begin
		if(counter[`QUERY_LEN-1] == reference_length) begin
			done <= 1'b1;
			result <= pe_op[`QUERY_LEN-1];
		end
		else begin
			done <= 1'b0;
			result <= 0;
		end
	end

	// control logic
	always_ff @(posedge clk)
	begin

		// reset signal values to 0
		if(rst)
		begin
			for(integer j=0; j<`QUERY_LEN; j++)
			begin
				active[j] <= 0;
				counter[j] <= 0;
			end
		end

		else if(start)
		begin

			// if PE is active, increment its counter or else hold counter value
			for(integer j=0; j<`QUERY_LEN; j++)
			begin	
				if(active[j])
					counter[j] <= counter[j] + 1;
				else 
					counter[j] <= counter[j];
 			end

 			
 			if(counter[0] == 0)
				active[0] <= 1;
				// activate PE0 when start signal arrives after it has been reset to 0
			else if(counter[0] == reference_length)
				active[0] <= 0;
				// deactivate PE0 when it finishes its column
			else
				active[0] <= active[0];

			for(integer j=1; j<`QUERY_LEN; j++)
				active[j] <= active[j-1];
				// propogate active high and active low to other PEs with one cycle delay
		end

		else
		begin
			for(integer j=0; j<`QUERY_LEN; j++)
			begin
				active[j] <= active[j];
				counter[j] <= counter[j];
			end
		end
	end
	
endmodule