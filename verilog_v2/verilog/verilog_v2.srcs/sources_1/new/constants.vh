//independent defines, tunable params before synthesis
//synthesis defines
`define SYNTH
//warper defines
`define DATA_WIDTH 8 // need to re-configure IP's too if this change
`define IP_DATA_WIDTH 10
`ifdef SYNTH
    `define QUERY_LEN 2 // array size
    `define REF_MAX_LEN 10
    `define READ_LEN 4  //input read size
    `define MAX_LOOP_CNT `READ_LEN/`QUERY_LEN // no of loop iterations needed
`else
    `define QUERY_LEN 10 // array size
    `define REF_MAX_LEN 100
    `define READ_LEN 4  //input read size
    `define MAX_LOOP_CNT `READ_LEN/`QUERY_LEN // no of loop iterations needed
`endif
`define BRAM_ADDR_WIDTH `DATA_WIDTH

//V2 modifications for bonus scoring
`define MAX_BONUS_WIDTH 7
`define MAX_BONUS 80
`define BONUS 8

`define DTW_THRESHOLD 10

//normalizer defines
`define NORM_DIV1_DIVISOR 8
`define NORM_DIV1_DIVIDEND 13
`define MAD_SHIFT_SCALE $clog2((2**`DATA_WIDTH))-$clog2((2*`NORM_DIV1_DIVISOR))
`define MAX_TVAL_SCALED `DATA_WIDTH*(2**`DATA_WIDTH/(2*`NORM_DIV1_DIVISOR))
`define MIN_TVAL_SCALED -1*`DATA_WIDTH*(2**`DATA_WIDTH/(2*`NORM_DIV1_DIVISOR))


//dependent defines

`define CNTR_STOP `QUERY_LEN+`REF_MAX_LEN
`define REF_SIZE_BITS ($clog2(`REF_MAX_LEN))
`define QUERY_SIZE_BITS ($clog2(`QUERY_LEN))
`define MAX_IP_VAL {`IP_DATA_WIDTH{1'b1}}
`define LOOP_CNTR_BITS $clog2(`MAX_LOOP_CNT)+1
`define NORM_SHIFTER_OP (`MAD_SHIFT_SCALE+`IP_DATA_WIDTH)

`define DATA_OUT_WIDTH ($clog2(`MAX_IP_VAL*`REF_MAX_LEN))
`define MAX_VAL {`DATA_OUT_WIDTH{1'b1}} //max val for output
`define CNTR_BITS ($clog2(`QUERY_LEN)+$clog2(`REF_MAX_LEN)+2)
`define BRAM_Q_ADR_WIDTH $clog2(`READ_LEN)

`define SUM_ACC_OP $clog2(`QUERY_LEN*`MAX_IP_VAL)

//`define MAX_VAL 15