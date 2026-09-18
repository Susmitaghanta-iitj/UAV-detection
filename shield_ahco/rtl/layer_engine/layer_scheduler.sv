module layer_scheduler(input logic clk,rst_n,start,input logic[2:0] op,
 input logic conv_done,dense_done,pool_done,
 output logic conv_start,dense_start,pool_start,busy,done);
 typedef enum logic[1:0]{IDLE,RUN,DONE} st_t;st_t st;
 always_comb begin
  conv_start=0;dense_start=0;pool_start=0;busy=(st==RUN);done=(st==DONE);
  if(st==IDLE&&start)case(op)3'd1:conv_start=1;3'd2:dense_start=1;3'd4:pool_start=1;default:;endcase
 end
 always_ff @(posedge clk or negedge rst_n)begin
  if(!rst_n)st<=IDLE;else case(st)IDLE:if(start)st<=RUN;RUN:if(conv_done||dense_done||pool_done)st<=DONE;DONE:st<=IDLE;endcase
 end
endmodule
