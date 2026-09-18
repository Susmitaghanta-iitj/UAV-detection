`timescale 1ns/1ps
module tb_conv1d_affine_engine;
  parameter CIN=2,COUT=3,LENGTH=16,K=3,STRIDE=1,PADDING=1,ACC_W=48;
  localparam OUTL=((LENGTH+2*PADDING-K)/STRIDE)+1;

  logic clk=0,rst_n=0,start=0;
  logic in_req,wgt_req,out_valid,done;
  logic [$clog2(CIN*LENGTH)-1:0] in_addr;
  logic [$clog2(COUT*CIN*K)-1:0] wgt_addr;
  logic [7:0] in_data,wgt_data;
  logic [$clog2(COUT)-1:0] out_oc;
  logic [$clog2(OUTL)-1:0] out_ox;
  logic signed [ACC_W-1:0] out_sum_qaqw,out_sum_qa;

  logic [7:0] INMEM[0:CIN*LENGTH-1];
  logic [7:0] WGT[0:COUT*CIN*K-1];

  conv1d_affine_engine #(
    .CIN(CIN),.COUT(COUT),.LENGTH(LENGTH),.K(K),
    .STRIDE(STRIDE),.PADDING(PADDING),.ACC_W(ACC_W)
  ) DUT(
    .clk,.rst_n,.start,
    .in_req,.in_addr,.in_data,
    .wgt_req,.wgt_addr,.wgt_data,
    .out_valid,.out_oc,.out_ox,.out_sum_qaqw,.out_sum_qa,.done
  );

  always #5 clk=~clk;
  always_comb begin
    in_data=INMEM[in_addr];
    wgt_data=WGT[wgt_addr];
  end

  integer fd;
  string in_file,wgt_file,out_file;

  initial begin
    if(!$value$plusargs("IN=%s",in_file)) in_file="conv_input.mem";
    if(!$value$plusargs("WGT=%s",wgt_file)) wgt_file="conv_weight.mem";
    if(!$value$plusargs("OUT=%s",out_file)) out_file="conv_rtl.log";
    $readmemh(in_file,INMEM);
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
        $fdisplay(fd,"CONV oc=%0d ox=%0d sum_qaqw=%0d sum_qa=%0d",
                  out_oc,out_ox,out_sum_qaqw,out_sum_qa);
    end
    $fclose(fd);
    $display("PASS conv");
    $finish;
  end
endmodule
