/**********************************************************************/
/*   ____  ____                                                       */
/*  /   /\/   /                                                       */
/* /___/  \  /                                                        */
/* \   \   \/                                                         */
/*  \   \        Copyright (c) 2003-2013 Xilinx, Inc.                 */
/*  /   /        All Right Reserved.                                  */
/* /---/   /\                                                         */
/* \   \  /  \                                                        */
/*  \___\/\___\                                                       */
/**********************************************************************/


#include "iki.h"
#include <string.h>
#include <math.h>
#ifdef __GNUC__
#include <stdlib.h>
#else
#include <malloc.h>
#define alloca _alloca
#endif
/**********************************************************************/
/*   ____  ____                                                       */
/*  /   /\/   /                                                       */
/* /___/  \  /                                                        */
/* \   \   \/                                                         */
/*  \   \        Copyright (c) 2003-2013 Xilinx, Inc.                 */
/*  /   /        All Right Reserved.                                  */
/* /---/   /\                                                         */
/* \   \  /  \                                                        */
/*  \___\/\___\                                                       */
/**********************************************************************/


#include "iki.h"
#include <string.h>
#include <math.h>
#ifdef __GNUC__
#include <stdlib.h>
#else
#include <malloc.h>
#define alloca _alloca
#endif
typedef void (*funcp)(char *, char *);
extern int main(int, char**);
extern void execute_517(char*, char *);
extern void execute_518(char*, char *);
extern void execute_528(char*, char *);
extern void execute_529(char*, char *);
extern void execute_530(char*, char *);
extern void execute_531(char*, char *);
extern void execute_532(char*, char *);
extern void execute_533(char*, char *);
extern void execute_534(char*, char *);
extern void execute_535(char*, char *);
extern void execute_536(char*, char *);
extern void execute_537(char*, char *);
extern void execute_516(char*, char *);
extern void vlog_simple_process_execute_0_fast_no_reg_no_agg(char*, char*, char*);
extern void execute_526(char*, char *);
extern void execute_527(char*, char *);
extern void execute_85(char*, char *);
extern void execute_88(char*, char *);
extern void execute_514(char*, char *);
extern void execute_515(char*, char *);
extern void execute_513(char*, char *);
extern void execute_100(char*, char *);
extern void execute_101(char*, char *);
extern void execute_102(char*, char *);
extern void execute_103(char*, char *);
extern void execute_104(char*, char *);
extern void execute_506(char*, char *);
extern void execute_501(char*, char *);
extern void execute_123(char*, char *);
extern void execute_129(char*, char *);
extern void execute_135(char*, char *);
extern void execute_141(char*, char *);
extern void execute_147(char*, char *);
extern void execute_153(char*, char *);
extern void execute_159(char*, char *);
extern void execute_169(char*, char *);
extern void execute_190(char*, char *);
extern void execute_206(char*, char *);
extern void execute_222(char*, char *);
extern void execute_238(char*, char *);
extern void execute_254(char*, char *);
extern void execute_271(char*, char *);
extern void execute_279(char*, char *);
extern void execute_294(char*, char *);
extern void execute_308(char*, char *);
extern void execute_322(char*, char *);
extern void execute_336(char*, char *);
extern void execute_350(char*, char *);
extern void execute_365(char*, char *);
extern void execute_397(char*, char *);
extern void execute_374(char*, char *);
extern void execute_376(char*, char *);
extern void execute_378(char*, char *);
extern void execute_381(char*, char *);
extern void execute_383(char*, char *);
extern void execute_385(char*, char *);
extern void execute_387(char*, char *);
extern void execute_389(char*, char *);
extern void execute_391(char*, char *);
extern void execute_393(char*, char *);
extern void execute_395(char*, char *);
extern void execute_402(char*, char *);
extern void execute_413(char*, char *);
extern void execute_422(char*, char *);
extern void execute_430(char*, char *);
extern void execute_435(char*, char *);
extern void execute_446(char*, char *);
extern void execute_452(char*, char *);
extern void execute_462(char*, char *);
extern void execute_471(char*, char *);
extern void execute_478(char*, char *);
extern void execute_485(char*, char *);
extern void execute_492(char*, char *);
extern void execute_499(char*, char *);
extern void execute_505(char*, char *);
extern void execute_176(char*, char *);
extern void execute_178(char*, char *);
extern void execute_180(char*, char *);
extern void execute_114(char*, char *);
extern void execute_115(char*, char *);
extern void execute_109(char*, char *);
extern void execute_112(char*, char *);
extern void execute_520(char*, char *);
extern void execute_521(char*, char *);
extern void execute_522(char*, char *);
extern void execute_538(char*, char *);
extern void execute_539(char*, char *);
extern void execute_540(char*, char *);
extern void execute_541(char*, char *);
extern void execute_542(char*, char *);
extern void transaction_16(char*, char*, unsigned, unsigned, unsigned);
extern void vlog_transfunc_eventcallback(char*, char*, unsigned, unsigned, unsigned, char *);
extern void transaction_18(char*, char*, unsigned, unsigned, unsigned);
extern void transaction_28(char*, char*, unsigned, unsigned, unsigned);
extern void transaction_33(char*, char*, unsigned, unsigned, unsigned);
extern void transaction_34(char*, char*, unsigned, unsigned, unsigned);
extern void vhdl_transfunc_eventcallback(char*, char*, unsigned, unsigned, unsigned, char *);
extern void transaction_4(char*, char*, unsigned, unsigned, unsigned);
funcp funcTab[98] = {(funcp)execute_517, (funcp)execute_518, (funcp)execute_528, (funcp)execute_529, (funcp)execute_530, (funcp)execute_531, (funcp)execute_532, (funcp)execute_533, (funcp)execute_534, (funcp)execute_535, (funcp)execute_536, (funcp)execute_537, (funcp)execute_516, (funcp)vlog_simple_process_execute_0_fast_no_reg_no_agg, (funcp)execute_526, (funcp)execute_527, (funcp)execute_85, (funcp)execute_88, (funcp)execute_514, (funcp)execute_515, (funcp)execute_513, (funcp)execute_100, (funcp)execute_101, (funcp)execute_102, (funcp)execute_103, (funcp)execute_104, (funcp)execute_506, (funcp)execute_501, (funcp)execute_123, (funcp)execute_129, (funcp)execute_135, (funcp)execute_141, (funcp)execute_147, (funcp)execute_153, (funcp)execute_159, (funcp)execute_169, (funcp)execute_190, (funcp)execute_206, (funcp)execute_222, (funcp)execute_238, (funcp)execute_254, (funcp)execute_271, (funcp)execute_279, (funcp)execute_294, (funcp)execute_308, (funcp)execute_322, (funcp)execute_336, (funcp)execute_350, (funcp)execute_365, (funcp)execute_397, (funcp)execute_374, (funcp)execute_376, (funcp)execute_378, (funcp)execute_381, (funcp)execute_383, (funcp)execute_385, (funcp)execute_387, (funcp)execute_389, (funcp)execute_391, (funcp)execute_393, (funcp)execute_395, (funcp)execute_402, (funcp)execute_413, (funcp)execute_422, (funcp)execute_430, (funcp)execute_435, (funcp)execute_446, (funcp)execute_452, (funcp)execute_462, (funcp)execute_471, (funcp)execute_478, (funcp)execute_485, (funcp)execute_492, (funcp)execute_499, (funcp)execute_505, (funcp)execute_176, (funcp)execute_178, (funcp)execute_180, (funcp)execute_114, (funcp)execute_115, (funcp)execute_109, (funcp)execute_112, (funcp)execute_520, (funcp)execute_521, (funcp)execute_522, (funcp)execute_538, (funcp)execute_539, (funcp)execute_540, (funcp)execute_541, (funcp)execute_542, (funcp)transaction_16, (funcp)vlog_transfunc_eventcallback, (funcp)transaction_18, (funcp)transaction_28, (funcp)transaction_33, (funcp)transaction_34, (funcp)vhdl_transfunc_eventcallback, (funcp)transaction_4};
const int NumRelocateId= 98;

