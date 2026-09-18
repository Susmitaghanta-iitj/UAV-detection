`timescale 1ns/1ps
module tb_conv1d_complete_engine;
  parameter CIN=2,COUT=3,LENGTH=8,K=3,STRIDE=1,PADDING=1,ACC_W=48,CONST_W=32,FRAC_W=24;
  localparam OUTL=((LENGTH+2*PADDING-K)/STRIDE)+1;

  logic clk=0,rst_n=0,start=0;
  logic signed [31:0] scale_aw_q,scale_al_q,alpha_q,out_scale_q;
  logic in_req,wgt_req,bias_req,out_valid,done;
  logic [$clog2(CIN*LENGTH)-1:0] in_addr;
  logic [$clog2(COUT*CIN*K)-1:0] wgt_addr;
  logic [$clog2(COUT)-1:0] bias_addr,out_oc;
  logic [$clog2(OUTL)-1:0] out_ox;
  logic [7:0] in_data,wgt_data,out_code;
  logic signed [31:0] bias_data;

  logic [7:0] INMEM[0:CIN*LENGTH-1];
  logic [7:0] WGT[0:COUT*CIN*K-1];
  logic [31:0] BIAS[0:COUT-1];
  logic [7:0] EXP[0:COUT*OUTL-1];

  conv1d_complete_engine #(
    .CIN(CIN),.COUT(COUT),.LENGTH(LENGTH),.K(K),.STRIDE(STRIDE),.PADDING(PADDING),
    .ACC_W(ACC_W),.CONST_W(CONST_W),.FRAC_W(FRAC_W)
  ) DUT(
    .clk,.rst_n,.start,.scale_aw_q,.scale_al_q,.alpha_q,.out_scale_q,
    .in_req,.in_addr,.in_data,.wgt_req,.wgt_addr,.wgt_data,
    .bias_req,.bias_addr,.bias_data,.out_valid,.out_oc,.out_ox,.out_code,.done
  );

  always #5 clk=~clk;
  always_comb begin
    in_data=INMEM[in_addr];
    wgt_data=WGT[wgt_addr];
    bias_data=BIAS[bias_addr];
  end

  integer fd;
  integer idx;
  string inf,wf,bf,ef,of;

  initial begin
    if(!$value$plusargs("IN=%s",inf))inf="conv_complete_input.mem";
    if(!$value$plusargs("WGT=%s",wf))wf="conv_complete_wgt.mem";
    if(!$value$plusargs("BIAS=%s",bf))bf="conv_complete_bias.mem";
    if(!$value$plusargs("EXP=%s",ef))ef="conv_complete_expected.mem";
    if(!$value$plusargs("OUT=%s",of))of="conv_complete_rtl.log";
    $readmemh(inf,INMEM);$readmemh(wf,WGT);$readmemh(bf,BIAS);$readmemh(ef,EXP);
    fd=$fopen(of,"w");

    scale_aw_q = 32'sd3107;
    scale_al_q = -32'sd394758;
    alpha_q = 32'sd100663296;
    out_scale_q = 32'sd394758;

    repeat(2)@(posedge clk);rst_n<=1;@(posedge clk);start<=1;@(posedge clk);start<=0;
    while(!done)begin
      @(posedge clk);
      if(out_valid)begin
        idx=out_oc*OUTL+out_ox;
        $fdisplay(fd,"CONV oc=%0d ox=%0d out=%0d exp=%0d",out_oc,out_ox,out_code,EXP[idx]);
      end
    end
    $fclose(fd);$finish;
  end
endmodule
