//`define CHAR_WIDTH 8
// check overflow: (log2[1M+1K]=21)
//10 and 22
`define DATA_WIDTH 4
`define DATA_OUT_WIDTH 9

`define QUERY_LEN 3
`define REF_MAX_LEN  6

`define REF_SIZE_BITS 17
`define MAX_VAL {`DATA_OUT_WIDTH{1'b1}}
//`define MAX_VAL 15