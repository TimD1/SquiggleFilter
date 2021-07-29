`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  
`timescale 1ns / 1ns

module mean_finder(
    input rst,
    input clk,
    input rd_done,
    input [`IP_DATA_WIDTH-1:0] in_sample,
    input in_sample_valid,
    input last_sample_in,

    output logic [`IP_DATA_WIDTH-1:0] out_mean,
    output logic out_mean_valid

);


wire [`SUM_ACC_OP-1:0] mean_sum_w;
logic [`SUM_ACC_OP-1:0] mean_sum, mean_sum_tmp;
logic sclr,sclr_tmp;
logic mean_en,out_mean_valid1;
logic accumulated_sum_valid,accumulated_sum_valid_tmp;



c_accum_0 mean_ac (
  .B(in_sample),        // input wire [7 : 0] B
  .CLK(clk),    // input wire CLK
  .CE(mean_en),      // input wire CE
  .SCLR(sclr),  // input wire SCLR
  .Q(mean_sum_w)        // output wire [20 : 0] Q
);

always_comb begin
  mean_en=in_sample_valid;  
  sclr_tmp= ~mean_en&&rd_done;

end
assign mean_sum = rd_done?mean_sum_w:0;
assign accumulated_sum_valid=rd_done;
wire [16+`SUM_ACC_OP-1:0] out_mean_w; //IP Specific
div_gen_0 MEAN_DIV1 (
      .aclk(clk),                                       // input wire aclk
      .s_axis_divisor_tvalid(accumulated_sum_valid),    // input wire s_axis_divisor_tvalid
      .s_axis_divisor_tdata({7'd0,9'd`QUERY_LEN}),      // input wire [9 : 0] s_axis_divisor_tdata
      .s_axis_dividend_tvalid(accumulated_sum_valid),  // input wire s_axis_dividend_tvalid
      .s_axis_dividend_tdata({5'd0,mean_sum}),    // input wire [21 : 0] s_axis_dividend_tdata
      .m_axis_dout_tvalid(out_mean_valid1),          // output wire m_axis_dout_tvalid
      .m_axis_dout_tdata(out_mean_w)             // output wire [37 : 0] m_axis_dout_tdata
);

always_ff@(posedge clk) begin //{

  if(rst) begin   
    mean_sum_tmp<=0;
    //mean_sum<=0;   
    out_mean<=0;  
    sclr<=0;
    //accumulated_sum_valid<=0;
    out_mean_valid<=0; 
  end
  else begin //{
    
    // if(rd_done) begin//{
    //   mean_sum_tmp<=mean_sum_w;            
    //   mean_sum<=mean_sum_tmp;
     
    // end//}
      //accumulated_sum_valid<=last_sample_in;
      //sclr_tmp1<=sclr_tmp;
      sclr<=sclr_tmp;
    


    if(out_mean_valid1) begin
      out_mean<=out_mean_w[16+:`IP_DATA_WIDTH];
      out_mean_valid<=out_mean_valid1;
     
    end
    //else out_mean_valid<=0;
  end //}
end //}

endmodule : mean_finder
