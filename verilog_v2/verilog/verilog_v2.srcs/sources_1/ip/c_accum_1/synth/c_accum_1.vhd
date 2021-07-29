-- (c) Copyright 1995-2020 Xilinx, Inc. All rights reserved.
-- 
-- This file contains confidential and proprietary information
-- of Xilinx, Inc. and is protected under U.S. and
-- international copyright and other intellectual property
-- laws.
-- 
-- DISCLAIMER
-- This disclaimer is not a license and does not grant any
-- rights to the materials distributed herewith. Except as
-- otherwise provided in a valid license issued to you by
-- Xilinx, and to the maximum extent permitted by applicable
-- law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
-- WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
-- AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
-- BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
-- INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
-- (2) Xilinx shall not be liable (whether in contract or tort,
-- including negligence, or under any other theory of
-- liability) for any loss or damage of any kind or nature
-- related to, arising under or in connection with these
-- materials, including for any direct, or any indirect,
-- special, incidental, or consequential loss or damage
-- (including loss of data, profits, goodwill, or any type of
-- loss or damage suffered as a result of any action brought
-- by a third party) even if such damage or loss was
-- reasonably foreseeable or Xilinx had been advised of the
-- possibility of the same.
-- 
-- CRITICAL APPLICATIONS
-- Xilinx products are not designed or intended to be fail-
-- safe, or for use in any application requiring fail-safe
-- performance, such as life-support or safety devices or
-- systems, Class III medical devices, nuclear facilities,
-- applications related to the deployment of airbags, or any
-- other applications that could lead to death, personal
-- injury, or severe property or environmental damage
-- (individually and collectively, "Critical
-- Applications"). Customer assumes the sole risk and
-- liability of any use of Xilinx products in Critical
-- Applications, subject only to applicable laws and
-- regulations governing limitations on product liability.
-- 
-- THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
-- PART OF THIS FILE AT ALL TIMES.
-- 
-- DO NOT MODIFY THIS FILE.

-- IP VLNV: xilinx.com:ip:c_accum:12.0
-- IP Revision: 13

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

LIBRARY c_accum_v12_0_13;
USE c_accum_v12_0_13.c_accum_v12_0_13;

ENTITY c_accum_1 IS
  PORT (
    B : IN STD_LOGIC_VECTOR(7 DOWNTO 0);
    CLK : IN STD_LOGIC;
    CE : IN STD_LOGIC;
    SCLR : IN STD_LOGIC;
    Q : OUT STD_LOGIC_VECTOR(20 DOWNTO 0)
  );
END c_accum_1;

ARCHITECTURE c_accum_1_arch OF c_accum_1 IS
  ATTRIBUTE DowngradeIPIdentifiedWarnings : STRING;
  ATTRIBUTE DowngradeIPIdentifiedWarnings OF c_accum_1_arch: ARCHITECTURE IS "yes";
  COMPONENT c_accum_v12_0_13 IS
    GENERIC (
      C_XDEVICEFAMILY : STRING;
      C_IMPLEMENTATION : INTEGER;
      C_VERBOSITY : INTEGER;
      C_B_WIDTH : INTEGER;
      C_OUT_WIDTH : INTEGER;
      C_B_TYPE : INTEGER;
      C_CE_OVERRIDES_SCLR : INTEGER;
      C_ADD_MODE : INTEGER;
      C_HAS_C_IN : INTEGER;
      C_HAS_CE : INTEGER;
      C_HAS_BYPASS : INTEGER;
      C_HAS_SCLR : INTEGER;
      C_LATENCY : INTEGER;
      C_SCALE : INTEGER;
      C_AINIT_VAL : STRING;
      C_SINIT_VAL : STRING;
      C_BYPASS_LOW : INTEGER;
      C_SCLR_OVERRIDES_SSET : INTEGER;
      C_HAS_SSET : INTEGER;
      C_HAS_SINIT : INTEGER
    );
    PORT (
      B : IN STD_LOGIC_VECTOR(7 DOWNTO 0);
      CLK : IN STD_LOGIC;
      ADD : IN STD_LOGIC;
      C_IN : IN STD_LOGIC;
      CE : IN STD_LOGIC;
      BYPASS : IN STD_LOGIC;
      SCLR : IN STD_LOGIC;
      SSET : IN STD_LOGIC;
      SINIT : IN STD_LOGIC;
      Q : OUT STD_LOGIC_VECTOR(20 DOWNTO 0)
    );
  END COMPONENT c_accum_v12_0_13;
  ATTRIBUTE X_CORE_INFO : STRING;
  ATTRIBUTE X_CORE_INFO OF c_accum_1_arch: ARCHITECTURE IS "c_accum_v12_0_13,Vivado 2019.1";
  ATTRIBUTE CHECK_LICENSE_TYPE : STRING;
  ATTRIBUTE CHECK_LICENSE_TYPE OF c_accum_1_arch : ARCHITECTURE IS "c_accum_1,c_accum_v12_0_13,{}";
  ATTRIBUTE CORE_GENERATION_INFO : STRING;
  ATTRIBUTE CORE_GENERATION_INFO OF c_accum_1_arch: ARCHITECTURE IS "c_accum_1,c_accum_v12_0_13,{x_ipProduct=Vivado 2019.1,x_ipVendor=xilinx.com,x_ipLibrary=ip,x_ipName=c_accum,x_ipVersion=12.0,x_ipCoreRevision=13,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED,C_XDEVICEFAMILY=artix7,C_IMPLEMENTATION=0,C_VERBOSITY=0,C_B_WIDTH=8,C_OUT_WIDTH=21,C_B_TYPE=1,C_CE_OVERRIDES_SCLR=0,C_ADD_MODE=0,C_HAS_C_IN=0,C_HAS_CE=1,C_HAS_BYPASS=0,C_HAS_SCLR=1,C_LATENCY=1,C_SCALE=0,C_AINIT_VAL=0,C_SINIT_VAL=0,C_BYPASS_LOW=0,C_SCLR_OVERRIDES_SSET=1,C_HAS_SSET=0,C_HAS_SINIT=0}";
  ATTRIBUTE X_INTERFACE_INFO : STRING;
  ATTRIBUTE X_INTERFACE_PARAMETER : STRING;
  ATTRIBUTE X_INTERFACE_PARAMETER OF Q: SIGNAL IS "XIL_INTERFACENAME q_intf, LAYERED_METADATA undef";
  ATTRIBUTE X_INTERFACE_INFO OF Q: SIGNAL IS "xilinx.com:signal:data:1.0 q_intf DATA";
  ATTRIBUTE X_INTERFACE_PARAMETER OF SCLR: SIGNAL IS "XIL_INTERFACENAME sclr_intf, POLARITY ACTIVE_HIGH, INSERT_VIP 0";
  ATTRIBUTE X_INTERFACE_INFO OF SCLR: SIGNAL IS "xilinx.com:signal:reset:1.0 sclr_intf RST";
  ATTRIBUTE X_INTERFACE_PARAMETER OF CE: SIGNAL IS "XIL_INTERFACENAME ce_intf, POLARITY ACTIVE_LOW";
  ATTRIBUTE X_INTERFACE_INFO OF CE: SIGNAL IS "xilinx.com:signal:clockenable:1.0 ce_intf CE";
  ATTRIBUTE X_INTERFACE_PARAMETER OF CLK: SIGNAL IS "XIL_INTERFACENAME clk_intf, ASSOCIATED_BUSIF q_intf:sinit_intf:sset_intf:bypass_intf:c_in_intf:add_intf:b_intf, ASSOCIATED_RESET SCLR, ASSOCIATED_CLKEN CE, FREQ_HZ 100000000, PHASE 0.000, INSERT_VIP 0";
  ATTRIBUTE X_INTERFACE_INFO OF CLK: SIGNAL IS "xilinx.com:signal:clock:1.0 clk_intf CLK";
  ATTRIBUTE X_INTERFACE_PARAMETER OF B: SIGNAL IS "XIL_INTERFACENAME b_intf, LAYERED_METADATA undef";
  ATTRIBUTE X_INTERFACE_INFO OF B: SIGNAL IS "xilinx.com:signal:data:1.0 b_intf DATA";
BEGIN
  U0 : c_accum_v12_0_13
    GENERIC MAP (
      C_XDEVICEFAMILY => "artix7",
      C_IMPLEMENTATION => 0,
      C_VERBOSITY => 0,
      C_B_WIDTH => 8,
      C_OUT_WIDTH => 21,
      C_B_TYPE => 1,
      C_CE_OVERRIDES_SCLR => 0,
      C_ADD_MODE => 0,
      C_HAS_C_IN => 0,
      C_HAS_CE => 1,
      C_HAS_BYPASS => 0,
      C_HAS_SCLR => 1,
      C_LATENCY => 1,
      C_SCALE => 0,
      C_AINIT_VAL => "0",
      C_SINIT_VAL => "0",
      C_BYPASS_LOW => 0,
      C_SCLR_OVERRIDES_SSET => 1,
      C_HAS_SSET => 0,
      C_HAS_SINIT => 0
    )
    PORT MAP (
      B => B,
      CLK => CLK,
      ADD => '1',
      C_IN => '0',
      CE => CE,
      BYPASS => '0',
      SCLR => SCLR,
      SSET => '0',
      SINIT => '0',
      Q => Q
    );
END c_accum_1_arch;
