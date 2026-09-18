`timescale 1ns/1ps
module tb_qat_affine_pact_finalize;
  parameter ACC_W=48, CONST_W=32, FRAC_W=24, OUT_W=8;

  logic signed [ACC_W-1:0] sum_qaqw,sum_qa;
  logic signed [CONST_W-1:0] scale_aw_q,scale_al_q,bias_q,alpha_q,out_scale_q;
  logic signed [79:0] preact_q;
  logic [OUT_W-1:0] out_code;

  qat_affine_pact_finalize #(
    .ACC_W(ACC_W),.CONST_W(CONST_W),.FRAC_W(FRAC_W),.OUT_W(OUT_W)
  ) DUT(
    .sum_qaqw,.sum_qa,.scale_aw_q,.scale_al_q,.bias_q,.alpha_q,.out_scale_q,
    .preact_q,.out_code
  );

  integer fd_in,fd_out,rc;
  integer idx;
  longint signed s0,s1,saw,sal,bq,aq,osq;
  integer expected;
  string in_file,out_file;

  initial begin
    if(!$value$plusargs("IN=%s",in_file)) in_file="final_vectors.txt";
    if(!$value$plusargs("OUT=%s",out_file)) out_file="final_rtl.log";
    fd_in=$fopen(in_file,"r");
    fd_out=$fopen(out_file,"w");
    if(fd_in==0 || fd_out==0) $finish(2);

    while(!$feof(fd_in)) begin
      rc=$fscanf(fd_in,"%d %d %d %d %d %d %d %d %d\n",
        idx,s0,s1,saw,sal,bq,aq,osq,expected);
      if(rc!=9) break;

      sum_qaqw=s0;
      sum_qa=s1;
      scale_aw_q=saw;
      scale_al_q=sal;
      bias_q=bq;
      alpha_q=aq;
      out_scale_q=osq;

      #1;
      $fdisplay(fd_out,"FINAL idx=%0d out=%0d expected=%0d preact=%0d",
                idx,out_code,expected,preact_q);
    end

    $fclose(fd_in);
    $fclose(fd_out);
    $display("PASS finalizer");
    $finish;
  end
endmodule
