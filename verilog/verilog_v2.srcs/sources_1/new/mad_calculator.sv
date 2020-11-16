`include "constants.vh"

module mad_calculator(
    input rst,
    input clk,

    input [`DATA_WIDTH-1:0] in_sample,
    input in_sample_valid,
    input last_sample_sent,

    input [23:0] in_mean,
    output logic ready,


    output logic [7:0] out_sample,
    output logic out_sample_valid,

    output logic [23:0] out_mad

);

    
    logic start_accumulating;
    logic [23:0] accumulated_mad;

    logic [15:0] common_divisor;

    assign common_divisor[$clog2(QUERY_LEN)-1:0] = QUERY_LEN;
    assign common_divisor[15:$clog2(QUERY_LEN)] = 'h0;


    logic [31:0] temp_query_len;

    logic ready;

    logic IN_MEM_wea;
    logic IN_MEM_ena;
    logic [$clog2(QUERY_LEN)-1:0] IN_MEM_addr;
    logic [23:0] IN_MEM_da;
    logic [23:0] IN_MEM_qa;


    logic mean_valid_q;


    assign ready = start_accumulating;

    always_ff @(posegde clk or posedge rst) begin
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

    bram_rw #(.WIDTH(24), .ADDR_WIDTH($clog2(QUERY_LEN)), .DEPTH(QUERY_LEN), PIPELINE(0), .MEMORY_TYPE("auto")) IN_MEM (
       .clk(clk),
       .wea(IN_MEM_wea),
       .ena(IN_MEM_ena),
       .addra(IN_MEM_addra),
       .da(IN_MEM_da),
       .qa(IN_MEM_qa)
    );


    assign ready = start_accumulating;


    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            start_accumulating <= 1'b1;
        end
        else begin
            if(start_accumulating && IN_MEM_addr == QUERY_LEN) begin
                start_accumulating <= 1'b0;
            end

            if(!start_accumulating && IN_MEM_addr == QUERY_LEN) begin
                start_accumulating <= 1'b1;
            end
        end
    end

    assign IN_MEM_wea = in_sample_valid && start_accumulating;

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            IN_MEM_ena_q <= 1'b0;
        end
        else begin
            IN_MEM_ena_q <= IN_MEM_ena & !start_accumulating;
        end
    end

    
    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            IN_MEM_addr <= ~0;
            IN_MEM_ena <= 1'b0;
            IN_MEM_wea <= 1'b1;
            IN_MEM_da <= 24'h0;
        end
        else begin
            if(start_accumulating && in_sample_valid) begin
                IN_MEM_addr <= IN_MEM_addr + 1'b1;
                IN_MEM_ena <= 1'b1;
                IN_MEM_da <= {16'h0,in_sample} - in_mean;
            end
            
            if(!start_accumulating && mean_valid_q) begin
                IN_MEM_addr <= IN_MEM_addr + 1'b1;
                IN_MEM_ena <= 1'b1;
            end


            if(last_sample_sent) begin
                IN_MEM_addr <= ~0;
                IN_MEM_wea <= 1'b0;
            end

        end
    end


    logic accumulated_sum_valid;

    always_ff @(posedge clk or posedge rst) begin
        if(rst) begin
            accumulated_mad <= 24'h0;
        end
        else begin
            if(in_sample_valid && start_accumulating) begin
                if(in_mean[7:0] < in_sample) begin
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

    div_gen_0 MEAN_DIV1 (
      .aclk(clk),                                       // input wire aclk
      .s_axis_divisor_tvalid(accumulated_sum_valid),    // input wire s_axis_divisor_tvalid
      .s_axis_divisor_tdata(common_divisor),      // input wire [15 : 0] s_axis_divisor_tdata
      .s_axis_dividend_tvalid(accumulated_sum_valid),  // input wire s_axis_dividend_tvalid
      .s_axis_dividend_tdata(accumulated_sum),    // input wire [23 : 0] s_axis_dividend_tdata
      .m_axis_dout_tvalid(out_mean_valid),          // output wire m_axis_dout_tvalid
      .m_axis_dout_tdata(out_mean)             // output wire [23 : 0] m_axis_dout_tdata
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
