module conv1d_engine #(parameter ADDR_W=18,DIM_W=16)(
 input logic clk,rst_n,start,input logic [1:0] mode,
 input logic [DIM_W-1:0] cin,cout,length,input logic [7:0] kernel,stride,padding,input logic do_relu,
 output logic feat_req,output logic [ADDR_W-1:0] feat_addr,input logic [7:0] feat_data,
 output logic weight_req,output logic [ADDR_W-1:0] weight_addr,input logic [7:0] weight_data,
 output logic out_we,output logic [ADDR_W-1:0] out_addr,output logic [7:0] out_data,output logic done);
 typedef enum logic[3:0]{IDLE,CLEAR,LOAD,MAC,FINALIZE,WRITE,ADV,DONE} st_t;st_t st;
 logic[DIM_W-1:0]oc,ic,ox,out_len;logic[7:0]k;
 integer ix;
 logic mc,me,mf,mv,nar;logic[7:0]mcode,rcode;logic signed[71:0]acc;
 assign out_len=((length+(padding<<1)-kernel)/stride)+1;
 always_comb ix = ox*stride + k - padding;
 shared_tp_mac_top M(.clk,.rst_n,.clear(mc),.en(me),.finalize(mf),.mode,
 .a_code((ix<0||ix>=length)?8'h00:feat_data),.b_code(weight_data),.valid(mv),.out_code(mcode),.nar_seen(nar),.acc_q32_32(acc));
 relu_tp R(.mode,.in_code(mcode),.out_code(rcode));
 always_comb begin
  feat_req=0;weight_req=0;out_we=0;done=0;mc=0;me=0;mf=0;
  feat_addr=(ix<0)?'0:ic*length+ix;weight_addr=(oc*cin+ic)*kernel+k;out_addr=oc*out_len+ox;out_data=do_relu?rcode:mcode;
  case(st)CLEAR:mc=1;LOAD:begin if(ix>=0&&ix<length)feat_req=1;weight_req=1;end
   MAC:me=1;FINALIZE:mf=1;WRITE:out_we=1;DONE:done=1;default:;endcase
 end
 always_ff @(posedge clk or negedge rst_n) begin
  if(!rst_n)begin st<=IDLE;oc<=0;ic<=0;ox<=0;k<=0;end else case(st)
   IDLE:if(start)begin oc<=0;ic<=0;ox<=0;k<=0;st<=CLEAR;end
   CLEAR:st<=LOAD; LOAD:st<=MAC;
   MAC:if(k==kernel-1)begin k<=0;if(ic==cin-1)begin ic<=0;st<=FINALIZE;end else begin ic<=ic+1'b1;st<=LOAD;end end
       else begin k<=k+1'b1;st<=LOAD;end
   FINALIZE:st<=WRITE; WRITE:st<=ADV;
   ADV:if(ox==out_len-1)begin ox<=0;if(oc==cout-1)st<=DONE;else begin oc<=oc+1'b1;st<=CLEAR;end end
       else begin ox<=ox+1'b1;st<=CLEAR;end
   DONE:st<=IDLE; default:st<=IDLE;
  endcase
 end
endmodule
