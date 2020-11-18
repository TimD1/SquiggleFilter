`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  
`timescale 1ns / 1ns

module mad_calculator(
    input rst,
    input clk,

    input [`DATA_WIDTH-1:0] in_sample,
    input in_sample_valid,
    input last_sample_sent,

    input [`DATA_OUT_WIDTH-1:0] in_mean,
    output logic ready,


    output logic [`DATA_WIDTH-1:0] out_sample,
    output logic out_sample_valid,

    output logic [`DATA_OUT_WIDTH-1:0] out_mad,
    input logic IN_MEM_wea,
    input logic IN_MEM_ena,
    input logic [`QUERY_SIZE_BITS-1:0] IN_MEM_addr,
    input logic [`DATA_OUT_WIDTH-1:0] IN_MEM_da,
    input logic [`DATA_OUT_WIDTH-1:0] IN_MEM_qa

);

    
    logic start_accumulating;
    logic [`DATA_OUT_WIDTH-1:0] accumulated_mad;

    logic [15:0] common_divisor;

    assign common_divisor[`QUERY_SIZE_BITS-1:0] = `QUERY_LEN;
    assign common_divisor[15:`QUERY_SIZE_BITS] = 'h0;


    logic [31:0] temp_query_len;

    //logic ready;

    //logic IN_MEM_wea;
    logic IN_MEM_ena_q;
//    logic [`QUERY_SIZE_BITS-2:0] IN_MEM_addr;
//    logic [23:0] IN_MEM_da;
//    logic [23:0] IN_MEM_qa;


    //HARI logic mean_valid_q;


    assign ready = start_accumulating;
    
    
      logic [`DATA_OUT_WIDTH-1 : 0] accumulated_sum;    // input wire [23 : 0] s_axis_dividend_tdata
      logic out_mean_valid;          // output wire m_axis_dout_tvalid
      logic [`DATA_OUT_WIDTH-1:0] out_mean ;            // output wire [23 : 0] m_axis_dout_tdata
//HARI
//    always_ff @(posedge clk or posedge rst) begin
//        if(rst) begin
//            mean_valid_q <= 1'b0;
//        end
//        else begin
//            if(ready) begin
//                mean_valid_q <= 1'b0;
//            end

//            if(out_mean_valid) begin
//                mean_valid_q <= 1'b1;
//            end
//        end
//    end

//    bram_rw #(.WIDTH(24), .ADDR_WIDTH(`QUERY_SIZE_BITS-1), .DEPTH(`QUERY_LEN), PIPELINE(0), .MEMORY_TYPE("auto")) IN_MEM (
//       .clk(clk),
//       .wea(IN_MEM_wea),
//       .ena(IN_MEM_ena),
//       .addra(IN_MEM_addr),
//       .da(IN_MEM_da),
//       .qa(IN_MEM_qa)
//    );


    assign ready = start_accumulating;


    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            start_accumulating <= 1'b1;
        end
        else begin
            if(start_accumulating && IN_MEM_addr == `QUERY_LEN) begin
                start_accumulating <= 1'b0;
            end

            if(!start_accumulating && IN_MEM_addr == `QUERY_LEN) begin
                start_accumulating <= 1'b1;
            end
        end
    end

    //HARI:assign IN_MEM_wea = in_sample_valid && start_accumulating;

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            IN_MEM_ena_q <= 1'b0;
        end
        else begin
            IN_MEM_ena_q <= IN_MEM_ena & !start_accumulating;
        end
    end

 // memory read control to be enabled when connected to BRAM
//    always_ff @(posedge clk or posedge rst) begin
//        if(rst) begin
//            IN_MEM_addr <= ~0;
//            IN_MEM_ena <= 1'b0;
//            IN_MEM_wea <= 1'b1;
//            IN_MEM_da <= 24'h0;
//        end
//        else begin
//            if(start_accumulating && in_sample_valid) begin
//                IN_MEM_addr <= IN_MEM_addr + 1'b1;
//                IN_MEM_ena <= 1'b1;
//                IN_MEM_da <= {16'h0,in_sample} - in_mean;
//            end
            
//            if(!start_accumulating && mean_valid_q) begin
//                IN_MEM_addr <= IN_MEM_addr + 1'b1;
//                IN_MEM_ena <= 1'b1;
//            end


//            if(last_sample_sent) begin
//                IN_MEM_addr <= ~0;
//                IN_MEM_wea <= 1'b0;
//            end

//        end
//    end


    logic accumulated_sum_valid;

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            accumulated_mad <= 24'h0;
        end
        else begin
            if(in_sample_valid && start_accumulating) begin
                if(in_mean[`DATA_WIDTH-1:0] < in_sample) begin
                    accumulated_mad <= in_sample - in_mean;
                end
                else begin
                    accumulated_mad <= in_mean - in_sample;
                end
            end
        end
    end

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            accumulated_sum_valid <= 1'b0;
        end
        else begin
            accumulated_sum_valid <= 1'b0;

            if(last_sample_sent) begin
                accumulated_sum_valid <= 1'b1;
            end
        end
    end
    wire [39:0] out_wire;
    assign out_mad= out_wire[38:16];
    div_gen_2 MEAN_DIV2 (
      .aclk(clk),                                       // input wire aclk
      .s_axis_divisor_tvalid(accumulated_sum_valid),    // input wire s_axis_divisor_tvalid
      .s_axis_divisor_tdata(common_divisor),      // input wire [15 : 0] s_axis_divisor_tdata
      .s_axis_dividend_tvalid(accumulated_sum_valid),  // input wire s_axis_dividend_tvalid
      .s_axis_dividend_tdata(accumulated_mad),    // input wire [23 : 0] s_axis_dividend_tdata
      .m_axis_dout_tvalid(out_mean_valid),          // output wire m_axis_dout_tvalid
      .m_axis_dout_tdata(out_wire)             // output wire [23 : 0] m_axis_dout_tdata
    );

   
    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            out_sample <= 8'h0;
            out_sample_valid <= 1'b0;
        end
        else begin
            if(IN_MEM_ena_q) begin
                out_sample <= IN_MEM_qa;
                out_sample_valid <= 1'b1;
            end
        end
    end


endmodule
