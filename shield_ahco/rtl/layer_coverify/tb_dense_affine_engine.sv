`timescale 1ns/1ps
module tb_dense_affine_engine;
  parameter DIN=32;
  parameter DOUT=8;
  parameter ACC_W=48;

  logic clk=0,rst_n=0,start=0;
  logic act_req,wgt_req,out_valid,done;
  logic [$clog2(DIN)-1:0] act_addr;
  logic [$clog2(DIN*DOUT)-1:0] wgt_addr;
  logic [7:0] act_data,wgt_data;
  logic [$clog2(DOUT)-1:0] out_index;
  logic signed [ACC_W-1:0] out_sum_qaqw,out_sum_qa;

  logic [7:0] ACT[0:DIN-1];
  logic [7:0] WGT[0:DIN*DOUT-1];

  dense_affine_engine #(.DIN(DIN),.DOUT(DOUT),.ACC_W(ACC_W)) DUT(
    .clk,.rst_n,.start,
    .act_req,.act_addr,.act_data,
    .wgt_req,.wgt_addr,.wgt_data,
    .out_valid,.out_index,.out_sum_qaqw,.out_sum_qa,.done
  );

  always #5 clk=~clk;
  always_comb begin
    act_data=ACT[act_addr];
    wgt_data=WGT[wgt_addr];
  end

  integer fd;
  string act_file,wgt_file,out_file;

  initial begin
    if(!$value$plusargs("ACT=%s",act_file)) act_file="dense_act.mem";
    if(!$value$plusargs("WGT=%s",wgt_file)) wgt_file="dense_weight.mem";
    if(!$value$plusargs("OUT=%s",out_file)) out_file="dense_rtl.log";
    $readmemh(act_file,ACT);
    $readmemh(wgt_file,WGT);
    fd=$fopen(out_file,"w");

    repeat(2) @(posedge clk);
    rst_n<=1;
    @(posedge clk);
    start<=1;
    @(posedge clk);
    start<=0;

    while(!done) begin
      @(posedge clk);
      if(out_valid)
        $fdisplay(fd,"DENSE o=%0d sum_qaqw=%0d sum_qa=%0d",
                  out_index,out_sum_qaqw,out_sum_qa);
    end
    $fclose(fd);
    $display("PASS dense");
    $finish;
  end
endmodule
