module conv1d_latency1_complete_engine #(
 parameter CIN=1,COUT=4,LENGTH=32,K=3,STRIDE=1,PADDING=1,
 parameter ACC_W=48,CONST_W=32,FRAC_W=24,AW=16
)(
 input logic clk,rst_n,start,
 input logic signed [31:0] scale_aw_q,scale_al_q,alpha_q,out_scale_q,
 output logic in_req, output logic [AW-1:0] in_addr,
 input logic [7:0] in_data,input logic in_valid,
 output logic wgt_req, output logic [AW-1:0] wgt_addr,
 input logic [7:0] wgt_data,input logic wgt_valid,
 output logic bias_req, output logic [$clog2(COUT)-1:0] bias_addr,
 input logic signed [31:0] bias_data,
 output logic out_we,output logic [AW-1:0] out_addr,output logic [7:0] out_code,
 output logic done
);
 localparam OUTL=((LENGTH+2*PADDING-K)/STRIDE)+1;
 typedef enum logic[3:0]{IDLE,CLEAR,ISSUE,WAIT,CONSUME,FINALIZE,WRITE,ADV,DONE} st_t;
 st_t st;
 integer oc,ox,ic,kk,ix;
 logic signed [ACC_W-1:0] s0,s1;
 logic signed [79:0] pre;
 logic [7:0] fin;

 qat_affine_pact_finalize #(.ACC_W(ACC_W),.CONST_W(CONST_W),.FRAC_W(FRAC_W),.OUT_W(8)) F(
  .sum_qaqw(s0),.sum_qa(s1),.scale_aw_q,.scale_al_q,.bias_q(bias_data),
  .alpha_q,.out_scale_q,.preact_q(pre),.out_code(fin));

 always_comb begin
  ix=ox*STRIDE+kk-PADDING;
  in_req=0;wgt_req=0;bias_req=0;out_we=0;done=0;
  in_addr=(ix<0||ix>=LENGTH)?'0:ic*LENGTH+ix;
  wgt_addr=(oc*CIN+ic)*K+kk;
  bias_addr=oc;out_addr=oc*OUTL+ox;out_code=fin;
  case(st)
   ISSUE:begin if(ix>=0&&ix<LENGTH)in_req=1;wgt_req=1;end
   FINALIZE:bias_req=1;
   WRITE:begin bias_req=1;out_we=1;end
   DONE:done=1;
   default:;
  endcase
 end

 always_ff @(posedge clk or negedge rst_n) begin
  if(!rst_n)begin st<=IDLE;oc<=0;ox<=0;ic<=0;kk<=0;s0<=0;s1<=0;end
  else case(st)
   IDLE:if(start)begin oc<=0;ox<=0;ic<=0;kk<=0;st<=CLEAR;end
   CLEAR:begin s0<=0;s1<=0;st<=ISSUE;end
   ISSUE:begin
     if(ix<0||ix>=LENGTH) st<=CONSUME;
     else st<=WAIT;
   end
   WAIT:if(in_valid&&wgt_valid)st<=CONSUME;
   CONSUME:begin
     if(ix>=0&&ix<LENGTH)begin s0<=s0+in_data*wgt_data;s1<=s1+in_data;end
     if(kk==K-1)begin kk<=0;if(ic==CIN-1)begin ic<=0;st<=FINALIZE;end else begin ic<=ic+1;st<=ISSUE;end end
     else begin kk<=kk+1;st<=ISSUE;end
   end
   FINALIZE:st<=WRITE;
   WRITE:st<=ADV;
   ADV:begin
    if(ox==OUTL-1)begin ox<=0;if(oc==COUT-1)st<=DONE;else begin oc<=oc+1;st<=CLEAR;end end
    else begin ox<=ox+1;st<=CLEAR;end
   end
   DONE:st<=IDLE;
   default:st<=IDLE;
  endcase
 end
endmodule
