module maxpool1d_engine #(parameter ADDR_W=18,DIM_W=16)(
 input logic clk,rst_n,start,input logic [1:0] mode,
 input logic [DIM_W-1:0] channels,length,input logic [7:0] kernel,stride,
 output logic feat_req,output logic [ADDR_W-1:0] feat_addr,input logic [7:0] feat_data,
 output logic out_we,output logic [ADDR_W-1:0] out_addr,output logic [7:0] out_data,output logic done);
 typedef enum logic[2:0]{IDLE,LOAD,CMP,WRITE,ADV,DONE} st_t;st_t st;
 logic [DIM_W-1:0] c,ox,out_len;logic[7:0] k,best;logic bn,cn;logic signed[31:0] bv,cv;
 assign out_len=((length-kernel)/stride)+1;
 tp_decode DB(.mode,.code(best),.is_nar(bn),.value_q16_16(bv));
 tp_decode DC(.mode,.code(feat_data),.is_nar(cn),.value_q16_16(cv));
 always_comb begin
  feat_req=0;out_we=0;done=0;feat_addr=c*length+ox*stride+k;out_addr=c*out_len+ox;out_data=best;
  if(st==LOAD)feat_req=1;if(st==WRITE)out_we=1;if(st==DONE)done=1;
 end
 always_ff @(posedge clk or negedge rst_n) begin
  if(!rst_n)begin st<=IDLE;c<=0;ox<=0;k<=0;best<=0;end else case(st)
   IDLE:if(start)begin c<=0;ox<=0;k<=0;st<=LOAD;end
   LOAD:st<=CMP;
   CMP:begin if(k==0||(!cn&&(bn||cv>bv)))best<=feat_data;
       if(k==kernel-1)begin k<=0;st<=WRITE;end else begin k<=k+1'b1;st<=LOAD;end end
   WRITE:st<=ADV;
   ADV:if(ox==out_len-1)begin ox<=0;if(c==channels-1)st<=DONE;else begin c<=c+1'b1;st<=LOAD;end end
       else begin ox<=ox+1'b1;st<=LOAD;end
   DONE:st<=IDLE; default:st<=IDLE;
  endcase
 end
endmodule
