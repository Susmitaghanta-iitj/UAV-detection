`timescale 1ns/1ps

module tb_qat_affine_mac_core;
  localparam ACT_W=8;
  localparam WGT_W=8;
  localparam ACC_W=48;
  localparam MAX_TAPS=4096;

  logic clk=0;
  logic rst_n=0;
  logic clear=0;
  logic en=0;
  logic [ACT_W-1:0] act_code;
  logic [WGT_W-1:0] wgt_code;
  logic signed [ACC_W-1:0] sum_qaqw;
  logic signed [ACC_W-1:0] sum_qa;

  qat_affine_mac_core #(
    .ACT_W(ACT_W),.WGT_W(WGT_W),.ACC_W(ACC_W)
  ) DUT (
    .clk,.rst_n,.clear,.en,.act_code,.wgt_code,.sum_qaqw,.sum_qa
  );

  always #5 clk=~clk;

  integer fd_in, fd_out, rc;
  integer seq, taps, i;
  integer a_i, w_i;
  reg [1023:0] line;
  string in_file;
  string out_file;

  initial begin
    if(!$value$plusargs("IN=%s",in_file))
      in_file="accum_sequences_flat.txt";
    if(!$value$plusargs("OUT=%s",out_file))
      out_file="rtl_results.log";

    fd_in=$fopen(in_file,"r");
    fd_out=$fopen(out_file,"w");
    if(fd_in==0 || fd_out==0) begin
      $display("ERROR opening files");
      $finish(2);
    end

    repeat(2) @(posedge clk);
    rst_n<=1;
    @(posedge clk);

    while(!$feof(fd_in)) begin
      rc=$fscanf(fd_in,"%d %d\n",seq,taps);
      if(rc!=2) break;

      clear<=1; en<=0;
      @(posedge clk);
      clear<=0;

      for(i=0;i<taps;i=i+1) begin
        rc=$fscanf(fd_in,"%d %d\n",a_i,w_i);
        act_code<=a_i[7:0];
        wgt_code<=w_i[7:0];
        en<=1;
        @(posedge clk);
      end
      en<=0;
      @(posedge clk);

      $fdisplay(fd_out,"RESULT seq=%0d sum_qaqw=%0d sum_qa=%0d",seq,sum_qaqw,sum_qa);
    end

    $fclose(fd_in);
    $fclose(fd_out);
    $display("PASS: regression completed");
    $finish;
  end
endmodule
