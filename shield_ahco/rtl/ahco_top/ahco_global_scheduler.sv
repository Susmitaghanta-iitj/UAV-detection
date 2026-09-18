module ahco_global_scheduler(
 input logic clk,rst_n,start,
 input logic layer_done,
 output logic layer_start,
 output logic [2:0] layer_id,
 output logic finished
);
 typedef enum logic[1:0]{IDLE,LAUNCH,WAIT,DONE} st_t;
 st_t st;

 always_comb begin
  layer_start=(st==LAUNCH);
  finished=(st==DONE);
 end

 always_ff @(posedge clk or negedge rst_n) begin
  if(!rst_n)begin st<=IDLE;layer_id<=0;end
  else case(st)
   IDLE:if(start)begin layer_id<=0;st<=LAUNCH;end
   LAUNCH:st<=WAIT;
   WAIT:if(layer_done)begin
      if(layer_id==6)st<=DONE;
      else begin layer_id<=layer_id+1'b1;st<=LAUNCH;end
   end
   DONE:st<=IDLE;
   default:st<=IDLE;
  endcase
 end
endmodule
