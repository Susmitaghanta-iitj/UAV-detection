`timescale 1ns/1ps
module tb_dense_complete_engine;
  parameter DIN=16,DOUT=4,ACC_W=48,CONST_W=32,FRAC_W=24;

  logic clk=0,rst_n=0,start=0;
  logic signed [31:0] scale_aw_q,scale_al_q,alpha_q,out_scale_q;
  logic act_req,wgt_req,bias_req,out_valid,done;
  logic [$clog2(DIN)-1:0] act_addr;
  logic [$clog2(DIN*DOUT)-1:0] wgt_addr;
  logic [$clog2(DOUT)-1:0] bias_addr,out_index;
  logic [7:0] act_data,wgt_data,out_code;
  logic signed [31:0] bias_data;

  logic [7:0] ACT[0:DIN-1];
  logic [7:0] WGT[0:DIN*DOUT-1];
  logic [31:0] BIAS[0:DOUT-1];
  logic [7:0] EXP[0:DOUT-1];

  dense_complete_engine #(.DIN(DIN),.DOUT(DOUT),.ACC_W(ACC_W),.CONST_W(CONST_W),.FRAC_W(FRAC_W)) DUT(
    .clk,.rst_n,.start,.scale_aw_q,.scale_al_q,.alpha_q,.out_scale_q,
    .act_req,.act_addr,.act_data,.wgt_req,.wgt_addr,.wgt_data,
    .bias_req,.bias_addr,.bias_data,.out_valid,.out_index,.out_code,.done
  );

  always #5 clk=~clk;
  always_comb begin
    act_data=ACT[act_addr];
    wgt_data=WGT[wgt_addr];
    bias_data=BIAS[bias_addr];
  end

  integer fd;
  string af,wf,bf,ef,of;

  initial begin
    if(!$value$plusargs("ACT=%s",af))af="dense_complete_act.mem";
    if(!$value$plusargs("WGT=%s",wf))wf="dense_complete_wgt.mem";
    if(!$value$plusargs("BIAS=%s",bf))bf="dense_complete_bias.mem";
    if(!$value$plusargs("EXP=%s",ef))ef="dense_complete_expected.mem";
    if(!$value$plusargs("OUT=%s",of))of="dense_complete_rtl.log";
    $readmemh(af,ACT);$readmemh(wf,WGT);$readmemh(bf,BIAS);$readmemh(ef,EXP);
    fd=$fopen(of,"w");

    // Must match synthetic complete layer generator defaults.
    scale_aw_q = 32'sd3107;
    scale_al_q = -32'sd394758;
    alpha_q = 32'sd100663296;
    out_scale_q = 32'sd394758;

    repeat(2)@(posedge clk);rst_n<=1;@(posedge clk);start<=1;@(posedge clk);start<=0;
    while(!done)begin
      @(posedge clk);
      if(out_valid)
        $fdisplay(fd,"DENSE o=%0d out=%0d exp=%0d",out_index,out_code,EXP[out_index]);
    end
    $fclose(fd);$finish;
  end
endmodule
