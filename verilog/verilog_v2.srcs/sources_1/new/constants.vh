//independent defines, tunable params before synthesis
`define DATA_WIDTH 8
`define QUERY_LEN 2
`define REF_MAX_LEN 10
`define DTW_THRESHOLD 100000


//dependent defines

`define REF_SIZE_BITS ($clog2(`REF_MAX_LEN)+1)
`define MAX_IP_VAL {`DATA_WIDTH{1'b1}}


`define DATA_OUT_WIDTH ($clog2(`MAX_IP_VAL*`REF_MAX_LEN)+1)
`define MAX_VAL {`DATA_OUT_WIDTH{1'b1}} //max val for output
`define CNTR_BITS ($clog2(`QUERY_LEN)+$clog2(`REF_MAX_LEN)+2)

//`define MAX_VAL 15