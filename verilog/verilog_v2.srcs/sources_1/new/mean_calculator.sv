`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  
`timescale 1ns / 1ns

module mean_calculator(
    input rst,
    input clk,

    input [`DATA_WIDTH-1:0] in_sample,
    input in_sample_valid,
    input [`DATA_WIDTH-1:0] IN_MEM_qa,

    output logic [`DATA_OUT_WIDTH-1:0] out_mean,
    output logic out_mean_valid,
    output logic last_sample_sent,

    output logic ready,
    output logic [`DATA_WIDTH-1:0] out_sample,
    output logic out_sample_valid,
    input next_stage_ready

);



    logic start_sending;
    logic start_accumulating;

    logic [`DATA_OUT_WIDTH-1:0] accumulated_sum;

    logic [15:0] common_divisor;

    assign common_divisor[`QUERY_SIZE_BITS-1:0] = `QUERY_LEN;
    assign common_divisor[15:`QUERY_SIZE_BITS] = 'h0;


    logic [31:0] temp_query_len;

    //logic ready;

    logic IN_MEM_wea;
    logic IN_MEM_ena;
    logic [`QUERY_SIZE_BITS-1:0] IN_MEM_addr;
    logic [`DATA_WIDTH-1:0] IN_MEM_da;
    //logic [`DATA_WIDTH-1:0] IN_MEM_qa;


    logic mean_valid_q;


    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            mean_valid_q <= 1'b0;
        end
        else begin
            if(ready) begin
                mean_valid_q <= 1'b0;
            end

            if(out_mean_valid) begin
                mean_valid_q <= 1'b1;
            end
        end
    end






//    bram_rw #(.WIDTH(8), .ADDR_WIDTH($clog2(QUERY_LEN)), .DEPTH(QUERY_LEN), PIPELINE(0), .MEMORY_TYPE("auto")) IN_MEM (
//       .clk(clk),
//       .wea(IN_MEM_wea),
//       .ena(IN_MEM_ena),
//       .addra(IN_MEM_addra),
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

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            last_sample_sent <= 1'b0;
        end
        else begin
            last_sample_sent <= 1'b0;

            if(!start_accumulating && IN_MEM_addr == `QUERY_LEN) begin
                last_sample_sent <= 1'b1;
            end
        end
    end

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            start_sending <= 1'b0;
        end
        else begin
            if(mean_valid_q && next_stage_ready) begin
                start_sending <= 1'b1;
            end

            if(ready) begin
                start_sending <= 1'b0;
            end
        end
    end

    assign IN_MEM_wea = in_sample_valid && start_accumulating;

    assign IN_MEM_ena = (in_sample_valid && start_accumulating) || (start_sending);
    assign IN_MEM_da = in_sample;

    logic IN_MEM_ena_q;

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            IN_MEM_ena_q <= 1'b0;
        end
        else begin
            IN_MEM_ena_q <= IN_MEM_ena & start_sending;
        end
    end

    
    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            IN_MEM_addr <= 'h0;
        end
        else begin
            if(IN_MEM_ena) begin
                IN_MEM_addr <= IN_MEM_addr + 1'b1;
            end

            if(IN_MEM_addr == `QUERY_LEN) begin
                IN_MEM_addr <= 'h0;
            end
        end
    end


    logic accumulated_sum_valid;

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            accumulated_sum <= 24'h0;
        end
        else begin
            if(in_sample_valid && start_accumulating) begin
                accumulated_sum <= accumulated_sum + in_sample;
            end
        end
    end

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            accumulated_sum_valid <= 1'b0;
        end
        else begin
            accumulated_sum_valid <= 1'b0;

            if(start_accumulating && IN_MEM_addr == `QUERY_LEN) begin
                accumulated_sum_valid <= 1'b1;
            end
        end
    end

    wire [39:0] out_wire;
    assign out_mean= out_wire[39:16];
    div_gen_0 MEAN_DIV1 (
      .aclk(clk),                                       // input wire aclk
      .s_axis_divisor_tvalid(accumulated_sum_valid),    // input wire s_axis_divisor_tvalid
      .s_axis_divisor_tdata(common_divisor),      // input wire [15 : 0] s_axis_divisor_tdata
      .s_axis_dividend_tvalid(accumulated_sum_valid),  // input wire s_axis_dividend_tvalid
      .s_axis_dividend_tdata(accumulated_sum),    // input wire [23 : 0] s_axis_dividend_tdata
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
