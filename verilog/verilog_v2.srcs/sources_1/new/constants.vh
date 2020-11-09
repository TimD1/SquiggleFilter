//independent defines, tunable params before synthesis
`define DATA_WIDTH 10
`define QUERY_LEN 50
`define REF_MAX_LEN 100
`define DTW_THRESHOLD 10000


//dependent defines
`define DATA_OUT_WIDTH (`DATA_WIDTH +1)
`define REF_SIZE_BITS ($clog2(`REF_MAX_LEN)+1)
`define MAX_VAL {`DATA_OUT_WIDTH{1'b1}}
`define CNTR_BITS ($clog2(`QUERY_LEN)+$clog2(`REF_MAX_LEN)+2)

//`define MAX_VAL 15