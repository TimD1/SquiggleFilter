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
extern void execute_1440(char*, char *);
extern void execute_1441(char*, char *);
extern void execute_1451(char*, char *);
extern void execute_1452(char*, char *);
extern void execute_1453(char*, char *);
extern void execute_1454(char*, char *);
extern void execute_1455(char*, char *);
extern void execute_1456(char*, char *);
extern void execute_1457(char*, char *);
extern void execute_1458(char*, char *);
extern void execute_1459(char*, char *);
extern void execute_1460(char*, char *);
extern void execute_1439(char*, char *);
extern void vlog_simple_process_execute_0_fast_no_reg_no_agg(char*, char*, char*);
extern void execute_1449(char*, char *);
extern void execute_1450(char*, char *);
extern void execute_85(char*, char *);
extern void execute_88(char*, char *);
extern void execute_1437(char*, char *);
extern void execute_1438(char*, char *);
extern void execute_1436(char*, char *);
extern void execute_100(char*, char *);
extern void execute_101(char*, char *);
extern void execute_102(char*, char *);
extern void execute_103(char*, char *);
extern void execute_104(char*, char *);
extern void execute_1429(char*, char *);
extern void execute_1424(char*, char *);
extern void execute_123(char*, char *);
extern void execute_129(char*, char *);
extern void execute_135(char*, char *);
extern void execute_141(char*, char *);
extern void execute_147(char*, char *);
extern void execute_153(char*, char *);
extern void execute_159(char*, char *);
extern void execute_165(char*, char *);
extern void execute_171(char*, char *);
extern void execute_177(char*, char *);
extern void execute_183(char*, char *);
extern void execute_189(char*, char *);
extern void execute_195(char*, char *);
extern void execute_205(char*, char *);
extern void execute_226(char*, char *);
extern void execute_242(char*, char *);
extern void execute_258(char*, char *);
extern void execute_274(char*, char *);
extern void execute_290(char*, char *);
extern void execute_306(char*, char *);
extern void execute_322(char*, char *);
extern void execute_338(char*, char *);
extern void execute_354(char*, char *);
extern void execute_370(char*, char *);
extern void execute_386(char*, char *);
extern void execute_403(char*, char *);
extern void execute_414(char*, char *);
extern void execute_431(char*, char *);
extern void execute_447(char*, char *);
extern void execute_463(char*, char *);
extern void execute_479(char*, char *);
extern void execute_495(char*, char *);
extern void execute_511(char*, char *);
extern void execute_527(char*, char *);
extern void execute_543(char*, char *);
extern void execute_559(char*, char *);
extern void execute_575(char*, char *);
extern void execute_591(char*, char *);
extern void execute_608(char*, char *);
extern void execute_619(char*, char *);
extern void execute_636(char*, char *);
extern void execute_652(char*, char *);
extern void execute_668(char*, char *);
extern void execute_684(char*, char *);
extern void execute_700(char*, char *);
extern void execute_716(char*, char *);
extern void execute_732(char*, char *);
extern void execute_748(char*, char *);
extern void execute_764(char*, char *);
extern void execute_780(char*, char *);
extern void execute_796(char*, char *);
extern void execute_813(char*, char *);
extern void execute_824(char*, char *);
extern void execute_841(char*, char *);
extern void execute_857(char*, char *);
extern void execute_873(char*, char *);
extern void execute_889(char*, char *);
extern void execute_905(char*, char *);
extern void execute_921(char*, char *);
extern void execute_937(char*, char *);
extern void execute_953(char*, char *);
extern void execute_969(char*, char *);
extern void execute_985(char*, char *);
extern void execute_1001(char*, char *);
extern void execute_1018(char*, char *);
extern void execute_1026(char*, char *);
extern void execute_1041(char*, char *);
extern void execute_1055(char*, char *);
extern void execute_1069(char*, char *);
extern void execute_1083(char*, char *);
extern void execute_1097(char*, char *);
extern void execute_1111(char*, char *);
extern void execute_1125(char*, char *);
extern void execute_1139(char*, char *);
extern void execute_1153(char*, char *);
extern void execute_1167(char*, char *);
extern void execute_1181(char*, char *);
extern void execute_1196(char*, char *);
extern void execute_1246(char*, char *);
extern void execute_1205(char*, char *);
extern void execute_1207(char*, char *);
extern void execute_1209(char*, char *);
extern void execute_1211(char*, char *);
extern void execute_1213(char*, char *);
extern void execute_1215(char*, char *);
extern void execute_1218(char*, char *);
extern void execute_1220(char*, char *);
extern void execute_1222(char*, char *);
extern void execute_1224(char*, char *);
extern void execute_1226(char*, char *);
extern void execute_1228(char*, char *);
extern void execute_1230(char*, char *);
extern void execute_1232(char*, char *);
extern void execute_1234(char*, char *);
extern void execute_1236(char*, char *);
extern void execute_1238(char*, char *);
extern void execute_1240(char*, char *);
extern void execute_1242(char*, char *);
extern void execute_1244(char*, char *);
extern void execute_1251(char*, char *);
extern void execute_1262(char*, char *);
extern void execute_1271(char*, char *);
extern void execute_1281(char*, char *);
extern void execute_1287(char*, char *);
extern void execute_1297(char*, char *);
extern void execute_1304(char*, char *);
extern void execute_1311(char*, char *);
extern void execute_1317(char*, char *);
extern void execute_1330(char*, char *);
extern void execute_1336(char*, char *);
extern void execute_1346(char*, char *);
extern void execute_1353(char*, char *);
extern void execute_1360(char*, char *);
extern void execute_1365(char*, char *);
extern void execute_1376(char*, char *);
extern void execute_1382(char*, char *);
extern void execute_1392(char*, char *);
extern void execute_1401(char*, char *);
extern void execute_1408(char*, char *);
extern void execute_1415(char*, char *);
extern void execute_1422(char*, char *);
extern void execute_1428(char*, char *);
extern void execute_212(char*, char *);
extern void execute_214(char*, char *);
extern void execute_216(char*, char *);
extern void execute_114(char*, char *);
extern void execute_115(char*, char *);
extern void execute_109(char*, char *);
extern void execute_112(char*, char *);
extern void execute_1443(char*, char *);
extern void execute_1444(char*, char *);
extern void execute_1445(char*, char *);
extern void execute_1461(char*, char *);
extern void execute_1462(char*, char *);
extern void execute_1463(char*, char *);
extern void execute_1464(char*, char *);
extern void execute_1465(char*, char *);
extern void vlog_transfunc_eventcallback(char*, char*, unsigned, unsigned, unsigned, char *);
extern void transaction_18(char*, char*, unsigned, unsigned, unsigned);
extern void transaction_31(char*, char*, unsigned, unsigned, unsigned);
extern void transaction_32(char*, char*, unsigned, unsigned, unsigned);
extern void transaction_33(char*, char*, unsigned, unsigned, unsigned);
extern void vhdl_transfunc_eventcallback(char*, char*, unsigned, unsigned, unsigned, char *);
funcp funcTab[171] = {(funcp)execute_1440, (funcp)execute_1441, (funcp)execute_1451, (funcp)execute_1452, (funcp)execute_1453, (funcp)execute_1454, (funcp)execute_1455, (funcp)execute_1456, (funcp)execute_1457, (funcp)execute_1458, (funcp)execute_1459, (funcp)execute_1460, (funcp)execute_1439, (funcp)vlog_simple_process_execute_0_fast_no_reg_no_agg, (funcp)execute_1449, (funcp)execute_1450, (funcp)execute_85, (funcp)execute_88, (funcp)execute_1437, (funcp)execute_1438, (funcp)execute_1436, (funcp)execute_100, (funcp)execute_101, (funcp)execute_102, (funcp)execute_103, (funcp)execute_104, (funcp)execute_1429, (funcp)execute_1424, (funcp)execute_123, (funcp)execute_129, (funcp)execute_135, (funcp)execute_141, (funcp)execute_147, (funcp)execute_153, (funcp)execute_159, (funcp)execute_165, (funcp)execute_171, (funcp)execute_177, (funcp)execute_183, (funcp)execute_189, (funcp)execute_195, (funcp)execute_205, (funcp)execute_226, (funcp)execute_242, (funcp)execute_258, (funcp)execute_274, (funcp)execute_290, (funcp)execute_306, (funcp)execute_322, (funcp)execute_338, (funcp)execute_354, (funcp)execute_370, (funcp)execute_386, (funcp)execute_403, (funcp)execute_414, (funcp)execute_431, (funcp)execute_447, (funcp)execute_463, (funcp)execute_479, (funcp)execute_495, (funcp)execute_511, (funcp)execute_527, (funcp)execute_543, (funcp)execute_559, (funcp)execute_575, (funcp)execute_591, (funcp)execute_608, (funcp)execute_619, (funcp)execute_636, (funcp)execute_652, (funcp)execute_668, (funcp)execute_684, (funcp)execute_700, (funcp)execute_716, (funcp)execute_732, (funcp)execute_748, (funcp)execute_764, (funcp)execute_780, (funcp)execute_796, (funcp)execute_813, (funcp)execute_824, (funcp)execute_841, (funcp)execute_857, (funcp)execute_873, (funcp)execute_889, (funcp)execute_905, (funcp)execute_921, (funcp)execute_937, (funcp)execute_953, (funcp)execute_969, (funcp)execute_985, (funcp)execute_1001, (funcp)execute_1018, (funcp)execute_1026, (funcp)execute_1041, (funcp)execute_1055, (funcp)execute_1069, (funcp)execute_1083, (funcp)execute_1097, (funcp)execute_1111, (funcp)execute_1125, (funcp)execute_1139, (funcp)execute_1153, (funcp)execute_1167, (funcp)execute_1181, (funcp)execute_1196, (funcp)execute_1246, (funcp)execute_1205, (funcp)execute_1207, (funcp)execute_1209, (funcp)execute_1211, (funcp)execute_1213, (funcp)execute_1215, (funcp)execute_1218, (funcp)execute_1220, (funcp)execute_1222, (funcp)execute_1224, (funcp)execute_1226, (funcp)execute_1228, (funcp)execute_1230, (funcp)execute_1232, (funcp)execute_1234, (funcp)execute_1236, (funcp)execute_1238, (funcp)execute_1240, (funcp)execute_1242, (funcp)execute_1244, (funcp)execute_1251, (funcp)execute_1262, (funcp)execute_1271, (funcp)execute_1281, (funcp)execute_1287, (funcp)execute_1297, (funcp)execute_1304, (funcp)execute_1311, (funcp)execute_1317, (funcp)execute_1330, (funcp)execute_1336, (funcp)execute_1346, (funcp)execute_1353, (funcp)execute_1360, (funcp)execute_1365, (funcp)execute_1376, (funcp)execute_1382, (funcp)execute_1392, (funcp)execute_1401, (funcp)execute_1408, (funcp)execute_1415, (funcp)execute_1422, (funcp)execute_1428, (funcp)execute_212, (funcp)execute_214, (funcp)execute_216, (funcp)execute_114, (funcp)execute_115, (funcp)execute_109, (funcp)execute_112, (funcp)execute_1443, (funcp)execute_1444, (funcp)execute_1445, (funcp)execute_1461, (funcp)execute_1462, (funcp)execute_1463, (funcp)execute_1464, (funcp)execute_1465, (funcp)vlog_transfunc_eventcallback, (funcp)transaction_18, (funcp)transaction_31, (funcp)transaction_32, (funcp)transaction_33, (funcp)vhdl_transfunc_eventcallback};
const int NumRelocateId= 171;

void relocate(char *dp)
{
	iki_relocate(dp, "xsim.dir/testbench_PE_behav/xsim.reloc",  (void **)funcTab, 171);
	iki_vhdl_file_variable_register(dp + 313008);
	iki_vhdl_file_variable_register(dp + 313064);


	/*Populate the transaction function pointer field in the whole net structure */
}

void sensitize(char *dp)
{
	iki_sensitize(dp, "xsim.dir/testbench_PE_behav/xsim.reloc");
}

	// Initialize Verilog nets in mixed simulation, for the cases when the value at time 0 should be propagated from the mixed language Vhdl net

void wrapper_func_0(char *dp)

{

	iki_vlog_schedule_transaction_signal_fast_vhdl_value_time_0(dp + 332016, dp + 330528, 0, 21, 0, 21, 22, 1);

}

void simulate(char *dp)
{
		iki_schedule_processes_at_time_zero(dp, "xsim.dir/testbench_PE_behav/xsim.reloc");
	wrapper_func_0(dp);

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
