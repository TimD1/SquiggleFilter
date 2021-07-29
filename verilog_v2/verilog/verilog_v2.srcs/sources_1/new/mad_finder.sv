`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  
`timescale 1ns / 1ns

module mad_finder(
    input rst,
    input clk,
    input rd_done,
    input [`IP_DATA_WIDTH-1:0] in_sample,
    input in_sample_valid,
    input last_sample_in,
    input logic [`IP_DATA_WIDTH-1:0] mean,
    input logic mean_valid,

    output logic [`IP_DATA_WIDTH-1:0] out_mad,
    output logic out_mad_valid

);


wire [`SUM_ACC_OP-1:0] mad_sum_w, abs_diff;
logic [`SUM_ACC_OP-1:0] mad_sum, mad_sum_tmp;
logic sclr,sclr_tmp;
logic mad_en;
logic accumulated_sum_valid,accumulated_sum_valid_tmp,out_mad_valid1;


//assign abs_diff = (in_sample>mean)?in_sample-mean:mean-in_sample;
// c_addsub_1 SUB0 (
//   .A(in_sample),        // input wire [7 : 0] A
//   .B(mean),        // input wire [7 : 0] B
//   .CLK(clk),    // input wire CLK
//   .CE(ce),      // input wire CE
//   .SCLR(clr),  // input wire SCLR
//   .S(abs_diff)        // output wire [8 : 0] S
// );
assign abs_diff = (in_sample>mean)?(in_sample-mean):(mean-in_sample);
// always @(in_sample) begin
//     ce=1;
// end
c_accum_0 mad_ac (
  .B(abs_diff),        // input wire [7 : 0] B
  .CLK(clk),    // input wire CLK
  .CE(mad_en),      // input wire CE
  .SCLR(sclr),  // input wire SCLR
  .Q(mad_sum_w)        // output wire [20 : 0] Q
);
always_comb begin
  mad_en=in_sample_valid;  
  sclr_tmp= ~mad_en&&rd_done;
end
assign mad_sum = rd_done?mad_sum_w:0;
assign accumulated_sum_valid=rd_done;
wire [16+`SUM_ACC_OP-1:0] out_mad_w; //IP Specific
div_gen_0 mad_DIV1 (
      .aclk(clk),                                       // input wire aclk
      .s_axis_divisor_tvalid(accumulated_sum_valid),    // input wire s_axis_divisor_tvalid
      .s_axis_divisor_tdata({7'd0,9'd`QUERY_LEN}),      // input wire [9 : 0] s_axis_divisor_tdata
      .s_axis_dividend_tvalid(accumulated_sum_valid),  // input wire s_axis_dividend_tvalid
      .s_axis_dividend_tdata({5'd0,mad_sum}),    // input wire [21 : 0] s_axis_dividend_tdata
      .m_axis_dout_tvalid(out_mad_valid1),          // output wire m_axis_dout_tvalid
      .m_axis_dout_tdata(out_mad_w)             // output wire [37 : 0] m_axis_dout_tdata
);

always_ff@(posedge clk) begin //{

  if(rst) begin
   
    // mad_sum_tmp<=0;
    // mad_sum<=0;   
    out_mad<=0;
    out_mad_valid<=0; 
    // accumulated_sum_valid<=0;
    // accumulated_sum_valid_tmp<=0;
   
  end
  else begin //{
    
    // if(last_sample_in) begin//{
    //   mean_sum<=mean_sum_w;            
      
     
    // end//}
    //   accumulated_sum_valid<=last_sample_in;
      //sclr_tmp1<=sclr_tmp;
      sclr<=sclr_tmp;
    


    if(out_mad_valid1) begin
      out_mad<=out_mad_w[16+:`IP_DATA_WIDTH];
      out_mad_valid<=out_mad_valid1;
    end
    //else out_mad_valid<=0;
  end //}
end //}

endmodule : mad_finder