void relocate(char *dp)
{
	iki_relocate(dp, "xsim.dir/testbench_PE_behav/xsim.reloc",  (void **)funcTab, 98);
	iki_vhdl_file_variable_register(dp + 34488);
	iki_vhdl_file_variable_register(dp + 34544);


	/*Populate the transaction function pointer field in the whole net structure */
}

void sensitize(char *dp)
{
	iki_sensitize(dp, "xsim.dir/testbench_PE_behav/xsim.reloc");
}

void simulate(char *dp)
{
		iki_schedule_processes_at_time_zero(dp, "xsim.dir/testbench_PE_behav/xsim.reloc");
	// Initialize Verilog nets in mixed simulation, for the cases when the value at time 0 should be propagated from the mixed language Vhdl net

	iki_vlog_schedule_transaction_signal_fast_vhdl_value_time_0(dp + 53496, dp + 52008, 0, 9, 0, 9, 10, 1);
	iki_execute_processes();

	// Schedule resolution functions for the multiply driven Verilog nets that have strength
	// Schedule transaction functions for the singly driven Verilog nets that have strength

}
#include "iki_bridge.h"
void relocate(char *);

void sensitize(char *);

void simulate(char *);

extern SYSTEMCLIB_IMP_DLLSPEC void local_register_implicit_channel(int, char*);
extern void implicit_HDL_SCinstatiate();

extern SYSTEMCLIB_IMP_DLLSPEC int xsim_argc_copy ;
extern SYSTEMCLIB_IMP_DLLSPEC char** xsim_argv_copy ;

int main(int argc, char **argv)
{
    iki_heap_initialize("ms", "isimmm", 0, 2147483648) ;
    iki_set_sv_type_file_path_name("xsim.dir/testbench_PE_behav/xsim.svtype");
    iki_set_crvs_dump_file_path_name("xsim.dir/testbench_PE_behav/xsim.crvsdump");
    void* design_handle = iki_create_design("xsim.dir/testbench_PE_behav/xsim.mem", (void *)relocate, (void *)sensitize, (void *)simulate, 0, isimBridge_getWdbWriter(), 0, argc, argv);
     iki_set_rc_trial_count(100);
    (void) design_handle;
    return iki_simulate_design();
}
