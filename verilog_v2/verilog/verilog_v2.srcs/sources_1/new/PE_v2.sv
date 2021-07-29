`timescale 1ns / 1ns
//////////////////////////////////////////////////////////////////////////////////
// Company: UofM
// Engineer: Harisankar Sadasivan
// 
// Create Date: 11/01/2020 10:45:14 PM
// Design Name: SquAl
// Module Name: PE
// Project Name: SquAl
// Target Devices: FPGA
// Tool Versions: 
// Description: defines the PE in the systolic array (warper) for SquAl
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////
//include global defines
`ifndef CONSTANTS
   `define CONSTANTS
   `include "constants.vh"
`endif  

//Processing element of the systolic array
module PE_v2(
      
    input clk,
    input rst,
    input [`DATA_WIDTH-1:0] query,
    input [`DATA_WIDTH-1:0] ip_reference,
      
    input activate,      
    //input [`DATA_OUT_WIDTH-1:0] top,
    input [`MAX_BONUS_WIDTH-1:0] ip_bonus,
    input [`DATA_OUT_WIDTH-1:0] left,
    input [`DATA_OUT_WIDTH-1:0] diag,     
    input init,             
    output logic[`DATA_OUT_WIDTH-1:0] prev_op, 
    output logic[`DATA_OUT_WIDTH-1:0] curr_op,
    output logic[`MAX_BONUS_WIDTH-1:0] prev_bonus, 
    //output logic stop_bit, 
    output [`DATA_WIDTH-1:0] query_o , 
    output [`DATA_WIDTH-1:0] op_reference         
);
  


  
     
    //internal logic and wires
    logic [`DATA_WIDTH-1:0] query_o_r;
    logic [1:0] set_bit=0;
    //wire stop_wire;
    wire [`DATA_WIDTH-1:0] diff,cum_bonus,bonus_wire_pre_cal;      //changed
    logic [`DATA_WIDTH-1:0] mv_stay_score,bonus_wire;
    wire signed [`DATA_WIDTH:0] move_score;
    wire move;
    logic[`MAX_BONUS_WIDTH-1:0] curr_bonus;

    //sign extended vars
    wire signed [`DATA_OUT_WIDTH-1:0] diag_s;
    wire [`MAX_BONUS_WIDTH-1:0] ip_bonus_s;

    logic [`DATA_OUT_WIDTH-1:0] score_wire;
    wire [`DATA_WIDTH-1:0] l_query;
    logic [`DATA_WIDTH-1:0] l_query_r;       
    wire  [`DATA_WIDTH-1:0] ip_ref ;
    logic [`DATA_WIDTH-1:0] ip_reference_r;



    //sign extension;
    assign diag_s={{1{1'b0}},diag};
    assign ip_bonus_s={{1{1'b0}},ip_bonus};

    //register streaming reference
    always @(posedge clk) begin

        ip_reference_r<=ip_reference;     
    end


    //wires for registered output from ref and query
    assign ip_ref=ip_reference_r;

    assign op_reference = ip_reference_r;

    assign l_query=l_query_r;
    assign query_o=query_o_r;

    
     //absolute delta score computation between reference and query
    assign diff= (l_query>ip_ref)?(l_query-ip_ref):(ip_ref-l_query);

    //calculate move score
    assign move_score=diag-ip_bonus_s;
    //compare move score vs stay
    assign move=(move_score<left)?1:0;





    //bonus value update
    assign cum_bonus=`BONUS +ip_bonus;
    //bonus score selection/rest and store path

    assign bonus_wire_pre_cal= (`MAX_BONUS>cum_bonus)?cum_bonus:`MAX_BONUS;
    always_comb begin
        case(move)
         1'b1: begin
            bonus_wire=0;
            mv_stay_score = move_score;
          end
         1'b0: begin
            bonus_wire= bonus_wire_pre_cal;
            mv_stay_score = left;
          end
        endcase
    end
    assign score_wire=mv_stay_score+diff;    

   
    //stopping score line
    //assign stop_wire= (score_wire>=`DTW_THRESHOLD);
 
    always_ff @(posedge clk) begin //{}

        if(rst) begin //{  //sync reset
            curr_op<=`MAX_VAL;
            prev_op<=`MAX_VAL;
            curr_bonus<=0;
            prev_bonus<=0;
            //stop_bit<=0;
        end //}
        else begin
            if(activate) begin //{ //Firing the PE
                //update sequentially
                curr_op<=score_wire;
                //stop_bit<=stop_wire;
                prev_op<=curr_op;    

                curr_bonus<=   bonus_wire ;
                prev_bonus<=   curr_bonus;         
            end //}
        end
    end //}

    always_ff @(posedge clk) begin //{}

        if(rst) begin //{  //sync reset
            set_bit<=0;
            l_query_r<=0;
            query_o_r<=0;
        end //}
        else begin
            if(init) begin //{ //PE initialization 
                if(set_bit<2'b1) begin
                    l_query_r<=query;
                    set_bit<=set_bit+1;
                end
                else begin 
                    query_o_r<=query;
                end
            end //}
        end
    end //}

endmodule : PE_v2