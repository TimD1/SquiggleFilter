`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  
`timescale 1ns / 1ns

module mean_mad_normalizer(
    input rst,
    input clk,

    input [`IP_DATA_WIDTH-1:0] in_sample,
    input in_sample_valid,
    input last_sample_in,
    input logic [`IP_DATA_WIDTH-1:0] mean,
    input logic mean_valid,
    input logic [`IP_DATA_WIDTH-1:0] mad,
    input logic mad_valid,

    output logic [`DATA_WIDTH-1:0] scaled_op,
    output logic scaled_op_valid

);


wire signed [`IP_DATA_WIDTH:0]  sub1;
wire signed [`NORM_SHIFTER_OP:0]  diff;
wire signed [`DATA_WIDTH:0] sub2;


logic ce2,ce3,clr,tmp,div_op_valid,tmp2;
//wire signed [31:0] scaled_op_w;
logic signed [`IP_DATA_WIDTH:0] scaled_op_filtered;
wire [1:0] min_state;
logic [`DATA_WIDTH-1:0] tmp1;


c_addsub_1 SUB1 (
  .A({1'b0,in_sample}),        // input wire [7 : 0] A
  .B({1'b0,mean}),        // input wire [7 : 0] B
  .CLK(clk),    // input wire CLK
  .CE(in_sample_valid),      // input wire CE
  .SCLR(clr),  // input wire SCLR
  .S(sub1)        // output wire [8 : 0] S
);


assign diff = sub1<<<`MAD_SHIFT_SCALE;

wire [16+`NORM_SHIFTER_OP+1:0] scaled_op_w; //IP Specific
div_gen_1 mad_DIV2 (
      .aclk(clk),                                       // input wire aclk
      .s_axis_divisor_tvalid(mad_valid),    // input wire s_axis_divisor_tvalid
      .s_axis_divisor_tdata({6'b0, mad}),      // input wire [9 : 0] s_axis_divisor_tdata
      .s_axis_dividend_tvalid(ce2),  // input wire s_axis_dividend_tvalid
      .s_axis_dividend_tdata({{1{diff[`NORM_SHIFTER_OP]}},diff}),    // input wire [21 : 0] s_axis_dividend_tdata
      .m_axis_dout_tvalid(div_op_valid),          // output wire m_axis_dout_tvalid
      .m_axis_dout_tdata(scaled_op_w)             // output wire [37 : 0] m_axis_dout_tdata
);

//state calculations for thresholding.
assign min_state[1]=scaled_op_w[17+`NORM_SHIFTER_OP:16]>`MAX_TVAL_SCALED ;
assign min_state[0]=scaled_op_w[17+`NORM_SHIFTER_OP:16]<`MIN_TVAL_SCALED ;

//find minimum among neighboring cells
always_comb begin
    case (min_state)
        2'b10: 
            scaled_op_filtered=`MAX_TVAL_SCALED;
        2'b01: 
            scaled_op_filtered=`MIN_TVAL_SCALED;      
        default:
        	  scaled_op_filtered={scaled_op_w[17+`NORM_SHIFTER_OP],scaled_op_w[`IP_DATA_WIDTH+15:16]};
    endcase 
end 

c_addsub_2 SUB2 (
  .A(scaled_op_filtered),        // input wire [7 : 0] A
  .B({1'b0,`IP_DATA_WIDTH'd`MAX_TVAL_SCALED}),        // input wire [7 : 0] B
  .CLK(clk),    // input wire CLK
  .CE(div_op_valid),      // input wire CE
  .SCLR(clr),  // input wire SCLR
  .S(sub2)        // output wire [8 : 0] S
);


always_ff@(posedge clk) begin //{

  if(rst) begin
   scaled_op<=0;
   //scaled_op_valid<=0;
 
   clr<=1;
   ce2<=0;
   tmp<=0;
  end
  else begin //{
    if(mean_valid&&mad_valid) begin
 
    clr<=0;
    scaled_op_valid<=0;
    end
    
    //control for subtract
    if(div_op_valid) begin

    
    tmp1<=sub2[`DATA_WIDTH-1:0]; 
    scaled_op<=tmp1;
    
    end
    tmp2<=div_op_valid;
    scaled_op_valid<=tmp2;

    //control for first divider
    if(in_sample_valid) begin
    tmp<=in_sample_valid;
    ce2<=tmp;
    end
    else 
      ce2<=0;
   
    
  end //}
end //}

endmodule : mean_mad_normalizer
