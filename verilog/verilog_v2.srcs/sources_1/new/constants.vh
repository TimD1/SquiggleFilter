//independent defines, tunable params before synthesis
//synthesis defines
//`define SYNTH
//warper defines
`define DATA_WIDTH 8 // need to re-configure IP's too if this change
`ifdef SYNTH
    `define QUERY_LEN 5000
    `define REF_MAX_LEN 60000
`else
    `define QUERY_LEN 50
    `define REF_MAX_LEN 200
`endif
`define BRAM_ADDR_WIDTH `DATA_WIDTH
`define DTW_THRESHOLD 1000


//dependent defines

`define REF_SIZE_BITS ($clog2(`REF_MAX_LEN))
`define QUERY_SIZE_BITS ($clog2(`QUERY_LEN))
`define MAX_IP_VAL {`DATA_WIDTH{1'b1}}


`define DATA_OUT_WIDTH ($clog2(`MAX_IP_VAL*`REF_MAX_LEN)+1)
`define MAX_VAL {`DATA_OUT_WIDTH{1'b1}} //max val for output
`define CNTR_BITS ($clog2(`QUERY_LEN)+$clog2(`REF_MAX_LEN)+2)

//`define MAX_VAL 15