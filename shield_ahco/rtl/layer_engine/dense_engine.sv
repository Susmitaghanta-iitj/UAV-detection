module dense_engine #(parameter ADDR_W=18,DIM_W=16)(
 input logic clk,rst_n,start,input logic [1:0] mode,
 input logic [DIM_W-1:0] din,dout,input logic do_relu,
 output logic feat_req,output logic [ADDR_W-1:0] feat_addr,input logic [7:0] feat_data,
 output logic weight_req,output logic [ADDR_W-1:0] weight_addr,input logic [7:0] weight_data,
 output logic out_we,output logic [ADDR_W-1:0] out_addr,output logic [7:0] out_data,output logic done);
 typedef enum logic[2:0]{IDLE,CLEAR,MAC,FINALIZE,WRITE,NEXT,DONE} st_t; st_t st;
 logic [DIM_W-1:0] i,o; logic mc,me,mf,mv; logic [7:0] mcode,rcode; logic nar; logic signed [71:0] acc;
 shared_tp_mac_top M(.clk,.rst_n,.clear(mc),.en(me),.finalize(mf),.mode,.a_code(feat_data),.b_code(weight_data),
 .valid(mv),.out_code(mcode),.nar_seen(nar),.acc_q32_32(acc));
 relu_tp R(.mode,.in_code(mcode),.out_code(rcode));
 always_comb begin
   feat_req=0;weight_req=0;out_we=0;done=0;mc=0;me=0;mf=0;
   feat_addr=i;weight_addr=o*din+i;out_addr=o;out_data=do_relu?rcode:mcode;
   case(st)
     CLEAR:mc=1; MAC:begin feat_req=1;weight_req=1;me=1;end
     FINALIZE:mf=1; WRITE:out_we=1; DONE:done=1; default:;
   endcase
 end
 always_ff @(posedge clk or negedge rst_n) begin
   if(!rst_n) begin st<=IDLE;i<=0;o<=0;end else case(st)
    IDLE:if(start)begin i<=0;o<=0;st<=CLEAR;end
    CLEAR:st<=MAC;
    MAC:if(i==din-1)begin i<=0;st<=FINALIZE;end else i<=i+1'b1;
    FINALIZE:st<=WRITE; WRITE:st<=NEXT;
    NEXT:if(o==dout-1)st<=DONE;else begin o<=o+1'b1;st<=CLEAR;end
    DONE:st<=IDLE; default:st<=IDLE;
   endcase
 end
endmodule
